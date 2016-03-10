import events
import card_data

class Hero():
    def __init__(self, game):
        self.game = game

    def moves(self):
        raise NotImplementedError

    def power(self):
        raise NotImplementedError

class SimpleHero(Hero):
    pass

class TargetCharacterHero(Hero):
    def moves(self):
        return self.game.ALL_CHARACTERS

class Hunter(SimpleHero):
    def power(self, **params):
        self.game.add_event(events.deal_damage, (self.game.enemy.board[0].minion_id, 2))

class Warrior(SimpleHero):
    def power(self, **params):
        self.game.player.armor += 2

class Shaman(SimpleHero):
    # this might not go through? how to reconcile this?
    def power(self, **params):
        game = self.game
        totems = ['Healing Totem', 'Searing Totem', 'Stoneclaw Totem', 'Wrath of Air Totem']
        for minion in game.player.board:
            if minion.name in totems:
                totems.remove(minion.name)
        if totems: # not all have been removed
            game.add_event(events.spawn, 
                (game.player, card_data.get_card(game.choice(totems, random=True), game.player)))
        else:
            print('all totems have already been summoned!')
        
class Mage(TargetCharacterHero):
    def power(self, **params):
        self.game.add_event(events.deal_damage, (params['target_id'], 1))

class Warlock(SimpleHero):
    def power(self, **params):
        game = self.game
        game.add_event(events.deal_damage, (game.player.board[0].minion_id, 2))
        game.add_event(events.draw, (game.player,))

class Rogue(SimpleHero):
    def power(self, **params):
        self.game.player.weapon = Weapon(1,2)

class Priest(TargetCharacterHero):
    def power(self, **params):
        self.game.add_event(events.heal, (params['target_id'], 2))

class Paladin(SimpleHero):
    def power(self, **params):
        self.game.add_event(events.spawn, (self.game.player, card_data.get_card('Silver Hand Recruit')))

class Druid(SimpleHero):
    def power(self, **params):
        self.game.player.armor += 1
        self.game.player.board[0].attack += 1
        # move the druid effect into this file
        self.game.effect_pool.append(minion_effects.effects['Druid'])
