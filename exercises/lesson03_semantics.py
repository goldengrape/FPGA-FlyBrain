"""Lesson 3 starter code: freeze semantics and design distinguishing probes."""


def lif_step_v0(
    v: float,
    current: float,
    alpha: float = 0.9,
    threshold: float = 1.0,
    reset: float = 0.0,
) -> tuple[float, bool, float]:
    """Implement the frozen v0 semantics.

    v0 contract:
    - update order: candidate_v = alpha * v + current
    - threshold comparison: candidate_v >= threshold
    - reset: immediate, to reset

    Return (next_v, spike, candidate_v).
    """
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: implement the frozen v0 semantics")
    # YOUR CODE ENDS HERE

    return next_v, spike, candidate_v


def threshold_boundary_case() -> tuple[float, float, float, float]:
    """Return (v, current, alpha, threshold) that distinguishes >= from >.

    The case should make alpha * v + current exactly equal threshold.
    """
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: construct a threshold boundary case")
    # YOUR CODE ENDS HERE


def update_order_counterexample() -> tuple[float, float, float]:
    """Return (v, current, alpha) that distinguishes two update orders.

    It must make these expressions different:
        alpha * v + current
        alpha * (v + current)
    Use a non-trivial 0 < alpha < 1 and non-zero current.
    """
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: construct an update-order counterexample")
    # YOUR CODE ENDS HERE
