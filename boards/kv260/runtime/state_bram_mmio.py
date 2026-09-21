#!/usr/bin/env python3
"""LAB-HW-07 self-checking PS/Linux -> BRAM neuron-state store.

Frozen teaching window:
    /dev/mem -> PS M_AXI_HPM0_FPD -> AXI BRAM Controller
             -> kv260_neuron_state_store @ 0xA0000000

The window contains 1024 x 32-bit state words (4 KiB total).
This helper intentionally exposes no arbitrary physical base-address option.
"""

from __future__ import annotations

import argparse
import json
import mmap
import os
import struct
from pathlib import Path
from typing import Protocol


STATE_BASE = 0xA0000000
STATE_WORDS = 1024
STATE_BYTES = STATE_WORDS * 4

INITIAL = {
    0: 0x10203040,
    1: 0x11223344,
    7: 0x55667788,
    31: 0x89ABCDEF,
    255: 0x0BADF00D,
    511: 0x13579BDF,
    1023: 0xFFFFFFFF,
}

REWRITE = {
    1: 0x01020304,
    511: 0xCAFEBABE,
}


class Transport(Protocol):
    def write_word(self, index: int, value: int) -> None: ...
    def read_word(self, index: int) -> int: ...
    def close(self) -> None: ...


def _check_index(index: int) -> None:
    if not 0 <= index < STATE_WORDS:
        raise ValueError(f"word index {index} outside 0..{STATE_WORDS - 1}")


class DryRunTransport:
    def __init__(self) -> None:
        self._words = [0] * STATE_WORDS

    def write_word(self, index: int, value: int) -> None:
        _check_index(index)
        self._words[index] = value & 0xFFFFFFFF

    def read_word(self, index: int) -> int:
        _check_index(index)
        return self._words[index]

    def close(self) -> None:
        pass


class DevMemTransport:
    def __init__(self, device: Path) -> None:
        if STATE_BASE % mmap.PAGESIZE:
            raise ValueError(
                f"frozen base 0x{STATE_BASE:x} must be page aligned "
                f"for page size 0x{mmap.PAGESIZE:x}"
            )
        self._fd = os.open(device, os.O_RDWR | os.O_SYNC)
        try:
            self._map = mmap.mmap(
                self._fd,
                STATE_BYTES,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=STATE_BASE,
            )
        except Exception:
            os.close(self._fd)
            raise

    def write_word(self, index: int, value: int) -> None:
        _check_index(index)
        struct.pack_into("<I", self._map, index * 4, value & 0xFFFFFFFF)

    def read_word(self, index: int) -> int:
        _check_index(index)
        return struct.unpack_from("<I", self._map, index * 4)[0]

    def close(self) -> None:
        self._map.close()
        os.close(self._fd)


def verify_phase(
    transport: Transport,
    expected: dict[int, int],
    phase: str,
) -> list[dict[str, int | str]]:
    trace: list[dict[str, int | str]] = []
    for index in sorted(expected):
        observed = transport.read_word(index)
        value = expected[index]
        row = {
            "phase": phase,
            "index": index,
            "byte_offset": index * 4,
            "expected": value,
            "read": observed,
        }
        trace.append(row)
        print(
            f"PHASE={phase} INDEX={index:04d} OFFSET=0x{index * 4:03x} "
            f"EXPECTED=0x{value:08x} READ=0x{observed:08x}"
        )
        if observed != value:
            raise AssertionError(
                f"{phase}: index {index}: expected 0x{value:08x}, "
                f"read 0x{observed:08x}"
            )
    return trace


def run(transport: Transport) -> list[dict[str, int | str]]:
    trace: list[dict[str, int | str]] = []

    for index, value in INITIAL.items():
        transport.write_word(index, value)
        print(f"WRITE_INITIAL INDEX={index:04d} VALUE=0x{value:08x}")

    expected = dict(INITIAL)
    trace.extend(verify_phase(transport, expected, "INITIAL_READBACK"))

    for index, value in REWRITE.items():
        transport.write_word(index, value)
        expected[index] = value
        print(f"WRITE_REWRITE INDEX={index:04d} VALUE=0x{value:08x}")

    trace.extend(verify_phase(transport, expected, "REWRITE_PRESERVATION"))
    return trace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=Path, default=Path("/dev/mem"))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="exercise the fixed memory oracle without physical hardware",
    )
    args = parser.parse_args()

    print("FPGA_FLYBRAIN_LAB=LAB-HW-07")
    print(f"STATE_BASE=0x{STATE_BASE:08x}")
    print(f"STATE_WORDS={STATE_WORDS}")
    print(f"STATE_BYTES={STATE_BYTES}")

    transport: Transport
    if args.dry_run:
        print("TRANSPORT=DRY_RUN_MODEL")
        transport = DryRunTransport()
    else:
        print("TRANSPORT=DEVMEM_FIXED_BRAM_WINDOW")
        print(f"MMIO_DEVICE={args.device}")
        if not args.device.exists():
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_DEVICE_MISSING")
            return 3
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_REQUIRES_ROOT")
            print("DETAIL=Run the physical check with sudo; do not change /dev/mem permissions.")
            return 4
        try:
            transport = DevMemTransport(args.device)
        except PermissionError as exc:
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_PERMISSION_OR_POLICY")
            print(f"DETAIL={exc}")
            return 5
        except OSError as exc:
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_MMAP_FAILED")
            print(f"DETAIL={exc}")
            return 6
        except ValueError as exc:
            print("STATUS=FAIL")
            print("ERROR=TRANSPORT_CONFIGURATION")
            print(f"DETAIL={exc}")
            return 7

    try:
        try:
            trace = run(transport)
        except AssertionError as exc:
            print("STATUS=FAIL")
            print("ERROR=STATE_READBACK_OR_ALIAS_MISMATCH")
            print(f"DETAIL={exc}")
            return 8
    finally:
        transport.close()

    if args.json_out:
        payload = {
            "lab_id": "LAB-HW-07",
            "transport": "dry-run" if args.dry_run else "devmem-fixed-bram-window",
            "state_base": STATE_BASE,
            "state_words": STATE_WORDS,
            "state_bytes": STATE_BYTES,
            "word_bytes": 4,
            "trace": trace,
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"JSON_OUT={args.json_out}")

    print(f"CHECKED_READS={len(trace)}")
    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
