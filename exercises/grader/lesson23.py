"""Checks for Lesson 23: benchmark metrics."""

from ._core import evaluate_group, report


def evaluate(benchmark_metrics, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Throughput", "检查 events / seconds。"),
            ("Energy per event", "检查 watts × seconds / events。"),
            ("Duration sensitivity", "检查 energy/event 会随 measurement duration 改变。"),
        )
        if zh
        else (
            ("Throughput", "Check events / seconds."),
            ("Energy per event", "Check watts × seconds / events."),
            ("Duration sensitivity", "Check energy/event changes with measurement duration."),
        )
    )

    def throughput():
        value, _ = benchmark_metrics(1000, 0.5, 20.0)
        return abs(value - 2000.0) < 1e-12

    def energy_per_event():
        _, value = benchmark_metrics(1000, 0.5, 20.0)
        return abs(value - 0.01) < 1e-12

    def duration_sensitivity():
        _, first = benchmark_metrics(1000, 0.5, 20.0)
        _, second = benchmark_metrics(1000, 1.0, 20.0)
        return abs(second - 2 * first) < 1e-12

    return [
        evaluate_group(labels[0][0], throughput, labels[0][1]),
        evaluate_group(labels[1][0], energy_per_event, labels[1][1]),
        evaluate_group(labels[2][0], duration_sensitivity, labels[2][1]),
    ]


def check(benchmark_metrics, language: str = "zh") -> bool:
    title = "第 23 课检查" if language.lower().startswith("zh") else "Lesson 23 checks"
    return report(title, evaluate(benchmark_metrics, language))
