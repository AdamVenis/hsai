from actions import parse_action
import events
import spells.spell_effects as spells

class HumanAgent():
    def __init__(self):
        pass
        
    def move(self, game):
        return parse_action(game, raw_input())

    def get_params(spell):
        if isinstance(spell, spells.SimpleSpell):
            return None
        elif isinstance(spell, spells.TargetCharacterSpell):
            return None
            # return events.target()
        else:
            return None