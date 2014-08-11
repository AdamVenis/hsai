from utils import *
import minion_effects
import spell_effects
import card_data


def draw(game, player):
    game.logger.info('DRAW %s' % ('P1' if player == game.player1 else 'P2'))
    if not player.deck:
        print "We're out of cards!"
        player.fatigue += 1
        player.board[0].current_health -= player.fatigue
    elif len(player.hand) == 10:
        print 'hand is full! %s is burned' % player.deck[0].name
        del player.deck[0]
    else:
        player.hand.append(player.deck[0])
        del player.deck[0]

        
def target(game, valid_targets=None):
    print 'pick a target'
    while True:
        user_input = raw_input().split(' ')
        if len(user_input) != 2:
            print 'wrong number of parameters'
            continue
        elif not is_int(user_input[1]):
            print 'second argument must be an integer'
            continue
        elif user_input[0] not in ['a', 'ally', 'e', 'enemy']:
            print 'first argument must refer to either the ally or the enemy'
            continue
            
        user_input[1] = int(user_input[1])
        if (user_input[0] in ['a', 'ally'] and user_input[1] not in range(len(game.player.board))) or (
                user_input[0] in ['e', 'enemy'] and user_input[1] not in range(len(game.enemy.board))):
            print 'second argument must be a valid index on the board'
            continue
            
        if user_input[0] in ['a', 'ally']:
            minion_id = game.player.board[user_input[1]].minion_id
        else:
            minion_id = game.enemy.board[user_input[1]].minion_id
        
        if valid_targets is not None and minion_id not in valid_targets:
            print 'this is an invalid target for this action'
            continue
        else:
            game.logger.info('TARGET %d' % minion_id)
            return minion_id


def summon(game, player, index):  # specifically for summoning from hand
    game.logger.info('SUMMON %s %d' % ('P1' if player == game.player1 else 'P2', index))
    card = player.hand[index]
    player.current_crystals -= card.cost(game)
    del player.hand[index]
    minion = spawn(game, player, card)
    trigger_effects(game, ['battlecry', minion.minion_id])


def spawn(game, player, card):  # equivalent of summon when not from hand
    minion = Minion(game, card)
    game.minion_pool[minion.minion_id] = minion
    game.minion_counter += 1
    player.board.append(minion)
    if 'Charge' in minion.mechanics:
        if 'Windfury' in minion.mechanics:
            minion.attacks_left = 2
        else:
            minion.attacks_left = 1
    if minion_effects.minion_effects.get(card.name):
        game.effect_pool.append(
            partial(minion_effects.minion_effects[card.name], id=minion.minion_id))
    game.logger.info('SPAWN %s %s' % ('P1' if player == game.player1 else 'P2', minion.name))
    return minion


def attack(game, ally_id, enemy_id):
    game.logger.info('ATTACK %s %s' % (ally_id, enemy_id))
    ally_minion = game.minion_pool[ally_id]
    enemy_minion = game.minion_pool[enemy_id]

    if ally_minion == ally_minion.owner.board[0] and game.player.weapon:
        game.player.weapon.durability -= 1
        if game.player.weapon.durability == 0:
            game.player.weapon = None

    if 'Stealth' in ally_minion.mechanics:
        ally_minion.mechanics.remove('Stealth')

    ally_minion.attacks_left -= 1

    if 'Divine Shield' in enemy_minion.mechanics:
        enemy_minion.mechanics.remove('Divine Shield')
    else:
        damage = ally_minion.attack(game)
        if damage > 0:
            game.action_queue.append(
                (deal_damage, (game, enemy_minion.minion_id, ally_minion.attack(game))))

    if 'Divine Shield' in ally_minion.mechanics:
        ally_minion.mechanics.remove('Divine Shield')
    else:
        damage = enemy_minion.attack(game)
        if enemy_minion == enemy_minion.owner.board[0] and enemy_minion.owner.weapon is not None:
            damage -= enemy_minion.owner.weapon.attack(game)
        if damage > 0:
            game.action_queue.append(
                (deal_damage, (game, ally_minion.minion_id, damage)))


