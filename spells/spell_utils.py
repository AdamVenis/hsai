
class Spell():
    def __init__(self, game):
        self.game = game

    def moves(self):
        raise NotImplementedError

    def execute(self, **params):
        raise NotImplementedError

class SimpleSpell(Spell):
    # for when no additional parameters are needed
    pass

class TargetAllyMinionSpell(Spell):
    def moves(self):
        return self.game.ALLY_MINIONS

class TargetCharacterSpell(Spell):
    def moves(self):
        return self.game.ALL_CHARACTERS

class TargetEnemyMinionSpell(Spell):
    def moves(self):
        return self.game.ENEMY_MINIONS

class TargetMinionSpell(Spell):
    def moves(self):
        return self.game.ALL_MINIONS