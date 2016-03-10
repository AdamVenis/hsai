from __future__ import print_function

from utils import *
import events
from card_types import MinionCard, SpellCard, WeaponCard
import minions.minion_effects
import spells.spell_effects as spell_effects
import card_data

import inspect

class Action():
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
        game.logger.info('WINNER: %s' % 'P2' if game.player == game.player1 else 'P1')
        if game.player == game.player1:
            game.winner = 2
        else:
            game.winner = 1

@lazy
class Summon(Action):
    def __init__(self, game, action_string):
        params = action_string.split()
        if len(params) not in [2, 3]:
            raise Exception(
                'SUMMON requires exactly one or two additional arguments')
        index = int(params[1])
        if index not in range(len(game.player.hand)):
            raise Exception('Must SUMMON a valid index from your hand')
        if not isinstance(game.player.hand[index], MinionCard):
            raise Exception('Must SUMMON a Minion type card')
        if game.player.hand[index].cost(game) > game.player.current_crystals:
            raise Exception('Insufficient funds')
        self.index = index

        if len(params) == 3:
            position = int(params[2])
            if position not in range(len(game.player.board)):
                raise Exception('Must provide a valid position to be summoned')
            self.position = position
        else:
            self.position = len(game.player.board) - 1
        
    def execute(self, game):
        game.logger.info('SUMMON %d' % self.index)
        card = game.player.hand[self.index]
        print('Player %d summons %s' % ((game.turn % 2) + 1, card.name))
        game.player.current_crystals -= card.cost(game)
        del game.player.hand[self.index]
        minion = events.spawn(game, game.player, card, self.position)
        trigger_effects(game, ['battlecry', minion.minion_id])
        trigger_effects(game, ['summon', minion.minion_id])

@lazy
class Attack(Action):
    # either action_string is supplied, or source_id and target_id are supplied
    # for things like rogue 'attack the minion next to you'. maybe not
    # necessary if deal_damage gets a source
    def __init__(self, game, action_string='', source_id=None, target_id=None):
        if action_string:
            params = action_string.split()
            if len(params) != 3:
                raise Exception('ATTACK requires exactly two additional arguments')
            source_index = int(params[1])
            target_index = int(params[2])
            if not (0 <= source_index < len(game.player.board)):
                raise Exception('Invalid source index')
            if not (0 <= target_index < len(game.enemy.board)):
                raise Exception('Invalid target index')
            # TODO(adamvenis): make sure you can't attack stealth,
            # or nontaunt when taunt exists
            ally_minion = game.player.board[source_index]
            enemy_minion = game.enemy.board[target_index]
            
            if ally_minion.attacks_left <= 0:
                raise Exception('This minion cannot attack')
            if ally_minion.attack <= 0:
                raise Exception('This minion has no attack')
            if 'Frozen' in ally_minion.mechanics or 'Thawing' in ally_minion.mechanics:
                raise Exception('This minion is frozen, and cannot attack')
            if 'Stealth' in enemy_minion.mechanics:
                raise Exception('Cannot attack a minion with stealth')
            if 'Taunt' not in enemy_minion.mechanics and any('Taunt' in minion.mechanics for minion in game.enemy.board[1:]):
                raise Exception('Must target a minion with taunt')

            self.ally_id = ally_minion.minion_id
            self.enemy_id = enemy_minion.minion_id
        else:
            self.ally_id = source_id
            self.enemy_id = target_id
        
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

@lazy
class Cast(Action):

    def __init__(self, game, action_string):
        params = action_string.split()
        if len(params) != 2:
            raise Exception('CAST requires exactly one additional argument')
        index = int(params[1])
        if not (0 <= index < len(game.player.hand)):
            raise Exception('Must CAST a valid index from your hand')
        card = game.player.hand[index]
        if not isinstance(card, SpellCard):
            raise Exception('Must CAST a Spell type card')
        if card.cost(game) > game.player.current_crystals:
            raise Exception('Insufficient funds')
        self.index = index
        self.spell_card = card
        self.spell_class = spell_effects.__dict__.get(card.name.replace(' ', ''))

    def execute(self, game, agent):
        trigger_effects(game, ['cast_spell', self.spell_card])
        game.logger.info('CAST %d' % self.index)
        game.player.current_crystals -= self.spell_card.cost(game)
        del game.player.hand[self.index]
        spell = self.spell_class(game)
        params = agent.spell_params(game, spell)
        print('Player %d casts %s with params %s' % ((game.turn % 2) + 1, self.spell_card.name, params))
        spell.execute(**params)


class HeroPower(Action):
    def __init__(self, game):
        if game.player.current_crystals < 2:
            raise Exception('not enough mana!')
        elif not game.player.can_hp:
            raise Exception('can only use this once per turn!')            

    def execute(self, game, agent):
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
