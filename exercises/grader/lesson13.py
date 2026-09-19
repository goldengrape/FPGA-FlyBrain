"""Checks for Lesson 13: simplified timing summary."""
from ._core import evaluate_group, report

def evaluate(timing_summary, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Critical path", "检查是否取最长路径。"),
        ("Slack boundary", "检查 slack 的符号与 slack=0 边界。"),
        ("Timing failure", "检查更短周期是否会产生 timing failure。"),
    ) if zh else (
        ("Critical path", "Check that the longest path is used."),
        ("Slack boundary", "Check slack sign and the zero-slack boundary."),
        ("Timing failure", "Check that a shorter period can fail timing."),
    )
    def a():
        c,s,m=timing_summary([2.0,4.5,3.2],5.0)
        return abs(c-4.5)<1e-9 and abs(s-0.5)<1e-9 and m is True
    def b():
        c,s,m=timing_summary([1.0,5.0,4.0],5.0)
        return abs(c-5.0)<1e-9 and abs(s)<1e-9 and m is True
    def c():
        p,s,m=timing_summary([5.25,2.0],5.0)
        return abs(p-5.25)<1e-9 and abs(s+0.25)<1e-9 and m is False
    return [evaluate_group(labels[0][0],a,labels[0][1]),evaluate_group(labels[1][0],b,labels[1][1]),evaluate_group(labels[2][0],c,labels[2][1])]

def check(timing_summary, language: str = "zh") -> bool:
    return report("第 13 课检查" if language.lower().startswith("zh") else "Lesson 13 checks", evaluate(timing_summary, language))
