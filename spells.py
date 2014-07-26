#NB: keep in alphabetical order

import Hearthstone
import events
import utils

spells = {} #TODO: populate this automatically (needs self-referral)

def arcane_missles(game):
   for i in range(3 + game.player.spellpower):
      game.event_queue.append((events.deal_damage, (game, choice(game.enemy.board).minion_id, 1)))
      
def arcane_explosion(game):
   for minion in game.enemy.board[1:]:
      game.event_queue.append((events.deal_damage, (game, minion.minion_id, 1 + game.player.spellpower)))
      
def arcane_intellect(game):
   for i in range(2):
      events.draw(game.player)
      
def fireball(game):
   target_id = Hearthstone.target(game)
   game.event_queue.append((events.deal_damage, (game, target_id, 6 + game.player.spellpower)))
   
def polymorph(game):
   target_id = Hearthstone.target(game)
   events.remove_traces(game, target_id)
   
   