"""Structural regression tests for the first KV260 Physical Lab batch."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LABS = [
    "00_vendor_toolchain_preflight.ipynb",
    "01_board_orientation.ipynb",
    "02_power_target_detection.ipynb",
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


def test_lab_readmes_name_only_the_implemented_first_batch():
    for name in ("README.md", "README.zh-CN.md"):
        text = (ROOT / "labs" / name).read_text(encoding="utf-8")
        for lab in ("LAB-HW-00", "LAB-HW-01", "LAB-HW-02"):
            assert lab in text
        assert "LAB-HW-03~10" in text


def test_trace_register_points_to_implemented_first_batch():
    expected = {
        "en": [
            "labs/en/00_vendor_toolchain_preflight.ipynb",
            "labs/en/01_board_orientation.ipynb",
            "labs/en/02_power_target_detection.ipynb",
        ],
        "zh": [
            "labs/zh/00_vendor_toolchain_preflight.ipynb",
            "labs/zh/01_board_orientation.ipynb",
            "labs/zh/02_power_target_detection.ipynb",
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
    ignore = (evidence / ".gitignore").read_text(encoding="utf-8")
    assert "!manifest.example.json" in ignore
    assert "!README.md" in ignore
