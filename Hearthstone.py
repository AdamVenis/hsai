# tested with python version 2.7.3

# need to install: 
# recordtype https://pypi.python.org/pypi/recordtype/

# card data:
# http://hearthstonejson.com/

# mechanics: Taunt, Stealth, Divine Shield, Windfury, Freeze, Enrage, HealTarget, Charge, Deathrattle, Aura, Combo, AdjacentBuff, Battlecry, Poisonous, Spellpower
# implemented event types: start_turn, end_turn, kill_minion, attack, summon, deal_damage, heal, modify_stats

from recordtype import recordtype
from json import loads
from random import shuffle, randint, choice
from functools import partial
import effects
import decks

Game = recordtype('Game', 'player enemy effect_pool event_queue minion_pool minion_counter')
Player = recordtype('Player', 'hero hand deck board secrets crystals current_crystals armor weapon spellpower fatigue can_hp')
Card = recordtype('Card', 'name cost attack health mechanics')
Minion = recordtype('Minion', 'name neutral_attack attack neutral_health max_health health mechanics attacks_left minion_id owner')
Weapon = recordtype('Weapon', 'attack durability')

def get_minions(): #for local temp variables
   raw_cards = loads(open("AllSets.json").read())
   minions = []
   for val in raw_cards.values():
      minions += filter(lambda x:x["type"]=="Minion", val)
   return minions
   
minions = get_minions()
   
def get_card_index(card):
   for index, minion in enumerate(minions):
      if minion['name'] == card:
         return index
   return None
   
def get_card(card):
   for index, minion in enumerate(minions):
      if minion['name'] == card:
         attributes = ['name', 'cost', 'attack', 'health', 'mechanics']
         rtn = Card(*map(minion.get, attributes))
         if not rtn.mechanics: # turn mechanics from None to [] for membership testing
            rtn.mechanics = []
         return rtn
         
def get_deck(names):
   deck = map(get_card, names)
   shuffle(deck) #LOL
   return deck
   
def display(p1, p2):

   p1_board_string = [[' '*9], 'P1 Board: %s' % ' '.join(map(lambda x:'|'+x.name+'|', p1.board[1:])), [' '*9]]
   p2_board_string = [[' '*9], 'P2 Board: %s' % ' '.join(map(lambda x:'|'+x.name+'|', p2.board[1:])), [' '*9]]
   
   for i in p1.board[1:]:
      p1_board_string[0].append('-'*(len(i.name)+2))
      p1_board_string[2].append('|' + str(i.attack) + ' '*(len(i.name) - len(str(i.attack)) - len(str(i.health))) + str(i.health) + '|')
      
   p1_board_string[0] = ' '.join(p1_board_string[0])
   p1_board_string[2] = ' '.join(p1_board_string[2])
   p1_board_string.append(p1_board_string[0])
   
   for i in p2.board[1:]:
      p2_board_string[0].append('-'*(len(i.name)+2))
      p2_board_string[2].append('|' + str(i.attack) + ' '*(len(i.name) - len(str(i.attack)) - len(str(i.health))) + str(i.health) + '|')
      
   p2_board_string[0] = ' '.join(p2_board_string[0])
   p2_board_string[2] = ' '.join(p2_board_string[2])
   p2_board_string.append(p2_board_string[0])   
   
   print '-'*79
   print 'P2 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (p2.hero, p2.current_crystals, p2.crystals, p2.board[0].health, 
                                                '' if p2.armor == 0 else ', Armor : ' + str(p2.armor),
                                                '' if p2.weapon == None else ', Weapon : ' + str(p2.weapon.attack) + '/' + str(p2.weapon.durability),
                                                '' if p2.board[0].attack == 0 else ', Attack : ' + str(p2.board[0].attack))
   print 'P2 Hand: %s' % ' | '.join(map(lambda x:x.name, p2.hand))
   for i in range(len(p2_board_string[0])/79 + 1):
      for j in p2_board_string:
         print j[i*79:(i+1)*79]
   for i in range(len(p1_board_string[0])/79 + 1):
      for j in p1_board_string:
         print j[i*79:(i+1)*79]
   print 'P1 Hand: %s' % ' | '.join(map(lambda x:x.name, p1.hand))
   print 'P1 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (p1.hero, p1.current_crystals, p1.crystals, p1.board[0].health, 
                                                '' if p1.armor == 0 else ', Armor : ' + str(p1.armor),
                                                '' if p1.weapon == None else ', Weapon : ' + str(p1.weapon.attack) + '/' + str(p1.weapon.durability),
                                                '' if p1.board[0].attack == 0 else ', Attack : ' + str(p1.board[0].attack))  
                                                
