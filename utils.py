from random import shuffle, randint, choice
from collections import deque
import card_data


class Game():
    def __init__(self, hero1, hero2, deck1, deck2, logger, aux_vals):
        # weirdly cyclic dependency with player, game and deck
        self.player1 = Player(hero=hero1, deck=None)
        self.player2 = Player(hero=hero2, deck=None)
        self.player1.deck = card_data.get_deck(deck1, self.player1)
        self.player2.deck = card_data.get_deck(deck2, self.player2)
        # consider changing this terminology to current_player and
        # current_enemy
        self.player = self.player1
        self.enemy = self.player2
        self.turn = 0
        self.effect_pool = []
        self.action_queue = deque()
        self.minion_pool = {}
        self.minion_counter = 1000  # dummy value
        self.logger = logger
        self.aux_vals = aux_vals
        
    def get_aux(self, size, random=False):
        if self.aux_vals:
            return aux_vals.pop()
        elif random:
            return randint(size)
        else:
            return target(game)


class Player():
    def __init__(self, hero, deck):
        self.hero = hero
        self.deck = deck
        self.hand = []
        self.board = []
        self.secrets = []
        self.crystals = 0
        self.current_crystals = 0
        self.armor = 0
        self.weapon = None
        self.auras = set([])
        self.spellpower = 0
        self.fatigue = 0
        self.can_hp = True
        self.overload = 0
        self.combo = 0

    def __str__(self):
        print 'PLAYER'  # TODO: this is stupid


class Minion():
    def __init__(self, game, card):
        self.name = card.name
        self.neutral_attack = card.attack
        self.current_attack = card.attack
        self.neutral_health = card.health
        self.max_health = card.health
        self.current_health = card.health
        self.mechanics = card.mechanics
        self.race = card.race
        self.attacks_left = 0
        self.minion_id = game.minion_counter
        self.owner = card.owner
        game.minion_pool[self.minion_id] = self
        game.minion_counter += 1

    def attack(self, game):  # TODO : add these to account for auras
        rtn = self.current_attack
        # this minion is a hero
        if self.owner.board.index(self) == 0 and self.owner.weapon:
            rtn += self.owner.weapon.attack
        rtn = apply_auras(game, self.owner, self, 'attack', rtn)
        return rtn

    def health(self, game):
        rtn = self.current_health
        rtn = apply_auras(game, self.owner, self, 'health', rtn)
        return rtn

    def transform_into(self, new_minion):
        self.name = new_minion.name
        self.neutral_attack = new_minion.neutral_attack
        self.current_attack = new_minion.current_attack
        self.neutral_health = new_minion.neutral_health
        self.max_health = new_minion.max_health
        self.current_health = new_minion.current_health
        self.mechanics = new_minion.mechanics
        self.attacks_left = 0

    def __repr__(self):
        return self.name


class Weapon():
    def __init__(self, attack, durability):
        self.current_attack = attack
        self.durability = durability

    def attack(self, game):  # to make room for auras (aka for spiteful smith)
        rtn = self.current_attack
        return rtn


class Aura():
    def __init__(self, id, modifier):
        self.id = id
        self.modifier = modifier
        self.aux_vars = {}


def apply_auras(game, player, object, stat, value):
    for aura in player.auras:
        value = aura.modifier(game, object, stat, value)
    return value


def validate_attack(game, player_ind, enemy_ind):
    if player_ind not in range(len(game.player.board)):
        print 'wrong index for ally minion. Must supply a number from 0 to %s' % str(len(game.player.board))
        return False
    elif enemy_ind not in range(len(game.enemy.board)):
        print 'wrong index for enemy minion. Must supply a number from 0 to %s' % str(len(game.enemy.board))
        return False

    ally_minion = game.player.board[player_ind]
    enemy_minion = game.enemy.board[enemy_ind]

    if ally_minion.attacks_left <= 0:
        print 'this minion cannot attack'
        return False
    elif ally_minion.attack(game) <= 0:
        print 'this minion has no attack'
        return False
    elif 'Frozen' in ally_minion.mechanics or 'Thawing' in ally_minion.mechanics:
        print 'This minion is frozen, and cannot attack'
        return False
    elif 'Stealth' in enemy_minion.mechanics:
        print 'cannot attack a minion with stealth'
        return False
    elif 'Taunt' not in enemy_minion.mechanics and any('Taunt' in minion.mechanics for minion in game.enemy.board[1:]):
        print 'must target a minion with taunt'
        return False
    return True


