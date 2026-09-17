import pytest

from exercises.lesson03_semantics import (
    lif_step_v0,
    threshold_boundary_case,
    update_order_counterexample,
)


def test_v0_uses_leak_then_input():
    next_v, spike, candidate = lif_step_v0(
        v=0.8, current=0.4, alpha=0.9, threshold=2.0, reset=0.0
    )
    assert candidate == pytest.approx(1.12)
    assert spike is False
    assert next_v == pytest.approx(1.12)


def test_v0_threshold_is_greater_than_or_equal():
    next_v, spike, candidate = lif_step_v0(
        v=0.75, current=0.25, alpha=1.0, threshold=1.0, reset=0.0
    )
    assert candidate == pytest.approx(1.0)
    assert spike is True
    assert next_v == pytest.approx(0.0)


def test_threshold_boundary_case_really_distinguishes_rules():
    v, current, alpha, threshold = threshold_boundary_case()
    candidate = alpha * v + current
    assert candidate == pytest.approx(threshold)
    assert (candidate >= threshold) is True
    assert (candidate > threshold) is False


def test_update_order_counterexample_really_distinguishes_rules():
    v, current, alpha = update_order_counterexample()
    assert 0.0 < alpha < 1.0
    assert current != 0.0
    leak_then_input = alpha * v + current
    input_then_leak = alpha * (v + current)
    assert leak_then_input != pytest.approx(input_then_leak)
