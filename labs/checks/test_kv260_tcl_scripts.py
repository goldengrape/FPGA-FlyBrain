"""Contract and syntax-path tests for the first KV260 Vivado Tcl helpers."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "boards" / "kv260" / "scripts" / "check_vivado.tcl"
DETECT = ROOT / "boards" / "kv260" / "scripts" / "detect_target.tcl"
BUILD03 = ROOT / "boards" / "kv260" / "scripts" / "build_lab03_marker.tcl"
BUILD04 = ROOT / "boards" / "kv260" / "scripts" / "build_lab04_blink.tcl"
PROGRAM = ROOT / "boards" / "kv260" / "scripts" / "program_bitstream.tcl"
BUILD06 = ROOT / "boards" / "kv260" / "scripts" / "build_lab06_loopback.tcl"
TCLSH = shutil.which("tclsh")


def _run_tcl(tmp_path: Path, prelude: str, script: Path, argv: list[str] | None = None):
    wrapper = tmp_path / "wrapper.tcl"
    argv = argv or []
    argv_literal = " ".join(f"{{{value}}}" for value in argv)
    wrapper.write_text(
        prelude
        + f"\nset argc {len(argv)}\n"
        + f"set argv [list {argv_literal}]\n"
        + f"source {{{script.as_posix()}}}\n",
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



def test_lab03_build_script_is_minimal_and_target_specific():
    text = BUILD03.read_text(encoding="utf-8")
    assert 'set part_name "xck26-sfvc784-2LV-c"' in text
    assert "kv260_marker_top.sv" in text
    assert "bank45_gpio.xdc" in text
    assert "synth_design -top kv260_marker_top" in text
    assert "place_design" in text
    assert "route_design" in text
    assert "write_bitstream -force" in text
    assert "report_timing_summary" in text
    assert "report_utilization" in text
    assert "report_drc" in text
    assert "get_clocks -quiet" in text
    assert "TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS" in text
    assert "UNEXPECTED_CLOCK_IN_CLOCKLESS_MARKER" in text
    assert text.index("TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS") < text.index("write_bitstream -force")
    assert "zynq_ultra_ps_e" not in text
    assert "axi" not in text.lower()


def test_lab04_build_script_freezes_ps_clock_and_design_local_reset_path():
    text = BUILD04.read_text(encoding="utf-8")
    assert 'set part_name "xck26-sfvc784-2LV-c"' in text
    assert 'set board_part_name "xilinx.com:kv260_som:part0:1.4"' in text
    assert "xilinx.com:ip:zynq_ultra_ps_e:" in text
    assert "xilinx.com:ip:proc_sys_reset:" in text
    assert "update_compile_order -fileset sources_1" in text
    assert "ps/pl_clk0" in text
    assert "ps/pl_resetn0" in text
    assert "rst/peripheral_aresetn" in text
    assert "blink_core/resetn" in text
    assert "launch_runs impl_1 -to_step route_design" in text
    assert "get_clocks -quiet" in text
    assert "get_timing_paths -quiet -setup" in text
    assert "get_timing_paths -quiet -hold" in text
    assert "TIMING_SETUP_WORST_SLACK_NS" in text
    assert "TIMING_HOLD_WORST_SLACK_NS" in text
    assert "NEGATIVE_SETUP_SLACK" in text
    assert "NEGATIVE_HOLD_SLACK" in text
    assert "write_bitstream -force" in text
    assert text.index("NEGATIVE_HOLD_SLACK") < text.index("write_bitstream -force")
    assert "report_timing_summary" in text
    assert "report_utilization" in text
    assert "report_drc" in text
    assert "M_AXI" not in text
    assert "S_AXI" not in text


def test_shared_program_helper_requires_unique_xck26_target():
    text = PROGRAM.read_text(encoding="utf-8")
    assert "BITSTREAM_ARGUMENT_REQUIRED" in text
    assert "BITSTREAM_NOT_FOUND" in text
    assert "BITSTREAM_EXTENSION_NOT_BIT" in text
    assert "get_hw_targets -quiet" in text
    assert "get_hw_devices -quiet -of_objects" in text
    assert "NO_KV260_FPGA_DEVICE" in text
    assert "AMBIGUOUS_KV260_FPGA_DEVICE" in text
    assert "KV260_HW_TARGET" in text
    assert "set_property PROGRAM.FILE" in text
    assert "program_hw_devices" in text
    assert "STATUS=PASS" in text


def _program_prelude(target_map: dict[str, list[str]]) -> str:
    target_list = " ".join(target_map)
    cases = "\n".join(
        f'if {{$target eq "{target}"}} {{ return [list {" ".join(devices)}] }}'
        for target, devices in target_map.items()
    )
    return f"""
