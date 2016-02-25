from functools import partial
from utils import Minion, is_int, trigger_effects
import minions.minion_effects

def deal_damage(game, minion_id, damage):
    minion = game.minion_pool[minion_id]
    player = minion.owner
    if minion.name == 'hero' and damage < player.armor:
        player.armor -= damage
    elif game.minion_pool[minion_id].name == 'hero' and player.armor:
        minion.current_health -= damage - player.armor
        player.armor = 0
    else:
        minion.current_health -= damage

    if minion.health <= 0:
        if minion.name == 'hero':
            # equivalent to highest priority?
            trigger_effects(game, ['kill_hero', player])
        else:
            game.add_event(kill_minion, (minion_id,))


def draw(game, player):
    if not player.deck:
        print("We're out of cards!")
        player.fatigue += 1
        player.board[0].current_health -= player.fatigue
    elif len(player.hand) == 10:
        print('hand is full! %s is burned' % player.deck[0].name)
        del player.deck[0]
    else:
        print('Player %d draws %s' % (1 if player == game.player1 else 2,
                                      player.deck[0].name))
        player.hand.append(player.deck[0])
        del player.deck[0]


def heal(game, minion_id, amount):
    minion = game.minion_pool[minion_id]
    minion.current_health = min(
        minion.current_health + amount, minion.max_health)


def kill_minion(game, minion_id): 
    minion = game.minion_pool[minion_id]
    minion.owner.board.remove(minion)
    minion.owner.auras = set(aura for aura in minion.owner.auras
                             if aura.id != minion_id)
    del game.minion_pool[minion_id]


def pick(game, options):
    # mostly for druid stuff

    if game.aux_vals: # loading from replay
        return game.aux_vals.popleft()

    print('Pick one of the following by typing the corresponding number:')
    for i, option in enumerate(options):
        print('%d : %s' % (i, option))
    while True:
        input = raw_input()
        try:
            int_input = int(input)
            return int_input
        except ValueError:
            continue


def silence(game, minion_id):
    # removes effects and auras of a minion. or does it? (gurubashi)
    try:
        minion = game.minion_pool[minion_id]
    except KeyError:
        return
    game.effect_pool = [effect for effect in game.effect_pool if effect.keywords.get('id') != minion_id]
    minion.owner.auras = set(aura for aura in minion.owner.auras if aura.id != minion_id)


def spawn(game, player, card, position=None):
    # equivalent of summon when not from hand
    
    if position is None: # default position is on the right
        position = len(player.board) - 1

    minion = Minion(game, card)
    player.board.insert(position + 1, minion) # never displace the hero
    if 'Charge' in minion.mechanics:
        if 'Windfury' in minion.mechanics:
            minion.attacks_left = 2
        else:
            minion.attacks_left = 1
    if minions.minion_effects.minion_effects.get(card.name):
        game.effect_pool.append(
            partial(minions.minion_effects.minion_effects[card.name], id=minion.minion_id))
    return minion


def start_turn(game):
    
    # implicit reference for convenience
    player = game.player
    player.crystals = min(player.crystals + 1, 10)
    player.current_crystals = player.crystals
    game.add_event(draw, (player,))

    print('\nIt is now Player %d\'s turn' % ((game.turn % 2) + 1))

    for minion in player.board:
        if 'Windfury' in minion.mechanics:
            minion.attacks_left = 2
        elif 'Frozen' in minion.mechanics:
            minion.mechanics.remove('Frozen')
            minion.mechanics.add('Thawing')
        elif 'Thawing' in minion.mechanics:
            minion.mechanics.remove('Thawing')
        else:
            minion.attacks_left = 1
    player.can_hp = True

    trigger_effects(game, ['start_turn', player])    


def target(game, valid_targets=None): # TODO(adamvenis): make this agent specific

    if game.aux_vals: # loading from replay
        return game.aux_vals.popleft()

    print('pick a target')
    while True:
        user_input = raw_input().split(' ')
        if len(user_input) != 2:
            print('wrong number of parameters')
            continue
        elif not is_int(user_input[1]):
            print('second argument must be an integer')
            continue
        elif user_input[0] not in ['a', 'ally', 'e', 'enemy']:
            print('first argument must refer to either the ally or the enemy')
            continue
            
        user_input[1] = int(user_input[1])
        if (user_input[0] in ['a', 'ally'] and user_input[1] not in range(len(game.player.board))) or (
                user_input[0] in ['e', 'enemy'] and user_input[1] not in range(len(game.enemy.board))):
            print('second argument must be a valid index on the board')
            continue
            
        if user_input[0] in ['a', 'ally']:
            minion_id = game.player.board[user_input[1]].minion_id
        else:
            minion_id = game.enemy.board[user_input[1]].minion_id

        if valid_targets is not None and minion_id not in valid_targets:
            print('this is an invalid target for this action')
            continue
        else:
            game.logger.info('AUX %d' % minion_id)
            return minion_id

