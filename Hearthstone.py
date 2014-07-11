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
      
   trigger_effects(game, ['battlecry', minion.minion_id])
      
def spawn(game, player, card): #equivalent of summon when not from hand
   print 'spawning %s' % card.name
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
        
def attack(game, x, y): #x and y are the indices of the ally and enemy minions respectively
   if x not in range(len(game.player.board)) or y not in range(len(game.enemy.board)):
      print 'Bad index!'
      return
      
   ally_minion = game.player.board[x]
   enemy_minion = game.enemy.board[y]
   
   if ally_minion.attacks_left == 0:
      print 'This minion has already attacked!'
      return
   elif 'Stealth' in enemy_minion.mechanics:
      print 'cannot target stealth minions!'
      return
   elif 'Taunt' not in enemy_minion.mechanics and any(map(lambda t:'Taunt' in t.mechanics, game.enemy.board)):
      print 'must attack taunting minions'
      return
            
   damage = 0
   if x == 0 and game.player.weapon:
      damage += game.player.weapon.attack
      game.player.weapon.durability -= 1 # this might need to be an event for gorehowl
      if game.player.weapon.durability == 0:
         game.player.weapon = None
   if ally_minion.attack:
      damage += ally_minion.attack
      
   if damage == 0:
      print 'this target cannot attack!'
   else:    
      if 'Stealth' in ally_minion.mechanics:
         ally_minion.mechanics.remove('Stealth')
      ally_minion.attacks_left -= 1
      game.event_queue.append((deal_damage, (game, enemy_minion.minion_id, damage)))
      game.event_queue.append((deal_damage, (game, ally_minion.minion_id, enemy_minion.attack)))
   
def deal_damage(game, id, damage):
   minion = game.minion_pool[id]
   player = minion.owner
   if minion.name == 'hero' and damage < player.armor:
      player.armor -= damage
   elif game.minion_pool[id].name == 'hero' and player.armor:
      minion.health -= damage - player.armor
      player.armor = 0
   elif 'Divine Shield' in minion.mechanics:
      minion.mechanics.remove('Divine Shield')
   else:
      minion.health -= damage
      
   if minion.health <= 0:
      if minion.name == 'hero':
         trigger_effects(game, ['kill_hero', player])
      else:
         game.event_queue.append((kill_minion, (game, id)))
         
def heal(game, minion_id, amount):
   minion = game.minion_pool[minion_id]
   minion.health = min(minion.health + amount, minion.max_health)
      
def kill_minion(game, id):
   minion = game.minion_pool[id]
   game.effect_pool = filter(lambda x: x.keywords.get('id') != id, game.effect_pool) #remove relevant effects
   minion.owner.board.remove(minion)
   del game.minion_pool[id]
   
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
      game.effect_pool.append(effects.effects['Druid'])
   game.player.can_hp = False
   game.player.current_crystals -= 2
   
def dummy_minion(game, player):
   minion = Minion(name='hero', neutral_attack=0, attack=0, neutral_health=30, max_health=30, health=30, 
                  mechanics=[], attacks_left=0, minion_id=game.minion_counter, owner=player)
   game.minion_counter += 1
   game.minion_pool[minion.minion_id] = minion
   return minion
   
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
   
   for i in range(3): # initial hand size
      draw(p1)
      draw(p2)
      
   game = Game(p2, p1, [], [], {}, 1000) # pre-switched
   
   for p in [p1, p2]:
      p.board.append(dummy_minion(game, p))
   
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
            minion.attacks_left = 0
            minion.mechanics.remove('Frozen')
         else:
            minion.attacks_left = 1
      p.can_hp = True
      
      trigger_effects(game, ['start_turn', p])
         
      while True: #loops through actions
         if game.event_queue: #performs any outstanding event
            event = game.event_queue[0]
            game.event_queue = game.event_queue[1:] # remove the first element. TODO: turn this into a deque?
            trigger_effects(game, [event[0].__name__] + list(event[1][1:]))
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
                  game.event_queue.append((summon, (game, p, int(action[1]))))
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
         