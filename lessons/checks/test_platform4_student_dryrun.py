"""Student-path execution checks for Platform 4 lessons.

These tests execute the same code cells a learner runs in Lessons 13–18 in
both Chinese and English. They complement structural checks: a notebook can
have all expected headings and still fail or produce confusing output when
actually executed.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _read(language: str, name: str):
    path = ROOT / "lessons" / language / name
    return json.loads(path.read_text(encoding="utf-8"))


def _code_cells(language: str, name: str) -> list[str]:
    notebook = _read(language, name)
    return [
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    ]


@pytest.mark.parametrize(
    ("language", "missing_message"),
    [
        ("zh", "没有找到 Yosys。"),
        ("en", "Yosys was not found."),
    ],
)
def test_lesson13_missing_yosys_is_actionable(language, missing_message, monkeypatch, capsys):
    code = _code_cells(language, "13_simulation_is_not_chip.ipynb")[0]
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("PATH", "")
    namespace: dict[str, object] = {}
    exec(compile(code, f"<lesson13-yosys-missing-{language}>", "exec"), namespace)
    output = capsys.readouterr().out
    assert missing_message in output
    assert "HDL_TOOLCHAIN_SETUP.md" in output


@pytest.mark.parametrize("language", ["zh", "en"])
def test_lesson13_timing_output_is_beginner_readable(language, capsys):
    code = _code_cells(language, "13_simulation_is_not_chip.ipynb")[1]
    namespace: dict[str, object] = {}
    exec(compile(code, f"<lesson13-timing-{language}>", "exec"), namespace)
    output = capsys.readouterr().out
    assert "critical path: 4.80 ns" in output
    assert "clock period: 5.00 ns" in output
    assert "slack: +0.20 ns" in output
    assert "0.20000000000000018" not in output
    assert "meets timing: True" in output


@pytest.mark.skipif(shutil.which("yosys") is None, reason="Yosys is not installed in this job")
@pytest.mark.parametrize("language", ["zh", "en"])
def test_lesson13_real_yosys_cell_produces_teaching_summary(language, monkeypatch, capsys):
    code = _code_cells(language, "13_simulation_is_not_chip.ipynb")[0]
    monkeypatch.chdir(ROOT)
    namespace: dict[str, object] = {}
    exec(compile(code, f"<lesson13-yosys-real-{language}>", "exec"), namespace)
    output = capsys.readouterr().out
    assert "Yosys synthesis succeeded." in output
    assert "Top module: clocked_accumulator" in output
    assert "Number of synthesized cells:" in output
    assert "Cell summary:" in output
    assert "Structural check problems: 0" in output
    assert isinstance(namespace.get("yosys_log"), str)
    assert len(namespace["yosys_log"]) > 100


EXAMPLE_CASES = [
    (
        "14_what_is_fpga_board.ipynb",
        ("cycles per visible tick: 50000000", "counter bits required: 26"),
    ),
    (
        "15_host_talks_to_fpga.ipynb",
        ("host readbacks: [12, 10]", "final PL register: 10"),
    ),
    (
        "16_data_movement_cost.ipynb",
        (
            "compute time: 1000.0 ns",
            "data-movement time: 4100.0 ns",
            "dominant cost: memory/data movement",
        ),
    ),
    (
        "17_external_memory_ddr.ipynb",
        ("sequential bursts: 2", "random-like bursts: 8"),
    ),
    (
        "18_axi_subset.ipynb",
        ("accepted cycles: [0, 2, 4]", "accepted data: [10, 11, 12]"),
    ),
]


@pytest.mark.parametrize("language", ["zh", "en"])
@pytest.mark.parametrize(("name", "expected"), EXAMPLE_CASES)
def test_lessons14_to18_example_cells_execute_as_students_see_them(
    language, name, expected, capsys
):
    namespace: dict[str, object] = {}
    for code in _code_cells(language, name):
        exec(compile(code, f"<{language}/{name}>", "exec"), namespace)
    output = capsys.readouterr().out
    for text in expected:
        assert text in output
