from utils import *
import effects
import Hearthstone

def draw(player):
   if not player.deck:
      print "We're out of cards!"
      player.fatigue += 1
      player.board[0].current_health -= player.fatigue
   elif len(player.hand) == 10:
      print 'hand is full! %s is burned' % player.deck[0].name
      del player.deck[0]
   else:
      player.hand.append(player.deck[0])
      del player.deck[0]

def summon(game, player, ind): #specifically for summoning from hand
   if ind >= len(player.hand):
      print 'Bad index!'
      return
   elif player.hand[ind].cost > player.current_crystals:
      print 'Not enough crystals! You need %s crystals for this.' % player.hand[ind].cost
      return
   else:
      card = player.hand[ind]
      player.current_crystals -= card.cost
      del player.hand[ind]
      
   minion = Minion(game, player, card)
   game.minion_pool[minion.minion_id] = minion
   game.minion_counter += 1
   player.board.append(minion)
   if 'Charge' in minion.mechanics:
      if 'Windfury' in minion.mechanics:
         minion.attacks_left = 2
      else:
         minion.attacks_left = 1
   if effects.effects.get(card.name):
      game.effect_pool.append(partial(effects.effects[card.name], id=minion.minion_id))
      
   Hearthstone.trigger_effects(game, ['battlecry', minion.minion_id])
      
def spawn(game, player, card): #equivalent of summon when not from hand
   minion = Minion(game, player, card)
   game.minion_pool[minion.minion_id] = minion
   game.minion_counter += 1
   player.board.append(minion)
   if 'Charge' in minion.mechanics:
      if 'Windfury' in minion.mechanics:
         minion.attacks_left = 2
      else:
         minion.attacks_left = 1
   if effects.effects.get(card.name):
      game.effect_pool.append(partial(effects.effects[card.name], id=minion.minion_id))
        
def attack(game, ally_id, enemy_id): #x and y are the indices of the ally and enemy minions respectively
  
   ally_minion = game.minion_pool[ally_id]
   enemy_minion = game.minion_pool[enemy_id]

   if ally_minion == ally_minion.owner.board[0] and game.player.weapon:
      game.player.weapon.durability -= 1 # this might need to be an event for gorehowl
      if game.player.weapon.durability == 0:
         game.player.weapon = None
         
   if 'Stealth' in ally_minion.mechanics:
      ally_minion.mechanics.remove('Stealth')
      
   ally_minion.attacks_left -= 1
   
   if 'Divine Shield' in enemy_minion.mechanics:
      enemy_minion.mechanics.remove('Divine Shield')
   else:
      damage = ally_minion.attack(game)
      if damage > 0:
         game.event_queue.append((deal_damage, (game, enemy_minion.minion_id, ally_minion.attack(game))))
      
   if 'Divine Shield' in ally_minion.mechanics:
      ally_minion.mechanics.remove('Divine Shield')
   else:      
      damage = enemy_minion.attack(game)
      if enemy_minion == enemy_minion.owner.board[0] and enemy_minion.owner.weapon is not None:
         damage -= enemy_minion.owner.weapon.attack(game)
      if damage > 0:
         game.event_queue.append((deal_damage, (game, ally_minion.minion_id, damage)))
   
def deal_damage(game, id, damage):
   minion = game.minion_pool[id]
   player = minion.owner
   if minion.name == 'hero' and damage < player.armor:
      player.armor -= damage
   elif game.minion_pool[id].name == 'hero' and player.armor:
      minion.current_health -= damage - player.armor
      player.armor = 0
   else:
      minion.current_health -= damage
      
   if minion.health(game) <= 0:
      if minion.name == 'hero':
         trigger_effects(game, ['kill_hero', player]) # equivalent to highest priority?
      else:
         game.event_queue.append((kill_minion, (game, id)))
         
def heal(game, minion_id, amount):
   minion = game.minion_pool[minion_id]
   minion.current_health = min(minion.current_health + amount, minion.max_health)
      
def remove_traces(game, id): #removes effects and auras of a minion
   minion = game.minion_pool[id]
   game.effect_pool = filter(lambda x: x.keywords.get('id') != id, game.effect_pool) #remove relevant effects
   
def replace_minion(game, id, new_minion): # unclear if this is right, might want to invoke spawn
   old_minion = game.minion_pool[id]
   new_minion.minion_id = id # questionable
   for i, minion in old_minion.owner:
      if minion == old_minion:
         minion.owner.board[i] = new_minion
         break
   game.minion_pool[id] = new_minion
   remove_traces(game, id)
         
def kill_minion(game, id):
   minion = game.minion_pool[id]
   remove_traces(game, id)
   minion.owner.board.remove(minion)   
   del game.minion_pool[id]
  