"""Checks for Lesson 17: simple burst grouping."""

from ._core import evaluate_group, report


def evaluate(estimate_burst_cycles, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Sequential grouping", "检查连续地址与 max burst。"),
            ("Gapped addresses", "检查地址不连续时新开 burst。"),
            ("Empty request", "检查空请求。"),
        )
        if zh
        else (
            ("Sequential grouping", "Check consecutive grouping and max burst."),
            ("Gapped addresses", "Check gaps start new bursts."),
            ("Empty request", "Check empty input."),
        )
    )

    def sequential_grouping():
        return estimate_burst_cycles([0, 1, 2, 3, 4], 4, 5, 1) == (2, 15)

    def gapped_addresses():
        return estimate_burst_cycles([0, 10, 20, 30, 40], 4, 5, 1) == (5, 30)

    def empty_request():
        return estimate_burst_cycles([], 4, 5, 1) == (0, 0)

    return [
        evaluate_group(labels[0][0], sequential_grouping, labels[0][1]),
        evaluate_group(labels[1][0], gapped_addresses, labels[1][1]),
        evaluate_group(labels[2][0], empty_request, labels[2][1]),
    ]


def check(estimate_burst_cycles, language: str = "zh") -> bool:
    title = "第 17 课检查" if language.lower().startswith("zh") else "Lesson 17 checks"
    return report(title, evaluate(estimate_burst_cycles, language))
