# tested with python version 2.7.3

# need to install: 
# recordtype https://pypi.python.org/pypi/recordtype/

# card data:
# http://hearthstonejson.com/

# mechanics: Taunt, Stealth, Divine Shield, Windfury, Freeze, Enrage, HealTarget, Charge, Deathrattle, Aura, Combo, AdjacentBuff, Battlecry, Poisonous, Spellpower
# implemented event types: start_turn, end_turn, kill_minion, attack, summon, deal_damage, heal, cast_spell

from json import loads
from random import shuffle, randint, choice
from collections import deque
from events import *
from utils import *
import minion_effects
import spell_effects
import decks

def get_minions_and_spells(): #for local temp variables
   raw_cards = loads(open("AllSets.json").read())
   minions = []
   spells = []
   for val in raw_cards.values():
      for card in val:
         if card['type'] == 'Minion':
            minions.append(card)
         elif card['type'] == 'Spell':
            spells.append(card)
   return minions, spells
   
minions, spells = get_minions_and_spells()
   
def get_card_index(card):
   for index, minion in enumerate(minions):
      if minion['name'] == card:
         return index
   return None
   
def get_card(card_name):
   for minion in minions:
      if minion['name'] == card_name:
         attributes = ['name', 'cost', 'attack', 'health', 'mechanics']
         rtn = Card(*map(minion.get, attributes))
         if not rtn.mechanics: # turn mechanics from None to emptyset for membership testing
            rtn.mechanics = set([])
         else:
            rtn.mechanics = set(rtn.mechanics)
         return rtn
   for spell in spells:
      if spell['name'] == card_name:
         return SpellCard(spell['name'], spell.get('cost') if spell.get('cost') is not None else 0) #for some reason some spells don't have a cost
   print 'ERROR: CARD NOT FOUND: %s' % card_name
         
def get_deck(names):
   deck = map(get_card, names)
   shuffle(deck) #LOL
   return deck
   
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

#TODO : get rid of this function true_stats                                                
def true_stats(game, id): #returns attack and health of a minion modified by auras, as a pair
   minion = game.minion_pool[id]
   rtn = minion.attack, minion.health
   for aura in minion.owner.auras:
      if aura.type == 'Allies' or aura.type == 'Adjacent' and abs(minion.owner.board.index(game.minion_pool[aura.id]) - minion.owner.board.index(minion)) == 1:
         rtn = rtn[0] + attack_modifier, rtn[1] + health_modifier
   return rtn
   
def target(game):
   print 'pick a target'
   while True:
      input = raw_input().split(' ')
      if len(input) != 2:
         print 'wrong number of parameters'
      elif input[0] in ['a', 'ally']:
         try:
            if int(input[1]) in range(len(game.player.board)):
               return game.player.board[int(input[1])].minion_id
            else:
               print 'wrong index'
         except ValueError:
            print 'invalid parameter: must be integer'
      elif input[0] in ['e', 'enemy']:
         try:
            if int(input[1]) in range(len(game.enemy.board)):
               return game.enemy.board[int(input[1])].minion_id
            else:
               print 'wrong index'
         except ValueError:
            print 'invalid parameter: must be integer'         
      else:
         print 'invalid input. e.g. enemy 0'   
   
def trigger_effects(game, trigger):
   game.effect_pool = filter(lambda x:not x(game, trigger), game.effect_pool)
         
def hero_power(game):
   if game.player.current_crystals < 2:
      print 'not enough mana!'
      return
   elif not game.player.can_hp:
      print 'can only use this once per turn!'
      return
   
   h = game.player.hero.lower()
   if h == 'hunter':
      game.event_queue.append((deal_damage, (game, game.enemy.board[0].minion_id, 2)))
   elif h == 'warrior':
      game.player.armor += 2
   elif h == 'shaman':
      totems = ['Healing Totem', 'Searing Totem', 'Stoneclaw Totem', 'Wrath of Air Totem']
      for i in game.player.board:
         if i.name in totems:
            totems.remove(i.name)
      if totems: # not all have been removed
         game.event_queue.append((spawn, (game, game.player, get_card(choice(totems)))))
      else:
         print 'all totems have already been summoned!'
         return
   elif h == 'mage':
      id = target(game)
      game.event_queue.append((deal_damage, (game, id, 1)))
   elif h == 'warlock':
      game.event_queue.append((deal_damage, (game, game.player, 0, 2)))
      draw(game.player)
   elif h == 'rogue':
      game.player.weapon = Weapon(1,2)
   elif h == 'priest':
      id = target(game)
      game.event_queue.append((heal, (game, id, 2)))
   elif h == 'paladin':
      game.event_queue.append((summon, (game, game.player, get_card('Silver Hand Recruit'))))
   elif h == 'druid':
      game.player.armor += 1
      game.player.board[0].attack += 1
      game.effect_pool.append(minion_effects.effects['Druid'])
   game.player.can_hp = False
   game.player.current_crystals -= 2
      
def opponent(game, player):
   if player == game.player:
      return game.enemy
   else:
      return game.player
   