proc version {{args}} {{ return "2026.1" }}
proc open_hw_manager {{}} {{}}
proc connect_hw_server {{args}} {{}}
proc get_hw_targets {{args}} {{ return [list {target_list}] }}
proc open_hw_target {{target}} {{}}
proc close_hw_target {{args}} {{}}
proc get_hw_devices {{args}} {{
    set target [lindex $args end]
    {cases}
    return {{}}
}}
proc current_hw_device {{device}} {{}}
proc refresh_hw_device {{args}} {{}}
array set mock_props {{}}
proc set_property {{name value obj}} {{
    global mock_props
    set mock_props($name,$obj) $value
}}
proc get_property {{name obj}} {{
    global mock_props
    if {{[info exists mock_props($name,$obj)]}} {{
        return $mock_props($name,$obj)
    }}
    return ""
}}
proc program_hw_devices {{device}} {{}}
proc disconnect_hw_server {{}} {{}}
proc close_hw_manager {{}} {{}}
"""


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_program_bitstream_selects_one_xck26_target(tmp_path):
    bit_file = tmp_path / "proof.bit"
    bit_file.write_bytes(b"mock")
    result = _run_tcl(
        tmp_path,
        _program_prelude({"target0": ["arm_dap_1", "xck26_0"]}),
        PROGRAM,
        [str(bit_file)],
    )
    assert result.returncode == 0, result.stderr
    assert "KV260_FPGA_CANDIDATE_COUNT=1" in result.stdout
    assert "KV260_HW_TARGET=target0" in result.stdout
    assert "KV260_FPGA_DEVICE=xck26_0" in result.stdout
    assert "STATUS=PASS" in result.stdout


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_program_bitstream_rejects_multiple_xck26_targets(tmp_path):
    bit_file = tmp_path / "proof.bit"
    bit_file.write_bytes(b"mock")
    result = _run_tcl(
        tmp_path,
        _program_prelude({
            "target0": ["xck26_0"],
            "target1": ["xck26_1"],
        }),
        PROGRAM,
        [str(bit_file)],
    )
    assert result.returncode == 9
    assert "ERROR=AMBIGUOUS_KV260_FPGA_DEVICE" in result.stderr


@pytest.mark.skipif(TCLSH is None, reason="tclsh is not installed")
def test_program_bitstream_rejects_target_without_xck26(tmp_path):
    bit_file = tmp_path / "proof.bit"
    bit_file.write_bytes(b"mock")
    result = _run_tcl(
        tmp_path,
        _program_prelude({"target0": ["arm_dap_1"]}),
        PROGRAM,
        [str(bit_file)],
    )
    assert result.returncode == 8
    assert "ERROR=NO_KV260_FPGA_DEVICE" in result.stderr



def test_lab06_build_script_freezes_minimal_mmio_transport():
    text = BUILD06.read_text(encoding="utf-8")
    assert 'set axi_gpio_base 0xA0010000' in text
    assert "CONFIG.PSU__USE__M_AXI_GP0 {1}" in text
    assert "xilinx.com:ip:axi_gpio:" in text
    assert "CONFIG.C_IS_DUAL {1}" in text
    assert "CONFIG.C_ALL_OUTPUTS {1}" in text
    assert "CONFIG.C_ALL_INPUTS_2 {1}" in text
    assert "ps/M_AXI_HPM0_FPD" in text
    assert "axi_smc/S00_AXI" in text
    assert "axi_smc/M00_AXI" in text
    assert "axi_gpio/S_AXI" in text
    assert "axi_gpio/gpio_io_o" in text
    assert "axi_gpio/gpio2_io_i" in text
    assert "assign_bd_address" in text
    assert "get_bd_addr_spaces ps/Data" in text
    assert "GPIO_DATA_OFFSET=0x0000" in text
    assert "GPIO2_DATA_OFFSET=0x0008" in text
    assert "DRC_ERROR_COUNT" in text
    assert "DRC_ERROR_PRESENT" in text
    assert "NEGATIVE_SETUP_SLACK" in text
    assert "NEGATIVE_HOLD_SLACK" in text
    assert text.index("DRC_ERROR_PRESENT") < text.index("write_bitstream -force")
    assert text.index("NEGATIVE_HOLD_SLACK") < text.index("write_bitstream -force")
