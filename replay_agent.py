from actions import parse_action
import events
import spells.spell_effects as spells

class ReplayAgent():
    # reads moves from a replay and plays out the moves as they were recorded
    def __init__(self):
        pass
        
    def move(self, game):
        pass

    def get_params(self, game, spell):
        if isinstance(spell, spells.SimpleSpell):
            return {}
        else:
            return {'target_id': game.aux_vals.popleft()}
