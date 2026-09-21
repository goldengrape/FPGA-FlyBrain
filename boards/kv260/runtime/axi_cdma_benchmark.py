#!/usr/bin/env python3
"""LAB-HW-10 AXI CDMA benchmark: small/scattered vs contiguous transfers.

Physical mode requires:
- KV260 PS/Linux
- LAB-HW-10 bitstream
- /dev/mem for AXI CDMA control registers
- course-approved /dev/udmabuf0 opened with O_SYNC

The result is an end-to-end software-controlled DMA workload observation.
It is not a peak-DDR specification measurement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import os
import platform
import statistics
import struct
import time
from pathlib import Path
from typing import Any, Protocol


LAB_ID = "LAB-HW-10"
PAYLOAD_ID = "shake256-256KiB-v1"
PAYLOAD_SEED = b"FPGA-FlyBrain/LAB-HW-10/axi-cdma-benchmark-v1"

CDMA_BASE = 0xA0020000
CDMA_MAP_BYTES = 0x1000

CDMACR = 0x00
CDMASR = 0x04
SA = 0x18
SA_MSB = 0x1C
DA = 0x20
DA_MSB = 0x24
BTT = 0x28

CDMACR_RESET = 1 << 2
CDMASR_IDLE = 1 << 1
CDMASR_DMA_INT_ERR = 1 << 4
CDMASR_DMA_DEC_ERR = 1 << 5
CDMASR_DMA_SLV_ERR = 1 << 6
CDMASR_IOC_IRQ = 1 << 12
CDMASR_ERR_IRQ = 1 << 14
CDMASR_ERROR_MASK = (
    CDMASR_DMA_INT_ERR
    | CDMASR_DMA_DEC_ERR
    | CDMASR_DMA_SLV_ERR
    | CDMASR_ERR_IRQ
)
CDMASR_CLEAR_MASK = CDMASR_IOC_IRQ | CDMASR_ERR_IRQ

DMA_BUFFER_MIN_BYTES = 2 * 1024 * 1024
SRC_OFFSET = 0
DST_OFFSET = 1 * 1024 * 1024
PAYLOAD_BYTES = 256 * 1024
SMALL_BLOCK_BYTES = 256
SMALL_BLOCK_COUNT = PAYLOAD_BYTES // SMALL_BLOCK_BYTES

WARMUP_RUNS = 5
MEASURED_RUNS = 20
BATCH_COUNT = 2
STABILITY_LIMIT_PCT = 10.0

HP0_DDR_LOW_BASE = 0x00000000
HP0_DDR_LOW_END = 0x80000000

UDMABUF_DEVICE = Path("/dev/udmabuf0")
UDMABUF_SYSFS = Path("/sys/class/u-dma-buf/udmabuf0")
DEVMEM_DEVICE = Path("/dev/mem")


class BenchmarkError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(detail or code)
        self.code = code
        self.detail = detail


class BenchmarkTransport(Protocol):
    buffer_size: int
    physical_base: int | None
    provider_info: dict[str, Any]

    def write_buffer(self, offset: int, data: bytes) -> None: ...
    def read_buffer(self, offset: int, size: int) -> bytes: ...
    def transfer(self, src_offset: int, dst_offset: int, size: int) -> None: ...
    def flush_buffer(self) -> None: ...
    def close(self) -> None: ...


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


def parse_int_text(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value.strip(), 0)
    except ValueError:
        return None


def environment_snapshot() -> dict[str, Any]:
    os_release: dict[str, str] = {}
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os_release[key] = value.strip().strip('"')
    except OSError:
        pass

    return {
        "board_model": read_text(Path("/proc/device-tree/model")),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "os_pretty_name": os_release.get("PRETTY_NAME"),
    }


def validate_kv260_environment(snapshot: dict[str, Any]) -> None:
    model = (snapshot.get("board_model") or "").lower()
    if "kv260" not in model and "kria" not in model:
        raise BenchmarkError(
            "NOT_KV260_RUNTIME_ENVIRONMENT",
            f"board_model={snapshot.get('board_model')!r}",
        )


def payload_bytes() -> bytes:
    return hashlib.shake_256(PAYLOAD_SEED).digest(PAYLOAD_BYTES)


def scattered_block_order() -> list[int]:
    order = [((257 * i) + 17) % SMALL_BLOCK_COUNT for i in range(SMALL_BLOCK_COUNT)]
    if len(set(order)) != SMALL_BLOCK_COUNT:
        raise RuntimeError("scattered permutation is not one-to-one")
    return order


def _u32_read(mm: mmap.mmap, offset: int) -> int:
    return struct.unpack_from("<I", mm, offset)[0]


def _u32_write(mm: mmap.mmap, offset: int, value: int) -> None:
    struct.pack_into("<I", mm, offset, value & 0xFFFFFFFF)


class DryRunTransport:
    def __init__(self) -> None:
        self.buffer = bytearray(DMA_BUFFER_MIN_BYTES)
        self.buffer_size = len(self.buffer)
        self.physical_base = None
        self.provider_info = {
            "provider": "dry-run-bytearray",
            "open_flags": None,
            "cache_contract": "not-applicable",
        }

    def write_buffer(self, offset: int, data: bytes) -> None:
        self.buffer[offset : offset + len(data)] = data

    def read_buffer(self, offset: int, size: int) -> bytes:
        return bytes(self.buffer[offset : offset + size])

    def transfer(self, src_offset: int, dst_offset: int, size: int) -> None:
        self.buffer[dst_offset : dst_offset + size] = self.buffer[
            src_offset : src_offset + size
        ]

    def flush_buffer(self) -> None:
        pass

    def close(self) -> None:
        pass


class PhysicalTransport:
    def __init__(
        self,
        udmabuf_device: Path = UDMABUF_DEVICE,
        udmabuf_sysfs: Path = UDMABUF_SYSFS,
        devmem_device: Path = DEVMEM_DEVICE,
        timeout_seconds: float = 2.0,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        if not udmabuf_device.exists():
            raise BenchmarkError("DMA_BUFFER_DEVICE_MISSING", str(udmabuf_device))
        if not udmabuf_sysfs.exists():
            raise BenchmarkError("DMA_BUFFER_SYSFS_MISSING", str(udmabuf_sysfs))
        if not devmem_device.exists():
            raise BenchmarkError("TRANSPORT_DEVICE_MISSING", str(devmem_device))
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            raise BenchmarkError("TRANSPORT_REQUIRES_ROOT", "physical mode needs /dev/mem")

        phys_addr = parse_int_text(read_text(udmabuf_sysfs / "phys_addr"))
        size = parse_int_text(read_text(udmabuf_sysfs / "size"))
        if phys_addr is None:
            raise BenchmarkError("DMA_BUFFER_PHYS_ADDR_MISSING", str(udmabuf_sysfs))
        if size is None:
            raise BenchmarkError("DMA_BUFFER_SIZE_MISSING", str(udmabuf_sysfs))
        if size < DMA_BUFFER_MIN_BYTES:
            raise BenchmarkError(
                "DMA_BUFFER_TOO_SMALL",
                f"size={size} required={DMA_BUFFER_MIN_BYTES}",
            )
        if not (
            HP0_DDR_LOW_BASE <= phys_addr
            and phys_addr + DMA_BUFFER_MIN_BYTES <= HP0_DDR_LOW_END
        ):
            raise BenchmarkError(
                "DMA_BUFFER_OUTSIDE_HP0_DDR_LOW",
                f"phys_addr=0x{phys_addr:x} size={size}",
            )

        self.buffer_size = size
        self.physical_base = phys_addr
        self.provider_info = {
            "provider": "u-dma-buf",
            "device": str(udmabuf_device),
            "sysfs": str(udmabuf_sysfs),
            "phys_addr": phys_addr,
            "size": size,
            "open_flags": "O_RDWR|O_SYNC",
            "cache_contract": "noncoherent-hp0-buffer-opened-o-sync",
            "dma_coherent": read_text(udmabuf_sysfs / "dma_coherent"),
            "sync_mode": read_text(udmabuf_sysfs / "sync_mode"),
            "sync_owner": read_text(udmabuf_sysfs / "sync_owner"),
        }

        self._buf_fd = -1
        self._mem_fd = -1
        self._buffer: mmap.mmap | None = None
        self._regs: mmap.mmap | None = None

        try:
            self._buf_fd = os.open(
                udmabuf_device, os.O_RDWR | getattr(os, "O_SYNC", 0)
            )
            self._buffer = mmap.mmap(
                self._buf_fd,
                DMA_BUFFER_MIN_BYTES,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=0,
            )

            self._mem_fd = os.open(
                devmem_device, os.O_RDWR | getattr(os, "O_SYNC", 0)
            )
            self._regs = mmap.mmap(
                self._mem_fd,
                CDMA_MAP_BYTES,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=CDMA_BASE,
            )
        except PermissionError as exc:
            self.close()
            raise BenchmarkError("TRANSPORT_PERMISSION_OR_POLICY", str(exc)) from exc
        except OSError as exc:
            self.close()
            raise BenchmarkError("TRANSPORT_MMAP_FAILED", str(exc)) from exc

        self._reset_cdma()

    @property
    def _buffer_mm(self) -> mmap.mmap:
        if self._buffer is None:
            raise BenchmarkError("TRANSPORT_CLOSED")
        return self._buffer

    @property
    def _regs_mm(self) -> mmap.mmap:
        if self._regs is None:
            raise BenchmarkError("TRANSPORT_CLOSED")
        return self._regs

    def _status(self) -> int:
        return _u32_read(self._regs_mm, CDMASR)

    def _check_status_error(self, status: int) -> None:
        if status & CDMASR_ERROR_MASK:
            raise BenchmarkError("CDMA_ERROR", f"CDMASR=0x{status:08x}")

    def _wait_idle(self) -> None:
        deadline = time.monotonic() + self.timeout_seconds
        last = 0
        while time.monotonic() < deadline:
            last = self._status()
            self._check_status_error(last)
            if last & CDMASR_IDLE:
                return
            time.sleep(0.00001)
        raise BenchmarkError("CDMA_TIMEOUT", f"last_CDMASR=0x{last:08x}")

    def _reset_cdma(self) -> None:
        _u32_write(self._regs_mm, CDMACR, CDMACR_RESET)
        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            if (_u32_read(self._regs_mm, CDMACR) & CDMACR_RESET) == 0:
                break
            time.sleep(0.00001)
        else:
            raise BenchmarkError("CDMA_RESET_TIMEOUT")
        self._wait_idle()
        _u32_write(self._regs_mm, CDMASR, CDMASR_CLEAR_MASK)

    def write_buffer(self, offset: int, data: bytes) -> None:
        self._buffer_mm[offset : offset + len(data)] = data

    def read_buffer(self, offset: int, size: int) -> bytes:
        return bytes(self._buffer_mm[offset : offset + size])

    def flush_buffer(self) -> None:
        try:
            self._buffer_mm.flush()
        except (BufferError, OSError, ValueError):
            pass

    def transfer(self, src_offset: int, dst_offset: int, size: int) -> None:
        if size <= 0:
            raise BenchmarkError("INVALID_TRANSFER_SIZE", str(size))
        if src_offset % 16 or dst_offset % 16 or size % 16:
            raise BenchmarkError(
                "UNALIGNED_TRANSFER",
                f"src={src_offset} dst={dst_offset} size={size}",
            )
        if src_offset + size > DMA_BUFFER_MIN_BYTES:
            raise BenchmarkError("SOURCE_OUT_OF_RANGE")
        if dst_offset + size > DMA_BUFFER_MIN_BYTES:
            raise BenchmarkError("DESTINATION_OUT_OF_RANGE")

        self._wait_idle()
        _u32_write(self._regs_mm, CDMASR, CDMASR_CLEAR_MASK)

        assert self.physical_base is not None
        src_addr = self.physical_base + src_offset
        dst_addr = self.physical_base + dst_offset

        _u32_write(self._regs_mm, SA, src_addr & 0xFFFFFFFF)
        _u32_write(self._regs_mm, SA_MSB, (src_addr >> 32) & 0xFFFFFFFF)
        _u32_write(self._regs_mm, DA, dst_addr & 0xFFFFFFFF)
        _u32_write(self._regs_mm, DA_MSB, (dst_addr >> 32) & 0xFFFFFFFF)
        _u32_write(self._regs_mm, BTT, size)
        self._wait_idle()

    def close(self) -> None:
        if self._regs is not None:
            try:
                self._regs.close()
            finally:
                self._regs = None
        if self._buffer is not None:
            try:
                self._buffer.close()
            finally:
                self._buffer = None
        if self._mem_fd >= 0:
            os.close(self._mem_fd)
            self._mem_fd = -1
        if self._buf_fd >= 0:
            os.close(self._buf_fd)
            self._buf_fd = -1


def execute_pattern(transport: BenchmarkTransport, pattern: str) -> None:
    if pattern == "contiguous":
        transport.transfer(SRC_OFFSET, DST_OFFSET, PAYLOAD_BYTES)
        return
    if pattern == "scattered":
        for block in scattered_block_order():
            offset = block * SMALL_BLOCK_BYTES
            transport.transfer(
                SRC_OFFSET + offset,
                DST_OFFSET + offset,
                SMALL_BLOCK_BYTES,
            )
        return
    raise ValueError(f"unknown pattern {pattern}")


def integrity_check(
    transport: BenchmarkTransport,
    pattern: str,
    expected: bytes,
    inject_corruption: bool = False,
) -> tuple[bool, str, str, int | None]:
    transport.write_buffer(SRC_OFFSET, expected)
    transport.write_buffer(DST_OFFSET, bytes(PAYLOAD_BYTES))
    transport.flush_buffer()

    execute_pattern(transport, pattern)

    if inject_corruption:
        observed0 = transport.read_buffer(DST_OFFSET, PAYLOAD_BYTES)
        modified = bytearray(observed0)
        modified[12345] ^= 0x01
        transport.write_buffer(DST_OFFSET, bytes(modified))
        transport.flush_buffer()

    observed = transport.read_buffer(DST_OFFSET, PAYLOAD_BYTES)
    expected_hash = hashlib.sha256(expected).hexdigest()
    observed_hash = hashlib.sha256(observed).hexdigest()

    mismatch = None
    if observed != expected:
        for i, (a, b) in enumerate(zip(expected, observed)):
            if a != b:
                mismatch = i
                break
    return observed == expected and expected_hash == observed_hash, expected_hash, observed_hash, mismatch


def synthetic_elapsed_ns(pattern: str, batch: int, repetition: int, unstable: bool) -> int:
    base = 700_000 if pattern == "contiguous" else 9_000_000
    jitter_permille = ((batch * 11 + repetition * 7 + (3 if pattern == "scattered" else 0)) % 19) - 9
    value = base * (1000 + jitter_permille) // 1000
    if unstable and batch == 1 and pattern == "scattered":
        value = value * 125 // 100
    return int(value)


def timed_pattern(
    transport: BenchmarkTransport,
    pattern: str,
    *,
    dry_run: bool,
    batch: int,
    repetition: int,
    unstable_for_test: bool,
) -> int:
    if dry_run:
        execute_pattern(transport, pattern)
        return synthetic_elapsed_ns(pattern, batch, repetition, unstable_for_test)

    start = time.perf_counter_ns()
    execute_pattern(transport, pattern)
    return time.perf_counter_ns() - start


def summarize(samples: list[int], byte_count: int) -> dict[str, Any]:
    median_ns = int(statistics.median(samples))
    min_ns = min(samples)
    max_ns = max(samples)
    median_mib_s = (byte_count / (1024 * 1024)) / (median_ns / 1_000_000_000)
    return {
        "samples_ns": samples,
        "median_ns": median_ns,
        "min_ns": min_ns,
        "max_ns": max_ns,
        "median_mib_per_s": median_mib_s,
    }


def stability_pct(a: int, b: int) -> float:
    denom = max(a, b)
    if denom <= 0:
        return 100.0
    return abs(a - b) / denom * 100.0


def print_batch(pattern: str, batch_index: int, summary: dict[str, Any]) -> None:
    prefix = pattern.upper()
    print(f"{prefix}_BATCH={batch_index + 1}")
    print(
        f"{prefix}_BATCH_{batch_index + 1}_SAMPLES_NS="
        + ",".join(str(x) for x in summary["samples_ns"])
    )
    print(f"{prefix}_BATCH_{batch_index + 1}_MEDIAN_NS={summary['median_ns']}")
    print(f"{prefix}_BATCH_{batch_index + 1}_MIN_NS={summary['min_ns']}")
    print(f"{prefix}_BATCH_{batch_index + 1}_MAX_NS={summary['max_ns']}")
    print(
        f"{prefix}_BATCH_{batch_index + 1}_MEDIAN_MIB_PER_S="
        f"{summary['median_mib_per_s']:.3f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--physical", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=2.0)
    parser.add_argument(
        "--inject-corruption-for-test",
        action="store_true",
        help="dry-run only: corrupt precheck destination",
    )
    parser.add_argument(
        "--unstable-for-test",
        action="store_true",
        help="dry-run only: force batch instability",
    )
    args = parser.parse_args()

    if args.timeout_seconds <= 0:
        print("STATUS=FAIL")
        print("ERROR=INVALID_TIMEOUT")
        return 2
    if args.physical and (args.inject_corruption_for_test or args.unstable_for_test):
        print("STATUS=FAIL")
        print("ERROR=TEST_INJECTION_NOT_ALLOWED_PHYSICAL")
        return 3

    snapshot = environment_snapshot()
    print(f"FPGA_FLYBRAIN_LAB={LAB_ID}")
    print(f"MODE={'PHYSICAL_KV260_AXI_CDMA' if args.physical else 'DRY_RUN_CDMA_MODEL'}")
    print(f"PAYLOAD_ID={PAYLOAD_ID}")
    print(f"CDMA_CONTROL_BASE=0x{CDMA_BASE:08x}")
    print("PL_DDR_PORT=S_AXI_HP0_FPD")
    print("PL_DDR_COHERENCY=NON_COHERENT")
    print(f"DMA_BUFFER_MIN_BYTES={DMA_BUFFER_MIN_BYTES}")
    print(f"SRC_OFFSET={SRC_OFFSET}")
    print(f"DST_OFFSET={DST_OFFSET}")
    print(f"PAYLOAD_BYTES={PAYLOAD_BYTES}")
    print(f"SMALL_BLOCK_BYTES={SMALL_BLOCK_BYTES}")
    print(f"SMALL_BLOCK_COUNT={SMALL_BLOCK_COUNT}")
    print("SCATTER_PERMUTATION=block=(257*i+17) mod 1024")
    print(f"WARMUP_RUNS={WARMUP_RUNS}")
    print(f"MEASURED_RUNS={MEASURED_RUNS}")
    print(f"BATCH_COUNT={BATCH_COUNT}")
    print(f"STABILITY_LIMIT_PCT={STABILITY_LIMIT_PCT:.1f}")
    print("TIMER_SCOPE=PYTHON_MMIO_PROGRAMMING_POLLING_PLUS_DMA_COMPLETION")
    print("BANDWIDTH_SCOPE=END_TO_END_SOFTWARE_CONTROLLED_DMA_WORKLOAD")
    print(f"HELPER_SHA256={sha256_file(Path(__file__).resolve())}")
    print(f"ENV_BOARD_MODEL={snapshot.get('board_model')}")
    print(f"ENV_KERNEL={snapshot.get('kernel')}")
    print(f"ENV_MACHINE={snapshot.get('machine')}")
    print(f"ENV_OS_PRETTY_NAME={snapshot.get('os_pretty_name')}")

    transport: BenchmarkTransport
    try:
        if args.physical:
            validate_kv260_environment(snapshot)
            transport = PhysicalTransport(timeout_seconds=args.timeout_seconds)
        else:
            transport = DryRunTransport()
    except BenchmarkError as exc:
        print("STATUS=FAIL")
        print(f"ERROR={exc.code}")
        if exc.detail:
            print(f"DETAIL={exc.detail}")
        return 4

    expected = payload_bytes()
    payload_hash = hashlib.sha256(expected).hexdigest()
    print(f"PAYLOAD_SHA256={payload_hash}")
    print("BUFFER_PROVIDER=" + str(transport.provider_info.get("provider")))
    if transport.physical_base is not None:
        print(f"DMA_BUFFER_PHYS_BASE=0x{transport.physical_base:x}")
    print(f"DMA_BUFFER_SIZE={transport.buffer_size}")
    print("DMA_BUFFER_OPEN_FLAGS=" + str(transport.provider_info.get("open_flags")))
    print("DMA_BUFFER_CACHE_CONTRACT=" + str(transport.provider_info.get("cache_contract")))

    result: dict[str, Any] = {
        "lab_id": LAB_ID,
        "mode": "physical" if args.physical else "dry-run",
        "environment": snapshot,
        "payload_id": PAYLOAD_ID,
        "payload_sha256": payload_hash,
        "cdma_control_base": CDMA_BASE,
        "pl_ddr_port": "S_AXI_HP0_FPD",
        "pl_ddr_coherency": "non-coherent",
        "provider": transport.provider_info,
        "workload": {
            "dma_buffer_min_bytes": DMA_BUFFER_MIN_BYTES,
            "src_offset": SRC_OFFSET,
            "dst_offset": DST_OFFSET,
            "payload_bytes": PAYLOAD_BYTES,
            "small_block_bytes": SMALL_BLOCK_BYTES,
            "small_block_count": SMALL_BLOCK_COUNT,
            "scattered_permutation": "block=(257*i+17) mod 1024",
            "warmup_runs": WARMUP_RUNS,
            "measured_runs": MEASURED_RUNS,
            "batch_count": BATCH_COUNT,
            "stability_limit_pct": STABILITY_LIMIT_PCT,
            "timer_scope": "python-mmio-programming-polling-plus-dma-completion",
        },
        "patterns": {},
    }

    try:
        for pattern in ("contiguous", "scattered"):
            ok, expected_hash, observed_hash, mismatch = integrity_check(
                transport,
                pattern,
                expected,
                inject_corruption=(
                    args.dry_run
                    and args.inject_corruption_for_test
                    and pattern == "contiguous"
                ),
            )
            print(f"PRECHECK_PATTERN={pattern}")
            print(f"PRECHECK_EXPECTED_SHA256={expected_hash}")
            print(f"PRECHECK_OBSERVED_SHA256={observed_hash}")
            if not ok:
                print("INTEGRITY=FAIL")
                print("PERFORMANCE_CONCLUSION_ALLOWED=0")
                print("ERROR=BENCHMARK_INTEGRITY_MISMATCH")
                if mismatch is not None:
                    print(f"FIRST_MISMATCH_OFFSET={mismatch}")
                result["integrity_pass"] = False
                result["performance_conclusion_allowed"] = False
                result["failed_pattern"] = pattern
                result["first_mismatch_offset"] = mismatch
                if args.json_out:
                    args.json_out.write_text(
                        json.dumps(result, indent=2) + "\n", encoding="utf-8"
                    )
                    print(f"JSON_OUT={args.json_out}")
                print("STATUS=FAIL")
                return 5

        result["integrity_pass"] = True
        print("PRECHECK_INTEGRITY=PASS")

        pattern_batches: dict[str, list[dict[str, Any]]] = {
            "contiguous": [],
            "scattered": [],
        }

        batch_orders = (
            ("scattered", "contiguous"),
            ("contiguous", "scattered"),
        )

        for batch_index in range(BATCH_COUNT):
            print(f"BATCH_ORDER_{batch_index + 1}=" + ",".join(batch_orders[batch_index]))
            for pattern in batch_orders[batch_index]:
                for warmup in range(WARMUP_RUNS):
                    timed_pattern(
                        transport,
                        pattern,
                        dry_run=args.dry_run,
                        batch=batch_index,
                        repetition=-(warmup + 1),
                        unstable_for_test=args.unstable_for_test,
                    )

                samples = [
                    timed_pattern(
                        transport,
                        pattern,
                        dry_run=args.dry_run,
                        batch=batch_index,
                        repetition=repetition,
                        unstable_for_test=args.unstable_for_test,
                    )
                    for repetition in range(MEASURED_RUNS)
                ]
                summary = summarize(samples, PAYLOAD_BYTES)
                pattern_batches[pattern].append(summary)
                print_batch(pattern, batch_index, summary)

                observed = transport.read_buffer(DST_OFFSET, PAYLOAD_BYTES)
                post_ok = observed == expected
                post_hash = hashlib.sha256(observed).hexdigest()
                print(
                    f"{pattern.upper()}_BATCH_{batch_index + 1}_POSTCHECK="
                    + ("PASS" if post_ok else "FAIL")
                )
                print(
                    f"{pattern.upper()}_BATCH_{batch_index + 1}_POST_SHA256={post_hash}"
                )
                if not post_ok:
                    print("PERFORMANCE_CONCLUSION_ALLOWED=0")
                    print("ERROR=POST_BENCHMARK_INTEGRITY_MISMATCH")
                    result["patterns"] = pattern_batches
                    result["performance_conclusion_allowed"] = False
                    if args.json_out:
                        args.json_out.write_text(
                            json.dumps(result, indent=2) + "\n", encoding="utf-8"
                        )
                        print(f"JSON_OUT={args.json_out}")
                    print("STATUS=FAIL")
                    return 6

        stability: dict[str, float] = {}
        stable = True
        for pattern in ("contiguous", "scattered"):
            b0, b1 = pattern_batches[pattern]
            pct = stability_pct(b0["median_ns"], b1["median_ns"])
            stability[pattern] = pct
            print(f"{pattern.upper()}_BATCH_MEDIAN_DIFFERENCE_PCT={pct:.3f}")
            pattern_stable = pct <= STABILITY_LIMIT_PCT
            print(
                f"{pattern.upper()}_STABLE="
                + ("1" if pattern_stable else "0")
            )
            stable = stable and pattern_stable

        result["patterns"] = pattern_batches
        result["stability_pct"] = stability
        result["measurement_stable"] = stable

        if not stable:
            result["performance_conclusion_allowed"] = False
            print("MEASUREMENT_STABLE=0")
            print("PERFORMANCE_CONCLUSION_ALLOWED=0")
            print("ERROR=MEASUREMENT_UNSTABLE")
            if args.json_out:
                args.json_out.write_text(
                    json.dumps(result, indent=2) + "\n", encoding="utf-8"
                )
                print(f"JSON_OUT={args.json_out}")
            print("STATUS=FAIL")
            return 7

        contiguous_median = statistics.median(
            [
                batch["median_ns"]
                for batch in pattern_batches["contiguous"]
            ]
        )
        scattered_median = statistics.median(
            [
                batch["median_ns"]
                for batch in pattern_batches["scattered"]
            ]
        )
        ratio = scattered_median / contiguous_median
        result["performance_conclusion_allowed"] = True
        result["contiguous_scattered_median_time_ratio"] = ratio

        print("MEASUREMENT_STABLE=1")
        print("PERFORMANCE_CONCLUSION_ALLOWED=1")
        print(f"SCATTERED_TO_CONTIGUOUS_MEDIAN_TIME_RATIO={ratio:.6f}")
        print("INTEGRITY=PASS")

        if args.json_out:
            args.json_out.write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            print(f"JSON_OUT={args.json_out}")

        print("STATUS=PASS")
        return 0

    except BenchmarkError as exc:
        print("PERFORMANCE_CONCLUSION_ALLOWED=0")
        print("STATUS=FAIL")
        print(f"ERROR={exc.code}")
        if exc.detail:
            print(f"DETAIL={exc.detail}")
        return 8
    finally:
        transport.close()


if __name__ == "__main__":
    raise SystemExit(main())
