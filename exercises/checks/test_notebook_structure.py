"""Structural checks for student-facing Exercise Notebooks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = [
    "01_membrane_to_lif.ipynb",
    "02_float_to_fixed.ipynb",
    "03_freeze_neuron_semantics.ipynb",
    "04_state_and_clock.ipynb",
    "05_logic_building_blocks.ipynb",
    "09_time_multiplex_many_neurons.ipynb",
    "10_spike_fifo_backpressure.ipynb",
    "11_sparse_synapse_lookup.ipynb",
    "12_one_spike_journey.ipynb",
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
