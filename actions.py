from __future__ import print_function

from utils import *
import events
import spells.spell_effects as spell_effects

import inspect

class Action(): # lawsuit!
    def execute(self, game):
        raise NotImplementedError


class End(Action):
    def __init__(self):
        # TODO validation that the string is precisely 'END'?
        pass
    
    def execute(self, game):
        print('Player %d ends their turn' % ((game.turn % 2) + 1))
        game.logger.info('END_TURN')
        trigger_effects(game, ['end_turn', game.player])
        game.turn += 1
        game.enemy, game.player = game.player, game.enemy        
        events.start_turn(game)


class Concede(Action):
    def __init__(self):
        pass

    def execute(self, game):
        print('Player %d concedes' % ((game.turn % 2) + 1))
        game.logger.info('WINNER: %s' % ('P2' if game.player == game.player1 else 'P1'))
        if game.player == game.player1:
            game.winner = 2
        else:
            game.winner = 1

class Summon(Action):
    def __init__(self, game, index, position=None):
        self.index = index
        self.position = position or len(game.player.board) - 1
        
    def execute(self, game):
        game.logger.info('SUMMON %d' % self.index)
        card = game.player.hand[self.index]
        print('Player %d summons %s' % ((game.turn % 2) + 1, card.name))
        game.player.current_crystals -= card.cost(game)
        del game.player.hand[self.index]
        minion = events.spawn(game, game.player, card, self.position)
        trigger_effects(game, ['battlecry', minion.minion_id])
        trigger_effects(game, ['summon', minion.minion_id])

class Attack(Action):
    # either action_string is supplied, or source_id and target_id are supplied
    # for things like rogue 'attack the minion next to you'. maybe not
    # necessary if deal_damage gets a source
    def __init__(self, game, source, target):
        if source >= 1000: # for when supplied source is an id instead of a hand index
            # TODO: only allow ids, fix golden replay for this
            self.ally_id = source
            self.enemy_id = target
        else:
            self.ally_id = game.player.board[source].minion_id
            self.enemy_id = game.enemy.board[target].minion_id
        
    def execute(self, game):
        game.logger.info('ATTACK %d %d' % (self.ally_id, self.enemy_id))
        trigger_effects(game, ['attack', self.ally_id, self.enemy_id])
        ally_minion = game.minion_pool[self.ally_id]
        enemy_minion = game.minion_pool[self.enemy_id]
        print('Player %d attacks %s with %s' % ((game.turn % 2) + 1, enemy_minion.name, ally_minion.name))

        if ally_minion == ally_minion.owner.board[0] and game.player.weapon:
            game.player.weapon.durability -= 1
            if game.player.weapon.durability == 0:
                game.player.weapon = None

        if 'Stealth' in ally_minion.mechanics:
            ally_minion.mechanics.remove('Stealth')

        ally_minion.attacks_left -= 1

        if 'Divine Shield' in enemy_minion.mechanics:
            enemy_minion.mechanics.remove('Divine Shield')
        else:
            damage = ally_minion.attack
            if damage > 0:
                game.add_event(events.deal_damage, (self.enemy_id, damage))

        if 'Divine Shield' in ally_minion.mechanics:
            ally_minion.mechanics.remove('Divine Shield')
        else:
            damage = enemy_minion.attack
            # TODO(adamvenis): is this check necessary? it claims that attacking into a hero with
            # attack will cause your attacking minion to take damage
            if enemy_minion == enemy_minion.owner.board[0] and enemy_minion.owner.weapon is not None:
                damage -= enemy_minion.owner.weapon.attack
            if damage > 0:
                game.add_event(events.deal_damage, (self.ally_id, damage))

class Cast(Action):

    def __init__(self, game, index):
        self.index = index
        self.spell_card = game.player.hand[index]
        self.spell = spell_effects.__dict__.get(self.spell_card.name.replace(' ', ''))(game)

    def execute(self, game, agent=None, params=None):
        # one of agent or params must be provided
        trigger_effects(game, ['cast_spell', self.spell_card])
        game.player.current_crystals -= self.spell_card.cost(game)
        del game.player.hand[self.index]
        if params is None:
            params = agent.spell_params(game, self.spell)
        print('Player %d casts %s with params %s' % ((game.turn % 2) + 1, self.spell_card.name, params))
        game.logger.info('CAST %d' % self.index) # TODO: add params here
        self.spell.execute(**params)


class HeroPower(Action):
    def __init__(self):
        pass

    def execute(self, game, agent=None, params=None):
        # one of agent or params must be provided
        game.logger.info('HERO POWER')
        trigger_effects(game, ['hero_power'])
        game.player.can_hp = False
        game.player.current_crystals -= 2
        params = agent.hero_power_params(game)
        print('Player %d uses hero power with params %s' % ((game.turn % 2) + 1, params))
        game.player.hero.power(**params)


def parse_action(game, input):

    input = input.lower()
    if input.startswith('summon'):
        return Summon(game, input)
    elif input.startswith('attack'):
        return Attack(game, input)
    elif input.startswith('cast'):
        return Cast(game, input)
    elif input.startswith('hero'):
        return HeroPower(game)
    elif input.startswith('end'):
        return End()
    elif input.startswith('concede'):
        return Concede()
    else:
        print('invalid input ', input)
        return Action()
