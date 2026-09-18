"""Lesson 5 starter: Boolean logic and threshold comparison."""

def gate_not(a: bool) -> bool:
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: NOT')
    # YOUR CODE ENDS HERE

def gate_and(a: bool,b: bool) -> bool:
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: AND')
    # YOUR CODE ENDS HERE

def gate_or(a: bool,b: bool) -> bool:
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: OR')
    # YOUR CODE ENDS HERE

def threshold_reached(value:int,threshold:int) -> bool:
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: use >=')
    # YOUR CODE ENDS HERE

def spike_enabled(enable:bool,value:int,threshold:int) -> bool:
    return gate_and(enable,threshold_reached(value,threshold))
