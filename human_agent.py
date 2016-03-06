from actions import parse_action
import events
import spells.spell_effects as spells

class HumanAgent():
    def __init__(self):
        pass
        
    def move(self, game):
        return parse_action(game, raw_input())

    def get_params(self, game, spell):
        if isinstance(spell, spells.SimpleSpell):
            return None
        elif isinstance(spell, spells.TargetAllyMinionSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.player.board[1:]])}
        elif isinstance(spell, spells.TargetCharacterSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.player.board] + 
                                      [minion.minion_id for minion in game.enemy.board])}
        elif isinstance(spell, spells.TargetEnemyMinionSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.enemy.board[1:]])}
        elif isinstance(spell, spells.TargetMinionSpell):
            return {'target_id': events.target(game,
                        valid_targets=[minion.minion_id for minion in game.player.board[1:]] + 
                                      [minion.minion_id for minion in game.enemy.board[1:]])}
        else:
            return None
