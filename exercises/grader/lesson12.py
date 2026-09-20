"""Checks for Lesson 12: one spike through sparse synapses."""

from ._core import evaluate_group, report


_INDEX = [(0, 2), (2, 1), (3, 1), (4, 0)]
_RECORDS = [(1, 2), (2, 1), (3, 2), (3, 1)]


def evaluate(process_one_spike, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Weighted event routing", "检查 source range 是否产生正确的 weighted events 并更新 targets。"),
        ("Source isolation", "检查一次 spike 是否只处理当前 source 的突触范围。"),
        ("Zero fanout and copy semantics", "检查无 outgoing synapse 时 accumulator 内容不变，并返回新的列表。"),
        ("Accumulation and input preservation", "检查从旧值累加、重复 target、负权重，以及输入 accumulator 保持不变。"),
    ) if zh else (
        ("Weighted event routing", "Check that the source range emits weighted events and updates targets."),
        ("Source isolation", "Check that one spike processes only the current source range."),
        ("Zero fanout and copy semantics", "Check unchanged values but a new list for a zero-fanout source."),
        ("Accumulation and input preservation", "Check prior values, repeated targets, negative weights, and unchanged input accumulator."),
    )

    def routing_ok():
        accum, events = process_one_spike(0, _INDEX, _RECORDS, [0, 0, 0, 0])
        return events == [(1, 2), (2, 1)] and accum == [0, 2, 1, 0]

    def isolation_ok():
        accum, events = process_one_spike(1, _INDEX, _RECORDS, [0, 0, 0, 0])
        return events == [(3, 2)] and accum == [0, 0, 0, 2]

    def zero_ok():
        initial = [4, 3, 2, 1]
        before = list(initial)
        accum, events = process_one_spike(3, _INDEX, _RECORDS, initial)
        return events == [] and accum == before and initial == before and accum is not initial

    def accumulation_ok():
        initial = [5, 7, -3, 9]
        before = list(initial)
        index = [(0, 1), (1, 3), (4, 0), (4, 0)]
        records = [(3, 8), (0, 2), (2, -4), (0, 3)]
        accum, events = process_one_spike(1, index, records, initial)
        return (
            accum == [10, 7, -7, 9]
            and events == [(0, 2), (2, -4), (0, 3)]
            and initial == before
            and accum is not initial
        )

    return [
        evaluate_group(labels[0][0], routing_ok, labels[0][1]),
        evaluate_group(labels[1][0], isolation_ok, labels[1][1]),
        evaluate_group(labels[2][0], zero_ok, labels[2][1]),
        evaluate_group(labels[3][0], accumulation_ok, labels[3][1]),
    ]


def check(process_one_spike, language: str = "zh") -> bool:
    title = "Lesson 12 checks" if not language.lower().startswith("zh") else "第 12 课检查"
    return report(title, evaluate(process_one_spike, language))