def deal_damage(game, minion_id, damage):
    game.logger.info('DEAL_DAMAGE %d %d' % (minion_id, damage))
    minion = game.minion_pool[minion_id]
    player = minion.owner
    if minion.name == 'hero' and damage < player.armor:
        player.armor -= damage
    elif game.minion_pool[minion_id].name == 'hero' and player.armor:
        minion.current_health -= damage - player.armor
        player.armor = 0
    else:
        minion.current_health -= damage

    if minion.health(game) <= 0:
        if minion.name == 'hero':
            # equivalent to highest priority?
            trigger_effects(game, ['kill_hero', player])
        else:
            game.action_queue.append((kill_minion, (game, minion_id)))


def heal(game, minion_id, amount):
    game.logger.info('HEAL %d %d' % (minion_id, amount))
    minion = game.minion_pool[minion_id]
    minion.current_health = min(
        minion.current_health + amount, minion.max_health)


def cast_spell(game, index):
    game.logger.info('CAST %d' % index)
    spell_card = game.player.hand[index]
    # assumes spells can only be played on your turn
    game.player.current_crystals -= spell_card.cost(game)
    del game.player.hand[index]
    spell_effects.__dict__[name_to_func(spell_card.name)](game)


def silence(game, minion_id):  # removes effects and auras of a minion. or does it? (gurubashi)
    game.logger.info('SILENCE %d' % minion_id)
    minion = game.minion_pool[minion_id]
    game.effect_pool = [effect for effect in game.effect_pool if effect.keywords.get('id') != minion_id]
    minion.owner.auras = set(aura for aura in minion.owner.auras if aura.id != minion_id)


def kill_minion(game, minion_id):
    game.logger.info('KILL_MINION %d' % minion_id)    
    minion = game.minion_pool[minion_id]
    minion.owner.board.remove(minion)
    minion.owner.auras = set(
        aura for aura in minion.owner.auras if aura.id != minion_id)
    del game.minion_pool[minion_id]


def hero_power(game):
    game.logger.info('HERO_POWER %s' % game.player.hero)    
    if game.player.current_crystals < 2:
        print 'not enough mana!'
        return
    elif not game.player.can_hp:
        print 'can only use this once per turn!'
        return

    h = game.player.hero.lower()
    if h == 'hunter':
        game.action_queue.append(
            (deal_damage, (game, game.enemy.board[0].minion_id, 2)))
    elif h == 'warrior':
        game.player.armor += 2
    elif h == 'shaman':
        totems = ['Healing Totem', 'Searing Totem',
                  'Stoneclaw Totem', 'Wrath of Air Totem']
        for minion in game.player.board:
            if minion.name in totems:
                totems.remove(minion.name)
        if totems:  # not all have been removed
            game.action_queue.append(
                (spawn, (game, game.player, card_data.get_card(choice(totems)))))
        else:
            print 'all totems have already been summoned!'
            return
    elif h == 'mage':
        target_id = target(game)
        game.action_queue.append((deal_damage, (game, target_id, 1)))
    elif h == 'warlock':
        game.action_queue.append((deal_damage, (game, game.player, 0, 2)))
        game.action_queue.append((draw, (game, game.player)))
    elif h == 'rogue':
        game.player.weapon = Weapon(1, 2)
    elif h == 'priest':
        target_id = target(game)
        game.action_queue.append((heal, (game, target_id, 2)))
    elif h == 'paladin':
        game.action_queue.append(
            (summon, (game, game.player, card_data.get_card('Silver Hand Recruit'))))
    elif h == 'druid':
        game.player.armor += 1
        game.player.board[0].attack += 1
        game.effect_pool.append(minion_effects.minion_effects['Druid'])
    game.player.can_hp = False
    game.player.current_crystals -= 2
