import actions
import events
import utils

def keeper_of_the_grove(game, trigger, id):
    if trigger[0] == 'summon' and trigger[1] == id:
        choice = events.pick(game, ['Deal 2 damage', 'Silence a minion'])
        if choice == 0:
            target_id = target(game)
            game.add_event(events.deal_damage, (target_id, 2))
        else:
            target_id = target(game)
            game.add_event(events.silence, (target_id,))
        return True
            