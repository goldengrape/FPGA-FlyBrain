"""Checks for Lesson 02: fixed-point representation."""

from math import isclose

from ._core import evaluate_group, report


def evaluate(signed_limits, quantize, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Signed range", "检查二补码有符号整数的可表示范围。"),
        ("Quantization", "检查格点值、舍入和负数表示。"),
        ("Saturation", "检查正负溢出是否采用 saturation，而不是 wraparound。"),
    ) if zh else (
        ("Signed range", "Check the representable two's-complement signed range."),
        ("Quantization", "Check grid values, rounding, and negative values."),
        ("Saturation", "Check that positive and negative overflow saturate instead of wrapping."),
    )

    def limits_ok():
        return signed_limits(4) == (-8, 7) and signed_limits(8) == (-128, 127)

    def quant_ok():
        c1, v1 = quantize(0.25, 8, 4)
        c2, v2 = quantize(0.22, 8, 4)
        c3, v3 = quantize(-0.3, 8, 4)
        return (
            c1 == 4 and isclose(v1, 0.25)
            and c2 == 4 and isclose(v2, 0.25)
            and c3 == -5 and isclose(v3, -0.3125)
        )

    def saturation_ok():
        cp, vp = quantize(100.0, 4, 2)
        cn, vn = quantize(-100.0, 4, 2)
        return cp == 7 and isclose(vp, 1.75) and cn == -8 and isclose(vn, -2.0)

    return [
        evaluate_group(labels[0][0], limits_ok, labels[0][1]),
        evaluate_group(labels[1][0], quant_ok, labels[1][1]),
        evaluate_group(labels[2][0], saturation_ok, labels[2][1]),
    ]


def check(signed_limits, quantize, language: str = "zh") -> bool:
    title = "Lesson 02 checks" if not language.lower().startswith("zh") else "第 02 课检查"
    return report(title, evaluate(signed_limits, quantize, language))
