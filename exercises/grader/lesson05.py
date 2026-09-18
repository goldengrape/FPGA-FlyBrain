"""Checks for Lesson 05: Boolean logic and threshold comparison."""

from itertools import product

from ._core import evaluate_group, report


def evaluate(gate_not, gate_and, gate_or, threshold_reached, spike_enabled, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Boolean gates", "检查 NOT、AND、OR 的完整真值表。"),
        ("Threshold behavior", "检查低于、达到和超过 threshold 时的行为。"),
        ("Enable behavior", "检查 enable 是否真正控制 spike 是否生效。"),
    ) if zh else (
        ("Boolean gates", "Check complete truth tables for NOT, AND, and OR."),
        ("Threshold behavior", "Check behavior below, at, and above threshold."),
        ("Enable behavior", "Check that enable actually gates the spike decision."),
    )

    def gates_ok():
        if gate_not(False) is not True or gate_not(True) is not False:
            return False
        for a, b in product([False, True], repeat=2):
            if gate_and(a, b) is not (a and b):
                return False
            if gate_or(a, b) is not (a or b):
                return False
        return True

    def threshold_ok():
        return (
            threshold_reached(3, 4) is False
            and threshold_reached(4, 4) is True
            and threshold_reached(5, 4) is True
        )

    def enable_ok():
        return (
            spike_enabled(False, 10, 4) is False
            and spike_enabled(True, 3, 4) is False
            and spike_enabled(True, 4, 4) is True
        )

    return [
        evaluate_group(labels[0][0], gates_ok, labels[0][1]),
        evaluate_group(labels[1][0], threshold_ok, labels[1][1]),
        evaluate_group(labels[2][0], enable_ok, labels[2][1]),
    ]


def check(gate_not, gate_and, gate_or, threshold_reached, spike_enabled, language: str = "zh") -> bool:
    title = "Lesson 05 checks" if not language.lower().startswith("zh") else "第 05 课检查"
    return report(title, evaluate(gate_not, gate_and, gate_or, threshold_reached, spike_enabled, language))
