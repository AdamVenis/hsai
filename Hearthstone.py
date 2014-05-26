# need to install: 
# recordtype https://pypi.python.org/pypi/recordtype/

# card data:
# http://hearthstonejson.com/

from recordtype import recordtype
from json import loads
from random import shuffle
from random import randint

Player = recordtype('Player', 'hero hand deck board secrets crystals')
Card = recordtype('Card', 'id name cost attack health')
Minion = recordtype('Minion', 'id name attack health has_attacked')

def get_minions(): #for local temp variables
   raw_cards = loads(open("AllSets.json").read())
   minions = []
   for val in raw_cards.values():
      minions += filter(lambda x:x["type"]=="Minion", val)
   return minions
   
minions = get_minions()
   
def get_card_index(card):
   for index,minion in enumerate(minions):
      if minion['name'] == card:
         return index
   return None
   
def get_card(card):
   for index,minion in enumerate(minions):
      if minion['name'] == card:
         return Card(index, minion['name'], minion['cost'], minion['attack'], minion['health'])
   
def get_starter_deck():
   deck_names = ['Chillwind Yeti', 'Boulderfist Ogre', 'Acidic Swamp Ooze', 'River Crocolisk', 'Wisp']
   deck = map(get_card, deck_names)
   shuffle(deck) #LOL
   return deck
   
def display(p1, p2):
   #print p1, p2 #debug
   print ''
   print 'P2 Crystals: %s, Life: %s' % (p2.crystals, p2.board[0].health)
   print 'P2 Hand: %s' % ' | '.join(map(lambda x:x.name, p2.hand))
   print 'P2 Board: %s' % ' | '.join(map(lambda x:x.name, p2.board[1:])) #don't display the hero
   print 'P1 Board: %s' % ' | '.join(map(lambda x:x.name, p1.board[1:]))
   print 'P1 Hand: %s' % ' | '.join(map(lambda x:x.name, p1.hand))
   print 'P1 Crystals: %s, Life: %s' % (p1.crystals, p1.board[0].health)
   
def draw(player):
   if not player.deck:
      print "We're out of cards!"
   else:
      player.hand.append(player.deck[0])
      del player.deck[0]
      
def summon(player, ind):
   if ind >= len(player.hand):
      print 'Bad index!'
   elif player.hand[ind].cost > player.crystals:
      print 'Not enough crystals!'
   else:
      player.crystals -= player.hand[ind].cost
      player.board.append(Minion(player.hand[ind].id, player.hand[ind].name, player.hand[ind].attack, player.hand[ind].health, True))
      del player.hand[ind]
      
def attack(p1, p2, x, y):
   if x >= len(p1.board) or y >= len(p2.board):
      print 'Bad index!'
   elif p1.board[x].has_attacked:
      print 'This minion has already attacked!'
   elif p1.board[x].attack <= 0:
      print 'This minion cannot attack!'
   else:
      p1.board[x].has_attacked = True
      p1.board[x].health -= p2.board[y].attack
      p2.board[y].health -= p1.board[x].attack
      if p1.board[x].health <= 0 and x > 0: # don't kill the hero here
         del p1.board[x]
      if p2.board[y].health <= 0 and y > 0: # don't kill the hero here
         del p2.board[y]
   
def current_players(p1, p2, turn):
   if turn%2: return (p2,p1) #counterintuitive turn incrementing, to be able to use turn//2 for crystals
   else: return (p1,p2)
   
def dummy_minion():
   return Minion(None, 'dummy', 0, 30, False)
      
def play():

   greeting = randint(1,3)
   if greeting == 1:
      print 'Take a seat by the hearth!'
   elif greeting == 2:
      print 'Welcome back!'
   else:
      print "Busy night! But there's always room for another!"
      
   print 'Choose your class (Player 1)'
   p1 = Player(raw_input(), [], get_starter_deck(), [dummy_minion()], [], 1)
   print 'Choose your class (Player 2)'
   p2 = Player(raw_input(), [], get_starter_deck(), [dummy_minion()], [], 1)
   print '%s versus %s!' % (p1.hero, p2.hero)
   
   turn = 0
   for i in range(2):
      draw(p1)
      draw(p2)
   
   while True: #loops through turns
      print " "
      print "It is now player %d's turn" % (turn%2 + 1)
      p, enemy = current_players(p1, p2, turn)
      p.crystals = turn // 2 + 1
      draw(p)
      turn += 1
      
      for minion in p.board:
         minion.has_attacked = False
         
      while True: #loops through actions
         display(p1, p2)
         if p1.board[0].health <= 0 or p2.board[0].health <= 0:
            break
            
         action = raw_input().split()
         if len(action) < 1:
            print 'unable to parse action'
         elif action[0].lower() == 'end':
            break
         elif action[0].lower() == 'summon':
            if len(action) < 2: 
               print 'incorrect number of arguments'
            else: 
               try:
                  summon(p, int(action[1]))
               except ValueError:
                  print 'invalid input: parameter must be integer, was given string'
         elif action[0].lower() == 'attack':
            if len(action) < 3:
               print 'incorrect number of arguments'
            else:
               try:
                  attack(p, enemy, int(action[1]), int(action[2]))
               except ValueError:
                  print 'invalid input: parameters must be integers, was given strings'
                  
      if p1.board[0].health <= 0 and p2.board[0].health <= 0:
         print "it's a draw!"
         break
      elif p1.board[0].health <= 0:
         print "player 2 wins!"
         break
      elif p2.board[0].health <= 0:
         print "player 1 wins!"
         break
         