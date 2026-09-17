import pytest

from exercises.lesson02_fixed_point import quantize, signed_limits


def test_signed_limits():
    assert signed_limits(4) == (-8, 7)
    assert signed_limits(8) == (-128, 127)


def test_exact_grid_value_is_unchanged():
    code, represented = quantize(0.25, total_bits=8, frac_bits=4)
    assert code == 4
    assert represented == pytest.approx(0.25)


def test_value_is_rounded_to_nearest_grid_point():
    code, represented = quantize(0.22, total_bits=8, frac_bits=4)
    assert code == 4
    assert represented == pytest.approx(0.25)


def test_negative_value_quantizes_correctly():
    code, represented = quantize(-0.3, total_bits=8, frac_bits=4)
    assert code == -5
    assert represented == pytest.approx(-0.3125)


def test_positive_overflow_saturates():
    code, represented = quantize(100.0, total_bits=4, frac_bits=2)
    assert code == 7
    assert represented == pytest.approx(1.75)


def test_negative_overflow_saturates():
    code, represented = quantize(-100.0, total_bits=4, frac_bits=2)
    assert code == -8
    assert represented == pytest.approx(-2.0)
