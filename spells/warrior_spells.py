import events

from spell_utils import *

class Charge(TargetAllyMinionSpell):
    def execute(self, **params):
        game = self.game
        minion = game.minion_pool[params['target_id']]
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
