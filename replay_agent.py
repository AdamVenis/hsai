from actions import parse_action
from heroes import *
import events
import spells.spell_effects as spells

import json

class ReplayAgent():
    # reads moves from a replay and plays out the moves as they were recorded
    def __init__(self, replay_file):
        with open(replay_file) as replay:
            lines = replay.readlines()
            self.pregame = json.loads(lines[0])
            self.heroes = [self.pregame['P2']['hero'], self.pregame['P1']['hero']]
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

    def pick_hero(self):
        return globals()[self.heroes.pop().capitalize()]

    def move(self, game):
        next
        return parse_action(game, self.move_list.pop())

    def hero_power_params(self, game):
        print('hi', game.player.hero, game.aux_vals, self.aux_vals)
        if isinstance(game.player.hero, SimpleHero):
            print('ONE')
            return None
        elif isinstance(game.player.hero, TargetCharacterHero):
            print('TONE')
            return {'target_id': game.aux_vals.popleft()}
        else:
            print('THONE')
            return None

    def spell_params(self, game, spell):
        if isinstance(spell, spells.SimpleSpell):
            return {}
        else:
            return {'target_id': game.aux_vals.popleft()}
