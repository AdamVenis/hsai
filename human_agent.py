from actions import parse_move

class HumanAgent():
    def __init__(self):
        pass
        
    def move(self, game):
        return parse_move(game, raw_input())
    