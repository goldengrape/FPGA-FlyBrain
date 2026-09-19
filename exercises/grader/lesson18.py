"""Checks for Lesson 18: VALID/READY accepted beats."""

from ._core import evaluate_group, report


def evaluate(accepted_beats, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("VALID && READY", "检查是否只有双方同时为真才接受。"),
            ("Backpressure stall", "检查 stall 不会提前消费 payload。"),
            ("READY without VALID", "检查 READY 单独为真不会产生 transfer。"),
        )
        if zh
        else (
            ("VALID && READY", "Check acceptance only when both are true."),
            ("Backpressure stall", "Check a stall does not consume early."),
            ("READY without VALID", "Check READY alone does not transfer."),
        )
    )

    def valid_and_ready():
        return accepted_beats(
            [True, True, True, False, True],
            [True, False, True, True, True],
            [10, 11, 11, 99, 12],
        ) == ([10, 11, 12], [0, 2, 4])

    def backpressure_stall():
        return accepted_beats(
            [True, True],
            [False, True],
            [7, 7],
        ) == ([7], [1])

    def ready_without_valid():
        return accepted_beats(
            [False, True, False],
            [True, True, True],
            [1, 2, 3],
        ) == ([2], [1])

    return [
        evaluate_group(labels[0][0], valid_and_ready, labels[0][1]),
        evaluate_group(labels[1][0], backpressure_stall, labels[1][1]),
        evaluate_group(labels[2][0], ready_without_valid, labels[2][1]),
    ]


def check(accepted_beats, language: str = "zh") -> bool:
    title = "第 18 课检查" if language.lower().startswith("zh") else "Lesson 18 checks"
    return report(title, evaluate(accepted_beats, language))
