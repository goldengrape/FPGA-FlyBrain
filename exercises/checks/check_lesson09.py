from exercises.lesson09_time_multiplexing import update_addressed_state, round_robin_pass

def test_only_selected_address_changes():
    assert update_addressed_state([3,4,5], 1, 7) == [3,11,5]

def test_negative_input_is_supported():
    assert update_addressed_state([10,20], 0, -3) == [7,20]

def test_round_robin_pass_and_trace():
    states, trace = round_robin_pass([0,10,-3,7], [2,-1,4,0])
    assert states == [2,9,1,7]
    assert trace == [(0,0,2),(1,10,9),(2,-3,1),(3,7,7)]

def test_length_mismatch_is_rejected():
    try:
        round_robin_pass([0,1], [1])
    except ValueError:
        pass
    else:
        raise AssertionError('expected ValueError')