def play():
   print choice(['Take a seat by the hearth!', 'Welcome back!', "Busy night! But there's always room for another!"])
      
   for i in range(2):
      print 'Choose your class (Player %s)' % (i+1)
      hero = raw_input()
      while hero.lower() not in ['warrior', 'hunter', 'mage', 'warlock', 'shaman', 'rogue', 'priest', 'paladin', 'druid']:
         print 'not a valid hero! choose again'
         hero = raw_input()   
      player = Player(hero=hero, hand=[], deck=get_deck(decks.default_mage), board=[], secrets=[], crystals=0, current_crystals=0, 
                     armor=0, weapon=None, auras=[], spellpower=0, fatigue=0, can_hp=True)
      if i == 0:
         p1 = player
      else:
         p2 = player

   print '%s versus %s!' % (p1.hero, p2.hero)
   
   for i in range(3):
      draw(p1)
   for i in range(4):
      draw(p2)
   p2.hand.append(get_card('The Coin'))
      
   game = Game(player=p2, enemy=p1, effect_pool=[], event_queue=deque(), minion_pool={}, minion_counter=1000) # pre-switched
   
   for p in [p1, p2]:
      spawn(game, p, Card('Dummy', 0, 0, 30, {}))
   
   while True: #loops through turns
      game.enemy, game.player = game.player, game.enemy
      p, enemy = game.player, game.enemy
      p.crystals = min(p.crystals + 1, 10)
      p.current_crystals = p.crystals
      draw(p)
      
      print " \nIt is now player %d's turn" % (1 if p == p1 else 2)
           
      for minion in p.board:
         if 'Windfury' in minion.mechanics:
            minion.attacks_left = 2
         elif 'Frozen' in minion.mechanics:
            minion.mechanics.remove('Frozen')
            minion.mechanics.add('Thawing')
         else:
            minion.attacks_left = 1
      p.can_hp = True
      
      trigger_effects(game, ['start_turn', p])
         
      while True: #loops through actions
         if game.event_queue: #performs any outstanding event
            event = game.event_queue.popleft()
            trigger_effects(game, [event[0].__name__] + list(event[1][1:])) #[1:] 'game' gets cut out, as it's always the first parameter
            event[0](*event[1]) # tuple with arguments in second slot
            continue
            
         display(game, p1, p2)
         if p1.board[0].health(game) <= 0 or p2.board[0].health(game) <= 0:
            break
            
         action = raw_input().split()
         if len(action) < 1:
            print 'unable to parse action'
         elif action[0].lower() in ['end', 'end turn']:
            trigger_effects(game, ['end_turn', p])
            break
         elif action[0].lower() == 'hero' and action[1].lower() == 'power':
            hero_power(game)
         elif action[0].lower() == 'summon':
            if len(action) != 2: 
               print 'incorrect number of arguments: needs exactly 2'
            else: 
               try:
                  index = int(action[1])
               except ValueError:
                  print 'invalid input: parameter must be integer, was given string'              
                  continue
               if index not in range(len(p.hand)):
                  print 'invalid index'
               elif p.hand[index].__class__ != Card: #this doesn't account for minion/spell name conflicts
                  print 'this card is not a minion and cannot be summoned'                  
               elif p.hand[index].cost > p.current_crystals:
                  print 'not enough crystals! need %s' % str(p.hand[index].cost)
               else:
                  game.event_queue.append((summon, (game, p, index)))
         elif action[0].lower() == 'cast':
            if len(action) != 2:
               print 'incorrect number of arguments: needs exactly 2'
            else:
               try:
                  index = int(action[1])
               except ValueError as e:
                  print 'invalid input: parameters must be integers, was given strings'
                  print e
                  continue
               if index not in range(len(p.hand)):
                  print 'invalid index'
               elif p.hand[index].__class__ != SpellCard:
                  print 'this card is not a spell and cannot be cast'
               elif p.hand[index].cost(game) > p.current_crystals:
                  print 'not enough crystals! need %s' % str(p.hand[index].cost(game))
               else:
                  game.event_queue.append((cast_spell, (game, index)))
         elif action[0].lower() == 'attack':
            if len(action) != 3:
               print 'incorrect number of arguments: needs exactly 3'
            else:
               try:
                  action[1], action[2] = int(action[1]), int(action[2])
                  if not validate_attack(game, action[1], action[2]):
                     continue
                  else:
                     game.event_queue.append((attack, (game, game.player.board[action[1]].minion_id, game.enemy.board[action[2]].minion_id)))
               except ValueError:
                  print 'invalid input: parameters must be integers, was given strings'
         elif action[0].lower() == 'debug':
            print 'effects: %s' % map(lambda x: '%s:%s' % (x.func.__name__, x.keywords), game.effect_pool)
            print 'events: %s' % game.event_queue
            print 'minion ids: %s' % game.minion_pool.keys()
         else:
            print 'unrecognized action'
      
      if p1.board[0].health <= 0 and p2.board[0].health <= 0:
         print "it's a draw!"
         break
      elif p1.board[0].health <= 0:
         print "player 2 wins!"
         break
      elif p2.board[0].health <= 0:
         print "player 1 wins!"
         break
         