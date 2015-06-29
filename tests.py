from Hearthstone import *

def test_hearthstone():
    g = load('replays/2015-01-21-09-14-36.hsrep')
    assert g.effect_pool == []
    assert g.minion_counter == 1009
    assert g.turn == 9
    assert g.aux_vals == deque()
    assert g.action_queue == deque()
    assert g.minion_pool.keys() == [1000, 1001, 1005, 1006, 1007, 1008]
