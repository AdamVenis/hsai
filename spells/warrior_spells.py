import actions
import card_data
import events
import utils

from spell_utils import *

def charge(game):
    target_id = events.target(game, [minion.minion_id for minion in game.player.board[1:]])
    minion = game.minion_pool[target_id]
    minion.current_attack += 2
    minion.mechanics.append('Charge')


def shield_block(game):
    game.player.armor += 5
    game.add_event(events.draw, (game.player,))


def whirlwhind(game):
    for minion in game.player.board[1:] + game.enemy.board[1:]:
        game.add_event(events.deal_damage, (minion.minion_id, 1 + game.player.spellpower))
    