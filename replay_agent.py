from actions import *
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

        input = self.move_list.pop().lower()
        if input.startswith('summon'):
            return Summon(game, *map(int, input.split()[1:]))
        elif input.startswith('attack'):
            return Attack(game, *map(int, input.split()[1:]))
        elif input.startswith('cast'):
            return Cast(game, *map(int, input.split()[1:]))
        elif input.startswith('hero'):
            return HeroPower()
        elif input.startswith('end'):
            return End()
        elif input.startswith('concede'):
            return Concede()
        else:
            print('invalid input ', input)
            return Action()

    def hero_power_params(self, game):
        if isinstance(game.player.hero, SimpleHero):
            return None
        elif isinstance(game.player.hero, TargetCharacterHero):
            return {'target_id': game.aux_vals.popleft()}
        else:
            return None

    def spell_params(self, game, spell):
        if isinstance(spell, spells.SimpleSpell):
            return {}
        else:
            return {'target_id': game.aux_vals.popleft()}
