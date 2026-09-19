"""Checks for Lesson 19: connectome degree summary."""

from ._core import evaluate_group, report


def evaluate(degree_summary, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Directed in-degree", "检查 target 方向的 incoming edge 统计。"),
            ("Directed out-degree", "检查 source 方向的 outgoing edge 统计。"),
            ("Zero-degree neurons", "检查没有连接的 neuron 仍出现在结果中。"),
        )
        if zh
        else (
            ("Directed in-degree", "Check incoming-edge counts by target."),
            ("Directed out-degree", "Check outgoing-edge counts by source."),
            ("Zero-degree neurons", "Check disconnected neurons still appear."),
        )
    )

    def directed_in():
        incoming, _ = degree_summary(
            [10, 20, 30],
            [(10, 20), (10, 30), (20, 30)],
        )
        return incoming == {10: 0, 20: 1, 30: 2}

    def directed_out():
        _, outgoing = degree_summary(
            [10, 20, 30],
            [(10, 20), (10, 30), (20, 30)],
        )
        return outgoing == {10: 2, 20: 1, 30: 0}

    def zero_degree():
        incoming, outgoing = degree_summary([1, 2, 3], [(1, 2)])
        return incoming == {1: 0, 2: 1, 3: 0} and outgoing == {1: 1, 2: 0, 3: 0}

    return [
        evaluate_group(labels[0][0], directed_in, labels[0][1]),
        evaluate_group(labels[1][0], directed_out, labels[1][1]),
        evaluate_group(labels[2][0], zero_degree, labels[2][1]),
    ]


def check(degree_summary, language: str = "zh") -> bool:
    title = "第 19 课检查" if language.lower().startswith("zh") else "Lesson 19 checks"
    return report(title, evaluate(degree_summary, language))
