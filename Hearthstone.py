# tested with python version 2.7.3

# need to install: 
# recordtype https://pypi.python.org/pypi/recordtype/

from collections import deque
from utils import *
import decks
import card_data
import events
import minion_effects
import spell_effects

def play():
   print choice(['Take a seat by the hearth!', 'Welcome back!', "Busy night! But there's always room for another!"])
      
   for i in range(2):
      print 'Choose your class (Player %s)' % (i+1)
      hero = raw_input()
      while hero.lower() not in ['warrior', 'hunter', 'mage', 'warlock', 'shaman', 'rogue', 'priest', 'paladin', 'druid']:
         print 'not a valid hero! choose again'
         hero = raw_input()   
      player = Player(hero=hero, hand=[], deck=get_deck(decks.default_mage), board=[], secrets=[], crystals=0, current_crystals=0, 
                     armor=0, weapon=None, auras=set([]), spellpower=0, fatigue=0, can_hp=True)
      if i == 0:
         p1 = player
      else:
         p2 = player

   print '%s versus %s!' % (p1.hero, p2.hero)
   
   for i in range(3):
      events.draw(p1)
   for i in range(4):
      events.draw(p2)
   p2.hand.append(get_card('The Coin'))
      
   game = Game(player=p2, enemy=p1, effect_pool=[], event_queue=deque(), minion_pool={}, minion_counter=1000) # pre-switched
   
   for p in [p1, p2]:
      events.spawn(game, p, Card('Dummy', 0, 0, 30, {}))
   
   while True: #loops through turns
      game.enemy, game.player = game.player, game.enemy
      p, enemy = game.player, game.enemy
      p.crystals = min(p.crystals + 1, 10)
      p.current_crystals = p.crystals
      events.draw(p)
      
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
            events.hero_power(game)
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
                  game.event_queue.append((events.summon, (game, p, index)))
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
                  game.event_queue.append((events.cast_spell, (game, index)))
         elif action[0].lower() == 'attack':
            if len(action) != 3:
               print 'incorrect number of arguments: needs exactly 3'
            else:
               try:
                  action[1], action[2] = int(action[1]), int(action[2])
                  if not validate_attack(game, action[1], action[2]):
                     continue
                  else:
                     game.event_queue.append((events.attack, (game, game.player.board[action[1]].minion_id, game.enemy.board[action[2]].minion_id)))
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
         