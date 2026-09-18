"""Checks for Lesson 01: Leaky Integrate-and-Fire."""

from math import isclose

from ._core import evaluate_group, report


def evaluate(leak_step, lif_step, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Leak 与 integration", "检查静息点、向静息电位泄漏以及输入累加。"),
        ("Threshold 与 reset", "检查阈值边界以及 spike 后的 reset。"),
    ) if zh else (
        ("Leak and integration", "Check the rest point, leak toward rest, and input integration."),
        ("Threshold and reset", "Check the threshold boundary and reset after a spike."),
    )

    def leak_ok():
        cases = [
            (-70.0, 0.0, 0.9, -70.0, -70.0),
            (-55.0, 0.0, 0.9, -70.0, -56.5),
            (-80.0, 0.0, 0.5, -70.0, -75.0),
            (-55.0, 6.0, 0.9, -70.0, -50.5),
        ]
        return all(isclose(leak_step(v, i, a, r), expected) for v, i, a, r, expected in cases)

    def threshold_ok():
        next_v, spike = lif_step(-60.0, 11.0, 0.9, -70.0, -50.0, -70.0)
        if spike is not True or not isclose(next_v, -70.0):
            return False
        next_v, spike = lif_step(-70.0, 5.0, 0.9, -70.0, -50.0, -70.0)
        return spike is False and isclose(next_v, -65.0)

    return [
        evaluate_group(labels[0][0], leak_ok, labels[0][1]),
        evaluate_group(labels[1][0], threshold_ok, labels[1][1]),
    ]


def check(leak_step, lif_step, language: str = "zh") -> bool:
    title = "Lesson 01 checks" if not language.lower().startswith("zh") else "第 01 课检查"
    return report(title, evaluate(leak_step, lif_step, language))
