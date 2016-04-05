from actions import *
from heroes import *
from card_types import MinionCard, SpellCard, WeaponCard
import events
import spells.spell_effects as spells

from random import choice

class HumanAgent():

    def __init__(self):

        pass

    def pick_hero(self):

        hero = raw_input('Choose your class: ')
        while hero.lower() not in ['warrior', 'hunter', 'mage', 'warlock',
                                   'shaman', 'rogue', 'priest', 'paladin', 'druid']:
            hero = raw_input('Not a valid hero! Choose again. ')
        return globals()[hero.capitalize()]

    def mulligan(self, game, player):
        # returns a list of ints

        hand_size = 3 if player == game.player else 4
        shown_cards = player.deck[:hand_size]
        print('Your cards are %s' % shown_cards)
        mulligans = raw_input('Indicate which cards you want shuffled back by typing space delimited indices.\n')
        while not all(0 <= int(index) < len(shown_cards) for index in mulligans.split()):
            mulligans = raw_input('Invalid input! Try again.')
        return map(int, mulligans.split())

    def move(self, game):
        input = raw_input().lower()
        tokens = input.split()

        if input.startswith('summon '):
            if len(tokens) not in [2,3]:
                raise Exception(
                    'SUMMON requires exactly one or two additional arguments')
            index = int(tokens[1])
            if index not in range(len(game.player.hand)):
                raise Exception('Must SUMMON a valid index from your hand')
            if not isinstance(game.player.hand[index], MinionCard):
                raise Exception('Must SUMMON a Minion type card')
            if game.player.hand[index].cost(game) > game.player.current_crystals:
                raise Exception('Insufficient funds')

            if len(tokens) == 3:
                position = int(tokens[2])
                if position not in range(len(game.player.board)):
                    raise Exception('Must provide a valid position to be summoned')
            else:
                position = len(game.player.board) - 1

            return Summon(game, index, position)

        elif input.startswith('attack'):
            if len(tokens) != 3:
                raise Exception('ATTACK requires exactly two additional arguments')
            source_index = int(tokens[1])
            target_index = int(tokens[2])
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

            return Attack(game, ally_minion.minion_id, enemy_minion.minion_id)

        elif input.startswith('cast'):
            if len(tokens) != 2:
                raise Exception('CAST requires exactly one additional argument')
            index = int(tokens[1])
            if not (0 <= index < len(game.player.hand)):
                raise Exception('Must CAST a valid index from your hand')
            card = game.player.hand[index]
            if not isinstance(card, SpellCard):
                raise Exception('Must CAST a Spell type card')
            if card.cost(game) > game.player.current_crystals:
                raise Exception('Insufficient funds')

            return Cast(game, index)

        elif input.startswith('hero'):

            if game.player.current_crystals < 2:
                raise Exception('not enough mana!')
            elif not game.player.can_hp:
                raise Exception('can only use this once per turn!')

            return HeroPower()

        elif input.startswith('end'):
            return End()
        elif input.startswith('concede'):
            return Concede()
        else:
            print('invalid input ', input)
            return Action()


    def hero_power_params(self, game):

        if isinstance(game.player.hero, SimpleHero):
            return None
        elif isinstance(game.player.hero, TargetCharacterHero):
            legal_params = game.player.hero.legal_params()
            while True:
                # TODO: move events.target into human_agent
                params = {'target_id': events.target(game)}
                if params in legal_params:
                    return params
                else:
                    print('Invalid hero power parameters. Try again.')
        else:
            return None

    def spell_params(self, game, spell):

        if isinstance(spell, spells.SimpleSpell):
            return {}
        elif isinstance(spell, spells.RandomSpell):
            # TODO: this shouldn't need to be specified here
            # i.e. don't give agents explicit control of randomness
            return choice(spell.legal_params())
        elif isinstance(spell, spells.Spell):
            legal_params = spell.legal_params()
            while True:
                params = {'target_id': events.target(game)}
                if params in legal_params:
                    return params
                else:
                    print('Invalid spell parameters. Try again.')
        else:
            return None
