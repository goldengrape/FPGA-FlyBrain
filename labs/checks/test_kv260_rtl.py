"""Open-source behavioral checks for the KV260 LAB-HW-03/04 teaching RTL."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
IVERILOG = shutil.which("iverilog")
VVP = shutil.which("vvp")


def _simulate(tmp_path: Path, top: str, rtl: str, tb: str):
    out = tmp_path / top
    compile_result = subprocess.run(
        [
            IVERILOG,
            "-g2012",
            "-s",
            top,
            "-o",
            str(out),
            str(ROOT / rtl),
            str(ROOT / tb),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert compile_result.returncode == 0, compile_result.stderr

    run_result = subprocess.run(
        [VVP, str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert run_result.returncode == 0, run_result.stderr
    return run_result.stdout


@pytest.mark.skipif(IVERILOG is None or VVP is None, reason="Icarus Verilog is not installed")
def test_lab03_marker_rtl(tmp_path):
    stdout = _simulate(
        tmp_path,
        "kv260_marker_top_tb",
        "boards/kv260/rtl/kv260_marker_top.sv",
        "boards/kv260/tb/kv260_marker_top_tb.sv",
    )
    assert "PASS: kv260_marker_top emits 10101" in stdout


@pytest.mark.skipif(IVERILOG is None or VVP is None, reason="Icarus Verilog is not installed")
def test_lab04_blink_core_clock_reset_behavior(tmp_path):
    stdout = _simulate(
        tmp_path,
        "kv260_blink_core_tb",
        "boards/kv260/rtl/kv260_blink_core.sv",
        "boards/kv260/tb/kv260_blink_core_tb.sv",
    )
    assert "PASS: kv260_blink_core clock/reset behavior" in stdout



@pytest.mark.skipif(IVERILOG is None or VVP is None, reason="Icarus Verilog is not installed")
def test_lab06_loopback_transform(tmp_path):
    stdout = _simulate(
        tmp_path,
        "kv260_loopback_transform_tb",
        "boards/kv260/rtl/kv260_loopback_transform.sv",
        "boards/kv260/tb/kv260_loopback_transform_tb.sv",
    )
    assert "PASS: kv260_loopback_transform +1 modulo 2^32" in stdout
