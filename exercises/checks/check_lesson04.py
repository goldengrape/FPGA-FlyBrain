from exercises.lesson04_state_clock import (
    clock_edge,
    combinational_step,
    run_clocked_accumulator,
)


def test_combinational_step_does_not_hide_candidate_state():
    candidate, spike, value_to_store = combinational_step(
        state=3, input_value=1, threshold=4, reset=0
    )
    assert candidate == 4
    assert spike is True
    assert value_to_store == 0


def test_clock_edge_stores_the_precomputed_value():
    assert clock_edge(state=3, value_to_store=7) == 7


def test_clocked_accumulator_sequence():
    states, spikes = run_clocked_accumulator(
        [1, 1, 1, 1, 2, 2], threshold=4, reset=0, initial_state=0
    )
    assert states == [0, 1, 2, 3, 0, 2, 0]
    assert spikes == [False, False, False, True, False, True]


def test_initial_state_is_visible_before_first_clock_edge():
    states, spikes = run_clocked_accumulator(
        [2], threshold=10, reset=0, initial_state=5
    )
    assert states == [5, 7]
    assert spikes == [False]
