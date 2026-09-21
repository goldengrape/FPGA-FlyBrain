"""Structural regression tests for implemented KV260 Physical Labs through LAB-HW-10."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LABS = [
    "00_vendor_toolchain_preflight.ipynb",
    "01_board_orientation.ipynb",
    "02_power_target_detection.ipynb",
    "03_first_bitstream.ipynb",
    "04_clock_reset_io.ipynb",
    "05_ps_linux_first_boot.ipynb",
    "06_host_pl_loopback.ipynb",
    "07_bram_neuron_state.ipynb",
    "08_small_flybrain_replay.ipynb",
    "09_ddr_integrity.ipynb",
    "10_axi_burst_measurement.ipynb",
]


def _read(language: str, name: str):
    path = ROOT / "labs" / language / name
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown(notebook) -> str:
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "markdown"
    )


def _code(notebook) -> str:
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )


def test_first_kv260_labs_are_bilingual_and_cell_aligned():
    for name in LABS:
        zh = _read("zh", name)
        en = _read("en", name)

        assert zh["nbformat"] == 4
        assert en["nbformat"] == 4
        assert [cell["cell_type"] for cell in zh["cells"]] == [
            cell["cell_type"] for cell in en["cells"]
        ]

        zh_ids = [cell.get("id") for cell in zh["cells"]]
        en_ids = [cell.get("id") for cell in en["cells"]]
        assert all(zh_ids)
        assert all(en_ids)
        assert len(zh_ids) == len(set(zh_ids))
        assert len(en_ids) == len(set(en_ids))
        assert zh_ids == en_ids


def test_lab_notebooks_are_clean_sources_without_saved_execution_output():
    for language in ("zh", "en"):
        for name in LABS:
            notebook = _read(language, name)
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    assert cell.get("execution_count") is None
                    assert cell.get("outputs", []) == []


def test_every_lab_has_evidence_human_check_trace_and_official_basis():
    required = {
        "zh": ("Expected Evidence", "Save Evidence", "Human Check", "Project Trace", "官方依据"),
        "en": ("Expected Evidence", "Save Evidence", "Human Check", "Project Trace", "Official basis"),
    }
    for language in ("zh", "en"):
        for name in LABS:
            text = _markdown(_read(language, name))
            for marker in required[language]:
                assert marker in text, f"{language}/{name} missing {marker}"


def test_new_physical_lab_diagrams_do_not_use_mermaid_or_ascii_art():
    for language in ("zh", "en"):
        for name in LABS:
            text = _markdown(_read(language, name))
            assert "```mermaid" not in text
            assert "```text" not in text


def test_lab00_freezes_vivado_preflight_without_claiming_board_pass():
    for language in ("zh", "en"):
        text = _markdown(_read(language, "00_vendor_toolchain_preflight.ipynb"))
        assert "Vivado 2026.1" in text
        assert "check_vivado.tcl" in text
        assert "board" in text.lower()
        assert "cable driver" in text.lower()
        assert "LAB-HW-02" in text
        assert "T-HW-001" in text
        assert "vivado -version" in text
        assert "install_drivers_wrapper.bat" in text
        assert "sudo ./install_drivers" in text


def test_lab01_inventory_teaches_the_actual_connector_and_reset_boundaries():
    required = ("J12", "J4", "J3", "J11", "J10", "J2", "SW2", "DS34")
    for language in ("zh", "en"):
        text = _markdown(_read(language, "01_board_orientation.ipynb"))
        for marker in required:
            assert marker in text
        assert "SOM" in text
        assert "rst_n" in text
        assert "PS done" in text

    assert _code(_read("zh", "01_board_orientation.ipynb")) == _code(
        _read("en", "01_board_orientation.ipynb")
    )


def test_lab02_has_inline_svg_connection_map_and_real_discovery_command():
    for language in ("zh", "en"):
        text = _markdown(_read(language, "02_power_target_detection.ipynb"))
        assert "<svg " in text and "</svg>" in text
        assert 'aria-label="KV260 LAB-HW-02 power and JTAG connection map"' in text
        assert 'fill="#e6f4ea"' in text
        assert "12 V / 3 A" in text
        assert "J12" in text and "J4" in text
        assert "detect_target.tcl" in text
        assert "get_hw_devices" in text
        assert "xck26" in text.lower()
        assert "arm_dap_1" in text
        assert "T-HW-002" in text
        assert "bitstream" in text.lower()


def test_lab_readmes_name_the_completed_first_stage_and_pending_second_stage():
    for name in ("README.md", "README.zh-CN.md"):
        text = (ROOT / "labs" / name).read_text(encoding="utf-8")
        for lab in ("LAB-HW-00", "LAB-HW-01", "LAB-HW-02", "LAB-HW-03", "LAB-HW-04", "LAB-HW-05", "LAB-HW-06", "LAB-HW-07", "LAB-HW-08", "LAB-HW-09", "LAB-HW-10"):
            assert lab in text
        assert "LAB-HW-10" in text


def test_trace_register_points_to_implemented_labs():
    expected = {
        "en": [
            "labs/en/00_vendor_toolchain_preflight.ipynb",
            "labs/en/01_board_orientation.ipynb",
            "labs/en/02_power_target_detection.ipynb",
            "labs/en/03_first_bitstream.ipynb",
            "labs/en/04_clock_reset_io.ipynb",
            "labs/en/05_ps_linux_first_boot.ipynb",
            "labs/en/06_host_pl_loopback.ipynb",
            "labs/en/07_bram_neuron_state.ipynb",
            "labs/en/08_small_flybrain_replay.ipynb",
            "labs/en/09_ddr_integrity.ipynb",
            "labs/en/10_axi_burst_measurement.ipynb",
        ],
        "zh": [
            "labs/zh/00_vendor_toolchain_preflight.ipynb",
            "labs/zh/01_board_orientation.ipynb",
            "labs/zh/02_power_target_detection.ipynb",
            "labs/zh/03_first_bitstream.ipynb",
            "labs/zh/04_clock_reset_io.ipynb",
            "labs/zh/05_ps_linux_first_boot.ipynb",
            "labs/zh/06_host_pl_loopback.ipynb",
            "labs/zh/07_bram_neuron_state.ipynb",
            "labs/zh/08_small_flybrain_replay.ipynb",
            "labs/zh/09_ddr_integrity.ipynb",
            "labs/zh/10_axi_burst_measurement.ipynb",
        ],
    }
    for language, paths in expected.items():
        trace = (ROOT / "docs" / language / "TRACE.md").read_text(encoding="utf-8")
        for path in paths:
            assert f"`{path}`" in trace
            assert (ROOT / path).exists()


def test_physical_evidence_template_is_versioned_but_generated_evidence_is_ignored():
    evidence = ROOT / "boards" / "kv260" / "evidence"
    template = json.loads((evidence / "manifest.example.json").read_text(encoding="utf-8"))
    assert template["lab_id"] == "LAB-HW-XX"
    assert template["board_model"] == "AMD Kria KV260 Vision AI Starter Kit"
    assert "git_commit" in template
    assert "vivado_version" in template
    assert "platform_version" in template
    assert "linux_image_version" in template
    assert "bitstream_sha256" in template
    assert "build_artifact_hashes" in template
    assert "test_input" in template
    assert "output_summary" in template
    assert "artifacts" in template
    ignore = (evidence / ".gitignore").read_text(encoding="utf-8")
    assert "!manifest.example.json" in ignore
    assert "!README.md" in ignore



def test_lab03_freezes_minimal_marker_build_and_program_contract():
    for language in ("zh", "en"):
        text = _markdown(_read(language, "03_first_bitstream.ipynb"))
        assert "5'b10101" in text
        assert "xck26-sfvc784-2LV-c" in text
        assert "build_lab03_marker.tcl" in text
        assert "program_bitstream.tcl" in text
        assert "SHA-256" in text
        assert "T-HW-003" in text
        assert "DS34" in text
        assert "TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS" in text
        assert "drc.rpt" in text
        assert "<svg " in text


def test_lab04_freezes_clock_reset_and_constraint_layers():
    for language in ("zh", "en"):
        text = _markdown(_read(language, "04_clock_reset_io.ipynb"))
        assert "pl_clk0" in text
        assert "pl_resetn0" in text
        assert "proc_sys_reset" in text
        assert "peripheral_aresetn" in text
        assert "PACKAGE_PIN J11" in text
        assert "IOSTANDARD LVCMOS33" in text
        assert "SW2" in text
        assert "T-HW-004" in text
        assert "Checkpoint A" in text
        assert "Checkpoint B" in text
        assert "TIMING_SETUP_WORST_SLACK_NS" in text
        assert "TIMING_HOLD_WORST_SLACK_NS" in text
        assert text.count("<svg ") >= 2


def test_bank45_xdc_matches_frozen_k26_package_mapping():
    xdc = (ROOT / "boards" / "kv260" / "constraints" / "bank45_gpio.xdc").read_text(
        encoding="utf-8"
    )
    expected = {
        0: "J11",
        1: "J10",
        2: "K13",
        3: "F11",
        4: "A12",
    }
    for bit, pin in expected.items():
        assert f"PACKAGE_PIN {pin} [get_ports {{bank45_gpio[{bit}]}}]" in xdc
        assert f"IOSTANDARD LVCMOS33 [get_ports {{bank45_gpio[{bit}]}}]" in xdc


def test_first_stage_board_sources_and_helpers_exist():
    expected_paths = [
        "boards/kv260/rtl/kv260_marker_top.sv",
        "boards/kv260/rtl/kv260_blink_core.sv",
        "boards/kv260/tb/kv260_marker_top_tb.sv",
        "boards/kv260/tb/kv260_blink_core_tb.sv",
        "boards/kv260/constraints/bank45_gpio.xdc",
        "boards/kv260/scripts/build_lab03_marker.tcl",
        "boards/kv260/scripts/build_lab04_blink.tcl",
        "boards/kv260/scripts/program_bitstream.tcl",
    ]
    for relative in expected_paths:
        assert (ROOT / relative).is_file(), relative



def test_lab02_troubleshooting_uses_current_discovery_error_names():
    for language in ("zh", "en"):
        text = _markdown(_read(language, "02_power_target_detection.ipynb"))
        assert "NO_HW_TARGET" in text
        assert "NO_KV260_FPGA_DEVICE" in text
        assert "NO_HW_DEVICE" not in text



def test_lab05_freezes_linux_uart_boundary_without_host_pl_transport():
    required = (
        "J4",
        "J11",
        "J12",
        "115200",
        "Ubuntu Server 24.04 LTS",
        "ubuntu",
        "collect_boot_info.sh",
        "hash_image.py",
        "T-HW-005",
        "T-HW-011",
        "sudo shutdown -h now",
    )
    for language in ("zh", "en"):
        text = _markdown(_read(language, "05_ps_linux_first_boot.ipynb"))
        for marker in required:
            assert marker in text
        assert "host↔PL" not in text
        assert "AXI-Lite" not in text
        assert "loopback_mmio.py" not in text



def test_lab06_freezes_minimal_ps_pl_roundtrip_without_turning_into_axi_course():
    required = (
        "0xA0010000",
        "M_AXI_HPM0_FPD",
        "SmartConnect",
        "GPIO_DATA",
        "GPIO2_DATA",
        "build_lab06_loopback.tcl",
        "program_bitstream.tcl",
        "loopback_mmio.py",
        "--dry-run",
        "TRANSPORT_REQUIRES_ROOT",
        "T-HW-006",
        "T-HW-011",
    )
    for language in ("zh", "en"):
        text = _markdown(_read(language, "06_host_pl_loopback.ipynb"))
        for marker in required:
            assert marker in text
        assert "read = (write + 1) mod 2^32" in text
        assert "--base 0xA0010000" not in text
        assert "DDR" in text
        if language == "en":
            assert "performance" in text.lower()
        else:
            assert "性能" in text



def test_lab07_freezes_bram_state_geometry_and_resource_oracle():
    required = (
        "1024",
        "32",
        "4 KiB",
        "0xA0000000",
        "M_AXI_HPM0_FPD",
        "AXI BRAM Controller",
        "kv260_neuron_state_store",
        "build_lab07_bram_state.tcl",
        "state_bram_mmio.py",
        "BRAM_PRIMITIVE_COUNT",
        "RAMB18",
        "RAMB36",
        "synchronous",
        "read-first",
        "T-HW-007",
        "T-HW-011",
    )
    for language in ("zh", "en"):
        text = _markdown(_read(language, "07_bram_neuron_state.ipynb"))
        for marker in required:
            assert marker in text
        assert "DDR" in text
        assert "LAB-HW-08" in text
        assert "--base" not in text
        assert "<svg " in text



def test_lab08_freezes_lesson12_replay_without_claiming_formal_lif():
    required = (
        "Lesson-12",
        "lab08_four_neuron_replay_v1.json",
        "lab08_replay_reference.py",
        "small_replay_mmio.py",
        "kv260_small_replay_engine",
        "0xA0000000",
        "0xA0010000",
        "[0,1,2,3]",
        "0x01020201",
        "0x02010101",
        "0x13020200",
        "0x23010301",
        "DIFFERENTIAL=PASS",
        "T-HW-008",
        "T-HW-011",
        "busy=1",
    )
    for language in ("zh", "en"):
        text = _markdown(_read(language, "08_small_flybrain_replay.ipynb"))
        for marker in required:
            assert marker in text
        assert "MOD-004~009" in text
        assert "DDR" in text
        assert "--base" not in text
        assert "<svg " in text
        assert "mermaid" not in text.lower()



def test_lab09_freezes_os_managed_ddr_integrity_before_axi_measurement():
    required = (
        "64 MiB",
        "1 MiB",
        "anonymous",
        "byte-for-byte",
        "SHA-256",
        "ddr_integrity.py",
        "--dry-run",
        "--physical",
        "DDR_INTEGRITY_MISMATCH",
        "PERFORMANCE_BLOCKED=1",
        "HOST_PATH_WRITE_MIB_PER_S",
        "HOST_PATH_READ_MIB_PER_S",
        "T-HW-009",
        "T-HW-011",
        "LAB-HW-10",
    )
    for language in ("zh", "en"):
        text = _markdown(_read(language, "09_ddr_integrity.ipynb"))
        for marker in required:
            assert marker in text
        assert "4 GB" in text
        assert "DDR4" in text
        assert "no new bitstream" in text.lower() or "不需要新 bitstream" in text
        assert "/dev/mem" in text
        assert "<svg " in text
        assert "mermaid" not in text.lower()



def test_lab10_freezes_real_axi_cdma_workload_and_measurement_gates():
    required = (
        "AXI CDMA",
        "Simple DMA",
        "0xA0020000",
        "M_AXI_HPM0_FPD",
        "S_AXI_HP0_FPD",
        "non-coherent",
        "u-dma-buf",
        "O_SYNC",
        "2 MiB",
        "256 KiB",
        "1024",
        "256 B",
        "block = (257*i + 17) mod 1024",
        "warm-up",
        "20",
        "≤10%",
        "MEASUREMENT_UNSTABLE",
        "PERFORMANCE_CONCLUSION_ALLOWED=0",
        "axi_cdma_benchmark.py",
        "build_lab10_axi_cdma.tcl",
        "T-HW-010",
        "T-HW-011",
    )
    for language in ("zh", "en"):
        text = _markdown(_read(language, "10_axi_burst_measurement.ipynb"))
        for marker in required:
            assert marker in text
        assert "128-bit" in text
        assert "max burst 64" in text
        assert "HP0_DDR_LOW" in text
        assert "<svg " in text
        assert "mermaid" not in text.lower()
        assert "'''text".replace("'''", "```") not in text
