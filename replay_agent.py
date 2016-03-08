from actions import parse_action
import events
import spells.spell_effects as spells

import json

class ReplayAgent():
    # reads moves from a replay and plays out the moves as they were recorded
    def __init__(self, replay_file):
        with open(replay_file) as replay:
            lines = replay.readlines()
            self.pregame = json.loads(lines[0])
            self.aux_vals = []
            self.move_list = []
            for action in lines[1:]:
                action = action.lower()
                if action.startswith('aux'):
                    action = action.split()
                    if len(action) != 2:
                        raise Exception("MALFORMED REPLAY")
                    self.aux_vals.append(int(action[1]))
                else:
                    self.move_list.append(action)
            self.move_list.reverse()

    def move(self, game):
        next
        return parse_action(game, self.move_list.pop())

    def get_params(self, game, spell):
        if isinstance(spell, spells.SimpleSpell):
            return {}
        else:
            return {'target_id': game.aux_vals.popleft()}
