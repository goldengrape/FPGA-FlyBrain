"""Checks for Lesson 21: stage utilization and bottleneck."""

from ._core import evaluate_group, report


def evaluate(bottleneck, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Utilization ratios", "检查 demand/capacity 的逐 stage 比例。"),
            ("Highest utilization", "检查 bottleneck 由 utilization 而不是 raw demand 决定。"),
            ("Under-capacity case", "检查所有 stage 小于 1.0 时仍能找出相对 bottleneck。"),
        )
        if zh
        else (
            ("Utilization ratios", "Check per-stage demand/capacity ratios."),
            ("Highest utilization", "Check bottleneck uses utilization, not raw demand."),
            ("Under-capacity case", "Check a relative bottleneck when all stages are below 1.0."),
        )
    )

    def ratios():
        util, _ = bottleneck(
            {"a": 4.0, "b": 6.0},
            {"a": 8.0, "b": 12.0},
        )
        return abs(util["a"] - 0.5) < 1e-12 and abs(util["b"] - 0.5) < 1e-12

    def highest_utilization():
        util, stage = bottleneck(
            {"raw-big": 8.0, "tight": 6.0},
            {"raw-big": 10.0, "tight": 6.0},
        )
        return stage == "tight" and abs(util["tight"] - 1.0) < 1e-12

    def under_capacity():
        util, stage = bottleneck(
            {"fifo": 2.0, "memory": 3.0, "update": 3.0},
            {"fifo": 10.0, "memory": 4.0, "update": 8.0},
        )
        return stage == "memory" and abs(util["memory"] - 0.75) < 1e-12

    return [
        evaluate_group(labels[0][0], ratios, labels[0][1]),
        evaluate_group(labels[1][0], highest_utilization, labels[1][1]),
        evaluate_group(labels[2][0], under_capacity, labels[2][1]),
    ]


def check(bottleneck, language: str = "zh") -> bool:
    title = "第 21 课检查" if language.lower().startswith("zh") else "Lesson 21 checks"
    return report(title, evaluate(bottleneck, language))
