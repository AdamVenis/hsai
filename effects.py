import Hearthstone

effects = {}

def loot_hoarder(game, trigger, id): #id gets partially applied when effect is created
   if len(trigger) == 2 and trigger[0] == 'kill_minion' and trigger[1] == id:
      Hearthstone.draw(game.minion_pool[id].owner)
      return True
   return False
effects['Loot Hoarder'] = loot_hoarder

def novice_engineer(game, trigger, id):
   if len(trigger) == 2 and trigger[0] == 'battlecry' and trigger[1] == id:
      Hearthstone.draw(game.player)
      return True
   return False
effects['Novice Engineer'] = novice_engineer  

'''def healing_totem(game, trigger, id):
   if len(trigger) == 1 and trigger[0] == 'end_turn':
      for minion in game.player.board[1:]:
         heal'''
   
def druid(game, trigger):
   if len(trigger) == 1 and trigger[0] == 'end_turn':
      game.player.board[0].attack -= 1
      return True
   return False
effects['Druid'] = druid

