# work in progress

def hunter(game):
   game.action_queue.append((deal_damage, (game, game.enemy.board[0].minion_id, 2)))

def warrior(game):
   game.player.armor += 2
   
def shaman(game):
    totems = ['Healing Totem', 'Searing Totem', 'Stoneclaw Totem', 'Wrath of Air Totem']
    for minion in game.player.board:
    if minion.name in totems:
        totems.remove(minion.name)
    if totems: # not all have been removed
        game.action_queue.append((spawn, (game, game.player, get_card(choice(totems)))))
    else:
        print 'all totems have already been summoned!'
        
   elif h == 'mage':
      id = target(game)
      game.action_queue.append((deal_damage, (game, id, 1)))
   elif h == 'warlock':
      game.action_queue.append((deal_damage, (game, game.player, 0, 2)))
      draw(game.player)
   elif h == 'rogue':
      game.player.weapon = Weapon(1,2)
   elif h == 'priest':
      id = target(game)
      game.action_queue.append((heal, (game, id, 2)))
   elif h == 'paladin':
      game.action_queue.append((summon, (game, game.player, get_card('Silver Hand Recruit'))))
   elif h == 'druid':
      game.player.armor += 1
      game.player.board[0].attack += 1
      game.effect_pool.append(minion_effects.effects['Druid'])