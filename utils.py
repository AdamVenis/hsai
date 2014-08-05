from functools import partial
from recordtype import recordtype
from random import shuffle, randint, choice
from collections import deque

import decks
import card_data

Game = recordtype('Game', 'player enemy effect_pool event_queue minion_pool minion_counter')
Player = recordtype('Player', 'hero hand deck board secrets crystals current_crystals armor weapon auras spellpower fatigue can_hp')

class Game():
   def __init__(self, hero1, hero2, deck1, deck2):
      self.player = Player(hero=hero1, hand=[], deck=deck1, board=[], secrets=[], crystals=0,
            current_crystals=0, armor=0, weapon=None, auras=set([]), spellpower=0, fatigue=0, can_hp=True)
      self.enemy = Player(hero=hero2, hand=[], deck=deck2, board=[], secrets=[], crystals=0,
            current_crystals=0, armor=0, weapon=None, auras=set([]), spellpower=0, fatigue=0, can_hp=True)       
      self.turn = 0
      self.effect_pool = []
      self.event_queue = deque()
      self.minion_pool = {}
      self.minion_counter = 1000 # dummy value
      
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
      rtn = apply_auras(game, self.owner, self, 'attack', rtn)
      return rtn         
      
   def health(self, game):
      rtn = self.current_health
      rtn = apply_auras(game, self.owner, self, 'health', rtn)
      return rtn
      
   def transform_into(self, new_minion):
      self.name = new_minion.name
      self.neutral_attack = new_minion.neutral_attack
      self.current_attack = new_minion.current_attack
      self.neutral_health = new_minion.neutral_health
      self.max_health = new_minion.max_health
      self.current_health = new_minion.current_health
      self.mechanics = new_minion.mechanics
      self.attacks_left = 0
            
class Weapon():
   def __init__(self, attack, durability):
      self.current_attack = attack
      self.durability = durability
   
   def attack(self, game): # to make room for auras (aka for spiteful smith)
      rtn = self.current_attack
      return rtn

class Aura():
   def __init__(self, id, modifier):
      self.id = id
      self.modifier = modifier 
      self.aux_vars = {}
      
def apply_auras(game, player, object, stat, value):
   for aura in player.auras:
      value = aura.modifier(game, object, stat, value)
   return value
   
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
   
def is_hero(minion):
   return minion.owner.board.index(minion) == 0
   
def display(game, p1, p2):   

   p1_board_string = [[' '*9], 'P1 Board: %s' % ' '.join(map(lambda x:'|'+x.name+'|', p1.board[1:])), [' '*9]]
   p2_board_string = [[' '*9], 'P2 Board: %s' % ' '.join(map(lambda x:'|'+x.name+'|', p2.board[1:])), [' '*9]]
   
   for minion in p1.board[1:]:
      p1_board_string[0].append('-'*(len(minion.name)+2))
      p1_board_string[2].append('|' + str(minion.attack(game)) 
         + ' '*(len(minion.name) - len(str(minion.attack(game))) - len(str(minion.health(game)))) 
         + str(minion.health(game)) + '|')
      
   p1_board_string[0] = ' '.join(p1_board_string[0])
   p1_board_string[2] = ' '.join(p1_board_string[2])
   p1_board_string.append(p1_board_string[0])
   
   for minion in p2.board[1:]:
      p2_board_string[0].append('-'*(len(minion.name)+2))
      p2_board_string[2].append('|' + str(minion.attack(game)) 
         + ' '*(len(minion.name) - len(str(minion.attack(game))) - len(str(minion.health(game)))) 
         + str(minion.health(game)) + '|')
      
   p2_board_string[0] = ' '.join(p2_board_string[0])
   p2_board_string[2] = ' '.join(p2_board_string[2])
   p2_board_string.append(p2_board_string[0])   
   
   print '-'*79
   print 'P2 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (p2.hero, p2.current_crystals, p2.crystals, p2.board[0].health(game), 
                                                '' if p2.armor == 0 else ', Armor : ' + str(p2.armor),
                                                '' if p2.weapon == None else ', Weapon : ' + str(p2.weapon.attack(game)) + '/' + str(p2.weapon.durability),
                                                '' if p2.board[0].attack == 0 else ', Attack : ' + str(p2.board[0].attack(game)))
   print 'P2 Hand: %s' % ' | '.join(map(lambda x:x.name, p2.hand))
   for i in range(len(p2_board_string[0])/79 + 1):
      for j in p2_board_string:
         print j[i*79:(i+1)*79]
   for i in range(len(p1_board_string[0])/79 + 1):
      for j in p1_board_string:
         print j[i*79:(i+1)*79]
   print 'P1 Hand: %s' % ' | '.join(map(lambda x:x.name, p1.hand))
   print 'P1 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (p1.hero, p1.current_crystals, p1.crystals, p1.board[0].health(game), 
                                                '' if p1.armor == 0 else ', Armor : ' + str(p1.armor),
                                                '' if p1.weapon == None else ', Weapon : ' + str(p1.weapon.attack(game)) + '/' + str(p1.weapon.durability),
                                                '' if p1.board[0].attack == 0 else ', Attack : ' + str(p1.board[0].attack(game)))  

def trigger_effects(game, trigger):
   game.effect_pool = filter(lambda x:not x(game, trigger), game.effect_pool)
              
def opponent(game, player):
   if player == game.player:
      return game.enemy
   else:
      return game.player

def get_card(card_name):
   for minion in card_data.minions:
      if minion['name'] == card_name:
         attributes = ['name', 'cost', 'attack', 'health', 'mechanics']
         rtn = Card(*map(minion.get, attributes))
         if not rtn.mechanics: # turn mechanics from None to emptyset for membership testing
            rtn.mechanics = set([])
         else:
            rtn.mechanics = set(rtn.mechanics)
         return rtn
   for spell in card_data.spells:
      if spell['name'] == card_name:
         return SpellCard(spell['name'], spell.get('cost') if spell.get('cost') is not None else 0) #for some reason some spells don't have a cost
   print 'ERROR: CARD NOT FOUND: %s' % card_name
         
def get_deck(names):
   deck = map(get_card, names)
   shuffle(deck) #LOL
   return deck
   