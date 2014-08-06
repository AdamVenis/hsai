# card data comes from:
# http://hearthstonejson.com/

# mechanics: Taunt, Stealth, Divine Shield, Windfury, Freeze, Enrage, HealTarget, Charge, Deathrattle, Aura, Combo, AdjacentBuff, Battlecry, Poisonous, Spellpower

from json import loads

def get_minions_and_spells(): #for local temp variables
   raw_cards = loads(open("AllSets.json").read())
   minions = []
   spells = []
   for val in raw_cards.values():
      for card in val:
         if card['type'] == 'Minion':
            minions.append(card)
         elif card['type'] == 'Spell':
            spells.append(card)
   return minions, spells
   
minions, spells = get_minions_and_spells()
