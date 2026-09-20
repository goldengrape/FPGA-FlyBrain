"""Maintainer tests for the external exercise graders.

These tests are intentionally outside the student notebooks. They verify that
reference implementations pass and representative conceptual mistakes fail.
"""

from exercises.grader._core import evaluate_group, report

from exercises.grader import (
    lesson01,
    lesson02,
    lesson03,
    lesson04,
    lesson05,
    lesson06,
    lesson07,
    lesson08,
    lesson09,
    lesson10,
    lesson11,
    lesson12,
    lesson13,
    lesson14,
    lesson15,
    lesson16,
    lesson17,
    lesson18,
    lesson19,
    lesson20,
    lesson21,
    lesson22,
    lesson23,
)





def test_grader_core_hides_traceback_by_default(monkeypatch, capsys):
    monkeypatch.delenv("FPGA_FLYBRAIN_GRADER_DEBUG", raising=False)

    def boom():
        raise RuntimeError("grader exploded")

    group = evaluate_group("Exploding group", boom, "student hint")
    assert group.passed is False
    assert group.error is None

    report("Debug test", [group])
    output = capsys.readouterr().out
    assert "student hint" in output
    assert "RuntimeError" not in output
    assert "grader exploded" not in output


def test_grader_core_exposes_traceback_in_maintainer_debug_mode(monkeypatch, capsys):
    monkeypatch.setenv("FPGA_FLYBRAIN_GRADER_DEBUG", "1")

    def boom():
        raise RuntimeError("grader exploded")

    group = evaluate_group("Exploding group", boom, "student hint")
    assert group.passed is False
    assert group.error is not None
    assert "RuntimeError: grader exploded" in group.error

    report("Debug test", [group])
    output = capsys.readouterr().out
    assert "Debug exception:" in output
    assert "RuntimeError: grader exploded" in output


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


def test_lesson06_grader_rejects_reset_or_state_semantic_errors():
    def good(state, input_value, rst_n):
        return 0 if not rst_n else state + input_value

    def ignores_reset(state, input_value, rst_n):
        return state + input_value

    def forgets_old_state(state, input_value, rst_n):
        return 0 if not rst_n else input_value

    assert _all_pass(lesson06.evaluate(good))
    assert _some_fail(lesson06.evaluate(ignores_reset))
    assert _some_fail(lesson06.evaluate(forgets_old_state))


def test_lesson07_grader_rejects_strict_threshold_and_bad_reset_edge():
    def good_comb(membrane_v, input_current, threshold, reset_value):
        candidate = membrane_v + input_current
        spike_next = candidate >= threshold
        next_v = reset_value if spike_next else candidate
        return candidate, next_v, spike_next

    def strict_comb(membrane_v, input_current, threshold, reset_value):
        candidate = membrane_v + input_current
        spike_next = candidate > threshold
        next_v = reset_value if spike_next else candidate
        return candidate, next_v, spike_next

    def good_edge(next_v, spike_next, rst_n, reset_value):
        if not rst_n:
            return reset_value, False
        return next_v, spike_next

    def bad_edge(next_v, spike_next, rst_n, reset_value):
        return next_v, spike_next

    assert _all_pass(lesson07.evaluate(good_comb, good_edge))
    assert _some_fail(lesson07.evaluate(strict_comb, good_edge))
    assert _some_fail(lesson07.evaluate(good_comb, bad_edge))


