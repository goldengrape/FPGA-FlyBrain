"""Structural checks for student-facing Exercise Notebooks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.start_exercise import EXERCISE_FILES


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = [
    "01_membrane_to_lif.ipynb",
    "02_float_to_fixed.ipynb",
    "03_freeze_neuron_semantics.ipynb",
    "04_state_and_clock.ipynb",
    "05_logic_building_blocks.ipynb",
    "06_what_is_rtl.ipynb",
    "07_first_rtl_neuron.ipynb",
    "08_testbench_waveform_simulation.ipynb",
    "09_time_multiplex_many_neurons.ipynb",
    "10_spike_fifo_backpressure.ipynb",
    "11_sparse_synapse_lookup.ipynb",
    "12_one_spike_journey.ipynb",
    "13_simulation_is_not_chip.ipynb",
    "14_what_is_fpga_board.ipynb",
    "15_host_talks_to_fpga.ipynb",
    "16_data_movement_cost.ipynb",
    "17_external_memory_ddr.ipynb",
    "18_axi_subset.ipynb",
    "19_what_is_connectome.ipynb",
    "20_load_malecns_subset.ipynb",
    "21_scaling_bottlenecks.ipynb",
    "22_closed_loop_world.ipynb",
    "23_cpu_gpu_fpga_benchmark.ipynb",
]

RTL_BRIDGE_NOTEBOOKS = [
    "06_what_is_rtl.ipynb",
    "07_first_rtl_neuron.ipynb",
    "08_testbench_waveform_simulation.ipynb",
]

PLATFORM4_NOTEBOOKS = [
    "13_simulation_is_not_chip.ipynb",
    "14_what_is_fpga_board.ipynb",
    "15_host_talks_to_fpga.ipynb",
    "16_data_movement_cost.ipynb",
    "17_external_memory_ddr.ipynb",
    "18_axi_subset.ipynb",
]

PLATFORM5_NOTEBOOKS = [
    "19_what_is_connectome.ipynb",
    "20_load_malecns_subset.ipynb",
    "21_scaling_bottlenecks.ipynb",
    "22_closed_loop_world.ipynb",
    "23_cpu_gpu_fpga_benchmark.ipynb",
]


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_bilingual_exercise_notebooks_exist_and_parse():
    for language in ("zh", "en"):
        for name in NOTEBOOKS:
            notebook = _read(ROOT / "exercises" / language / name)
            assert notebook["nbformat"] == 4
            assert notebook["cells"]


def test_student_notebooks_do_not_embed_assertions_or_concrete_test_functions():
    for language in ("zh", "en"):
        for name in NOTEBOOKS:
            notebook = _read(ROOT / "exercises" / language / name)
            code = "\n".join(
                "".join(cell.get("source", []))
                for cell in notebook["cells"]
                if cell.get("cell_type") == "code"
            )
            assert "assert " not in code
            assert "def test_" not in code


def test_student_notebooks_use_external_graders_and_keep_todos():
    for language in ("zh", "en"):
        for name in NOTEBOOKS:
            notebook = _read(ROOT / "exercises" / language / name)
            code = "\n".join(
                "".join(cell.get("source", []))
                for cell in notebook["cells"]
                if cell.get("cell_type") == "code"
            )
            assert "from exercises.grader." in code
            assert "_repo_root = next(" in code
            assert "YOUR CODE STARTS HERE" in code
            assert "NotImplementedError" in code



def test_each_exercise_has_pre_code_reasoning():
    headings = {
        "zh": "先不用代码",
        "en": "Before coding",
    }
    for language, heading in headings.items():
        for name in NOTEBOOKS:
            notebook = _read(ROOT / "exercises" / language / name)
            markdown = "\n".join(
                "".join(cell.get("source", []))
                for cell in notebook["cells"]
                if cell.get("cell_type") == "markdown"
            )
            assert heading in markdown, f"{language}/{name} is missing pre-code reasoning"


def test_bilingual_exercises_keep_matching_structure_and_code():
    for name in NOTEBOOKS:
        zh = _read(ROOT / "exercises" / "zh" / name)
        en = _read(ROOT / "exercises" / "en" / name)

        assert [cell["cell_type"] for cell in zh["cells"]] == [
            cell["cell_type"] for cell in en["cells"]
        ], f"{name} has drifted cell structure"

        zh_code = [
            "".join(cell.get("source", [])).replace('language="zh"', 'language="LANG"')
            for cell in zh["cells"]
            if cell.get("cell_type") == "code"
        ]
        en_code = [
            "".join(cell.get("source", [])).replace('language="en"', 'language="LANG"')
            for cell in en["cells"]
            if cell.get("cell_type") == "code"
        ]
        assert zh_code == en_code, f"{name} has drifted code between zh/en versions"



def test_grader_bootstrap_works_from_notebook_directory():
    snippet = r"""
