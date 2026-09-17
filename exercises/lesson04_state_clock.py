"""Lesson 4 starter code: combinational next-state logic and clocked state."""


def combinational_step(
    state: int,
    input_value: int,
    threshold: int,
    reset: int = 0,
) -> tuple[int, bool, int]:
    """Compute, but do not clock in, the next-state decision.

    Return (candidate_state, spike, value_to_store).
    """
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: compute combinational next-state logic")
    # YOUR CODE ENDS HERE

    return candidate_state, spike, value_to_store


def clock_edge(state: int, value_to_store: int) -> int:
    """Model the register update that occurs on a clock edge."""
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: update the register at the clock edge")
    # YOUR CODE ENDS HERE


def run_clocked_accumulator(
    inputs: list[int],
    threshold: int,
    reset: int = 0,
    initial_state: int = 0,
) -> tuple[list[int], list[bool]]:
    """Run one clock edge per input.

    states includes the initial register value, so len(states) == len(inputs) + 1.
    spikes contains one Boolean per input cycle.
    """
    state = initial_state
    states = [state]
    spikes = []

    for input_value in inputs:
        candidate_state, spike, value_to_store = combinational_step(
            state, input_value, threshold, reset
        )
        del candidate_state  # observable candidate; register stores value_to_store

        # YOUR CODE STARTS HERE
        raise NotImplementedError("TODO: apply the clock edge and record the cycle")
        # YOUR CODE ENDS HERE

    return states, spikes
