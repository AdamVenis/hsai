from actions import parse_action
from heroes import *
import events
import spells.spell_effects as spells

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
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.player.board] + 
                                      [minion.minion_id for minion in game.enemy.board])}
        else:
            return None

    def spell_params(self, game, spell):

        if isinstance(spell, spells.SimpleSpell):
            return None
        elif isinstance(spell, spells.TargetAllyMinionSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.ALLY_MINIONS])}
        elif isinstance(spell, spells.TargetCharacterSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.ALL_CHARACTERS])}
        elif isinstance(spell, spells.TargetEnemyMinionSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.ENEMY_MINIONS])}
        elif isinstance(spell, spells.TargetMinionSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.ALL_MINIONS])}
        else:
            return None
