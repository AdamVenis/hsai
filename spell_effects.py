# NB: keep in alphabetical order

import actions
# can't import * from here cause locals() is used below, and it needs to
# be kept clean
import events
import utils


def arcane_missiles(game):
    for i in range(3 + game.player.spellpower):
        game.action_queue.append(
            (events.deal_damage, (game, game.choice(game.enemy.board, random = True).minion_id, 1)))


def arcane_explosion(game):
    for minion in game.enemy.board[1:]:
        game.action_queue.append(
            (events.deal_damage, (game, minion.minion_id, 1 + game.player.spellpower)))


def arcane_intellect(game):
    for i in range(2):
        game.action_queue.append((events.draw, (game, game.player,)))


def fireball(game):
    target_id = events.target(game)
    game.action_queue.append(
        (events.deal_damage, (game, target_id, 6 + game.player.spellpower)))


def polymorph(game):  # TODO: this needs validation (cannot target heroes)
    target_id = events.target(game, [minion.minion_id for minion in game.player.board[1:]] + 
            [minion.minion_id for minion in game.enemy.board[1:]])
    events.silence(game, target_id)
    minion = game.minion_pool[target_id]
    chicken = utils.Minion(game, card_data.get_card('Chicken'))
    minion.transform_into(chicken)


def the_coin(game):
    game.player.current_crystals += 1  # should this be capped at 10?

exceptions = ['actions', 'utils', 'exceptions', 'hunters_mark']
spell_effects = {utils.func_to_name(key): val for key, val in locals(
).items() if key[0] != '_' and key not in exceptions}
# spell_effects["Hunter's Mark"] = hunters_mark # this is an example of
# how exceptions work
