"""Lesson 11 starter: sparse source index plus contiguous synapse records."""

Edge = tuple[int, int, int]  # (source, target, weight)
Record = tuple[int, int]     # (target, weight)

def build_source_index(num_sources: int, edges: list[Edge]) -> tuple[list[tuple[int,int]], list[Record]]:
    """Return (source_index, records), where index entries are (start,count)."""
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: pack edges by source')
    # YOUR CODE ENDS HERE
    return source_index, records

def lookup_source(source_id: int, source_index: list[tuple[int,int]], records: list[Record]) -> list[Record]:
    """Return exactly the contiguous record slice for one source."""
    # YOUR CODE STARTS HERE
    raise NotImplementedError('TODO: slice by start,count')
    # YOUR CODE ENDS HERE
