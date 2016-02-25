# don't import * here so locals() stays clean
import actions
import card_data
import events
import utils

from spell_utils import *

def arcane_missiles(game):
    for i in range(3 + game.player.spellpower):
        game.add_event(events.deal_damage, 
            (game.choice([m.minion_id for m in game.enemy.board], random=True), 1))


def arcane_explosion(game):
    for minion in game.enemy.board[1:]:
        game.add_event(events.deal_damage,
                       (minion.minion_id, 1 + game.player.spellpower))


def arcane_intellect(game):
    for i in range(2):
        game.add_event(events.draw, (game.player,))


def fireball(game):
    target_id = events.target(game)
    game.add_event(events.deal_damage, (target_id, 6 + game.player.spellpower))

class Polymorph(TargetMinionSpell):
    id = 'CS2_022'
    def execute(self, **params):
        events.silence(self.game, params['target_id'])
        minion = self.game.minion_pool[params['target_id']]
        chicken = utils.Minion(self.game, card_data.get_card('Sheep', self.game.player))
        minion.transform_into(chicken)