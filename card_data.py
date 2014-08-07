# card data comes from:
# http://hearthstonejson.com/
# last updated: August 7th, 2014
# mechanics: Taunt, Stealth, Divine Shield, Windfury, Freeze, Enrage, HealTarget, Charge, Deathrattle, Aura, Combo, AdjacentBuff, Battlecry, Poisonous, Spellpower

from json import loads

def get_all_cards():
   raw_cards = loads(open("AllSets.json").read())
   cards = []
   for val in raw_cards.values():
      cards += val
   return cards
   
cards = get_all_cards()
