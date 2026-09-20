#!/usr/bin/env python3
"""LAB-HW-06 self-checking PS/Linux -> PL MMIO loopback.

Frozen teaching transport:
    /dev/mem -> PS M_AXI_HPM0_FPD -> AXI GPIO @ 0xA0010000

Channel 1 GPIO_DATA (+0x0) is a 32-bit output written by the runtime host.
Channel 2 GPIO2_DATA (+0x8) is a 32-bit input driven by PL.
The PL teaching transform returns (write + 1) modulo 2^32.

The physical base address is intentionally not configurable from the CLI.  This
helper is for the bitstream built by build_lab06_loopback.tcl, not a generic
physical-memory poking tool.
"""

from __future__ import annotations

import argparse
import json
import mmap
import os
import struct
from pathlib import Path
from typing import Protocol


MMIO_BASE = 0xA0010000
MAP_SIZE = 0x1000
GPIO_DATA = 0x0000
GPIO2_DATA = 0x0008
VECTORS = (
    0x00000000,
    0x00000001,
    0x00000007,
    0x12345678,
    0xFFFFFFFE,
    0xFFFFFFFF,
)


def expected_result(value: int) -> int:
    return (value + 1) & 0xFFFFFFFF


class Transport(Protocol):
    def write32(self, offset: int, value: int) -> None: ...
    def read32(self, offset: int) -> int: ...
    def close(self) -> None: ...


class DryRunTransport:
    def __init__(self) -> None:
        self._value = 0

    def write32(self, offset: int, value: int) -> None:
        if offset != GPIO_DATA:
            raise ValueError(f"unexpected dry-run write offset 0x{offset:x}")
        self._value = value & 0xFFFFFFFF

    def read32(self, offset: int) -> int:
        if offset != GPIO2_DATA:
            raise ValueError(f"unexpected dry-run read offset 0x{offset:x}")
        return expected_result(self._value)

    def close(self) -> None:
        pass


class DevMemTransport:
    def __init__(self, device: Path) -> None:
        if MMIO_BASE % mmap.PAGESIZE:
            raise ValueError(
                f"frozen MMIO base 0x{MMIO_BASE:x} must be page aligned "
                f"for page size 0x{mmap.PAGESIZE:x}"
            )
        self._fd = os.open(device, os.O_RDWR | os.O_SYNC)
        try:
            self._map = mmap.mmap(
                self._fd,
                MAP_SIZE,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=MMIO_BASE,
            )
        except Exception:
            os.close(self._fd)
            raise

    def write32(self, offset: int, value: int) -> None:
        struct.pack_into("<I", self._map, offset, value & 0xFFFFFFFF)

    def read32(self, offset: int) -> int:
        return struct.unpack_from("<I", self._map, offset)[0]

    def close(self) -> None:
        self._map.close()
        os.close(self._fd)


def run(transport: Transport, rounds: int) -> list[dict[str, int]]:
    trace: list[dict[str, int]] = []
    for round_index in range(rounds):
        for value in VECTORS:
            expected = expected_result(value)
            transport.write32(GPIO_DATA, value)
            observed = transport.read32(GPIO2_DATA)
            trace.append(
                {
                    "round": round_index,
                    "write": value,
                    "expected": expected,
                    "read": observed,
                }
            )
            print(
                f"ROUND={round_index} "
                f"WRITE=0x{value:08x} "
                f"EXPECTED=0x{expected:08x} "
                f"READ=0x{observed:08x}"
            )
            if observed != expected:
                raise AssertionError(
                    f"write 0x{value:08x}: expected 0x{expected:08x}, "
                    f"read 0x{observed:08x}"
                )
    return trace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=Path, default=Path("/dev/mem"))
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="exercise the semantic oracle without touching physical hardware",
    )
    args = parser.parse_args()

    if args.rounds < 1:
        print("STATUS=FAIL")
        print("ERROR=INVALID_ROUND_COUNT")
        return 2

    print("FPGA_FLYBRAIN_LAB=LAB-HW-06")
    print(f"MMIO_BASE=0x{MMIO_BASE:08x}")
    print(f"GPIO_DATA_OFFSET=0x{GPIO_DATA:04x}")
    print(f"GPIO2_DATA_OFFSET=0x{GPIO2_DATA:04x}")

    transport: Transport
    if args.dry_run:
        print("TRANSPORT=DRY_RUN_MODEL")
        transport = DryRunTransport()
    else:
        print("TRANSPORT=DEVMEM_FIXED_MMIO")
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
            trace = run(transport, args.rounds)
        except AssertionError as exc:
            print("STATUS=FAIL")
            print("ERROR=CORE_BEHAVIOR_MISMATCH")
            print(f"DETAIL={exc}")
            return 8
    finally:
        transport.close()

    if args.json_out:
        payload = {
            "lab_id": "LAB-HW-06",
            "transport": "dry-run" if args.dry_run else "devmem-fixed-mmio",
            "base": MMIO_BASE,
            "gpio_data_offset": GPIO_DATA,
            "gpio2_data_offset": GPIO2_DATA,
            "rounds": args.rounds,
            "semantic_contract": "read=(write+1) mod 2^32",
            "trace": trace,
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"JSON_OUT={args.json_out}")

    print(f"SAMPLE_COUNT={len(trace)}")
    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