def draw(player):
   if not player.deck:
      print "We're out of cards!"
      player.fatigue += 1
      player.board[0].health -= player.fatigue
   elif len(player.hand) == 10:
      print 'hand is full! %s is burned' % player.deck[0].name
      del player.deck[0]
   else:
      player.hand.append(player.deck[0])
      del player.deck[0]
      
def summon(game, player, ind=None, card=None): #ind is for summoning from hand, card is used otherwise
   if not card:
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
      
   minion = Minion(card.name, card.attack, card.attack, card.health, card.health, card.health, card.mechanics, 0, game.minion_counter, player)
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
      
   if ind:
      trigger_effects(game, ['battlecry', minion.minion_id])
      
def attack(game, x, y): #x and y are the indices of the ally and enemy minions respectively
   if x not in range(len(game.player.board)) or y not in range(len(game.enemy.board)):
      print 'Bad index!'
   elif game.player.board[x].attacks_left == 0:
      print 'This minion has already attacked!'
   elif 'Stealth' in game.enemy.board[y].mechanics:
      print 'cannot target stealth minions!'
   elif 'Taunt' not in game.enemy.board[y].mechanics and any(map(lambda t:'Taunt' in t.mechanics, game.enemy.board)):
      print 'must attack taunting minions'
   elif x == 0: #hero attacking behaviour
      if game.player.weapon:
         game.player.board[0].attacks_left -= 1
         deal_damage(game, game.enemy, y, game.player.weapon.attack)
         deal_damage(game, game.player, x, game.enemy.board[y].attack)
         game.player.weapon.durability -= 1 # this will need to be an event for gorehowl
         if game.player.weapon.durability == 0:
            game.player.weapon = None
      elif game.player.board[0].attack:
         game.player.board[0].attacks_left -= 1
         deal_damage(game, game.enemy, y, game.player.board[0].attack)
         deal_damage(game, game.player, x, game.enemy.board[y].attack)
      else:
         print 'hero cannot attack!'
   elif game.player.board[x].attack <= 0:
      print 'This minion cannot attack!'
   else:
      game.player.board[x].attacks_left -= 1      
      if 'Stealth' in game.player.board[x].mechanics:
         game.player.board[x].mechanics.remove('Stealth')
      deal_damage(game, game.player, x, game.enemy.board[y].attack)
      deal_damage(game, game.enemy, y, game.player.board[x].attack)
         
def deal_damage(game, player, ind, damage):
   trigger_effects(game, ['deal_damage', player.board[ind].minion_id, damage])
   if ind == 0 and damage < player.armor:
      player.armor -= damage
   elif ind == 0 and player.armor:
      player.board[ind].health -= damage - player.armor
      player.armor = 0
   elif 'Divine Shield' in player.board[ind].mechanics:
      player.board[ind].mechanics.remove('Divine Shield')
   else:
      player.board[ind].health -= damage
      
   if player.board[ind].health <= 0:
      if ind == 0:
         trigger_effects(game, ['kill_hero', player])
      else:
         game.event_queue.append((kill_minion, (game, player, ind)))
         
def heal(game, minion_id, amount):
   trigger_effects(game, ['heal', minion_id, amount])
   minion = game.minion_pool[minion_id]
   minion.health = min(minion.health + amount, minion.max_health)
      
def kill_minion(game, player, ind):
   trigger_effects(game, ['kill_minion', player.board[ind].minion_id])
   del game.minion_pool[player.board[ind].minion_id]
   del player.board[ind]   
   
