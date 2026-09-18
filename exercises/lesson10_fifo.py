"""Lesson 10 starter: bounded FIFO behavior and backpressure."""

def fifo_push(queue: list[int], event: int, capacity: int) -> tuple[list[int], bool]:
    """Return (new_queue, accepted). Do not overwrite old events when full.

    accepted=False means this push did not occur; the caller retains the event
    and may retry the same event after space becomes available.
    """
    result = list(queue)
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: bounded push')
    # YOUR CODE ENDS HERE
    return result, accepted

def fifo_pop(queue: list[int]) -> tuple[list[int], int | None]:
    """Return (new_queue, popped_event); return None when empty."""
    result = list(queue)
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: FIFO pop')
    # YOUR CODE ENDS HERE
    return result, popped
