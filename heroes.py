# work in progress, currently unused

def hunter(game):
    game.add_event(deal_damage, (game.enemy.board[0].minion_id, 2))

def warrior(game):
    game.player.armor += 2
   
def shaman(game):
    totems = ['Healing Totem', 'Searing Totem', 'Stoneclaw Totem', 'Wrath of Air Totem']
    for minion in game.player.board:
        if minion.name in totems:
            totems.remove(minion.name)
    if totems: # not all have been removed
        game.add_event(spawn, 
            (game.player, card_data.get_card(game.choice(totems, random=True), game.player)))
    else:
        print 'all totems have already been summoned!'
        '''
    elif h == 'mage':
        id = target(game)
        game.add_event(deal_damage, (target_id, 1))
    elif h == 'warlock':
        game.add_event(deal_damage, (game.player.board[0].minion_id, 2))
        game.add_event(draw, (game.player,))
    elif h == 'rogue':
        game.player.weapon = Weapon(1,2)
    elif h == 'priest':
        id = target(game)
        game.add_event(heal, (target_id, 2))
    elif h == 'paladin':
        game.add_event(spawn, (game.player, card_data.get_card('Silver Hand Recruit')))
    elif h == 'druid':
        game.player.armor += 1
        game.player.board[0].attack += 1
        game.effect_pool.append(minion_effects.effects['Druid'])
        '''