def func_to_name(s):
    s = s.split('_')
    return ' '.join([word[0].upper() + word[1:] for word in s])


def name_to_func(s):
    s = s.replace(' ', '_')
    return s.lower()


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_hero(minion):
    return minion.owner.board.index(minion) == 0


def display(game):
    print game.minion_pool
    player1_board_string = [[' ' * 9], 'P1 Board: %s' %
                            ' '.join(map(lambda x:'|' + x.name + '|', game.player1.board[1:])), [' ' * 9]]
    player2_board_string = [[' ' * 9], 'P2 Board: %s' %
                            ' '.join(map(lambda x:'|' + x.name + '|', game.player2.board[1:])), [' ' * 9]]

    for minion in game.player1.board[1:]:
        player1_board_string[0].append('-' * (len(minion.name) + 2))
        player1_board_string[2].append('|' + str(minion.attack(game))
                                       + ' ' *
                                       (len(
                                           minion.name) - len(str(minion.attack(game))) - len(str(minion.health(game))))
                                       + str(minion.health(game)) + '|')

    player1_board_string[0] = ' '.join(player1_board_string[0])
    player1_board_string[2] = ' '.join(player1_board_string[2])
    player1_board_string.append(player1_board_string[0])

    for minion in game.player2.board[1:]:
        player2_board_string[0].append('-' * (len(minion.name) + 2))
        player2_board_string[2].append('|' + str(minion.attack(game))
                                       + ' ' *
                                       (len(
                                           minion.name) - len(str(minion.attack(game))) - len(str(minion.health(game))))
                                       + str(minion.health(game)) + '|')

    player2_board_string[0] = ' '.join(player2_board_string[0])
    player2_board_string[2] = ' '.join(player2_board_string[2])
    player2_board_string.append(player2_board_string[0])

    print '-' * 79
    print 'Player2 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (
          game.player2.hero, game.player2.current_crystals, game.player2.crystals, game.player2.board[
              0].health(game),
          '' if game.player2.armor == 0 else ', Armor : ' +
        str(game.player2.armor),
          '' if game.player2.weapon == None else ', Weapon : ' +
        str(game.player2.weapon.attack(game)) +
        '/' + str(game.player2.weapon.durability),
          '' if game.player2.board[0].attack == 0 else ', Attack : ' + str(game.player2.board[0].attack(game)))
    print 'Player2 Hand: %s' % ' | '.join(map(lambda x: x.name, game.player2.hand))
    for i in range(len(player2_board_string[0]) / 79 + 1):
        for j in player2_board_string:
            print j[i * 79:(i + 1) * 79]
    for i in range(len(player1_board_string[0]) / 79 + 1):
        for j in player1_board_string:
            print j[i * 79:(i + 1) * 79]
    print 'Player1 Hand: %s' % ' | '.join(map(lambda x: x.name, game.player1.hand))
    print 'Player1 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (
          game.player1.hero, game.player1.current_crystals, game.player1.crystals, game.player1.board[
              0].health(game),
          '' if game.player1.armor == 0 else ', Armor : ' +
        str(game.player1.armor),
          '' if game.player1.weapon == None else ', Weapon : ' +
        str(game.player1.weapon.attack(game)) +
        '/' + str(game.player1.weapon.durability),
          '' if game.player1.board[0].attack == 0 else ', Attack : ' + str(game.player1.board[0].attack(game)))


def trigger_effects(game, trigger):
    game.effect_pool = filter(lambda x: not x(game, trigger), game.effect_pool)


def opponent(game, player):
    if player == game.player:
        return game.enemy
    else:
        return game.player
