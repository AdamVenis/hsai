
import actions
import card_data
import events
import utils

def charge(game):
    target_id = events.target(game, [minion.minion_id for minion in game.player.board[1:]])
    minion = game.minion_pool[target_id]
    minion.current_attack += 2
    minion.mechanics.append('Charge')


def shield_block(game):
    game.player.armor += 5
    game.action_queue.append((events.draw, (game, game.player)))


def whirlwhind(game):
    for minion in game.player.board[1:] + game.enemy.board[1:]:
        game.action_queue.append(
            (events.deal_damage, (game, minion.minion_id, 1 + game.player.spellpower)))
    