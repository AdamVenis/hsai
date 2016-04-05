
from utils import *
import card_data

from collections import deque
from random import randint

class Game():
    def __init__(self, hero1, hero2, deck1, deck2, save_replay=True):
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
        self.logger = get_logger(save_replay)
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

    def add_event(self, event, args=()):
        self.action_queue.append((event, (self,) + args))

    def resolve(self):
        while self.action_queue:
            #display(self) # uncomment this?
            action = self.action_queue.popleft() # TODO(adamvenis): fix resolution order
            # [1:] 'game' gets cut out, as it's always the first parameter
            trigger_effects(self, [action[0].__name__] + list(action[1][1:]))
            action[0](*action[1])  # tuple with arguments in second slot

    @property
    def ALL_MINIONS(self):
        return self.player.board[1:] + self.enemy.board[1:]

    @property
    def ALLY_MINIONS(self):
        return self.player.board[1:]

    @property
    def ENEMY_MINIONS(self):
        return self.enemy.board[1:]

    @property
    def ALL_CHARACTERS(self):
        return self.player.board + self.enemy.board


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


class Spell():
	@staticmethod
	def cast():
		raise NotImplementedError('Subclasses should implement this!')
