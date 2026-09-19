"""Checks for Lesson 16: simplified compute/memory model."""

from ._core import evaluate_group, report


def evaluate(transfer_profile, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Memory-bound case", "检查 data volume、bandwidth 与 startup latency。"),
            ("Compute-bound case", "检查较慢算术能成为 bottleneck。"),
            ("Balanced case", "检查时间相等时返回 balanced。"),
        )
        if zh
        else (
            ("Memory-bound case", "Check data volume, bandwidth, and startup latency."),
            ("Compute-bound case", "Check slower arithmetic can dominate."),
            ("Balanced case", "Check equal times return balanced."),
        )
    )

    def memory_bound():
        compute, transfer, bottleneck = transfer_profile(100, 8, 2.0, 2.0, 20.0)
        return (
            abs(compute - 200) < 1e-9
            and abs(transfer - 420) < 1e-9
            and bottleneck == "memory"
        )

    def compute_bound():
        compute, transfer, bottleneck = transfer_profile(10, 4, 10.0, 4.0, 0.0)
        return (
            abs(compute - 100) < 1e-9
            and abs(transfer - 10) < 1e-9
            and bottleneck == "compute"
        )

    def balanced():
        compute, transfer, bottleneck = transfer_profile(10, 4, 2.0, 2.0, 0.0)
        return (
            abs(compute - 20) < 1e-9
            and abs(transfer - 20) < 1e-9
            and bottleneck == "balanced"
        )

    return [
        evaluate_group(labels[0][0], memory_bound, labels[0][1]),
        evaluate_group(labels[1][0], compute_bound, labels[1][1]),
        evaluate_group(labels[2][0], balanced, labels[2][1]),
    ]


def check(transfer_profile, language: str = "zh") -> bool:
    title = "第 16 课检查" if language.lower().startswith("zh") else "Lesson 16 checks"
    return report(title, evaluate(transfer_profile, language))
