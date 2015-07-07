import actions
import events
import utils

def keeper_of_the_grove(game, trigger, id):
    if trigger[0] == 'summon' and trigger[1] == id:
        choice = events.pick(game, ['Deal 2 damage', 'Silence a minion'])
        if choice == 0:
            target_id = target(game)
            game.action_queue.append((events.deal_damage, (game, target_id, 2)))
        else:
            target_id = target(game)
            game.action_queue.append((events.silence, (game, target_id)))
        return True
            