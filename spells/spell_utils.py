
class Spell():
    def __init__(self, game):
        self.game = game

    def legal_params(self):
        raise NotImplementedError

    def execute(self, **params):
        raise NotImplementedError

class SimpleSpell(Spell):
    # for when no additional parameters are needed
    def legal_params(self):
        return None

class TargetAllyMinionSpell(Spell):
    def legal_params(self):
        return [{'target_id': m.minion_id} for m in self.game.ALLY_MINIONS]

class TargetCharacterSpell(Spell):
    def legal_params(self):
        return [{'target_id': m.minion_id} for m in self.game.ALL_CHARACTERS]

class TargetEnemyMinionSpell(Spell):
    def legal_params(self):
        return [{'target_id': m.minion_id} for m in self.game.ENEMY_MINIONS]

class TargetMinionSpell(Spell):
    def legal_params(self):
        return [{'target_id': m.minion_id} for m in self.game.ALL_MINIONS]

class RandomSpell(Spell):
    pass
