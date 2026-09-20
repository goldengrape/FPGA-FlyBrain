"""Checks for Lesson 06: one clocked RTL state update."""

from ._core import evaluate_group, report


def evaluate(clocked_accumulator_edge, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Normal edge", "检查 rst_n 为真时是否用旧 state 加上当前 input。"),
        ("Synchronous reset", "检查低有效 reset 是否在这个上升沿优先把 state 写成 0。"),
        ("State chaining", "检查连续多个 edge 是否真的使用前一个 edge 保存的 state。"),
    ) if zh else (
        ("Normal edge", "Check that rst_n=True adds the current input to the old state."),
        ("Synchronous reset", "Check that active-low reset takes precedence on the sampled rising edge."),
        ("State chaining", "Check that consecutive edges use the state stored by the previous edge."),
    )

    def normal_edge():
        return (
            clocked_accumulator_edge(12, -5, True) == 7
            and clocked_accumulator_edge(-4, 9, True) == 5
        )

    def reset_edge():
        return (
            clocked_accumulator_edge(27, 6, False) == 0
            and clocked_accumulator_edge(-12, -3, False) == 0
        )

    def chaining():
        state = 0
        for value in (3, -1, 5):
            state = clocked_accumulator_edge(state, value, True)
        return state == 7

    return [
        evaluate_group(labels[0][0], normal_edge, labels[0][1]),
        evaluate_group(labels[1][0], reset_edge, labels[1][1]),
        evaluate_group(labels[2][0], chaining, labels[2][1]),
    ]


def check(clocked_accumulator_edge, language: str = "zh") -> bool:
    title = "第 06 课检查" if language.lower().startswith("zh") else "Lesson 06 checks"
    return report(title, evaluate(clocked_accumulator_edge, language))
