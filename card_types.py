from utils import *

class Card():
    def __init__(self, name, neutral_cost, owner, card_id):
        self.name = name
        self.neutral_cost = neutral_cost
        self.owner = owner
        self.card_id = card_id

    def cost(self, game):
        rtn = self.neutral_cost
        rtn = apply_auras(game, self.owner, self, 'play', rtn)
        return rtn
        
    def __repr__(self):
        return self.name


class MinionCard(Card):
    def __init__(self, name, neutral_cost, attack, health, mechanics, race, owner, card_id):
        Card.__init__(self, name, neutral_cost, owner, card_id)
        self.attack = attack
        self.health = health
        self.mechanics = mechanics
        self.race = race


class SpellCard(Card):
    def __init__(self, name, neutral_cost, owner, card_id):
        Card.__init__(self, name, neutral_cost, owner, card_id)


class WeaponCard(Card):
    def __init__(self, name, neutral_cost, attack, durability, owner, card_id):
        Card.__init__(self, name, neutral_cost, owner, card_id)
        self.attack = attack
        self.durability = durability
