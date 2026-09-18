from exercises.lesson12_event_journey import process_one_spike

INDEX=[(0,2),(2,1),(3,1),(4,0)]
RECORDS=[(1,2),(2,1),(3,2),(3,1)]

def test_source_zero_emits_two_weighted_events():
    accum,events=process_one_spike(0,INDEX,RECORDS,[0,0,0,0])
    assert events == [(1,2),(2,1)]
    assert accum == [0,2,1,0]

def test_source_one_updates_only_target_three():
    accum,events=process_one_spike(1,INDEX,RECORDS,[0,0,0,0])
    assert events == [(3,2)]
    assert accum == [0,0,0,2]

def test_source_three_has_no_outgoing_events():
    initial=[4,3,2,1]
    accum,events=process_one_spike(3,INDEX,RECORDS,initial)
    assert events == []
    assert accum == initial
    assert accum is not initial
