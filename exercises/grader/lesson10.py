"""Checks for Lesson 10: bounded FIFO and backpressure."""

from ._core import evaluate_group, report


def evaluate(fifo_push, fifo_pop, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("FIFO ordering", "检查事件是否保持 first-in, first-out 顺序。"),
        ("Full / empty behavior", "检查 full 时不覆盖旧事件、empty 时返回空结果。"),
        ("Backpressure retry", "检查被阻塞的事件能否在空间释放后重新尝试。"),
    ) if zh else (
        ("FIFO ordering", "Check first-in, first-out ordering."),
        ("Full / empty behavior", "Check that full never overwrites old events and empty returns no event."),
        ("Backpressure retry", "Check that a blocked event can be retried after space opens."),
    )

    def ordering_ok():
        q = []
        for event in [2, 5, 7]:
            q, accepted = fifo_push(q, event, 3)
            if accepted is not True:
                return False
        out = []
        for _ in range(3):
            q, event = fifo_pop(q)
            out.append(event)
        return out == [2, 5, 7] and q == []

    def boundary_ok():
        q, accepted = fifo_push([2, 5], 7, 2)
        if accepted is not False or q != [2, 5]:
            return False
        q, event = fifo_pop([])
        return q == [] and event is None

    def retry_ok():
        blocked = 7
        q, accepted = fifo_push([2, 5], blocked, 2)
        if accepted is not False or q != [2, 5]:
            return False
        q, popped = fifo_pop(q)
        if popped != 2:
            return False
        q, accepted = fifo_push(q, blocked, 2)
        return accepted is True and q == [5, 7]

    return [
        evaluate_group(labels[0][0], ordering_ok, labels[0][1]),
        evaluate_group(labels[1][0], boundary_ok, labels[1][1]),
        evaluate_group(labels[2][0], retry_ok, labels[2][1]),
    ]


def check(fifo_push, fifo_pop, language: str = "zh") -> bool:
    title = "Lesson 10 checks" if not language.lower().startswith("zh") else "第 10 课检查"
    return report(title, evaluate(fifo_push, fifo_pop, language))
