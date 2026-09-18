from exercises.lesson10_fifo import fifo_push, fifo_pop

def test_fifo_ordering():
    q=[]
    for e in [2,5,7]:
        q, ok = fifo_push(q,e,3)
        assert ok is True
    out=[]
    for _ in range(3):
        q,e=fifo_pop(q); out.append(e)
    assert out == [2,5,7]
    assert q == []

def test_full_queue_applies_backpressure_without_corruption():
    q,ok=fifo_push([2,5],7,2)
    assert ok is False
    assert q == [2,5]

def test_empty_pop():
    q,e=fifo_pop([])
    assert q == [] and e is None

def test_space_reopens_after_pop():
    q,e=fifo_pop([2,5])
    assert e == 2
    q,ok=fifo_push(q,7,2)
    assert ok is True and q == [5,7]
