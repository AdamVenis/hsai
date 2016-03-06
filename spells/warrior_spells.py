import actions
import card_data
import events
import utils

from spell_utils import *

class Charge(SimpleSpell):
    def execute(self, **params):
        game = self.game
        target_id = events.target(game, [minion.minion_id for minion in game.player.board[1:]])
        minion = game.minion_pool[target_id]
        minion.current_attack += 2
        minion.mechanics.append('Charge')

class ShieldBlock(SimpleSpell):
    def execute(self, **params):
        game = self.game
        game.player.armor += 5
        game.add_event(events.draw, (game.player,))

class Whirlwind(SimpleSpell):
    def execute(self, **params):
        game = self.game
        for minion in game.player.board[1:] + game.enemy.board[1:]:
            game.add_event(events.deal_damage, (minion.minion_id, 1 + game.player.spellpower))
