# don't import * here so locals() stays clean
import actions
import card_data
import events
import utils

from spell_utils import *

from itertools import product

class ArcaneMissiles(SimpleSpell):
    def execute(self, **params):
        game = self.game
        for i in range(3 + game.player.spellpower):
            game.add_event(events.deal_damage, 
                (game.choice([m.minion_id for m in game.enemy.board], random=True), 1))

class ProtoArcaneMissiles(RandomSpell):
    def legal_params(self):
        game = self.game
        character_ids = [m.minion_id for m in game.ALL_CHARACTERS]
        return [{'random': x} for x in product(character_ids, 3 + game.player.spellpower)]

    def execute(self, **params):
        game = self.game
        for i in range(3 + game.player.spellpower):
            game.add_event(events.deal_damage, (params['random'][i], 1))

class ArcaneExplosion(SimpleSpell):
    def execute(self, **params):
        game = self.game
        for minion in game.enemy.board[1:]:
            game.add_event(events.deal_damage,
                           (minion.minion_id, 1 + game.player.spellpower))

class ArcaneIntellect(SimpleSpell):
    def execute(self, **params):
        game = self.game
        for i in range(2):
            game.add_event(events.draw, (game.player,))

class ConeOfCold(TargetMinionSpell):
    def execute(self, **params):
        minion = self.game.minion_pool[params['target_id']]
        player = minion.owner
        index = player.board.index(minion)
        for i in range(max(1, index - 1), min(index + 2, len(player.board))):
            player.board[i].mechanics.add('Frozen')
            game.add_event(events.deal_damage, (player.board[i].minion_id, 1 + player.spellpower))

class Fireball(TargetCharacterSpell):
    def execute(self, **params):
        game = self.game
        game.add_event(events.deal_damage, (params['target_id'], 6 + game.player.spellpower))

class Polymorph(TargetMinionSpell):
    id = 'CS2_022'
    def execute(self, **params):
        game = self.game
        events.silence(game, params['target_id'])
        minion = game.minion_pool[params['target_id']]
        chicken = utils.Minion(game, card_data.get_card('Sheep', game.player))
        minion.transform_into(chicken)