def test_lesson08_grader_rejects_prefix_only_or_late_mismatch_reporting():
    def good(actual, expected):
        common = min(len(actual), len(expected))
        for cycle in range(common):
            if actual[cycle] != expected[cycle]:
                return False, cycle
        if len(actual) != len(expected):
            return False, common
        return True, None

    def prefix_only(actual, expected):
        for cycle, (a, e) in enumerate(zip(actual, expected)):
            if a != e:
                return False, cycle
        return True, None

    def last_mismatch(actual, expected):
        bad = None
        for cycle, (a, e) in enumerate(zip(actual, expected)):
            if a != e:
                bad = cycle
        return (True, None) if bad is None else (False, bad)

    assert _all_pass(lesson08.evaluate(good))
    assert _some_fail(lesson08.evaluate(prefix_only))
    assert _some_fail(lesson08.evaluate(last_mismatch))


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

    def mutating_push(queue, event, capacity):
        if len(queue) >= capacity:
            return queue, False
        queue.append(event)
        return queue, True

    def mutating_pop(queue):
        return (queue, queue.pop(0)) if queue else (queue, None)

    assert _some_fail(lesson10.evaluate(mutating_push, pop))
    assert _some_fail(lesson10.evaluate(push, mutating_pop))


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

    def ungrouped_build(num_sources, edges):
        index = []
        offset = 0
        for source in range(num_sources):
            count = sum(s == source for s, _, _ in edges)
            index.append((offset, count))
            offset += count
        return index, [(target, weight) for _, target, weight in edges]

    def sorted_targets_build(num_sources, edges):
        return build(num_sources, sorted(edges))

    assert _some_fail(lesson11.evaluate(ungrouped_build, lookup))
    assert _some_fail(lesson11.evaluate(sorted_targets_build, lookup))


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

    def overwrites(source_id, source_index, records, target_accum):
        updated = list(target_accum)
        start, count = source_index[source_id]
        events = records[start:start + count]
        for target, weight in events:
            updated[target] = weight
        return updated, events

    def loses_repeated_updates(source_id, source_index, records, target_accum):
        updated = list(target_accum)
        start, count = source_index[source_id]
        events = records[start:start + count]
        for target, weight in events:
            updated[target] = target_accum[target] + weight
        return updated, events

    def mutates_input(source_id, source_index, records, target_accum):
        updated, events = good(source_id, source_index, records, target_accum)
        target_accum[:] = updated
        return updated, events

    def ignores_negative_weights(source_id, source_index, records, target_accum):
        updated = list(target_accum)
        start, count = source_index[source_id]
        events = records[start:start + count]
        for target, weight in events:
            updated[target] += max(0, weight)
        return updated, events

    for wrong in (overwrites, loses_repeated_updates, mutates_input, ignores_negative_weights):
        assert _some_fail(lesson12.evaluate(wrong)), wrong.__name__


def test_lesson13_grader_rejects_wrong_critical_path():
    def good(delays, period):
        critical=max(delays); slack=period-critical
        return critical, slack, slack >= 0
    def bad(delays, period):
        critical=min(delays); slack=period-critical
        return critical, slack, slack >= 0
    assert _all_pass(lesson13.evaluate(good))
    assert _some_fail(lesson13.evaluate(bad))


def test_lesson14_grader_rejects_wrong_counter_width():
    def good(input_hz, target_hz):
        cycles=input_hz//target_hz
        return cycles, max(1,(cycles-1).bit_length())
    def bad(input_hz, target_hz):
        cycles=input_hz//target_hz
        return cycles, cycles.bit_length()
    assert _all_pass(lesson14.evaluate(good))
    assert _some_fail(lesson14.evaluate(bad))


def test_lesson15_grader_rejects_nonpersistent_state():
    def good(commands, initial_register=0):
        register=initial_register; reads=[]
        for op,value in commands:
            if op=="write": register=value
            elif op=="add": register+=value
            elif op=="read": reads.append(register)
        return reads, register
    def bad(commands, initial_register=0):
        register=initial_register; reads=[]
        for op,value in commands:
            if op=="write": register=value
            elif op=="add": register=value
            elif op=="read": reads.append(initial_register)
        return reads, register
    assert _all_pass(lesson15.evaluate(good))
    assert _some_fail(lesson15.evaluate(bad))


def test_lesson16_grader_rejects_missing_data_volume():
    def good(n, bpi, cpi, bw, startup=0.0):
        c=n*cpi; t=startup+n*bpi/bw
        return c,t,"memory" if t>c else "compute" if c>t else "balanced"
    def bad(n, bpi, cpi, bw, startup=0.0):
        c=n*cpi; t=startup+bpi/bw
        return c,t,"memory" if t>c else "compute" if c>t else "balanced"
    assert _all_pass(lesson16.evaluate(good))
    assert _some_fail(lesson16.evaluate(bad))


