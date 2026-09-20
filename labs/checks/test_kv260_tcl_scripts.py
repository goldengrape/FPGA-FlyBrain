"""Contract and syntax-path tests for the first KV260 Vivado Tcl helpers."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "boards" / "kv260" / "scripts" / "check_vivado.tcl"
DETECT = ROOT / "boards" / "kv260" / "scripts" / "detect_target.tcl"
TCLSH = shutil.which("tclsh")


def _run_tcl(tmp_path: Path, prelude: str, script: Path):
    wrapper = tmp_path / "wrapper.tcl"
    wrapper.write_text(
        prelude + f"\nsource {{{script.as_posix()}}}\n",
        encoding="utf-8",
    )
    return subprocess.run(
        [TCLSH, str(wrapper)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_preflight_script_has_machine_searchable_contract():
    text = CHECK.read_text(encoding="utf-8")
    assert 'set expected_vivado_prefix "2026.1"' in text
    assert "version -short" in text
    assert "get_board_parts -quiet *kv260*" in text
    assert "AUTHORING_BASELINE_MISMATCH" in text
    assert "NO_KV260_BOARD_PART" in text
    assert "STATUS=PASS" in text


def test_target_discovery_script_stops_before_programming():
    text = DETECT.read_text(encoding="utf-8")
    assert "connect_hw_server -url localhost:3121" in text
    assert "get_hw_targets -quiet" in text
    assert "open_hw_target" in text
    assert "get_hw_devices -quiet -of_objects" in text
    assert "NO_KV260_FPGA_DEVICE" in text
    assert "program_hw_device" not in text
    assert "PROGRAM.FILE" not in text


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_check_vivado_success_path_is_valid_tcl(tmp_path):
    result = _run_tcl(
        tmp_path,
        """
proc version {args} { return "2026.1" }
proc get_board_parts {args} {
    return [list "xilinx.com:kv260_som:part0:1.4" "xilinx.com:kv260_carrier:part0:1.3"]
}
""",
        CHECK,
    )
    assert result.returncode == 0, result.stderr
    assert "KV260_BOARD_PART_COUNT=2" in result.stdout
    assert "STATUS=PASS" in result.stdout


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_check_vivado_rejects_wrong_release(tmp_path):
    result = _run_tcl(
        tmp_path,
        """
proc version {args} { return "2025.2" }
proc get_board_parts {args} { return [list "xilinx.com:kv260_som:part0:1.4"] }
""",
        CHECK,
    )
    assert result.returncode == 2
    assert "ERROR=AUTHORING_BASELINE_MISMATCH" in result.stderr


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_check_vivado_rejects_missing_kv260_board_data(tmp_path):
    result = _run_tcl(
        tmp_path,
        """
proc version {args} { return "2026.1" }
proc get_board_parts {args} { return {} }
""",
        CHECK,
    )
    assert result.returncode == 3
    assert "ERROR=NO_KV260_BOARD_PART" in result.stderr


def _detect_prelude(targets: str, devices: str) -> str:
    return f"""
proc version {{args}} {{ return "2026.1" }}
proc open_hw_manager {{}} {{}}
proc connect_hw_server {{args}} {{ return "localhost" }}
proc get_hw_targets {{args}} {{ return {targets} }}
proc open_hw_target {{target}} {{}}
proc get_hw_devices {{args}} {{ return {devices} }}
proc close_hw_target {{args}} {{}}
proc disconnect_hw_server {{}} {{}}
proc close_hw_manager {{}} {{}}
"""


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_detect_target_success_path_is_valid_tcl(tmp_path):
    result = _run_tcl(
        tmp_path,
        _detect_prelude("[list target0]", "[list xck26_0]"),
        DETECT,
    )
    assert result.returncode == 0, result.stderr
    assert "HW_TARGET_COUNT=1" in result.stdout
    assert "HW_DEVICE=xck26_0" in result.stdout
    assert "STATUS=PASS" in result.stdout


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_detect_target_rejects_missing_target(tmp_path):
    result = _run_tcl(
        tmp_path,
        _detect_prelude("{}", "{}"),
        DETECT,
    )
    assert result.returncode == 4
    assert "ERROR=NO_HW_TARGET" in result.stderr


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_detect_target_rejects_target_without_device(tmp_path):
    result = _run_tcl(
        tmp_path,
        _detect_prelude("[list target0]", "{}"),
        DETECT,
    )
    assert result.returncode == 5
    assert "ERROR=NO_KV260_FPGA_DEVICE" in result.stderr


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_detect_target_rejects_ps_debug_object_without_xck26(tmp_path):
    result = _run_tcl(
        tmp_path,
        _detect_prelude("[list target0]", "[list arm_dap_1]"),
        DETECT,
    )
    assert result.returncode == 5
    assert "HW_DEVICE=arm_dap_1" in result.stdout
    assert "ERROR=NO_KV260_FPGA_DEVICE" in result.stderr


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_detect_target_reports_hw_server_failure(tmp_path):
    prelude = """
proc version {args} { return "2026.1" }
proc open_hw_manager {} {}
proc connect_hw_server {args} { error "mock server unavailable" }
proc close_hw_manager {} {}
"""
    result = _run_tcl(tmp_path, prelude, DETECT)
    assert result.returncode == 3
    assert "ERROR=HW_SERVER_CONNECT_FAILED" in result.stderr
    assert "mock server unavailable" in result.stderr
