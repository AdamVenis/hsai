from utils import *
from events import deal_damage, draw, heal, spawn, start_turn, target
from card_types import MinionCard, SpellCard, WeaponCard
import minions.minion_effects
import spell_effects
import card_data

class Action():
    def execute(self, game):
        pass


class End(Action):
    def __init__(self):
        # TODO validation that the string is precisely "END"?
        pass
    
    def execute(self, game):
        game.logger.info('END_TURN')
        trigger_effects(game, ['end_turn', game.player])
        game.turn += 1
        game.enemy, game.player = game.player, game.enemy        
        start_turn(game)


class Concede(Action):
    def __init__(self):
        pass

    def execute(self, game):
        game.logger.info('WINNER: %s' % 'P2' if game.player == game.player1 else 'P1')
        if game.player == game.player1:
            game.winner = 2
        else:
            game.winner = 1

@lazy
class Summon(Action):
    def __init__(self, game, action_string):
        params = action_string.split()
        if len(params) != 2:
            raise Exception("SUMMON requires exactly one additional argument")
        index = int(params[1])
        if not (0 <= index < len(game.player.hand)):
            raise Exception("Must SUMMON a valid index from your hand")
        if not isinstance(game.player.hand[index], MinionCard):
            raise Exception("Must SUMMON a Minion type card")
        if game.player.hand[index].cost(game) > game.player.current_crystals:
            raise Exception("Insufficient funds")
        self.index = index
        
    def execute(self, game):
        game.logger.info('SUMMON %d' % self.index)
        card = game.player.hand[self.index]
        game.player.current_crystals -= card.cost(game)
        del game.player.hand[self.index]
        minion = spawn(game, game.player, card)
        trigger_effects(game, ['battlecry', minion.minion_id])

@lazy
class Attack(Action):
    # either action_string is supplied, or source_id and target_id are supplied
    def __init__(self, game, action_string="", source_id=None, target_id=None):
        if action_string:
            params = action_string.split()
            if len(params) != 3:
                raise Exception("ATTACK requires exactly two additional arguments")
            source_index = int(params[1])
            target_index = int(params[2])
            if not (0 <= source_index < len(game.player.board)):
                raise Exception("Invalid source index")
            if not (0 <= target_index < len(game.enemy.board)):
                raise Exception("Invalid target index")
            # TODO(adamvenis): make sure you can't attack stealth,
            # or nontaunt when taunt exists
            ally_minion = game.player.board[source_index]
            enemy_minion = game.enemy.board[target_index]
            
            if ally_minion.attacks_left <= 0:
                raise Exception("This minion cannot attack")
            if ally_minion.attack <= 0:
                raise Exception("This minion has no attack")
            if 'Frozen' in ally_minion.mechanics or 'Thawing' in ally_minion.mechanics:
                raise Exception("This minion is frozen, and cannot attack")
            if 'Stealth' in enemy_minion.mechanics:
                raise Exception("Cannot attack a minion with stealth")
            if 'Taunt' not in enemy_minion.mechanics and any('Taunt' in minion.mechanics for minion in game.enemy.board[1:]):
                raise Exception("Must target a minion with taunt")

            self.ally_id = ally_minion.minion_id
            self.enemy_id = enemy_minion.minion_id
        else:
            self.ally_id = source_id
            self.enemy_id = target_id
        
    def execute(self, game):
        game.logger.info('ATTACK %d %d' % (self.ally_id, self.enemy_id))
        ally_minion = game.minion_pool[self.ally_id]
        enemy_minion = game.minion_pool[self.enemy_id]

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
                game.action_queue.append((deal_damage, (game, self.enemy_id, damage)))

        if 'Divine Shield' in ally_minion.mechanics:
            ally_minion.mechanics.remove('Divine Shield')
        else:
            damage = enemy_minion.attack
            # TODO(adamvenis): is this check necessary? it claims that attacking into a hero with
            # attack will cause your attacking minion to take damage
            if enemy_minion == enemy_minion.owner.board[0] and enemy_minion.owner.weapon is not None:
                damage -= enemy_minion.owner.weapon.attack
            if damage > 0:
                game.action_queue.append((deal_damage, (game, self.ally_id, damage)))        

