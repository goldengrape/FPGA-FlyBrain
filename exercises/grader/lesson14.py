"""Checks for Lesson 14: board-clock divider planning."""
from ._core import evaluate_group, report

def evaluate(clock_divider_plan, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Cycles per tick", "检查 clock 与 tick 的整数比。"),
        ("Counter width", "检查表示 0..N-1 所需的最小 bit width。"),
        ("Minimum width", "检查 cycles_per_tick=1 时仍至少返回 1 bit。"),
    ) if zh else (
        ("Cycles per tick", "Check the integer clock/tick ratio."),
        ("Counter width", "Check the minimum bit width required for 0..N-1."),
        ("Minimum width", "Check that cycles_per_tick=1 still returns at least one bit."),
    )

    def cycles():
        value, _ = clock_divider_plan(12, 3)
        return value == 4

    def width():
        cycles_per_tick, bits = clock_divider_plan(8, 1)
        return cycles_per_tick == 8 and bits == 3

    def minimum():
        cycles_per_tick, bits = clock_divider_plan(8, 8)
        return cycles_per_tick == 1 and bits == 1

    return [
        evaluate_group(labels[0][0], cycles, labels[0][1]),
        evaluate_group(labels[1][0], width, labels[1][1]),
        evaluate_group(labels[2][0], minimum, labels[2][1]),
    ]

def check(clock_divider_plan, language: str = "zh") -> bool:
    title = "第 14 课检查" if language.lower().startswith("zh") else "Lesson 14 checks"
    return report(title, evaluate(clock_divider_plan, language))