from pathlib import Path
import sys

_repo_root = next(
    path for path in (Path.cwd(), *Path.cwd().parents)
    if (path / "exercises" / "grader").is_dir()
)
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from exercises.grader.lesson01 import check
assert callable(check)
"""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    for language in ("zh", "en"):
        completed = subprocess.run(
            [sys.executable, "-c", snippet],
            cwd=ROOT / "exercises" / language,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr



def test_each_todo_has_a_student_readable_semantic_contract():
    role_markers = {
        "zh": ("### 这个函数做什么？", "### 这些函数做什么？"),
        "en": ("### What does this function do?", "### What do these functions do?"),
    }
    output_markers = {
        "zh": ("输出",),
        "en": ("output",),
    }

    for language in ("zh", "en"):
        for name in NOTEBOOKS:
            notebook = _read(ROOT / "exercises" / language / name)
            cells = notebook["cells"]

            for index, cell in enumerate(cells):
                if cell.get("cell_type") != "code":
                    continue

                code = "".join(cell.get("source", []))
                if "YOUR CODE STARTS HERE" not in code:
                    continue

                assert index > 0, f"{language}/{name} TODO has no preceding explanation"
                previous = cells[index - 1]
                assert previous.get("cell_type") == "markdown", (
                    f"{language}/{name} TODO must be preceded by a Markdown semantic contract"
                )

                prose = "".join(previous.get("source", []))
                assert any(marker in prose for marker in role_markers[language]), (
                    f"{language}/{name} TODO is missing a natural-language role explanation"
                )
                assert any(
                    marker.lower() in prose.lower()
                    for marker in output_markers[language]
                ), f"{language}/{name} TODO is missing an output explanation"



def test_exercise_registry_matches_structural_test_inventory():
    assert set(NOTEBOOKS) == set(EXERCISE_FILES.values())


def test_exercise_registry_covers_every_lesson_01_through_23():
    expected_lessons = {f"{number:02d}" for number in range(1, 24)}
    assert set(EXERCISE_FILES) == expected_lessons

    for lesson in expected_lessons:
        grader = ROOT / "exercises" / "grader" / f"lesson{lesson}.py"
        assert grader.is_file(), f"Lesson {lesson} is missing its external grader"


def test_platform4_and5_todos_have_explicit_inputs_outputs_and_return_order():
    input_markers = {
        "zh": "### 输入",
        "en": "### Inputs",
    }
    output_markers = {
        "zh": "### 输出",
        "en": "### Output",
    }
    return_markers = {
        "zh": "返回",
        "en": "Return",
    }

    for language in ("zh", "en"):
        for name in RTL_BRIDGE_NOTEBOOKS + PLATFORM4_NOTEBOOKS + PLATFORM5_NOTEBOOKS:
            notebook = _read(ROOT / "exercises" / language / name)
            cells = notebook["cells"]

            for index, cell in enumerate(cells):
                if cell.get("cell_type") != "code":
                    continue
                code = "".join(cell.get("source", []))
                if "YOUR CODE STARTS HERE" not in code:
                    continue

                prose = "".join(cells[index - 1].get("source", []))
                assert input_markers[language] in prose, (
                    f"{language}/{name} TODO is missing an explicit input section"
                )
                assert output_markers[language] in prose, (
                    f"{language}/{name} TODO is missing an explicit output section"
                )
                if "tuple[" in code:
                    assert return_markers[language] in prose and "(" in prose and ")" in prose, (
                        f"{language}/{name} tuple TODO must explain return order in prose"
                    )
