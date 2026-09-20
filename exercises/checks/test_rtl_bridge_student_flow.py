"""End-to-end student-workbook flow for Lessons 06-08."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts.start_exercise import create_work_copy


ROOT = Path(__file__).resolve().parents[2]

EXERCISES = [
    "06_what_is_rtl.ipynb",
    "07_first_rtl_neuron.ipynb",
    "08_testbench_waveform_simulation.ipynb",
]

REFERENCE_IMPLEMENTATIONS = {
    "06_what_is_rtl.ipynb": """
def clocked_accumulator_edge(state, input_value, rst_n):
    return 0 if not rst_n else state + input_value
""",
    "07_first_rtl_neuron.ipynb": """
def if_neuron_comb(membrane_v, input_current, threshold, reset_value):
    candidate = membrane_v + input_current
    spike_next = candidate >= threshold
    next_v = reset_value if spike_next else candidate
    return candidate, next_v, spike_next

def if_neuron_register_edge(next_v, spike_next, rst_n, reset_value):
    if not rst_n:
        return reset_value, False
    return next_v, spike_next
""",
    "08_testbench_waveform_simulation.ipynb": """
def check_sampled_trace(actual, expected):
    common = min(len(actual), len(expected))
    for cycle in range(common):
        if actual[cycle] != expected[cycle]:
            return False, cycle
    if len(actual) != len(expected):
        return False, common
    return True, None
""",
}


def _notebook(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _template(language: str, name: str) -> Path:
    return ROOT / "exercises" / language / name


def _code_cells(path: Path) -> list[str]:
    notebook = _notebook(path)
    return [
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    ]


@pytest.mark.parametrize("language", ["zh", "en"])
@pytest.mark.parametrize("name", EXERCISES)
def test_rtl_bridge_workbook_runs_from_personal_copy(
    language, name, tmp_path, monkeypatch, capsys
):
    lesson = name[:2]
    fake_repo = tmp_path / "repo"
    template = fake_repo / "exercises" / language / name
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(
        _template(language, name).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    shutil.copytree(
        ROOT / "exercises" / "grader",
        fake_repo / "exercises" / "grader",
    )

    work_copy, created = create_work_copy(fake_repo, lesson, language)
    assert created
    assert work_copy == fake_repo / "exercises" / "work" / language / name

    monkeypatch.chdir(work_copy.parent)
    namespace: dict[str, object] = {}

    for index, code in enumerate(_code_cells(work_copy)):
        if "YOUR CODE STARTS HERE" in code:
            code = REFERENCE_IMPLEMENTATIONS[name]
        exec(
            compile(code, f"<rtl-bridge-flow/{language}/{name}/{index}>", "exec"),
            namespace,
        )

    output = capsys.readouterr().out
    assert "3 / 3 groups passed" in output
