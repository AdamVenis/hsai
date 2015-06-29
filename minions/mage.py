import hsai.actions
import hsai.events
import hsai.utils

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