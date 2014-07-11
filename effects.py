#alphabetical order!
import Hearthstone

effects = {}

def acolyte_of_pain(game, trigger, id):
   if trigger[0] == 'deal_damage' and trigger[1] == id:
      Hearthstone.draw(game.minion_pool[id].owner)
effects['Acolyte of Pain'] = acolyte_of_pain

'''def amani_berserker(game, trigger, id): # this is probably wrong on conjunction with Auchenai Soulpriest
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
effects['Arcane Golem'] = arcane_golem

def armorsmith(game, trigger, id):
   if trigger[0] == 'deal_damage' and game.minion_pool[trigger[1]] in game.minion_pool[id].owner.board[1:]:
      game.minion_pool[id].owner.armor += 1
effects['Armorsmith'] = armorsmith

def cairne_bloodhoof(game, trigger, id):
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      game.event_queue.append((Hearthstone.spawn, (game, game.minion_pool[id].owner, Hearthstone.get_card('Baine Bloodhoof'))))
      return True
effects['Cairne Bloodhoof'] = cairne_bloodhoof

def druid(game, trigger, player): # hero power
   if trigger[0] == 'end_turn':
      game.player.board[0].attack -= 1
      return True
effects['Druid'] = druid

def earthen_ring_farseer(game, trigger, id):
   if trigger[0] == 'battlecry' and trigger[1] == id:
      target_id = Hearthstone.target(game)
      game.event_queue.append((Hearthstone.heal, (game, target_id, 3)))
      return True
   return False
effects['Earthen Ring Farseer'] = earthen_ring_farseer

def gnomish_inventor(game, trigger, id):
   if trigger[0] == 'battlecry' and trigger[1] == id:
      Hearthstone.draw(game.player)
      return True
effects['Gnomish Inventor'] = gnomish_inventor

def harvest_golem(game, trigger, id):
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      game.event_queue.append((Hearthstone.spawn, (game, game.minion_pool[id].owner, Hearthstone.get_card('Damaged Golem'))))
      return True
effects['Harvest Golem'] = harvest_golem

def healing_totem(game, trigger, id):
   if trigger[0] == 'end_turn' and game.minion_pool[id].owner == trigger[1]:
      for minion in game.minion_pool[id].owner.board[1:]:
         game.event_queue.append((Hearthstone.heal, (game, minion.minion_id, 1)))
effects['Healing Totem'] = healing_totem

def leper_gnome(game, trigger, id):
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      game.event_queue.append((Hearthstone.deal_damage, (game, Hearthstone.opponent(game, game.minion_pool[id].owner).board[0].minion_id, 2)))
      return True
effects['Leper Gnome'] = leper_gnome

def loot_hoarder(game, trigger, id): #id gets partially applied when effect is created
   if trigger[0] == 'kill_minion' and trigger[1] == id:
      Hearthstone.draw(game.minion_pool[id].owner)
      return True
effects['Loot Hoarder'] = loot_hoarder

def novice_engineer(game, trigger, id):
   if trigger[0] == 'battlecry' and trigger[1] == id:
      Hearthstone.draw(game.player)
      return True
effects['Novice Engineer'] = novice_engineer  
   

