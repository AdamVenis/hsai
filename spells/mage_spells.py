# don't import * here so locals() stays clean
import actions
import card_data
import events
import utils

def arcane_missiles(game):
    for i in range(3 + game.player.spellpower):
        game.add_event(events.deal_damage, 
            (game.choice([m.minion_id for m in game.enemy.board], random=True), 1))


def arcane_explosion(game):
    for minion in game.enemy.board[1:]:
        game.add_event(events.deal_damage, (minion.minion_id, 1 + game.player.spellpower))


def arcane_intellect(game):
    for i in range(2):
        game.add_event(events.draw, (game.player,))


def fireball(game):
    target_id = events.target(game)
    game.add_event(events.deal_damage, (target_id, 6 + game.player.spellpower))


def polymorph(game):  # TODO: this needs validation (cannot target heroes)
    target_id = events.target(game,
            [minion.minion_id for minion in game.player.board[1:]] + 
            [minion.minion_id for minion in game.enemy.board[1:]])
    events.silence(game, target_id)
    minion = game.minion_pool[target_id]
    chicken = utils.Minion(game, card_data.get_card('Chicken', game.player))
    minion.transform_into(chicken)
