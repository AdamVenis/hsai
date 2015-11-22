import actions
import events
import utils

def armorsmith(game, trigger, id):
    if trigger[0] == 'deal_damage' and game.minion_pool[trigger[1]] in game.minion_pool[id].owner.board[1:]:
        game.minion_pool[id].owner.armor += 1


