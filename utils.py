from functools import partial
from recordtype import recordtype
from random import choice

Game = recordtype('Game', 'player enemy effect_pool event_queue minion_pool minion_counter')
Player = recordtype('Player', 'hero hand deck board secrets crystals current_crystals armor weapon auras spellpower fatigue can_hp')
#Card = recordtype('Card', 'name cost attack health mechanics')
#Minion = recordtype('Minion', 'name neutral_attack attack neutral_health max_health health mechanics attacks_left minion_id owner')
Aura = recordtype('Aura', 'type attack_modifier health_modifier id') 

class Card():
   def __init__(self, name, cost, attack, health, mechanics):
      self.name = name
      self.cost = cost
      self.attack = attack
      self.health = health
      self.mechanics = mechanics
       
class SpellCard():
   def __init__(self, name, cost):
      self.name = name
      self.neutral_cost = cost
      
   def cost(self, game):
      rtn = self.neutral_cost
      return rtn
     
class Minion():
   def __init__(self, game, player, card):
      self.name = card.name
      self.neutral_attack = card.attack
      self.current_attack = card.attack
      self.neutral_health = card.health
      self.max_health = card.health
      self.current_health = card.health
      self.mechanics = card.mechanics
      self.attacks_left = 0
      self.minion_id = game.minion_counter
      self.owner = player
      game.minion_counter += 1
            
   def attack(self, game): #TODO : add these to account for auras
      rtn = self.current_attack
      if self.owner.board.index(self) == 0 and self.owner.weapon: # this minion is a hero
         rtn += self.owner.weapon.attack
      return rtn         
      
   def health(self, game):
      rtn = self.current_health
      return rtn
      
class Weapon():
   def __init__(self, attack, durability):
      self.current_attack = attack
      self.durability = durability
   
   def attack(self, game): # to make room for auras (aka for spiteful smith)
      rtn = self.current_attack
      return rtn

def validate_attack(game, player_ind, enemy_ind):
   if player_ind not in range(len(game.player.board)):
      print 'wrong index for ally minion. Must supply a number from 0 to %s' % str(len(game.player.board))
      return False
   elif enemy_ind not in range(len(game.enemy.board)):
      print 'wrong index for enemy minion. Must supply a number from 0 to %s' % str(len(game.enemy.board))
      return False
      
   ally_minion = game.player.board[player_ind]
   enemy_minion = game.enemy.board[enemy_ind]
   
   if ally_minion.attacks_left <= 0:
      print 'this minion cannot attack'
      return False
   elif ally_minion.attack(game) <= 0:
      print 'this minion has no attack'
      return False
   elif 'Frozen' in ally_minion.mechanics or 'Thawing' in ally_minion.mechanics:
      print 'This minion is frozen, and cannot attack'
      return False      
   elif 'Stealth' in enemy_minion.mechanics:
      print 'cannot attack a minion with stealth'
      return False
   elif 'Taunt' not in enemy_minion.mechanics and any('Taunt' in minion.mechanics for minion in game.enemy.board[1:]):
      print 'must target a minion with taunt'
      return False
   return True
   
def func_to_name(s):
   s = s.split('_')
   return ' '.join([word[0].upper() + word[1:] for word in s])
   
def name_to_func(s):
   s = s.replace(' ', '_')
   return s.lower()
   
