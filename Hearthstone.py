# tested with python version 2.7.3

from utils import *
import card_data
import decks
from actions import *
import events
import minions.minion_effects
import spell_effects
from card_types import MinionCard, SpellCard
from human_agent import HumanAgent

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
    play_out(game, HumanAgent(), HumanAgent())


def load(replay_file):

    with open(replay_file) as replay:
        lines = replay.readlines()
        pregame = json.loads(lines[0])

        game = Game(pregame['P1']['hero'], pregame['P2']['hero'],
                    pregame['P1']['deck'], pregame['P2']['deck'])

        for i in range(3):
            game.action_queue.append((events.draw, (game, game.player1,)))
        for i in range(4):
            game.action_queue.append((events.draw, (game, game.player2,)))
        game.player2.hand.append(card_data.get_card('The Coin', game.player2))

        for player in [game.player1, game.player2]:
            events.spawn(game, player,
                         MinionCard(name='Hero', neutral_cost=None, attack=0, health=30,
                                    mechanics={}, race=None, owner=player, card_id=None))

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

        return play_out(game, HumanAgent(), HumanAgent())
    print 'how could we ever get here?'


def play_out(game, agent1, agent2):

    while not game.winner:  # loops through actions
        player = game.player
        agent = agent1 if player == game.player1 else agent2

        # TODO(adamvenis): turn this into a triggered effect?
        if game.player1.board[0].health <= 0 and game.player2.board[0].health <= 0:
            game.winner = 3
            break
        elif game.player1.board[0].health <= 0:
            game.winner = 2
            break
        elif game.player2.board[0].health <= 0:
            game.winner = 1
            break

        while True:
            try:
                game.resolve()
                display(game)
                action = agent.move(game)
                action.execute(game)
                break
            except Exception as e:
                print e

        if isinstance(action, Concede):
            break

    if game.winner == 3:
        print "It's a draw!"
    elif game.winner == 2:
        print "Player 2 wins!"
    elif game.winner == 1:
        print "Player 1 wins!"
    return game # so the tests can verify the game state
        
# new_game()  # for debugging, just so it autoruns
