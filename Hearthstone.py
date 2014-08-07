# tested with python version 2.7.3

from utils import *
import decks
import card_data
import actions
import minion_effects
import spell_effects

def play():
   print choice(['Take a seat by the hearth!', 'Welcome back!', "Busy night! But there's always room for another!"])
   heroes = [None, None]
   for i in range(2):
      print 'Choose your class (Player %s)' % (i+1)
      heroes[i] = raw_input()
      while heroes[i].lower() not in ['warrior', 'hunter', 'mage', 'warlock', 'shaman', 'rogue', 'priest', 'paladin', 'druid']:
         print 'not a valid hero! choose again'
         heroes[i] = raw_input()   
   
   print '%s versus %s!' % tuple(heroes)
   game = Game(heroes[0], heroes[1], get_deck(decks.default_mage), get_deck(decks.default_mage))
   p1, p2 = game.player, game.enemy
      
   for i in range(3):
      game.action_queue.append((actions.draw, (game.player,)))
   for i in range(4):
      game.action_queue.append((actions.draw, (game.enemy,)))
   game.enemy.hand.append(get_card('The Coin'))    
   
   for player in [game.player, game.enemy]:
      actions.spawn(game, player, Card(name='Dummy', cost=0, attack=0, health=30, mechanics={})) 
      
   while True: #loops through turns
      if game.turn > 0:
         game.enemy, game.player = game.player, game.enemy
      player, enemy = game.player, game.enemy # implicit references for convenience
      player.crystals = min(player.crystals + 1, 10)
      player.current_crystals = player.crystals
      game.action_queue.append((actions.draw, (game.player,)))
      
      print " \nIt is now player %d's turn" % ((game.turn % 2) + 1)
           
      for minion in player.board:
         if 'Windfury' in minion.mechanics:
            minion.attacks_left = 2
         elif 'Frozen' in minion.mechanics:
            minion.mechanics.remove('Frozen')
            minion.mechanics.add('Thawing')
         else:
            minion.attacks_left = 1
      player.can_hp = True
      
      trigger_effects(game, ['start_turn', player])
         
      while True: #loops through actions
         if game.action_queue: #performs any outstanding action
            action = game.action_queue.popleft()
            trigger_effects(game, [action[0].__name__] + list(action[1][1:])) #[1:] 'game' gets cut out, as it's always the first parameter
            action[0](*action[1]) # tuple with arguments in second slot
            continue
            
         display(game, p1, p2)
         if p1.board[0].health(game) <= 0 or p2.board[0].health(game) <= 0:
            break
            
         action = raw_input().split()
         if len(action) < 1:
            print 'unable to parse action'
         elif action[0].lower() in ['end', 'end turn']:
            trigger_effects(game, ['end_turn', player])
            game.turn += 1
            break
         elif action[0].lower() == 'hero' and action[1].lower() == 'power':
            actions.hero_power(game)
         elif action[0].lower() == 'summon':
            if len(action) != 2: 
               print 'incorrect number of arguments: needs exactly 2'
            else: 
               try:
                  index = int(action[1])
               except ValueError:
                  print 'invalid input: parameter must be integer, was given string'              
                  continue
               if index not in range(len(player.hand)):
                  print 'invalid index'
               elif player.hand[index].__class__ != Card: #this doesn't account for minion/spell name conflicts
                  print 'this card is not a minion and cannot be summoned'                  
               elif player.hand[index].cost > player.current_crystals:
                  print 'not enough crystals! need %s' % str(player.hand[index].cost)
               else:
                  game.action_queue.append((actions.summon, (game, player, index)))
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
               if index not in range(len(player.hand)):
                  print 'invalid index'
               elif player.hand[index].__class__ != SpellCard:
                  print 'this card is not a spell and cannot be cast'
               elif player.hand[index].cost(game) > player.current_crystals:
                  print 'not enough crystals! need %s' % str(player.hand[index].cost(game))
               else:
                  game.action_queue.append((actions.cast_spell, (game, index)))
         elif action[0].lower() == 'attack':
            if len(action) != 3:
               print 'incorrect number of arguments: needs exactly 3'
            else:
               try:
                  action[1], action[2] = int(action[1]), int(action[2])
                  if not validate_attack(game, action[1], action[2]):
                     continue
                  else:
                     game.action_queue.append((actions.attack, (game, game.player.board[action[1]].minion_id, game.enemy.board[action[2]].minion_id)))
               except ValueError:
                  print 'invalid input: parameters must be integers, was given strings'
         elif action[0].lower() == 'debug':
            print 'effects: %s' % map(lambda x: '%s:%s' % (x.func.__name__, x.keywords), game.effect_pool)
            print 'actions: %s' % game.action_queue
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
         