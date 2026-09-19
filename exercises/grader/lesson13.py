"""Checks for Lesson 13: simplified timing summary."""
from ._core import evaluate_group, report

def evaluate(timing_summary, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Critical path", "检查是否取最长路径。"),
        ("Slack boundary", "检查 slack=0 时仍然满足本课 timing 规则。"),
        ("Timing failure", "检查负 slack 是否会产生 timing failure。"),
    ) if zh else (
        ("Critical path", "Check that the longest path is used."),
        ("Slack boundary", "Check that zero slack still meets this lesson's timing rule."),
        ("Timing failure", "Check that negative slack produces timing failure."),
    )

    def critical_path():
        c, _, _ = timing_summary([2.0, 4.5, 3.2], 5.0)
        return abs(c - 4.5) < 1e-9

    def zero_slack():
        _, s, meets = timing_summary([1.0, 5.0, 4.0], 5.0)
        return abs(s) < 1e-9 and meets is True

    def negative_slack():
        _, s, meets = timing_summary([5.25, 2.0], 5.0)
        return abs(s + 0.25) < 1e-9 and meets is False

    return [
        evaluate_group(labels[0][0], critical_path, labels[0][1]),
        evaluate_group(labels[1][0], zero_slack, labels[1][1]),
        evaluate_group(labels[2][0], negative_slack, labels[2][1]),
    ]

def check(timing_summary, language: str = "zh") -> bool:
    title = "第 13 课检查" if language.lower().startswith("zh") else "Lesson 13 checks"
    return report(title, evaluate(timing_summary, language))
