"""Lesson 12 starter: process one source spike through sparse synapses."""

def process_one_spike(
    source_id: int,
    source_index: list[tuple[int,int]],
    records: list[tuple[int,int]],
    target_accum: list[int],
) -> tuple[list[int], list[tuple[int,int]]]:
    """Return (updated_accum, weighted_events).

    Each weighted event is (target, weight). Process only this source range.
    """
    updated = list(target_accum)
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: lookup range and apply weighted events')
    # YOUR CODE ENDS HERE
    return updated, weighted_events
