from itertools import product
from exercises.lesson05_logic import gate_not,gate_and,gate_or,threshold_reached,spike_enabled

def test_not():
    assert gate_not(False) is True; assert gate_not(True) is False
def test_and():
    for a,b in product([False,True],repeat=2): assert gate_and(a,b) is (a and b)
def test_or():
    for a,b in product([False,True],repeat=2): assert gate_or(a,b) is (a or b)
def test_threshold_boundary():
    assert threshold_reached(3,4) is False
    assert threshold_reached(4,4) is True
    assert threshold_reached(5,4) is True
def test_spike_enable():
    assert spike_enabled(False,10,4) is False
    assert spike_enabled(True,3,4) is False
    assert spike_enabled(True,4,4) is True
