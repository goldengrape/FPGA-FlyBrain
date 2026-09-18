from exercises.lesson11_sparse_graph import build_source_index, lookup_source

EDGES=[(0,1,2),(0,3,-1),(2,1,3),(3,2,1)]

def test_exact_source_ranges():
    index,records=build_source_index(4,EDGES)
    assert index == [(0,2),(2,0),(2,1),(3,1)]
    assert records == [(1,2),(3,-1),(1,3),(2,1)]

def test_lookup_each_source():
    index,records=build_source_index(4,EDGES)
    assert lookup_source(0,index,records) == [(1,2),(3,-1)]
    assert lookup_source(1,index,records) == []
    assert lookup_source(2,index,records) == [(1,3)]
    assert lookup_source(3,index,records) == [(2,1)]

def test_input_edge_order_within_source_is_preserved():
    index,records=build_source_index(2,[(0,1,4),(0,0,5)])
    assert lookup_source(0,index,records) == [(1,4),(0,5)]