@lazy
class Cast(Action):

    def __init__(self, game, action_string):
        params = action_string.split()
        if len(params) != 2:
            raise Exception("CAST requires exactly one additional argument")
        index = int(params[1])
        print game.player.hand, index
        if not (0 <= index < len(game.player.hand)):
            raise Exception("Must CAST a valid index from your hand")
        if not isinstance(game.player.hand[index], SpellCard):
            raise Exception("Must CAST a Spell type card")
        if game.player.hand[index].cost(game) > game.player.current_crystals:
            raise Exception("Insufficient funds")
        self.index = index
        
    def execute(self, game):
        game.logger.info('CAST %d' % self.index)
        spell_card = game.player.hand[self.index]
        game.player.current_crystals -= spell_card.cost(game)
        del game.player.hand[self.index]
        spell_effects.__dict__[name_to_func(spell_card.name)](game)


class HeroPower(Action):
    def __init__(self, game):
        pass

    def execute(self, game):
        hero_power(game) # TODO: inline this
        
#these lowercase functions are deprecated
def summon(game, player, index):  # specifically for summoning from hand

    card = player.hand[index]
    player.current_crystals -= card.cost(game)
    del player.hand[index]
    minion = spawn(game, player, card)
    trigger_effects(game, ['battlecry', minion.minion_id])


def attack(game, ally_index, enemy_index):
    ally_minion = game.player.board[ally_index]
    enemy_minion = game.enemy.board[enemy_index]

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
            game.action_queue.append(
                (deal_damage, (game, enemy_minion.minion_id, ally_minion.attack)))

    if 'Divine Shield' in ally_minion.mechanics:
        ally_minion.mechanics.remove('Divine Shield')
    else:
        damage = enemy_minion.attack
        if enemy_minion == enemy_minion.owner.board[0] and enemy_minion.owner.weapon is not None:
            damage -= enemy_minion.owner.weapon.attack
        if damage > 0:
            game.action_queue.append(
                (deal_damage, (game, ally_minion.minion_id, damage)))


def cast_spell(game, index):
    
    spell_card = game.player.hand[index]
    # assumes spells can only be played on your turn
    game.player.current_crystals -= spell_card.cost(game)
    del game.player.hand[index]
    spell_effects.__dict__[name_to_func(spell_card.name)](game)


def hero_power(game):
  
    if game.player.current_crystals < 2:
        print 'not enough mana!'
        return
    elif not game.player.can_hp:
        print 'can only use this once per turn!'
        return

    h = game.player.hero.lower()
    if h == 'hunter':
        game.action_queue.append(
            (deal_damage, (game, game.enemy.board[0].minion_id, 2)))
    elif h == 'warrior':
        game.player.armor += 2
    elif h == 'shaman':
        totems = ['Healing Totem', 'Searing Totem',
                  'Stoneclaw Totem', 'Wrath of Air Totem']
        for minion in game.player.board:
            if minion.name in totems:
                totems.remove(minion.name)
        if totems:  # not all have been removed
            game.action_queue.append(
                (spawn, (game, game.player, card_data.get_card(game.choice(totems, random=True), game.player))))
        else:
            print 'all totems have already been summoned!'
            return
    elif h == 'mage':
        target_id = target(game)
        game.action_queue.append((deal_damage, (game, target_id, 1)))
    elif h == 'warlock':
        game.action_queue.append((deal_damage, (game, game.player.board[0].minion_id, 2)))
        game.action_queue.append((draw, (game, game.player)))
    elif h == 'rogue':
        game.player.weapon = Weapon(game, 1, 2)
    elif h == 'priest':
        target_id = target(game)
        game.action_queue.append((heal, (game, target_id, 2)))
    elif h == 'paladin':
        game.action_queue.append(
            (summon, (game, game.player, card_data.get_card('Silver Hand Recruit'))))
    elif h == 'druid':
        game.player.armor += 1
        game.player.board[0].attack += 1
        game.effect_pool.append(minion_effects.minion_effects['Druid'])
    game.player.can_hp = False
    game.player.current_crystals -= 2
