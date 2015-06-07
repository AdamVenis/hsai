# tested with python version 2.7.3

from utils import *
import card_data
import decks
from actions import *
import events
import minion_effects
import spell_effects
from card_types import MinionCard, SpellCard
import json
from random import shuffle

def mulligan(game, player):
    hand_size = 3 if player == game.player else 4
    shown_cards = player.deck[:hand_size]
    print 'Your cards are %s' % shown_cards
    mulligans = raw_input('Indicate which cards you want shuffled back by typing space delimited indices.')
    while not all(0 <= i < len(shown_cards) for i in map(int, mulligans.split())):
        mulligans = raw_input('Invalid input! Try again.')
    for i in map(int, mulligans.split()):
        player.deck[i], player.deck[-i] = player.deck[-i], player.deck[i]
    return mulligans


def new_game():

    print choice(['Take a seat by the hearth!', 'Welcome back!', "Busy night! But there's always room for another!"])
    heroes = [None, None]
    for i in range(2):
        heroes[i] = raw_input('Choose your class (Player %s) ' % (i + 1))
        while heroes[i].lower() not in ['warrior', 'hunter', 'mage', 'warlock', 'shaman', 'rogue', 'priest', 'paladin', 'druid']:
            heroes[i] = raw_input('Not a valid hero! Choose again. ')

    print '%s versus %s!' % tuple(heroes)
    game = Game(heroes[0], heroes[1], decks.default_mage, decks.default_mage)   
    shuffle(game.player1.deck)
    shuffle(game.player2.deck)
    p1_mulligans = mulligan(game, game.player1)
    p2_mulligans = mulligan(game, game.player2)        
    
    for i in range(3):
        game.action_queue.append((events.draw, (game, game.player1,)))
    for i in range(4):
        game.action_queue.append((events.draw, (game, game.player2,)))
    game.player2.hand.append(card_data.get_card('The Coin', game.player2))

    pregame_logs = {}
    pregame_logs['P1'] = {'hero': game.player1.hero,
                          'deck': [minion.name for minion in game.player1.deck], 
                          'kept': p1_mulligans}
    pregame_logs['P2'] = {'hero': game.player2.hero,
                          'deck': [minion.name for minion in game.player2.deck],
                          'kept': p2_mulligans}
    game.logger.info(json.dumps(pregame_logs))  
    
    for player in [game.player1, game.player2]:
        events.spawn(game, player, MinionCard(name='Hero', neutral_cost=None, attack=0,
                                               health=30, mechanics={}, race=None, owner=player, card_id=None))

    events.start_turn(game)
    play_out(game)


def parse_move(game, input):
    input = input.lower()
    if input.startswith("summon"):
        return Summon(game, input)
    elif input.startswith("attack"):
        return Attack(game, input)
    elif input.startswith("cast"):
        return Cast(game, input)
    elif input.startswith("hero"):
        return HeroPower(game)
    elif input.startswith("end"):
        return End()
    elif input.startswith("concede"):
        return Concede()
    else:
        print 'we lost boys', input
        return Action() # wtf is this


def load(replay_file):

    with open(replay_file) as replay:
        lines = replay.readlines()
        pregame = json.loads(lines[0])

        game = Game(pregame['P1']['hero'], pregame['P2']['hero'], pregame['P1']['deck'],
                pregame['P2']['deck'])

        for i in range(3):
            game.action_queue.append((events.draw, (game, game.player1,)))
        for i in range(4):
            game.action_queue.append((events.draw, (game, game.player2,)))
        game.player2.hand.append(card_data.get_card('The Coin', game.player2))

        for player in [game.player1, game.player2]:
            events.spawn(game, player, MinionCard(name='Hero', neutral_cost=None, attack=0,
                                                   health=30, mechanics={}, race=None, owner=player, card_id=None))

        events.start_turn(game)

        moves = []
        for action in lines[1:]:
            action = action.lower()
            if action.startswith('aux'):
                action = action.split()
                if len(action) != 2:
                    raise Exception("MALFORMED REPLAY")
                game.aux_vals.append(int(action[1]))
            else:
                moves.append(action)
                
        for move in moves:
            parsed_move = parse_move(game, move)
            if isinstance(parsed_move, Concede):
                return game
            game.action_queue.append((parsed_move.execute, (game,)))
            game.resolve()

        return play_out(game)
    print 'how could we ever get here?'


def play_out(game):

    while True:  # loops through actions

        player = game.player

        # TODO(adamvenis): turn this into a triggered effect?
        if game.player1.board[0].health <= 0 or game.player2.board[0].health <= 0:
            break

        game.resolve()
        display(game)

        action = raw_input().split()
        if len(action) < 1:
            print 'unable to parse action'
        elif action[0].lower() in ['end', 'end turn']:
            End().execute(game)
        elif action[0].lower() == 'hero' and action[1].lower() == 'power':
            game.logger.info('HERO_POWER %s' % game.player.hero)  
            hero_power(game)
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
                # this doesn't account for minion/spell name conflicts
                elif not isinstance(player.hand[index], MinionCard):
                    print 'this card is not a minion and cannot be summoned'
                elif player.hand[index].cost(game) > player.current_crystals:
                    print 'not enough crystals! need %s' % str(player.hand[index].cost(game))
                else:
                    game.logger.info('SUMMON %d' % index)
                    game.action_queue.append(
                        (summon, (game, player, index)))
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
                elif not isinstance(player.hand[index], SpellCard):
                    print 'this card is not a spell and cannot be cast'
                elif player.hand[index].cost(game) > player.current_crystals:
                    print 'not enough crystals! need %s' % str(player.hand[index].cost(game))
                else:
                    game.logger.info('CAST %d' % index)
                    game.action_queue.append(
                        (cast_spell, (game, index)))
        elif action[0].lower() == 'attack':
            if len(action) != 3:
                print 'incorrect number of arguments: needs exactly 3'
            else:
                try:
                    action[1], action[2] = int(action[1]), int(action[2])
                    if not validate_attack(game, action[1], action[2]):
                        continue
                    else:
                        game.logger.info('ATTACK %s %s' % (action[1], action[2]))
                        game.action_queue.append((attack, (game, action[1], action[2])))
                except ValueError:
                    print 'invalid input: parameters must be integers, was given strings'
        elif action[0].lower() == 'debug':
            print 'effects: %s' % ['%s:%s' % (effect.func.__name, effect.keywords) for effect in game.effect_pool]
            print 'actions: %s' % game.action_queue
            print 'minion ids: %s' % game.minion_pool.keys()
        elif action[0].lower() == 'concede':
            game.logger.info('CONCEDE %s' % ('P1' if player == game.player1 else 'P2'))
            game.player.board[0].current_health = 0
            break
        else:
            print 'unrecognized action'

    if game.player1.board[0].health <= 0 and game.player2.board[0].health <= 0:
        print "It's a draw!"
    elif game.player1.board[0].health <= 0:
        print "Player 2 wins!"
    elif game.player2.board[0].health <= 0:
        print "Player 1 wins!"
    return game # so the tests can verify the game state

# new_game()  # for debugging, just so it autoruns
