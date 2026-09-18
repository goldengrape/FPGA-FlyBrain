"""Checks for Lesson 09: addressed state and time multiplexing."""

from ._core import evaluate_group, report


def evaluate(update_addressed_state, round_robin_pass, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Addressed state update", "检查一次操作是否只修改被 address 选中的 state。"),
        ("Round-robin service", "检查一轮服务的最终 state 和处理顺序。"),
        ("Interface contract", "检查 states 与 inputs 长度不一致时是否拒绝执行。"),
    ) if zh else (
        ("Addressed state update", "Check that one operation changes only the addressed state."),
        ("Round-robin service", "Check final state and service order for one pass."),
        ("Interface contract", "Check that mismatched state/input lengths are rejected."),
    )

    def addressed_ok():
        return (
            update_addressed_state([3, 4, 5], 1, 7) == [3, 11, 5]
            and update_addressed_state([10, 20], 0, -3) == [7, 20]
        )

    def rr_ok():
        states, trace = round_robin_pass([0, 10, -3, 7], [2, -1, 4, 0])
        return states == [2, 9, 1, 7] and trace == [(0, 0, 2), (1, 10, 9), (2, -3, 1), (3, 7, 7)]

    def contract_ok():
        try:
            round_robin_pass([0, 1], [1])
        except ValueError:
            return True
        return False

    return [
        evaluate_group(labels[0][0], addressed_ok, labels[0][1]),
        evaluate_group(labels[1][0], rr_ok, labels[1][1]),
        evaluate_group(labels[2][0], contract_ok, labels[2][1]),
    ]


def check(update_addressed_state, round_robin_pass, language: str = "zh") -> bool:
    title = "Lesson 09 checks" if not language.lower().startswith("zh") else "第 09 课检查"
    return report(title, evaluate(update_addressed_state, round_robin_pass, language))
