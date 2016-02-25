# NB: keep spells in alphabetical order

spell_effects = {} # hack to avoid circular imports
import actions
# can't import * from here because locals() is used below, and it needs to
# be kept clean
import card_data
import events
import utils

from spell_utils import *
from mage_spells import *
from warrior_spells import *

class TheCoin(SimpleSpell):
    id = 'GAME_005'
    def execute(self, params):
        if self.game.player.current_crystals < 10:
            self.game.player.current_crystals += 1

# these are spells that have non-alphanumeric characters in their name
exceptions = ['actions', 'card_data', 'events', 'utils', 'exceptions', 'hunters_mark']
spell_effects = {utils.func_to_name(key): val
                 for key, val in locals().items()
                 if type(val) == type(lambda x:x) and
                 key[0] != '_' and key not in exceptions}
# spell_effects["Hunter's Mark"] = hunters_mark
# ^ this is an example of how exceptions work
