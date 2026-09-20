"""Checks for Lesson 08: sampled waveform comparison."""

from ._core import evaluate_group, report


def evaluate(check_sampled_trace, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Exact match", "检查长度和每个 sampled output 都相同时是否通过。"),
        ("First mismatch", "检查 membrane/spike 第一次分叉的位置。"),
        ("Trace length and inputs", "检查截短/多余 sample 是否失败，并且输入列表不被修改。"),
    ) if zh else (
        ("Exact match", "Check pass behavior when length and every sampled output match."),
        ("First mismatch", "Check the first cycle where membrane/spike diverges."),
        ("Trace length and inputs", "Check truncated/extra samples fail and input lists remain unchanged."),
    )

    def exact_match():
        samples = [(2, False), (5, False), (0, True)]
        return check_sampled_trace(samples, list(samples)) == (True, None)

    def first_mismatch():
        return (
            check_sampled_trace(
                [(2, False), (5, True), (0, True)],
                [(2, False), (5, False), (0, True)],
            ) == (False, 1)
            and check_sampled_trace(
                [(2, False), (6, False)],
                [(2, False), (5, False)],
            ) == (False, 1)
        )

    def length_and_inputs():
        actual = [(1, False), (2, False)]
        expected = [(1, False), (2, False), (0, True)]
        actual_before = list(actual)
        expected_before = list(expected)
        result = check_sampled_trace(actual, expected)
        return (
            result == (False, 2)
            and actual == actual_before
            and expected == expected_before
        )

    return [
        evaluate_group(labels[0][0], exact_match, labels[0][1]),
        evaluate_group(labels[1][0], first_mismatch, labels[1][1]),
        evaluate_group(labels[2][0], length_and_inputs, labels[2][1]),
    ]


def check(check_sampled_trace, language: str = "zh") -> bool:
    title = "第 08 课检查" if language.lower().startswith("zh") else "Lesson 08 checks"
    return report(title, evaluate(check_sampled_trace, language))
