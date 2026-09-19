"""Checks for Lesson 22: deterministic closed-loop trace."""

from ._core import evaluate_group, report


def evaluate(closed_loop_trace, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Move toward target", "检查每一步都根据当前 position 朝 target 移动。"),
            ("Stop at target", "检查到达 target 后不会越过。"),
            ("Trace length", "检查包含 initial state 且长度为 steps + 1。"),
        )
        if zh
        else (
            ("Move toward target", "Check each step moves from the current position toward target."),
            ("Stop at target", "Check the trace does not overshoot after reaching target."),
            ("Trace length", "Check the initial state is included and length is steps + 1."),
        )
    )

    def move_toward():
        return closed_loop_trace(0, 3, 2) == [0, 1, 2]

    def stop_at_target():
        return closed_loop_trace(1, 2, 4) == [1, 2, 2, 2, 2]

    def trace_length():
        return closed_loop_trace(5, 1, 0) == [5] and len(closed_loop_trace(5, 1, 3)) == 4

    return [
        evaluate_group(labels[0][0], move_toward, labels[0][1]),
        evaluate_group(labels[1][0], stop_at_target, labels[1][1]),
        evaluate_group(labels[2][0], trace_length, labels[2][1]),
    ]


def check(closed_loop_trace, language: str = "zh") -> bool:
    title = "第 22 课检查" if language.lower().startswith("zh") else "Lesson 22 checks"
    return report(title, evaluate(closed_loop_trace, language))
