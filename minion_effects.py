#alphabetical order!

import Hearthstone
import events
import utils

def acolyte_of_pain(game, trigger, id):
   if trigger[0] == 'deal_damage' and trigger[1] == id:
      events.draw(game.minion_pool[id].owner)

'''def amani_berserker(game, trigger, id): # this is probably wrong in conjunction with Auchenai Soulpriest
   minion = game.minion_pool[id]
   if trigger[0] == 'deal_damage' and trigger[1] == id:
      minion.attack += 3
   elif trigger[0] == 'heal' and trigger[1] == id and minion.health < minion.max_health and minion.health + trigger[2] >= minion.max_health:
      minion.attack -= 3
effects['Amani Berserker'] = amani_berserker''' #work in progress

def arcane_golem(game, trigger, id):
   if trigger[0] == 'battlecry' and trigger[1] == id:
      game.enemy.crystals += 1
      return True

def armorsmith(game, trigger, id):
   if trigger[0] == 'deal_damage' and game.minion_pool[trigger[1]] in game.minion_pool[id].owner.board[1:]:
      game.minion_pool[id].owner.armor += 1

def cairne_bloodhoof(game, trigger, id):
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      game.event_queue.append((events.spawn, (game, game.minion_pool[id].owner, Hearthstone.get_card('Baine Bloodhoof'))))
      return True

def druid(game, trigger, player): # hero power (TODO: this doesn't belong in this file)
   if trigger[0] == 'end_turn':
      game.player.board[0].attack -= 1
      return True

def earthen_ring_farseer(game, trigger, id):
   if trigger[0] == 'battlecry' and trigger[1] == id:
      target_id = Hearthstone.target(game)
      game.event_queue.append((events.heal, (game, target_id, 3)))
      return True
   return False

def gnomish_inventor(game, trigger, id):
   if trigger[0] == 'battlecry' and trigger[1] == id:
      events.draw(game.player)
      return True

def harvest_golem(game, trigger, id):
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      game.event_queue.append((events.spawn, (game, game.minion_pool[id].owner, Hearthstone.get_card('Damaged Golem'))))
      return True

def healing_totem(game, trigger, id):
   if trigger[0] == 'end_turn' and game.minion_pool[id].owner == trigger[1]:
      for minion in game.minion_pool[id].owner.board[1:]:
         game.event_queue.append((events.heal, (game, minion.minion_id, 1)))

def leper_gnome(game, trigger, id):
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      game.event_queue.append((events.deal_damage, (game, Hearthstone.opponent(game, game.minion_pool[id].owner).board[0].minion_id, 2)))
      return True

def loot_hoarder(game, trigger, id): #id gets partially applied when effect is created
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      events.draw(game.minion_pool[id].owner)
      return True

def novice_engineer(game, trigger, id):
   if trigger[0] == 'battlecry' and trigger[1] == id:
      events.draw(game.player)
      return True 
   
def water_elemental(game, trigger, id):
   if trigger[0] == 'attack' and id in trigger[1:]:
      enemy = game.minion_pool[filter(lambda x:x != id, trigger[1:])[0]]
      enemy.attacks_left = 0
      enemy.mechanics.add('Frozen')

exceptions = ['events', 'Hearthstone', 'utils', 'exceptions', 'senjin_shieldmasta']
minion_effects = {utils.func_to_name(key):val for key,val in locals().items() if key[0] != '_' and key not in exceptions}
# minion_effects["Sen'jin Shieldmasta"] = senjin_shieldmasta # this is an example of how exceptions work
