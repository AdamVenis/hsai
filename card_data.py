# card data comes from:
# http://hearthstonejson.com/
# last updated: August 7th, 2014
# mechanics: Taunt, Stealth, Divine Shield, Windfury, Freeze, Enrage,
# HealTarget, Charge, Deathrattle, Aura, Combo, AdjacentBuff, Battlecry,
# Poisonous, Spellpower

from json import loads
from random import shuffle
from card_types import MinionCard, SpellCard


def get_all_cards():
    raw_cards = loads(open("AllSets.json").read())
    cards = []
    for val in raw_cards.values():
        cards += val
    return cards

cards = get_all_cards()


def get_card(card_name, owner):
    for card in cards:
        if card.get('name') == card_name:
            params = {'name': card.get('name'), 'neutral_cost': card.get(
                'cost', 0), 'owner': owner, 'card_id': card.get('id')}
            if card.get('type') == 'Minion':
                params['attack'] = card.get('attack')
                params['health'] = card.get('health')
                params['mechanics'] = card.get('mechanics', [])
                params['race'] = card.get('race')
                return MinionCard(**params)
            elif card.get('type') == 'Spell':
                return SpellCard(**params)
            elif card.get('type') == 'Weapon':
                params['attack'] = card.get('attack')
                params['durability'] = card.get('durability')
                return WeaponCard(**params)
    print 'ERROR: CARD NOT FOUND'


def get_deck(names, owner):
    deck = [get_card(name, owner) for name in names]
    shuffle(deck)  # LOL
    return deck