def test_lesson17_grader_rejects_one_burst_for_everything():
    def good(addresses, max_burst_words, setup_cycles, word_cycles=1):
        if not addresses: return 0,0
        bursts=1; run=1
        for prev,cur in zip(addresses,addresses[1:]):
            if cur==prev+1 and run<max_burst_words: run+=1
            else: bursts+=1; run=1
        return bursts,bursts*setup_cycles+len(addresses)*word_cycles
    def bad(addresses, max_burst_words, setup_cycles, word_cycles=1):
        if not addresses: return 0,0
        return 1,setup_cycles+len(addresses)*word_cycles
    assert _all_pass(lesson17.evaluate(good))
    assert _some_fail(lesson17.evaluate(bad))


def test_lesson18_grader_rejects_valid_without_ready():
    def good(valid, ready, data):
        accepted=[]; cycles=[]
        for i,(v,r,d) in enumerate(zip(valid,ready,data)):
            if v and r: accepted.append(d); cycles.append(i)
        return accepted,cycles
    def bad(valid, ready, data):
        accepted=[]; cycles=[]
        for i,(v,r,d) in enumerate(zip(valid,ready,data)):
            if v: accepted.append(d); cycles.append(i)
        return accepted,cycles
    assert _all_pass(lesson18.evaluate(good))
    assert _some_fail(lesson18.evaluate(bad))



def test_lesson14_wrong_width_feedback_points_to_counter_width():
    def bad(input_hz, target_hz):
        cycles = input_hz // target_hz
        return cycles, cycles.bit_length()

    groups = {group.name: group.passed for group in lesson14.evaluate(bad)}
    assert groups["Cycles per tick"] is True
    assert groups["Counter width"] is False
    assert groups["Minimum width"] is True


def test_lesson13_wrong_critical_path_does_not_hide_other_feedback_groups():
    def bad(delays, period):
        true_critical = max(delays)
        wrong_critical = min(delays)
        slack = period - true_critical
        return wrong_critical, slack, slack >= 0

    groups = {group.name: group.passed for group in lesson13.evaluate(bad)}
    assert groups["Critical path"] is False
    assert groups["Slack boundary"] is True
    assert groups["Timing failure"] is True



def test_lesson19_grader_rejects_reversed_edge_meaning():
    def good(neuron_ids, edges):
        incoming = {n: 0 for n in neuron_ids}
        outgoing = {n: 0 for n in neuron_ids}
        for source, target in edges:
            outgoing[source] += 1
            incoming[target] += 1
        return incoming, outgoing

    def bad(neuron_ids, edges):
        incoming = {n: 0 for n in neuron_ids}
        outgoing = {n: 0 for n in neuron_ids}
        for source, target in edges:
            incoming[source] += 1
            outgoing[target] += 1
        return incoming, outgoing

    def mutates_inputs(neuron_ids, edges):
        incoming, outgoing = good(neuron_ids, edges)
        neuron_ids.clear()
        edges.clear()
        return incoming, outgoing

    def drops_zero_degree_nodes(neuron_ids, edges):
        incoming = {}
        outgoing = {}
        for source, target in edges:
            outgoing[source] = outgoing.get(source, 0) + 1
            incoming[target] = incoming.get(target, 0) + 1
        return incoming, outgoing

    assert _all_pass(lesson19.evaluate(good))
    assert _some_fail(lesson19.evaluate(bad))
    assert _some_fail(lesson19.evaluate(mutates_inputs))
    assert _some_fail(lesson19.evaluate(drops_zero_degree_nodes))


