# need to install: 
# recordtype https://pypi.python.org/pypi/recordtype/

# card data:
# http://hearthstonejson.com/

from recordtype import recordtype
from json import loads
from random import shuffle

Player = recordtype('Player', 'hero hand deck board secrets health crystals')
Card = recordtype('Card', 'name cost attack health id')
Minion = recordtype('Minion', 'id name attack health')

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
         return Card(minion['name'], minion['cost'], minion['attack'], minion['health'], index)
   
def get_starter_deck():
   deck = []
   deck.append(get_card('Chillwind Yeti'))
   deck.append(get_card('Boulderfist Ogre'))
   deck.append(get_card('Acidic Swamp Ooze'))
   deck.append(get_card('River Crocolisk'))
   deck.append(get_card('Wisp'))
   shuffle(deck)
   return deck
   
def display(p1, p2):
   print ''
   print 'P2 Hand: %s' % ' | '.join(map(lambda x:x.name, p2.hand))
   print 'P2 Board: %s' % ' | '.join(map(lambda x:x.name, p2.board))
   print 'P1 Board: %s' % ' | '.join(map(lambda x:x.name, p1.board))
   print 'P1 Hand: %s' % ' | '.join(map(lambda x:x.name, p1.hand))
   
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
      player.board.append(player.hand[ind])
      del player.hand[ind]
   
def current_player(p1, p2, turn):
   if turn%2: return p1
   else: return p2
      
def play():

   print 'Take a seat by the hearth!'
   print 'Choose your class (Player 1)'
   p1 = Player(raw_input(), [], get_starter_deck(), [], [], 30, 1)
   print 'Choose your class (Player 2)'
   p2 = Player(raw_input(), [], get_starter_deck(), [], [], 30, 1)
   print '%s versus %s!' % (p1.hero, p2.hero)
   
   turn = 0
   for i in range(2):
      draw(p1)
      draw(p2)
   
   print "It is now player %d's turn" % (turn%2 + 1)
   p = current_player(p1, p2, turn)
   p.crystals = turn // 2 + 1
   
   display(p1, p2)
   summon(p, 0)
   display(p1, p2)
   