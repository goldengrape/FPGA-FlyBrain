"""Lesson 1 starter code: Leaky Integrate-and-Fire (LIF)."""


def leak_step(v: float, input_value: float, alpha: float, v_rest: float) -> float:
    """Return the membrane voltage after one leak + integrate step.

    Keep the function signature unchanged. Fill only the TODO region.
    """
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: implement one leak + integrate step")
    # YOUR CODE ENDS HERE


def lif_step(
    v: float,
    input_value: float,
    alpha: float,
    v_rest: float,
    threshold: float,
    reset: float,
) -> tuple[float, bool]:
    """Return (next_v, spike) for one LIF time step.

    The Lesson 1 contract is:
    1. leak old state toward v_rest, then add current input;
    2. spike when candidate_v >= threshold;
    3. reset immediately after a spike.
    """
    candidate_v = leak_step(v, input_value, alpha, v_rest)

    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: implement threshold and reset")
    # YOUR CODE ENDS HERE

    return next_v, spike
