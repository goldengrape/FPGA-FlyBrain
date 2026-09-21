#!/usr/bin/env python3
"""LAB-HW-10 Ubuntu/u-dma-buf prerequisite preflight.

Dry-run validates the checker itself. Physical mode must run on the KV260
runtime host and intentionally does not install or reconfigure the kernel.
"""

from __future__ import annotations

import argparse
import json
import mmap
import os
import platform
import sys
from pathlib import Path

LAB_ID = "LAB-HW-10-PREREQ"
UPSTREAM_COMMIT = "15bcde3cb960321e99983e227aeacc5807888333"
DRIVER_VERSION = "5.5.0"
DMA_BUFFER_MIN_BYTES = 2 * 1024 * 1024
COURSE_BUFFER_BYTES = 4 * 1024 * 1024
HP0_DDR_LOW_BASE = 0x00000000
HP0_DDR_LOW_END = 0x80000000
ALLOWED_SYNC_MODES = {1, 2}

UDMABUF_DEVICE = Path("/dev/udmabuf0")
UDMABUF_SYSFS = Path("/sys/class/u-dma-buf/udmabuf0")
DEVMEM_DEVICE = Path("/dev/mem")
MODULE_SYSFS = Path("/sys/module/u_dma_buf")
BOARD_MODEL = Path("/proc/device-tree/model")


class PreflightError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip("\x00\n ")
    except (OSError, UnicodeError):
        return None


def parse_int_text(text: str | None) -> int | None:
    if text is None:
        return None
    try:
        return int(text.strip(), 0)
    except ValueError:
        return None


def _physical_payload() -> dict[str, object]:
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        raise PreflightError(
            "PREFLIGHT_REQUIRES_ROOT",
            "run physical preflight with sudo so device open/mmap policy is tested",
        )

    model = read_text(BOARD_MODEL)
    if not model or ("Kria" not in model and "KV260" not in model):
        raise PreflightError("NOT_KV260_RUNTIME_ENVIRONMENT", str(model))

    machine = platform.machine()
    if machine not in {"aarch64", "arm64"}:
        raise PreflightError("UNEXPECTED_RUNTIME_ARCH", machine)

    if not MODULE_SYSFS.exists():
        raise PreflightError("U_DMA_BUF_MODULE_NOT_LOADED", str(MODULE_SYSFS))
    if not UDMABUF_DEVICE.exists():
        raise PreflightError("DMA_BUFFER_DEVICE_MISSING", str(UDMABUF_DEVICE))
    if not UDMABUF_SYSFS.exists():
        raise PreflightError("DMA_BUFFER_SYSFS_MISSING", str(UDMABUF_SYSFS))
    if not DEVMEM_DEVICE.exists():
        raise PreflightError("TRANSPORT_DEVICE_MISSING", str(DEVMEM_DEVICE))

    phys_addr = parse_int_text(read_text(UDMABUF_SYSFS / "phys_addr"))
    size = parse_int_text(read_text(UDMABUF_SYSFS / "size"))
    sync_mode = parse_int_text(read_text(UDMABUF_SYSFS / "sync_mode"))
    dma_coherent = parse_int_text(read_text(UDMABUF_SYSFS / "dma_coherent"))

    if phys_addr is None:
        raise PreflightError("DMA_BUFFER_PHYS_ADDR_MISSING", str(UDMABUF_SYSFS))
    if size is None:
        raise PreflightError("DMA_BUFFER_SIZE_MISSING", str(UDMABUF_SYSFS))
    if size < DMA_BUFFER_MIN_BYTES:
        raise PreflightError(
            "DMA_BUFFER_TOO_SMALL",
            f"size={size} required={DMA_BUFFER_MIN_BYTES}",
        )
    if sync_mode is None:
        raise PreflightError("DMA_BUFFER_SYNC_MODE_MISSING", str(UDMABUF_SYSFS))
    if sync_mode not in ALLOWED_SYNC_MODES:
        raise PreflightError(
            "DMA_BUFFER_UNSAFE_SYNC_MODE",
            f"sync_mode={sync_mode} allowed={sorted(ALLOWED_SYNC_MODES)}",
        )
    if not (
        HP0_DDR_LOW_BASE <= phys_addr
        and phys_addr + DMA_BUFFER_MIN_BYTES <= HP0_DDR_LOW_END
    ):
        raise PreflightError(
            "DMA_BUFFER_OUTSIDE_HP0_DDR_LOW",
            f"phys_addr=0x{phys_addr:x} required_window={DMA_BUFFER_MIN_BYTES}",
        )

    buf_fd = -1
    buf_map: mmap.mmap | None = None
    mem_fd = -1
    try:
        buf_fd = os.open(UDMABUF_DEVICE, os.O_RDWR | getattr(os, "O_SYNC", 0))
        buf_map = mmap.mmap(
            buf_fd,
            min(mmap.PAGESIZE, size),
            flags=mmap.MAP_SHARED,
            prot=mmap.PROT_READ | mmap.PROT_WRITE,
            offset=0,
        )
        mem_fd = os.open(DEVMEM_DEVICE, os.O_RDWR | getattr(os, "O_SYNC", 0))
    except PermissionError as exc:
        raise PreflightError("TRANSPORT_PERMISSION_OR_POLICY", str(exc)) from exc
    except OSError as exc:
        raise PreflightError("TRANSPORT_OPEN_OR_MMAP_FAILED", str(exc)) from exc
    finally:
        if buf_map is not None:
            buf_map.close()
        if buf_fd >= 0:
            os.close(buf_fd)
        if mem_fd >= 0:
            os.close(mem_fd)

    return {
        "lab_id": LAB_ID,
        "mode": "PHYSICAL_KV260_UDMABUF_PREFLIGHT",
        "board_model": model,
        "machine": machine,
        "kernel_release": platform.release(),
        "provider": "u-dma-buf",
        "expected_upstream_commit": UPSTREAM_COMMIT,
        "expected_driver_version": DRIVER_VERSION,
        "device": str(UDMABUF_DEVICE),
        "sysfs": str(UDMABUF_SYSFS),
        "physical_base": phys_addr,
        "size": size,
        "sync_mode": sync_mode,
        "dma_coherent": dma_coherent,
        "open_flags": "O_RDWR|O_SYNC",
        "minimum_bytes": DMA_BUFFER_MIN_BYTES,
        "course_buffer_bytes": COURSE_BUFFER_BYTES,
        "hp0_ddr_low_base": HP0_DDR_LOW_BASE,
        "hp0_ddr_low_end_exclusive": HP0_DDR_LOW_END,
        "module_loaded": True,
        "devmem_open": True,
        "status": "PASS",
    }


