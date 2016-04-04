from actions import parse_action
from heroes import *
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

        return parse_action(game, raw_input())

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
            return None
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
