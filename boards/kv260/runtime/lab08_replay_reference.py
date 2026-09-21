#!/usr/bin/env python3
"""LAB-HW-08 deterministic replay oracle for the Lesson-12 teaching event machine."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_fixture(path: Path) -> dict[str, Any]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != 1:
        raise ValueError("unsupported fixture schema_version")
    if fixture.get("fixture_id") != "lesson12_four_neuron_replay_v1":
        raise ValueError("unexpected LAB-HW-08 fixture_id")
    if fixture["model"].get("kind") != "teaching_event_machine":
        raise ValueError("fixture must identify the Lesson-12 teaching event machine")
    if fixture["model"].get("stochastic") is not False:
        raise ValueError("LAB-HW-08 v1 fixture must be deterministic")
    return fixture


def encode_event(source: int, target: int, weight: int, accum_after_add: int, spiked: bool) -> int:
    if not 0 <= source <= 0xF:
        raise ValueError("source does not fit 4 bits")
    if not 0 <= target <= 0xF:
        raise ValueError("target does not fit 4 bits")
    if not -128 <= weight <= 127:
        raise ValueError("weight does not fit signed 8 bits")
    if not 0 <= accum_after_add <= 0xFF:
        raise ValueError("teaching accumulator trace does not fit 8 bits")
    return (
        (source << 28)
        | (target << 24)
        | ((weight & 0xFF) << 16)
        | ((accum_after_add & 0xFF) << 8)
        | int(spiked)
    )


def decode_event(word: int) -> dict[str, int | bool]:
    raw_weight = (word >> 16) & 0xFF
    weight = raw_weight - 256 if raw_weight & 0x80 else raw_weight
    return {
        "source": (word >> 28) & 0xF,
        "target": (word >> 24) & 0xF,
        "weight": weight,
        "accumulator_after_add": (word >> 8) & 0xFF,
        "spiked": bool(word & 1),
    }


def replay(fixture: dict[str, Any]) -> dict[str, Any]:
    network = fixture["network"]
    input_spec = fixture["input"]

    neuron_count = int(network["neuron_count"])
    source_index = [tuple(map(int, row)) for row in network["source_index"]]
    records = [(int(row["target"]), int(row["weight"])) for row in network["records"]]
    thresholds = [int(x) for x in network["thresholds"]]
    state = [int(x) for x in input_spec["initial_state"]]
    queue = deque(int(x) for x in input_spec["initial_queue"])

    if len(source_index) != neuron_count:
        raise ValueError("source_index length must equal neuron_count")
    if len(thresholds) != neuron_count or len(state) != neuron_count:
        raise ValueError("threshold/state length must equal neuron_count")

    spike_order: list[int] = []
    events: list[dict[str, Any]] = []
    event_words: list[int] = []

    while queue:
        source = queue.popleft()
        if not 0 <= source < neuron_count:
            raise ValueError(f"source {source} outside neuron range")

        spike_order.append(source)
        start, count = source_index[source]
        for target, weight in records[start : start + count]:
            before = state[target]
            after_add = before + weight
            spiked = after_add >= thresholds[target]
            after = 0 if spiked else after_add
            state[target] = after
            if spiked:
                queue.append(target)

            word = encode_event(source, target, weight, after_add, spiked)
            event_words.append(word)
            events.append(
                {
                    "source": source,
                    "target": target,
                    "weight": weight,
                    "accumulator_before": before,
                    "accumulator_after_add": after_add,
                    "spiked": spiked,
                    "state_after": after,
                    "encoded_word": word,
                }
            )

    return {
        "fixture_id": fixture["fixture_id"],
        "spike_order": spike_order,
        "spike_count": len(spike_order),
        "events": events,
        "event_words": event_words,
        "event_count": len(events),
        "final_state": state,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    try:
        fixture = load_fixture(args.fixture)
        result = replay(fixture)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("STATUS=FAIL")
        print("ERROR=FIXTURE_ORACLE_INVALID")
        print(f"DETAIL={exc}")
        return 2

    print("FPGA_FLYBRAIN_LAB=LAB-HW-08")
    print(f"FIXTURE_ID={fixture['fixture_id']}")
    print(f"FIXTURE_SHA256={sha256_file(args.fixture)}")
    print("MODEL=LESSON12_TEACHING_EVENT_MACHINE")
    print("STOCHASTIC=0")
    print("SPIKE_ORDER=" + ",".join(map(str, result["spike_order"])))
    print("FINAL_STATE=" + ",".join(map(str, result["final_state"])))
    for i, row in enumerate(result["events"]):
        print(
            f"EVENT={i} SOURCE={row['source']} TARGET={row['target']} "
            f"WEIGHT={row['weight']} ACCUM_AFTER_ADD={row['accumulator_after_add']} "
            f"SPIKED={int(row['spiked'])} WORD=0x{row['encoded_word']:08x}"
        )

    if args.json_out:
        payload = {
            "lab_id": "LAB-HW-08",
            "fixture_sha256": sha256_file(args.fixture),
            **result,
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"JSON_OUT={args.json_out}")

    expected_spikes = [0, 1, 2, 3]
    expected_state = [0, 0, 0, 0]
    if result["spike_order"] != expected_spikes or result["final_state"] != expected_state:
        print("STATUS=FAIL")
        print("ERROR=LESSON12_REFERENCE_DRIFT")
        return 3

    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
