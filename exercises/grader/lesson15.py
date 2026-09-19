"""Checks for Lesson 15: host/PL command ordering."""

from ._core import evaluate_group, report


def evaluate(run_host_pl_commands, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Persistent PL state", "检查 write/add 是否按顺序作用于同一 register。"),
            ("Readback ordering", "检查 read 是否按时间顺序观察 state。"),
            ("Initial state", "检查 initial_register。"),
        )
        if zh
        else (
            ("Persistent PL state", "Check ordered operations on one persistent register."),
            ("Readback ordering", "Check readback time order."),
            ("Initial state", "Check initial_register."),
        )
    )

    def persistent_state():
        return run_host_pl_commands(
            [("write", 7), ("add", 5), ("read", None), ("add", -2)],
            0,
        ) == ([12], 10)

    def readback_ordering():
        return run_host_pl_commands(
            [
                ("write", 4),
                ("read", None),
                ("add", 3),
                ("read", None),
                ("read", None),
            ],
            0,
        ) == ([4, 7, 7], 7)

    def initial_state():
        return run_host_pl_commands(
            [("read", None), ("add", 2), ("read", None)],
            5,
        ) == ([5, 7], 7)

    return [
        evaluate_group(labels[0][0], persistent_state, labels[0][1]),
        evaluate_group(labels[1][0], readback_ordering, labels[1][1]),
        evaluate_group(labels[2][0], initial_state, labels[2][1]),
    ]


def check(run_host_pl_commands, language: str = "zh") -> bool:
    title = "第 15 课检查" if language.lower().startswith("zh") else "Lesson 15 checks"
    return report(title, evaluate(run_host_pl_commands, language))
