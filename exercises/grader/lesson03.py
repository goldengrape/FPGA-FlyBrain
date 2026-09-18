"""Checks for Lesson 03: frozen neuron semantics."""

from math import isclose

from ._core import evaluate_group, report


def evaluate(lif_step_v0, threshold_boundary_case, update_order_counterexample, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("v0 update contract", "检查 candidate、threshold 和 immediate reset 的固定语义。"),
        ("Threshold distinguishing probe", "构造一个能够区分 >= 与 > 的边界例子。"),
        ("Update-order counterexample", "构造一个能够区分两种更新顺序的反例。"),
    ) if zh else (
        ("v0 update contract", "Check the frozen candidate, threshold, and immediate-reset semantics."),
        ("Threshold distinguishing probe", "Construct a boundary case that distinguishes >= from >."),
        ("Update-order counterexample", "Construct a case that distinguishes the two update orders."),
    )

    def contract_ok():
        n, s, c = lif_step_v0(0.8, 0.4, 0.9, 2.0, 0.0)
        if not (isclose(c, 1.12) and s is False and isclose(n, 1.12)):
            return False
        n, s, c = lif_step_v0(0.75, 0.25, 1.0, 1.0, 0.0)
        return isclose(c, 1.0) and s is True and isclose(n, 0.0)

    def boundary_ok():
        v, current, alpha, threshold = threshold_boundary_case()
        candidate = alpha * v + current
        return isclose(candidate, threshold) and candidate >= threshold and not (candidate > threshold)

    def order_ok():
        v, current, alpha = update_order_counterexample()
        if not (0.0 < alpha < 1.0 and current != 0.0):
            return False
        return not isclose(alpha * v + current, alpha * (v + current))

    return [
        evaluate_group(labels[0][0], contract_ok, labels[0][1]),
        evaluate_group(labels[1][0], boundary_ok, labels[1][1]),
        evaluate_group(labels[2][0], order_ok, labels[2][1]),
    ]


def check(lif_step_v0, threshold_boundary_case, update_order_counterexample, language: str = "zh") -> bool:
    title = "Lesson 03 checks" if not language.lower().startswith("zh") else "第 03 课检查"
    return report(title, evaluate(lif_step_v0, threshold_boundary_case, update_order_counterexample, language))
