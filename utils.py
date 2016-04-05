from __future__ import print_function

import logging
from random import sample
from time import strftime, gmtime



def apply_auras(game, player, object, stat, value):
    for aura in player.auras:
        value = aura.modifier(game, object, stat, value)
    return value


def func_to_name(s):
    """some_function_name becomes Some Function Name"""
    s = s.split('_')
    return ' '.join(word.capitalize() for word in s)


def name_to_func(s):
    return s.lower().replace(' ', '_')


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_hero(minion):
    return minion == minion.owner.board[0]


def display(game):

    player1_board_string = [[' ' * 9],
                            'P1 Board: ' + ' '.join('|%s|' % m for m in game.player1.board[1:]),
                            [' ' * 9]]
    player2_board_string = [[' ' * 9],
                            'P2 Board: ' + ' '.join('|%s|' % m for m in game.player2.board[1:]),
                            [' ' * 9]]

    for minion in game.player1.board[1:]:
        player1_board_string[0].append('-' * (len(minion.name) + 2))
        player1_board_string[2].append('|' + str(minion.attack)
                                       + ' ' * (len(minion.name)
                                                - len(str(minion.attack))
                                                - len(str(minion.health)))
                                       + str(minion.health) + '|')

    player1_board_string[0] = ' '.join(player1_board_string[0])
    player1_board_string[2] = ' '.join(player1_board_string[2])
    player1_board_string.append(player1_board_string[0])

    for minion in game.player2.board[1:]:
        player2_board_string[0].append('-' * (len(minion.name) + 2))
        player2_board_string[2].append('|' + str(minion.attack)
                                       + ' ' * (len(minion.name)
                                                - len(str(minion.attack))
                                                - len(str(minion.health)))
                                       + str(minion.health) + '|')

    player2_board_string[0] = ' '.join(player2_board_string[0])
    player2_board_string[2] = ' '.join(player2_board_string[2])
    player2_board_string.append(player2_board_string[0])

    print('-' * 79)
    print('Player2 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (
        game.player2.hero, game.player2.current_crystals, 
        game.player2.crystals, game.player2.board[0].health,
        '' if game.player2.armor == 0 else ', Armor: %d' % game.player2.armor,
        '' if game.player2.weapon == None else ', Weapon: %s' % game.player2.weapon,
        '' if game.player2.board[0].attack == 0 else ', Attack: %d' % game.player2.board[0].attack))
    print('Player2 Hand: ' + ' | '.join(minion.name for minion in game.player2.hand))
    for i in range(len(player2_board_string[0]) / 79 + 1):
        for j in player2_board_string:
            print(j[i * 79:(i + 1) * 79])
    for i in range(len(player1_board_string[0]) / 79 + 1):
        for j in player1_board_string:
            print(j[i * 79:(i + 1) * 79])
    print('Player1 Hand: ' + ' | '.join(minion.name for minion in game.player1.hand))
    print('Player1 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (
        game.player1.hero, game.player1.current_crystals,
        game.player1.crystals, game.player1.board[0].health,
        '' if game.player1.armor == 0 else ', Armor: %d' % game.player1.armor,
        '' if game.player1.weapon == None else ', Weapon: %s' % game.player1.weapon,
        '' if game.player1.board[0].attack == 0 else ', Attack: %d' % game.player1.board[0].attack))


def trigger_effects(game, trigger):
    game.effect_pool = [effect for effect in game.effect_pool
                        if not effect(game, trigger)]

def opponent(game, player):
    return game.enemy if player == game.player else game.player

def get_logger(save_replay):
    logger = logging.getLogger()
    time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    if save_replay:
        log_file_handler = logging.FileHandler('replays/%s.hsrep' % time)
        logger.addHandler(log_file_handler)
    logger.setLevel(logging.INFO)
    return logger

def replace_hand(deck, from_inds, to_inds=None):
    if to_inds is None:
        to_inds = sample(range(4, 30), len(from_inds))
    for i, j in zip(from_inds, to_inds):
        deck[i], deck[j] = deck[j], deck[i]
    return to_inds
