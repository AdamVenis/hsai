import actions
import events
import utils

def flame_leviathan(game, trigger, id):
    if trigger[0] == 'draw' and id in trigger[1:]:
        for minion_id in game.minion_pool:
            game.add_event(events.deal_damage, (minion_id, 2))


def mana_worm(game, trigger, id):
    if trigger[0] == 'cast_spell' and game.minion_pool[id].owner == game.player:
        game.minion_pool[id].current_attack += 1


def snowchugger(game, trigger, id):
    if trigger[0] == 'attack' and id in trigger[1:]:
        enemy = game.minion_pool[filter(lambda x:x != id, trigger[1:])[0]]
        enemy.attacks_left = 0
        enemy.mechanics.add('Frozen')


def water_elemental(game, trigger, id):
    if trigger[0] == 'attack' and id in trigger[1:]:
        enemy = game.minion_pool[filter(lambda x:x != id, trigger[1:])[0]]
        enemy.attacks_left = 0
        enemy.mechanics.add('Frozen')