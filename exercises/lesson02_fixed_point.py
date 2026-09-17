"""Lesson 2 starter code: finite-width fixed-point numbers."""


def signed_limits(total_bits: int) -> tuple[int, int]:
    """Return the minimum and maximum signed integer codes for total_bits."""
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: compute the signed integer range")
    # YOUR CODE ENDS HERE


def quantize(
    x: float,
    total_bits: int = 8,
    frac_bits: int = 4,
) -> tuple[int, float]:
    """Quantize x using rounding plus saturation.

    Return (integer_code, represented_value).
    Use Python's round() for this lesson and saturate to signed_limits().
    """
    scale = 1 << frac_bits
    min_i, max_i = signed_limits(total_bits)

    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO: round, saturate, and decode")
    # YOUR CODE ENDS HERE

    return integer_code, represented_value