def test_lesson20_grader_rejects_bad_integrity_or_provenance():
    import hashlib

    def good(payload, schema_version, source_release, converter_version):
        return {
            "schema_version": schema_version,
            "source_release": source_release,
            "converter_version": converter_version,
            "byte_count": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def bad_digest(payload, schema_version, source_release, converter_version):
        return {
            "schema_version": schema_version,
            "source_release": source_release,
            "converter_version": converter_version,
            "byte_count": len(payload),
            "sha256": str(len(payload)),
        }

    def uppercase_digest(payload, schema_version, source_release, converter_version):
        result = good(payload, schema_version, source_release, converter_version)
        result["sha256"] = result["sha256"].upper()
        return result

    def wrong_byte_count(payload, schema_version, source_release, converter_version):
        result = good(payload, schema_version, source_release, converter_version)
        result["byte_count"] += 1
        return result

    def extra_key(payload, schema_version, source_release, converter_version):
        result = good(payload, schema_version, source_release, converter_version)
        result["extra"] = "not allowed"
        return result

    seen = {}

    def nondeterministic(payload, schema_version, source_release, converter_version):
        key = (payload, schema_version, source_release, converter_version)
        count = seen.get(key, 0)
        seen[key] = count + 1
        result = good(payload, schema_version, source_release, converter_version)
        if count:
            result["converter_version"] = converter_version + "-changed"
        return result

    assert _all_pass(lesson20.evaluate(good))
    assert _some_fail(lesson20.evaluate(bad_digest))
    assert _some_fail(lesson20.evaluate(uppercase_digest))
    assert _some_fail(lesson20.evaluate(wrong_byte_count))
    assert _some_fail(lesson20.evaluate(extra_key))

    groups = {group.name: group.passed for group in lesson20.evaluate(nondeterministic)}
    assert groups["Schema and provenance"] is True
    assert groups["Byte integrity"] is False
    assert groups["Payload sensitivity"] is True


def test_lesson21_grader_rejects_raw_demand_as_bottleneck():
    def good(stage_demand, stage_capacity):
        utilization = {
            stage: stage_demand[stage] / stage_capacity[stage]
            for stage in stage_demand
        }
        return utilization, max(utilization, key=utilization.get)

    def bad(stage_demand, stage_capacity):
        utilization = {
            stage: stage_demand[stage] / stage_capacity[stage]
            for stage in stage_demand
        }
        return utilization, max(stage_demand, key=stage_demand.get)

    def mutates_inputs(stage_demand, stage_capacity):
        utilization, stage = good(stage_demand, stage_capacity)
        stage_demand.clear()
        stage_capacity.clear()
        return utilization, stage

    assert _all_pass(lesson21.evaluate(good))
    assert _some_fail(lesson21.evaluate(bad))
    assert _some_fail(lesson21.evaluate(mutates_inputs))


def test_lesson22_grader_rejects_open_loop_or_one_direction_logic():
    def good(initial_position, target_position, steps):
        position = initial_position
        trace = [position]
        for _ in range(steps):
            if position < target_position:
                position += 1
            elif position > target_position:
                position -= 1
            trace.append(position)
        return trace

    def overshoots(initial_position, target_position, steps):
        direction = 1 if target_position >= initial_position else -1
        return [initial_position + direction * step for step in range(steps + 1)]

    def only_moves_right(initial_position, target_position, steps):
        position = initial_position
        trace = [position]
        for _ in range(steps):
            if position < target_position:
                position += 1
            trace.append(position)
        return trace

    def drops_initial_position(initial_position, target_position, steps):
        return good(initial_position, target_position, steps)[1:]

    assert _all_pass(lesson22.evaluate(good))
    assert _some_fail(lesson22.evaluate(overshoots))
    assert _some_fail(lesson22.evaluate(only_moves_right))
    assert _some_fail(lesson22.evaluate(drops_initial_position))


def test_lesson23_grader_rejects_energy_without_duration():
    def good(events, seconds, watts):
        return events / seconds, watts * seconds / events

    def bad(events, seconds, watts):
        return events / seconds, watts / events

    def swaps_metrics(events, seconds, watts):
        throughput, energy_per_event = good(events, seconds, watts)
        return energy_per_event, throughput

    assert _all_pass(lesson23.evaluate(good))
    assert _some_fail(lesson23.evaluate(bad))
    assert _some_fail(lesson23.evaluate(swaps_metrics))
