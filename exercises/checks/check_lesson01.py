import pytest

from exercises.lesson01_lif import leak_step, lif_step


def test_rest_is_a_fixed_point():
    assert leak_step(-70.0, 0.0, 0.9, -70.0) == pytest.approx(-70.0)


def test_voltage_above_rest_leaks_toward_rest():
    assert leak_step(-55.0, 0.0, 0.9, -70.0) == pytest.approx(-56.5)


def test_voltage_below_rest_also_leaks_toward_rest():
    assert leak_step(-80.0, 0.0, 0.5, -70.0) == pytest.approx(-75.0)


def test_input_is_added_after_leak():
    assert leak_step(-55.0, 6.0, 0.9, -70.0) == pytest.approx(-50.5)


def test_equal_threshold_spikes_and_resets():
    next_v, spike = lif_step(-60.0, 11.0, 0.9, -70.0, -50.0, -70.0)
    assert spike is True
    assert next_v == pytest.approx(-70.0)


def test_below_threshold_does_not_spike():
    next_v, spike = lif_step(-70.0, 5.0, 0.9, -70.0, -50.0, -70.0)
    assert spike is False
    assert next_v == pytest.approx(-65.0)
