#!/usr/bin/env python3
"""LAB-HW-09 PS/Linux-managed DDR integrity sanity check.

Physical mode deliberately uses an OS-managed anonymous mapping. It does not
guess or expose a raw physical DDR address, and it does not claim PL/AXI peak
bandwidth. LAB-HW-10 owns the first PL->DDR AXI/burst measurement slice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import os
import platform
import time
from pathlib import Path
from typing import Any


LAB_ID = "LAB-HW-09"
PAYLOAD_ID = "shake256-chunk-index-v1"
PAYLOAD_SEED = b"FPGA-FlyBrain/LAB-HW-09/ddr-integrity-v1"
PHYSICAL_BYTES = 64 * 1024 * 1024
DRY_RUN_BYTES = 4 * 1024 * 1024
CHUNK_BYTES = 1 * 1024 * 1024
ACCESS_PATTERN = "contiguous-sequential-1MiB-chunks"
MIN_PHYSICAL_BOARD_MARKERS = ("kv260", "kria")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip("\x00\n ")
    except OSError:
        return None


def parse_meminfo(path: Path = Path("/proc/meminfo")) -> dict[str, int]:
    out: dict[str, int] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            key, rest = line.split(":", 1)
            fields = rest.strip().split()
            if not fields:
                continue
            try:
                value = int(fields[0])
            except ValueError:
                continue
            out[key] = value
    except OSError:
        pass
    return out


def parse_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            out[key] = value.strip().strip('"')
    except OSError:
        pass
    return out


def make_chunk(chunk_index: int, size: int = CHUNK_BYTES) -> bytes:
    material = PAYLOAD_SEED + chunk_index.to_bytes(8, "little", signed=False)
    return hashlib.shake_256(material).digest(size)


def first_mismatch(expected: bytes, observed: bytes) -> int | None:
    if expected == observed:
        return None
    for i, (a, b) in enumerate(zip(expected, observed)):
        if a != b:
            return i
    if len(expected) != len(observed):
        return min(len(expected), len(observed))
    return None


def mib_per_second(byte_count: int, elapsed_ns: int) -> float:
    if elapsed_ns <= 0:
        return 0.0
    return (byte_count / (1024 * 1024)) / (elapsed_ns / 1_000_000_000)


def prefault(mapping: mmap.mmap, byte_count: int) -> None:
    page = mmap.PAGESIZE
    for offset in range(0, byte_count, page):
        mapping[offset : offset + 1] = b"\x00"


def environment_snapshot() -> dict[str, Any]:
    mem = parse_meminfo()
    os_release = parse_os_release()
    board_model = read_text(Path("/proc/device-tree/model"))
    return {
        "board_model": board_model,
        "kernel": platform.release(),
        "machine": platform.machine(),
        "os_pretty_name": os_release.get("PRETTY_NAME"),
        "mem_total_kib": mem.get("MemTotal"),
        "mem_available_kib": mem.get("MemAvailable"),
        "swap_total_kib": mem.get("SwapTotal"),
        "swap_free_kib": mem.get("SwapFree"),
    }


def validate_physical_environment(snapshot: dict[str, Any]) -> tuple[bool, str]:
    model = (snapshot.get("board_model") or "").lower()
    if not model:
        return False, "missing /proc/device-tree/model"
    if not any(marker in model for marker in MIN_PHYSICAL_BOARD_MARKERS):
        return False, f"unrecognized board model: {snapshot.get('board_model')}"
    return True, ""


def run_integrity(byte_count: int, inject_corruption: bool) -> dict[str, Any]:
    if byte_count % CHUNK_BYTES != 0:
        raise ValueError("byte_count must be a multiple of CHUNK_BYTES")

    chunk_count = byte_count // CHUNK_BYTES
    expected_hash = hashlib.sha256()
    observed_hash = hashlib.sha256()
    write_elapsed_ns = 0
    read_elapsed_ns = 0
    mismatch: dict[str, int] | None = None

    with mmap.mmap(-1, byte_count, access=mmap.ACCESS_WRITE) as mapping:
        prefault(mapping, byte_count)

        for chunk_index in range(chunk_count):
            chunk = make_chunk(chunk_index)
            expected_hash.update(chunk)
            start = time.perf_counter_ns()
            mapping[
                chunk_index * CHUNK_BYTES : (chunk_index + 1) * CHUNK_BYTES
            ] = chunk
            write_elapsed_ns += time.perf_counter_ns() - start

        if inject_corruption:
            corrupt_offset = min(byte_count - 1, (byte_count // 2) + 123)
            old = mapping[corrupt_offset]
            mapping[corrupt_offset : corrupt_offset + 1] = bytes([old ^ 0x01])

        for chunk_index in range(chunk_count):
            start = time.perf_counter_ns()
            observed = mapping[
                chunk_index * CHUNK_BYTES : (chunk_index + 1) * CHUNK_BYTES
            ]
            read_elapsed_ns += time.perf_counter_ns() - start
            observed_hash.update(observed)

            expected = make_chunk(chunk_index)
            local = first_mismatch(expected, observed)
            if local is not None and mismatch is None:
                absolute = chunk_index * CHUNK_BYTES + local
                mismatch = {
                    "chunk_index": chunk_index,
                    "chunk_offset": local,
                    "absolute_offset": absolute,
                    "expected_byte": expected[local],
                    "observed_byte": observed[local],
                }

    return {
        "byte_count": byte_count,
        "chunk_bytes": CHUNK_BYTES,
        "chunk_count": chunk_count,
        "expected_sha256": expected_hash.hexdigest(),
        "observed_sha256": observed_hash.hexdigest(),
        "mismatch": mismatch,
        "write_elapsed_ns": write_elapsed_ns,
        "read_elapsed_ns": read_elapsed_ns,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--physical", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument(
        "--inject-corruption-for-test",
        action="store_true",
        help="dry-run only: flip one byte after write to prove integrity failure",
    )
    args = parser.parse_args()

    if args.physical and args.inject_corruption_for_test:
        print("STATUS=FAIL")
        print("ERROR=INJECTION_NOT_ALLOWED_PHYSICAL")
        return 2

    byte_count = PHYSICAL_BYTES if args.physical else DRY_RUN_BYTES
    snapshot = environment_snapshot()

    print(f"FPGA_FLYBRAIN_LAB={LAB_ID}")
    print(f"MODE={'PHYSICAL_KV260_PS_LINUX' if args.physical else 'DRY_RUN_HOST_MEMORY_MODEL'}")
    print(f"PAYLOAD_ID={PAYLOAD_ID}")
    print(f"TEST_BYTES={byte_count}")
    print(f"CHUNK_BYTES={CHUNK_BYTES}")
    print(f"CHUNK_COUNT={byte_count // CHUNK_BYTES}")
    print(f"ACCESS_PATTERN={ACCESS_PATTERN}")
    print(f"PAGE_BYTES={mmap.PAGESIZE}")
    print(f"HELPER_SHA256={sha256_file(Path(__file__).resolve())}")

    for key in (
        "board_model",
        "kernel",
        "machine",
        "os_pretty_name",
        "mem_total_kib",
        "mem_available_kib",
        "swap_total_kib",
        "swap_free_kib",
    ):
        print(f"ENV_{key.upper()}={snapshot.get(key)}")

    if args.physical:
        ok, detail = validate_physical_environment(snapshot)
        if not ok:
            print("STATUS=FAIL")
            print("ERROR=NOT_KV260_RUNTIME_ENVIRONMENT")
            print(f"DETAIL={detail}")
            return 3

        available_kib = snapshot.get("mem_available_kib")
        if isinstance(available_kib, int) and available_kib * 1024 < byte_count * 2:
            print("STATUS=FAIL")
            print("ERROR=INSUFFICIENT_AVAILABLE_MEMORY")
            print(f"DETAIL=MemAvailable={available_kib} KiB")
            return 4

    try:
        result = run_integrity(byte_count, args.inject_corruption_for_test)
    except (BufferError, MemoryError, OSError, ValueError) as exc:
        print("STATUS=FAIL")
        print("ERROR=MEMORY_TEST_SETUP_FAILED")
        print(f"DETAIL={exc}")
        return 5

    print(f"EXPECTED_SHA256={result['expected_sha256']}")
    print(f"OBSERVED_SHA256={result['observed_sha256']}")

    integrity_ok = (
        result["mismatch"] is None
        and result["expected_sha256"] == result["observed_sha256"]
    )

    payload = {
        "lab_id": LAB_ID,
        "mode": "physical" if args.physical else "dry-run",
        "payload_id": PAYLOAD_ID,
        "access_pattern": ACCESS_PATTERN,
        "environment": snapshot,
        **result,
        "integrity_pass": integrity_ok,
        "performance_blocked": not integrity_ok,
    }

    if not integrity_ok:
        print("INTEGRITY=FAIL")
        print("PERFORMANCE_BLOCKED=1")
        print("ERROR=DDR_INTEGRITY_MISMATCH")
        if result["mismatch"] is not None:
            m = result["mismatch"]
            print(
                "FIRST_MISMATCH="
                f"absolute_offset={m['absolute_offset']} "
                f"chunk_index={m['chunk_index']} "
                f"chunk_offset={m['chunk_offset']} "
                f"expected=0x{m['expected_byte']:02x} "
                f"observed=0x{m['observed_byte']:02x}"
            )
        if args.json_out:
            args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            print(f"JSON_OUT={args.json_out}")
        print("STATUS=FAIL")
        return 6

    write_ns = int(result["write_elapsed_ns"])
    read_ns = int(result["read_elapsed_ns"])
    write_mib_s = mib_per_second(byte_count, write_ns)
    read_mib_s = mib_per_second(byte_count, read_ns)
    payload["write_mib_per_s"] = write_mib_s
    payload["read_mib_per_s"] = read_mib_s

    print("INTEGRITY=PASS")
    print("PERFORMANCE_BLOCKED=0")
    print("TIMER_WRITE_BOUNDARY=chunk payload copy into prefaulted anonymous mapping")
    print("TIMER_READ_BOUNDARY=chunk copy out of anonymous mapping; compare/hash excluded")
    print(f"WRITE_ELAPSED_NS={write_ns}")
    print(f"READ_ELAPSED_NS={read_ns}")
    print(f"HOST_PATH_WRITE_MIB_PER_S={write_mib_s:.3f}")
    print(f"HOST_PATH_READ_MIB_PER_S={read_mib_s:.3f}")
    print("BANDWIDTH_SCOPE=HOST_PATH_OBSERVATION_NOT_PEAK_DDR_OR_PL_AXI")

    if args.json_out:
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"JSON_OUT={args.json_out}")

    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
