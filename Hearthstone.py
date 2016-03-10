# tested with python version 2.7.3

from utils import *
import card_data
import decks
from actions import *
import events
import minions.minion_effects
import spells.spell_effects as spell_effects
from card_types import MinionCard, SpellCard
from human_agent import HumanAgent
from replay_agent import ReplayAgent

import json
from random import shuffle

def mulligan(game, player):

    hand_size = 3 if player == game.player else 4
    shown_cards = player.deck[:hand_size]
    print('Your cards are %s' % shown_cards)
    mulligans = raw_input('Indicate which cards you want shuffled back by typing space delimited indices.\n')
    while not all(0 <= int(index) < len(shown_cards) for index in mulligans.split()):
        mulligans = raw_input('Invalid input! Try again.')
    # TODO(adamvenis): bad logic, user could know where in the deck the shuffled cards went
    for i in map(int, mulligans.split()):
        player.deck[i], player.deck[-i] = player.deck[-i], player.deck[i]
    return mulligans


def new_game(agent1=HumanAgent(), agent2=HumanAgent()):

    print(choice(['Take a seat by the hearth!', 'Welcome back!',
                  'Busy night! But there\'s always room for another!']))

    game = Game(agent1.pick_hero(), agent2.pick_hero(), decks.default_mage, decks.default_mage)
    game.player1.hero, game.player2.hero = game.player1.hero(game), game.player2.hero(game)
    print('%s versus %s!' % (game.player1.hero, game.player2.hero))

    shuffle(game.player1.deck)
    shuffle(game.player2.deck)
    p1_mulligans = mulligan(game, game.player1)
    p2_mulligans = mulligan(game, game.player2)        
    
    for _ in range(3):
        game.add_event(events.draw, (game.player1,))
    for _ in range(4):
        game.add_event(events.draw, (game.player2,))
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
        events.spawn(game, player,
                     MinionCard(name='Hero', neutral_cost=None, attack=0,
                                health=30, mechanics={}, race=None,
                                owner=player, card_id=None))

    events.start_turn(game)
    return play_out(game, HumanAgent(), HumanAgent())


def load(replay_file):
    agent = ReplayAgent(replay_file)

    with open(replay_file) as replay:
        lines = replay.readlines()
        pregame = json.loads(lines[0])

        game = Game(agent.pick_hero(), agent.pick_hero(),
                    pregame['P1']['deck'], pregame['P2']['deck'])
        # unfortunate circular dependency
        game.player1.hero, game.player2.hero = game.player1.hero(game), game.player2.hero(game)

        for _ in range(3):
            game.add_event(events.draw, (game.player1,))
        for _ in range(4):
            game.add_event(events.draw, (game.player2,))
        game.player2.hand.append(card_data.get_card('The Coin', game.player2))

        for player in [game.player1, game.player2]:
            events.spawn(game, player,
                         MinionCard(name='Hero', neutral_cost=None, attack=0, health=30,
                                    mechanics={}, race=None, owner=player, card_id=None))

        events.start_turn(game)

        # this whole bit needs to go
        for action in lines[1:]:
            action = action.lower()
            if action.startswith('aux'):
                action = action.split()
                if len(action) != 2:
                    raise Exception("MALFORMED REPLAY")
                game.aux_vals.append(int(action[1]))

        while agent.move_list:
            game.resolve()
            action = agent.move(game)
            if isinstance(action, Cast) or isinstance(action, HeroPower):
                action.execute(game, agent)
            else:
                action.execute(game)

        return play_out(game, HumanAgent(), HumanAgent())
    print('how could we ever get here?')


def play_out(game, agent1, agent2):

    while not game.winner:  # loops through actions
        player = game.player
        agent = agent1 if player == game.player1 else agent2

        # TODO(adamvenis): turn this into a triggered effect?
        p1_dead = (len(game.player1.board) == 0 or
                   game.player1.board[0].name != 'Hero')
        p2_dead = (len(game.player2.board) == 0 or
                   game.player2.board[0].name != 'Hero')
        if p1_dead and p2_dead:
            game.winner = 3
            break
        elif p1_dead:
            game.winner = 2
            break
        elif p2_dead:
            game.winner = 1
            break

        while True:
            try:
                game.resolve()
                display(game)
                action = agent.move(game)
                if isinstance(action, Cast) or isinstance(action, HeroPower):
                    action.execute(game, agent)
                else:
                    action.execute(game)
                break
            except Exception as e: #user error - catch this elsewhere?
                print(e)

        if isinstance(action, Concede):
            break

    if game.winner == 3:
        print('It\'s a draw!')
    elif game.winner == 2:
        print('Player 2 wins!')
    elif game.winner == 1:
        print('Player 1 wins!')
    return game # so the tests can verify the game state
        
# new_game()  # for debugging, just so it autoruns