def trigger_effects(game, trigger):
   for i in reversed(range(len(game.effect_pool))): # looping backwards to accomodate multiple deletions
      if game.effect_pool[i](game, trigger): # returning true means the effect should be removed
         del game.effect_pool[i]
   
def hero_power(g):
   if g.player.current_crystals < 2:
      print 'not enough mana!'
      return
   elif not g.player.can_hp:
      print 'can only use this once per turn!'
      return
   
   h = g.player.hero.lower()
   if h == 'hunter':
      deal_damage(g, g.enemy, 0, 2)
   elif h == 'warrior':
      g.player.armor += 2
   elif h == 'shaman':
      totems = ['Healing Totem', 'Searing Totem', 'Stoneclaw Totem', 'Wrath of Air Totem']
      for i in g.player.board:
         if i.name in totems:
            totems.remove(i.name)
      if totems: # not all have been removed
         summon(g, g.player, card=get_card(choice(totems)))      
      else:
         print 'all totems have already been summoned!'
         return
   elif h == 'mage':
      pass
   elif h == 'warlock':
      deal_damage(g, g.player, 0, 2)
      draw(g.player)
   elif h == 'rogue':
      g.player.weapon = Weapon(1,2)
   elif h == 'priest':
      pass
   elif h == 'paladin':
      summon(g, g.player, card=get_card('Silver Hand Recruit'))
   elif h == 'druid':
      g.player.armor += 1
      g.player.board[0].attack += 1
      g.effect_pool.append(effects.effects['Druid'])
   g.player.can_hp = False
   g.player.current_crystals -= 2
   
def dummy_minion(game):
   #game.minion_counter += 1
   return Minion(name='dummy', neutral_attack=0, attack=0, neutral_health=30, max_health=30, health=30, 
                  mechanics=[], attacks_left=0, minion_id=game.minion_counter-1, owner=None)
   
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
      player = Player(hero, [], get_deck(decks.starter), [], [], 0, 0, 0, None, 0, 0, True)
      if i == 0:
         p1 = player
      else:
         p2 = player

   print '%s versus %s!' % (p1.hero, p2.hero)
   
   for i in range(2): # initial hand size
      draw(p1)
      draw(p2)
      
   game = Game(p2, p1, [], [], {}, 1547657) # pre-switched
   
   for p in [p1, p2]:
      p.board.append(dummy_minion(game))
   
   while True: #loops through turns
      game.enemy, game.player = game.player, game.enemy
      p, enemy = game.player, game.enemy
      p.crystals = min(p.crystals + 1, 10)
      p.current_crystals = p.crystals
      draw(p)
      
      print " "
      print "It is now player %d's turn" % (1 if p == p1 else 2)
           
      for minion in p.board:
         if 'Windfury' in minion.mechanics:
            minion.attacks_left = 2
         else:
            minion.attacks_left = 1
      p.can_hp = True
      
      trigger_effects(game, ['start_turn', p])
         
      while True: #loops through actions
         if game.event_queue: #performs any outstanding event
            event = game.event_queue.pop()
            event[0](*event[1]) # tuple with arguments in second slot
            continue
            
         #TODO: check if effects are triggered?
         display(p1, p2)
         if p1.board[0].health <= 0 or p2.board[0].health <= 0:
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
            if len(action) < 2: 
               print 'incorrect number of arguments'
            else: 
               try:
                  summon(game, p, int(action[1]))
               except ValueError:
                  print 'invalid input: parameter must be integer, was given string'
         elif action[0].lower() == 'attack':
            if len(action) < 3:
               print 'incorrect number of arguments'
            else:
               try:
                  attack(game, int(action[1]), int(action[2]))
               except ValueError:
                  print 'invalid input: parameters must be integers, was given strings'
         elif action[0].lower() == 'debug':
            print 'effects: %s' % map(lambda x: '%s:%s' % (x.func.__name__, x.keywords), game.effect_pool)
            print 'events: %s' % game.event_queue
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
         