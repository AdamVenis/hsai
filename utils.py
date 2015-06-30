from random import shuffle, randint, choice
from collections import deque
import card_data
import logging
from time import strftime, gmtime


class Game():
    def __init__(self, hero1, hero2, deck1, deck2):
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
        self.logger = get_logger()
        self.aux_vals = deque()
        self.winner = 0 # 0 for no winner yet, 1 for P1 has won, 2 for P2, 3 for tie
        
    def choice(self, lst, random=False):
        rtn = None
        if self.aux_vals:
            rtn = self.aux_vals.popleft()
        elif random:
            rtn = lst[randint(0, len(lst) - 1)]
        else:
            # TODO(adamvenis): add a pretty prompt here
            rtn = lst[input()]
        self.logger.info('AUX %d' % rtn)
        return rtn
        
    def get_aux(self, size, random=False):
        rtn = None
        if self.aux_vals:
            rtn = self.aux_vals.popleft()
        elif random:
            rtn = randint(0, size)
        else:
            rtn = target(self)

        self.logger.info('AUX %d' % rtn)
        return rtn

    def resolve(self):
        while self.action_queue:
            display(self)
            action = self.action_queue.popleft() #TODO(adamvenis): fix resolution order
            print 'ACTION:', action[0].__name__, list(action[1][1:])
            # [1:] 'game' gets cut out, as it's always the first parameter
            trigger_effects(self, [action[0].__name__] + list(action[1][1:]))
            action[0](*action[1])  # tuple with arguments in second slot        


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
        self.auras = set()
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
        self.game = game
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

    @property
    def attack(self):  # TODO : add these to account for auras
        rtn = self.current_attack
        if self.name == 'Hero' and self.owner.weapon:
            rtn += self.owner.weapon.attack
        rtn = apply_auras(self.game, self.owner, self, 'attack', rtn)
        return rtn

    @property
    def health(self):
        rtn = self.current_health
        rtn = apply_auras(self.game, self.owner, self, 'health', rtn)
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

    def __str__(self):
        return self.name


class Weapon():
    def __init__(self, game, attack, durability):
        self.game = game
        self.current_attack = attack
        self.durability = durability

    @property
    def attack(self, game):  # to make room for auras (aka for spiteful smith)
        rtn = self.current_attack
        return rtn

    def __str__(self):
        return '%d/%d' % (self.current_attack, self.durability)


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
    elif ally_minion.attack <= 0:
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

    print '-' * 79
    print 'Player2 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (
        game.player2.hero, game.player2.current_crystals, 
        game.player2.crystals, game.player2.board[0].health,
        '' if game.player2.armor == 0 else ', Armor : %d' % game.player2.armor,
        '' if game.player2.weapon == None else ', Weapon : %s' % game.player2.weapon,
        '' if game.player2.board[0].attack == 0 else ', Attack : %d' % game.player2.board[0].attack)
    print 'Player2 Hand: ' + ' | '.join(minion.name for minion in game.player2.hand)
    for i in range(len(player2_board_string[0]) / 79 + 1):
        for j in player2_board_string:
            print j[i * 79:(i + 1) * 79]
    for i in range(len(player1_board_string[0]) / 79 + 1):
        for j in player1_board_string:
            print j[i * 79:(i + 1) * 79]
    print 'Player1 Hand: ' + ' | '.join(minion.name for minion in game.player1.hand)
    print 'Player1 Hero: %s, Crystals: %s/%s, Life: %s%s%s%s' % (
        game.player1.hero, game.player1.current_crystals,
        game.player1.crystals, game.player1.board[0].health,
        '' if game.player1.armor == 0 else ', Armor : %d' % game.player1.armor,
        '' if game.player1.weapon == None else ', Weapon : %s' % game.player1.weapon,
        '' if game.player1.board[0].attack == 0 else ', Attack : %d' % game.player1.board[0].attack)


def trigger_effects(game, trigger):
    game.effect_pool = filter(lambda x: not x(game, trigger), game.effect_pool)


def opponent(game, player):
    if player == game.player:
        return game.enemy
    else:
        return game.player


def lazy(original_class):
    orig_init = original_class.__init__
    orig_execute = original_class.execute
    
    def __init__(self, *args):
        self.is_init = False
        self.init_args = args

    def execute(self, game):
        if not self.is_init:
            self.is_init = True
            orig_init(self, *self.init_args)
        orig_execute(self, game)
    
    original_class.__init__ = __init__
    original_class.execute = execute
    return original_class


def get_logger():
    logger = logging.getLogger()
    time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    log_file_handler = logging.FileHandler('replays/%s.hsrep' % time)
    logger.addHandler(log_file_handler)
    logger.setLevel(logging.INFO)
    return logger
