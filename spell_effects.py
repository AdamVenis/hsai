#NB: keep in alphabetical order

import actions
import utils # can't import * from here cause locals() is used below, and it needs to be kept clean

def arcane_missiles(game):
   for i in range(3 + game.player.spellpower):
      game.action_queue.append((actions.deal_damage, (game, utils.choice(game.enemy.board).minion_id, 1)))
      
def arcane_explosion(game):
   for minion in game.enemy.board[1:]:
      game.action_queue.append((actions.deal_damage, (game, minion.minion_id, 1 + game.player.spellpower)))
      
def arcane_intellect(game):
   for i in range(2):
      game.action_queue.append((actions.draw, (game.player,)))
      
def fireball(game):
   target_id = actions.target(game)
   game.action_queue.append((actions.deal_damage, (game, target_id, 6 + game.player.spellpower)))
   
def polymorph(game): #TODO: this needs validation (cannot target heroes)
   target_id = actions.target(game)
   actions.silence(game, target_id)
   minion = game.minion_pool[target_id]
   chicken = utils.Minion(game, minion.owner, utils.get_card('Chicken'))
   minion.transform_into(chicken)
   
def the_coin(game):
   game.player.current_crystals += 1 # should this be capped at 10?
 
exceptions = ['actions', 'utils', 'exceptions', 'hunters_mark']
spell_effects = {utils.func_to_name(key):val for key,val in locals().items() if key[0] != '_' and key not in exceptions}
# spell_effects["Hunter's Mark"] = hunters_mark # this is an example of how exceptions work  