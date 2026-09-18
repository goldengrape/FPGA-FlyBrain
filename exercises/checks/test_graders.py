"""Maintainer tests for the external exercise graders.

These tests are intentionally outside the student notebooks. They verify that
reference implementations pass and representative conceptual mistakes fail.
"""

from exercises.grader import (
    lesson01,
    lesson02,
    lesson03,
    lesson04,
    lesson05,
    lesson09,
    lesson10,
    lesson11,
    lesson12,
)


def _all_pass(groups):
    return all(group.passed for group in groups)


def _some_fail(groups):
    return any(not group.passed for group in groups)


def test_lesson01_grader_accepts_reference_and_rejects_strict_threshold():
    def leak(v, input_value, alpha, v_rest):
        return v_rest + alpha * (v - v_rest) + input_value

    def good(v, input_value, alpha, v_rest, threshold, reset):
        candidate = leak(v, input_value, alpha, v_rest)
        spike = candidate >= threshold
        return (reset if spike else candidate), spike

    def bad(v, input_value, alpha, v_rest, threshold, reset):
        candidate = leak(v, input_value, alpha, v_rest)
        spike = candidate > threshold
        return (reset if spike else candidate), spike

    assert _all_pass(lesson01.evaluate(leak, good))
    assert _some_fail(lesson01.evaluate(leak, bad))


def test_lesson02_grader_accepts_reference_and_rejects_wraparound():
    def limits(bits):
        return -(1 << (bits - 1)), (1 << (bits - 1)) - 1

    def good(x, total_bits=8, frac_bits=4):
        scale = 1 << frac_bits
        lo, hi = limits(total_bits)
        code = round(x * scale)
        code = min(max(code, lo), hi)
        return code, code / scale

    def bad(x, total_bits=8, frac_bits=4):
        scale = 1 << frac_bits
        modulus = 1 << total_bits
        code = round(x * scale) % modulus
        if code >= (1 << (total_bits - 1)):
            code -= modulus
        return code, code / scale

    assert _all_pass(lesson02.evaluate(limits, good))
    assert _some_fail(lesson02.evaluate(limits, bad))


def test_lesson03_grader_checks_frozen_semantics_and_distinguishing_probes():
    def good(v, current, alpha=0.9, threshold=1.0, reset=0.0):
        candidate = alpha * v + current
        spike = candidate >= threshold
        return (reset if spike else candidate), spike, candidate

    def bad(v, current, alpha=0.9, threshold=1.0, reset=0.0):
        candidate = alpha * (v + current)
        spike = candidate >= threshold
        return (reset if spike else candidate), spike, candidate

    boundary = lambda: (0.5, 0.5, 1.0, 1.0)
    order_case = lambda: (0.5, 0.5, 0.5)

    assert _all_pass(lesson03.evaluate(good, boundary, order_case))
    assert _some_fail(lesson03.evaluate(bad, boundary, order_case))


def test_lesson04_grader_detects_bad_clock_edge():
    def comb(state, input_value, threshold, reset=0):
        candidate = state + input_value
        spike = candidate >= threshold
        return candidate, spike, reset if spike else candidate

    def edge(state, value_to_store):
        return value_to_store

    def run(inputs, threshold, reset=0, initial_state=0):
        state = initial_state
        states = [state]
        spikes = []
        for value in inputs:
            _, spike, store = comb(state, value, threshold, reset)
            state = edge(state, store)
            states.append(state)
            spikes.append(spike)
        return states, spikes

    def bad_edge(state, value_to_store):
        return state

    assert _all_pass(lesson04.evaluate(comb, edge, run))
    assert _some_fail(lesson04.evaluate(comb, bad_edge, run))


def test_lesson05_grader_detects_strict_threshold():
    not_ = lambda a: not a
    and_ = lambda a, b: a and b
    or_ = lambda a, b: a or b
    good_threshold = lambda value, threshold: value >= threshold
    bad_threshold = lambda value, threshold: value > threshold
    good_spike = lambda enable, value, threshold: and_(enable, good_threshold(value, threshold))
    bad_spike = lambda enable, value, threshold: and_(enable, bad_threshold(value, threshold))

    assert _all_pass(lesson05.evaluate(not_, and_, or_, good_threshold, good_spike))
    assert _some_fail(lesson05.evaluate(not_, and_, or_, bad_threshold, bad_spike))


def test_lesson09_grader_detects_non_addressed_update():
    def update(states, address, input_value):
        result = list(states)
        result[address] += input_value
        return result

    def round_robin(states, inputs):
        if len(states) != len(inputs):
            raise ValueError
        current = list(states)
        trace = []
        for address, value in enumerate(inputs):
            before = current[address]
            current = update(current, address, value)
            trace.append((address, before, current[address]))
        return current, trace

    def bad_update(states, address, input_value):
        return [x + input_value for x in states]

    assert _all_pass(lesson09.evaluate(update, round_robin))
    assert _some_fail(lesson09.evaluate(bad_update, round_robin))


def test_lesson10_grader_detects_overwrite_on_full():
    def push(queue, event, capacity):
        result = list(queue)
        if len(result) >= capacity:
            return result, False
        result.append(event)
        return result, True

    def pop(queue):
        result = list(queue)
        if not result:
            return result, None
        return result[1:], result[0]

    def bad_push(queue, event, capacity):
        result = list(queue)
        if len(result) >= capacity:
            result = result[1:] + [event]
            return result, True
        result.append(event)
        return result, True

    assert _all_pass(lesson10.evaluate(push, pop))
    assert _some_fail(lesson10.evaluate(bad_push, pop))


def test_lesson11_grader_detects_wrong_lookup_range():
    def build(num_sources, edges):
        records = []
        index = []
        by_source = [[] for _ in range(num_sources)]
        for source, target, weight in edges:
            by_source[source].append((target, weight))
        for group in by_source:
            start = len(records)
            records.extend(group)
            index.append((start, len(group)))
        return index, records

    def lookup(source_id, source_index, records):
        start, count = source_index[source_id]
        return records[start:start + count]

    def bad_lookup(source_id, source_index, records):
        return list(records)

    assert _all_pass(lesson11.evaluate(build, lookup))
    assert _some_fail(lesson11.evaluate(build, bad_lookup))


def test_lesson12_grader_detects_scanning_all_records():
    def good(source_id, source_index, records, target_accum):
        updated = list(target_accum)
        start, count = source_index[source_id]
        events = []
        for target, weight in records[start:start + count]:
            events.append((target, weight))
            updated[target] += weight
        return updated, events

    def bad(source_id, source_index, records, target_accum):
        updated = list(target_accum)
        events = []
        for target, weight in records:
            events.append((target, weight))
            updated[target] += weight
        return updated, events

    assert _all_pass(lesson12.evaluate(good))
    assert _some_fail(lesson12.evaluate(bad))
