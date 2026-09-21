#!/usr/bin/env python3
"""LAB-HW-08 differential checker: Python oracle vs KV260 PL replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import os
import struct
import sys
import time
from pathlib import Path
from typing import Protocol

from lab08_replay_reference import decode_event, load_fixture, replay, sha256_file


STATE_BASE = 0xA0000000
GPIO_BASE = 0xA0010000
MAP_BYTES = 0x1000
GPIO_DATA = 0x0000
GPIO2_DATA = 0x0008

BUSY_BIT = 0
DONE_BIT = 1
ERROR_BIT = 2


class ReplayTransport(Protocol):
    def read_state_word(self, index: int) -> int: ...
    def write_state_word(self, index: int, value: int) -> None: ...
    def read_status(self) -> int: ...
    def write_control(self, value: int) -> None: ...
    def close(self) -> None: ...


def _u32_read(mm: mmap.mmap, offset: int) -> int:
    return struct.unpack_from("<I", mm, offset)[0]


def _u32_write(mm: mmap.mmap, offset: int, value: int) -> None:
    struct.pack_into("<I", mm, offset, value & 0xFFFFFFFF)


class DevMemReplayTransport:
    def __init__(self, device: Path) -> None:
        self._fd = os.open(device, os.O_RDWR | os.O_SYNC)
        try:
            self._state = mmap.mmap(
                self._fd,
                MAP_BYTES,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=STATE_BASE,
            )
            self._gpio = mmap.mmap(
                self._fd,
                MAP_BYTES,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=GPIO_BASE,
            )
        except Exception:
            os.close(self._fd)
            raise

    def read_state_word(self, index: int) -> int:
        if not 0 <= index < 1024:
            raise ValueError("state word outside 0..1023")
        return _u32_read(self._state, index * 4)

    def write_state_word(self, index: int, value: int) -> None:
        if not 0 <= index < 1024:
            raise ValueError("state word outside 0..1023")
        _u32_write(self._state, index * 4, value)

    def read_status(self) -> int:
        return _u32_read(self._gpio, GPIO2_DATA)

    def write_control(self, value: int) -> None:
        _u32_write(self._gpio, GPIO_DATA, value)

    def close(self) -> None:
        self._state.close()
        self._gpio.close()
        os.close(self._fd)


class DryRunReplayTransport:
    def __init__(self, fixture: dict, expected: dict) -> None:
        self.words = [0] * 1024
        self.status = 0
        self.fixture = fixture
        self.expected = expected

    def read_state_word(self, index: int) -> int:
        return self.words[index]

    def write_state_word(self, index: int, value: int) -> None:
        self.words[index] = value & 0xFFFFFFFF

    def read_status(self) -> int:
        return self.status

    def write_control(self, value: int) -> None:
        if value & 1:
            mm = self.fixture["memory_map"]
            for i, value0 in enumerate(self.expected["final_state"]):
                self.words[int(mm["state_base_word"]) + i] = value0
            for i, source in enumerate(self.expected["spike_order"]):
                self.words[int(mm["spike_trace_base_word"]) + i] = source
            self.words[int(mm["spike_count_word"])] = self.expected["spike_count"]
            for i, word in enumerate(self.expected["event_words"]):
                self.words[int(mm["event_trace_base_word"]) + i] = word
            self.words[int(mm["event_count_word"])] = self.expected["event_count"]
            self.status = (
                (1 << DONE_BIT)
                | (self.expected["spike_count"] << 4)
                | (self.expected["event_count"] << 8)
            )
        else:
            self.status = 0

    def close(self) -> None:
        pass


def file_sha256_self() -> str:
    return sha256_file(Path(__file__).resolve())


def prepare_memory(transport: ReplayTransport, fixture: dict) -> None:
    mm = fixture["memory_map"]
    initial = fixture["input"]["initial_state"]

    for i, value in enumerate(initial):
        transport.write_state_word(int(mm["state_base_word"]) + i, int(value))

    for i in range(4):
        transport.write_state_word(int(mm["spike_trace_base_word"]) + i, 0xDEADBEEF)
        transport.write_state_word(int(mm["event_trace_base_word"]) + i, 0xDEADBEEF)

    transport.write_state_word(int(mm["spike_count_word"]), 0xDEADBEEF)
    transport.write_state_word(int(mm["event_count_word"]), 0xDEADBEEF)


def readback(transport: ReplayTransport, fixture: dict, expected: dict) -> dict:
    mm = fixture["memory_map"]
    state = [
        transport.read_state_word(int(mm["state_base_word"]) + i)
        for i in range(len(expected["final_state"]))
    ]
    spike_count = transport.read_state_word(int(mm["spike_count_word"]))
    spike_words = [
        transport.read_state_word(int(mm["spike_trace_base_word"]) + i)
        for i in range(spike_count)
    ]
    event_count = transport.read_state_word(int(mm["event_count_word"]))
    event_words = [
        transport.read_state_word(int(mm["event_trace_base_word"]) + i)
        for i in range(event_count)
    ]
    return {
        "final_state": state,
        "spike_count": spike_count,
        "spike_order": spike_words,
        "event_count": event_count,
        "event_words": event_words,
        "events": [decode_event(word) for word in event_words],
    }


def compare(expected: dict, observed: dict) -> list[str]:
    errors: list[str] = []
    for key in ("final_state", "spike_count", "spike_order", "event_count", "event_words"):
        if observed[key] != expected[key]:
            errors.append(f"{key}: expected={expected[key]!r} observed={observed[key]!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--device", type=Path, default=Path("/dev/mem"))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    args = parser.parse_args()

    if args.timeout_seconds <= 0:
        print("STATUS=FAIL")
        print("ERROR=INVALID_TIMEOUT")
        return 2

    try:
        fixture = load_fixture(args.fixture)
        expected = replay(fixture)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("STATUS=FAIL")
        print("ERROR=FIXTURE_ORACLE_INVALID")
        print(f"DETAIL={exc}")
        return 3

    print("FPGA_FLYBRAIN_LAB=LAB-HW-08")
    print(f"FIXTURE_ID={fixture['fixture_id']}")
    print(f"FIXTURE_SHA256={sha256_file(args.fixture)}")
    print(f"CHECKER_SHA256={file_sha256_self()}")
    print(f"STATE_BASE=0x{STATE_BASE:08x}")
    print(f"CONTROL_BASE=0x{GPIO_BASE:08x}")

    transport: ReplayTransport
    if args.dry_run:
        print("TRANSPORT=DRY_RUN_REPLAY_MODEL")
        transport = DryRunReplayTransport(fixture, expected)
    else:
        print("TRANSPORT=DEVMEM_FIXED_REPLAY_WINDOWS")
        if not args.device.exists():
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_DEVICE_MISSING")
            return 4
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_REQUIRES_ROOT")
            return 5
        try:
            transport = DevMemReplayTransport(args.device)
        except PermissionError as exc:
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_PERMISSION_OR_POLICY")
            print(f"DETAIL={exc}")
            return 6
        except OSError as exc:
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_MMAP_FAILED")
            print(f"DETAIL={exc}")
            return 7

    try:
        status0 = transport.read_status()
        if status0 & (1 << BUSY_BIT):
            print("STATUS=FAIL")
            print("ERROR=ENGINE_ALREADY_BUSY")
            return 8

        transport.write_control(0)
        prepare_memory(transport, fixture)
        transport.write_control(1)

        deadline = time.monotonic() + args.timeout_seconds
        final_status = 0
        while time.monotonic() < deadline:
            final_status = transport.read_status()
            if final_status & (1 << ERROR_BIT):
                print("STATUS=FAIL")
                print("ERROR=ENGINE_REPORTED_ERROR")
                print(f"STATUS_WORD=0x{final_status:08x}")
                return 9
            if (final_status & (1 << DONE_BIT)) and not (final_status & (1 << BUSY_BIT)):
                break
            time.sleep(0.001)
        else:
            print("STATUS=FAIL")
            print("ERROR=ENGINE_TIMEOUT")
            print(f"LAST_STATUS_WORD=0x{final_status:08x}")
            return 10

        transport.write_control(0)
        observed = readback(transport, fixture, expected)
    finally:
        transport.close()

    errors = compare(expected, observed)

    print("EXPECTED_SPIKES=" + ",".join(map(str, expected["spike_order"])))
    print("OBSERVED_SPIKES=" + ",".join(map(str, observed["spike_order"])))
    print("EXPECTED_FINAL_STATE=" + ",".join(map(str, expected["final_state"])))
    print("OBSERVED_FINAL_STATE=" + ",".join(map(str, observed["final_state"])))
    for i, (exp, got) in enumerate(zip(expected["event_words"], observed["event_words"])):
        print(f"EVENT_COMPARE={i} EXPECTED=0x{exp:08x} OBSERVED=0x{got:08x}")

    payload = {
        "lab_id": "LAB-HW-08",
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": sha256_file(args.fixture),
        "checker_sha256": file_sha256_self(),
        "transport": "dry-run" if args.dry_run else "devmem-fixed-replay-windows",
        "state_base": STATE_BASE,
        "control_base": GPIO_BASE,
        "expected": expected,
        "observed": observed,
        "differential_errors": errors,
    }

    if args.json_out:
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"JSON_OUT={args.json_out}")

    if errors:
        print("STATUS=FAIL")
        print("ERROR=REPLAY_DIFFERENTIAL_MISMATCH")
        for error in errors:
            print(f"DIFF={error}")
        return 11

    print("DIFFERENTIAL=PASS")
    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
