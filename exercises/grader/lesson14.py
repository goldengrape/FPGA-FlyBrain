"""Checks for Lesson 14: board-clock divider planning."""
from ._core import evaluate_group, report

def evaluate(clock_divider_plan, language: str = "zh"):
    zh=language.lower().startswith("zh")
    labels=(("Cycles per tick","检查 clock 与 tick 的整数比。"),("Counter width","检查 0..N-1 的最小 bit width。"),("Minimum width","检查最少返回 1 bit。")) if zh else (("Cycles per tick","Check the clock/tick ratio."),("Counter width","Check minimum width for 0..N-1."),("Minimum width","Check a minimum of one bit."))
    return [
        evaluate_group(labels[0][0],lambda: clock_divider_plan(12,3)==(4,2),labels[0][1]),
        evaluate_group(labels[1][0],lambda: clock_divider_plan(100_000_000,2)==(50_000_000,26),labels[1][1]),
        evaluate_group(labels[2][0],lambda: clock_divider_plan(8,8)==(1,1),labels[2][1]),
    ]

def check(clock_divider_plan, language: str = "zh") -> bool:
    return report("第 14 课检查" if language.lower().startswith("zh") else "Lesson 14 checks", evaluate(clock_divider_plan, language))