def _dry_run_payload() -> dict[str, object]:
    return {
        "lab_id": LAB_ID,
        "mode": "DRY_RUN_PREFLIGHT_MODEL",
        "board_model": "AMD Kria KV260 Vision AI Starter Kit (synthetic)",
        "machine": "aarch64",
        "kernel_release": "synthetic",
        "provider": "u-dma-buf",
        "expected_upstream_commit": UPSTREAM_COMMIT,
        "expected_driver_version": DRIVER_VERSION,
        "device": str(UDMABUF_DEVICE),
        "sysfs": str(UDMABUF_SYSFS),
        "physical_base": 0x10000000,
        "size": COURSE_BUFFER_BYTES,
        "sync_mode": 1,
        "dma_coherent": 0,
        "open_flags": "O_RDWR|O_SYNC",
        "minimum_bytes": DMA_BUFFER_MIN_BYTES,
        "course_buffer_bytes": COURSE_BUFFER_BYTES,
        "hp0_ddr_low_base": HP0_DDR_LOW_BASE,
        "hp0_ddr_low_end_exclusive": HP0_DDR_LOW_END,
        "module_loaded": True,
        "devmem_open": True,
        "status": "PASS",
    }


def emit(payload: dict[str, object]) -> None:
    print(f"FPGA_FLYBRAIN_LAB={payload['lab_id']}")
    print(f"MODE={payload['mode']}")
    print(f"BUFFER_PROVIDER={payload['provider']}")
    print(f"EXPECTED_UDMABUF_COMMIT={payload['expected_upstream_commit']}")
    print(f"EXPECTED_UDMABUF_DRIVER_VERSION={payload['expected_driver_version']}")
    print(f"DMA_BUFFER_MIN_BYTES={payload['minimum_bytes']}")
    print(f"COURSE_BUFFER_BYTES={payload['course_buffer_bytes']}")
    print(f"DMA_BUFFER_PHYS_BASE=0x{int(payload['physical_base']):x}")
    print(f"DMA_BUFFER_SIZE={payload['size']}")
    print(f"DMA_BUFFER_SYNC_MODE={payload['sync_mode']}")
    print(f"DMA_BUFFER_DMA_COHERENT={payload['dma_coherent']}")
    print(f"DMA_BUFFER_OPEN_FLAGS={payload['open_flags']}")
    print("HP0_DDR_LOW=0x00000000..0x80000000(end-exclusive)")
    print(f"STATUS={payload['status']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--physical", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    try:
        payload = _physical_payload() if args.physical else _dry_run_payload()
        emit(payload)
        if args.json_out:
            args.json_out.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        return 0
    except PreflightError as exc:
        payload = {
            "lab_id": LAB_ID,
            "mode": "PHYSICAL_KV260_UDMABUF_PREFLIGHT" if args.physical else "DRY_RUN_PREFLIGHT_MODEL",
            "error": exc.code,
            "detail": exc.detail,
            "status": "FAIL",
        }
        print(f"FPGA_FLYBRAIN_LAB={LAB_ID}")
        print(f"ERROR={exc.code}")
        print(f"DETAIL={exc.detail}")
        print("STATUS=FAIL")
        if args.json_out:
            args.json_out.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        return 3


if __name__ == "__main__":
    sys.exit(main())
