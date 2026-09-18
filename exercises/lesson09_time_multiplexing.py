"""Lesson 9 starter: addressed state and time-multiplexed service."""

def update_addressed_state(states: list[int], address: int, input_value: int) -> list[int]:
    """Return a new state list with only the selected address updated by addition."""
    result = list(states)
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: update only the selected address')
    # YOUR CODE ENDS HERE
    return result

def round_robin_pass(states: list[int], inputs: list[int]) -> tuple[list[int], list[tuple[int,int,int]]]:
    """Serve addresses 0..N-1 once; return (final_states, trace).

    trace entries are (address, before, after).
    """
    if len(states) != len(inputs):
        raise ValueError('states and inputs must have the same length')
    current = list(states)
    trace: list[tuple[int,int,int]] = []
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: serve every address in order')
    # YOUR CODE ENDS HERE
    return current, trace
