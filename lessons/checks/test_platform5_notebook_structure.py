"""Structural regression tests for Platform 5 lesson notebooks."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LESSONS = [
    "19_what_is_connectome.ipynb",
    "20_load_malecns_subset.ipynb",
    "21_scaling_bottlenecks.ipynb",
    "22_closed_loop_world.ipynb",
    "23_cpu_gpu_fpga_benchmark.ipynb",
]


def _read(language: str, name: str):
    path = ROOT / "lessons" / language / name
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown(notebook) -> str:
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "markdown"
    )


def _numbered_sections(notebook):
    sections = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "markdown":
            continue
        first = "".join(cell.get("source", [])).splitlines()[0]
        match = re.match(r"^## (\d+)\. ", first)
        if match:
            sections.append((int(match.group(1)), first))
    return sections


def test_platform5_lessons_are_bilingual_and_cell_ids_align():
    for name in LESSONS:
        zh = _read("zh", name)
        en = _read("en", name)
        assert zh["nbformat"] == 4
        assert en["nbformat"] == 4
        assert [cell["cell_type"] for cell in zh["cells"]] == [
            cell["cell_type"] for cell in en["cells"]
        ]
        zh_ids = [cell.get("id") for cell in zh["cells"]]
        en_ids = [cell.get("id") for cell in en["cells"]]
        assert all(zh_ids) and all(en_ids)
        assert len(set(zh_ids)) == len(zh_ids)
        assert len(set(en_ids)) == len(en_ids)
        assert zh_ids == en_ids


def test_platform5_numbered_sections_are_unique_and_monotonic():
    for language in ("zh", "en"):
        for name in LESSONS:
            numbers = [n for n, _ in _numbered_sections(_read(language, name))]
            assert numbers == list(range(1, len(numbers) + 1)), (
                f"{language}/{name} numbered sections drifted: {numbers}"
            )


def test_platform5_keeps_core_teaching_sections():
    required = {
        "zh": ("概念账本", "Try It", "AI Task", "Human Check", "Engineering Handoff", "Project Trace", "Exit Ticket"),
        "en": ("Concept ledger", "Try It", "AI Task", "Human Check", "Engineering Handoff", "Project Trace", "Exit Ticket"),
    }
    for language in ("zh", "en"):
        for name in LESSONS:
            text = _markdown(_read(language, name))
            for marker in required[language]:
                assert marker in text, f"{language}/{name} missing {marker}"


def test_lesson19_separates_connectome_structure_from_dynamic_state():
    zh = _markdown(_read("zh", LESSONS[0]))
    en = _markdown(_read("en", LESSONS[0]))
    assert "connectome 是结构" in zh
    assert "dynamic model state" in zh
    assert "structure, not a running brain" in en
    assert "dynamic model state" in en


def test_lesson20_does_not_claim_teaching_fixture_is_real_malecns():
    for language in ("zh", "en"):
        text = _markdown(_read(language, LESSONS[1]))
        assert "teaching fixture" in text
        assert "RMD-017" in text and "RMD-018" in text
    assert "不声称这份 fixture 就是真实 MaleCNS 数据" in _markdown(_read("zh", LESSONS[1]))
    assert "does not claim that the fixture is real MaleCNS data" in _markdown(_read("en", LESSONS[1]))


def test_lesson21_marks_scale_numbers_as_teaching_not_measurements():
    zh = _markdown(_read("zh", LESSONS[2]))
    en = _markdown(_read("en", LESSONS[2]))
    assert "教学数字" in zh and "不是 FPGA 实测结果" in zh
    assert "teaching numbers" in en and "not measured FPGA results" in en


def test_lesson22_labels_toy_world_as_nonbiological_teaching_model():
    zh = _markdown(_read("zh", LESSONS[3]))
    en = _markdown(_read("en", LESSONS[3]))
    assert "不声称代表真实果蝇行为" in zh
    assert "engineering teaching model" in en
    assert "not a claim about real Drosophila behavior" in en


def test_lesson23_labels_benchmark_values_as_synthetic():
    zh = _markdown(_read("zh", LESSONS[4]))
    en = _markdown(_read("en", LESSONS[4]))
    assert "synthetic measurement" in zh
    assert "不代表任何真实 CPU、GPU 或 FPGA" in zh
    assert "synthetic teaching measurements" in en
    assert "not claims about any real CPU, GPU, or FPGA" in en


def test_platform5_trace_register_contains_lessons():
    expected_files = {
        "zh": [
            "19_what_is_connectome.ipynb",
            "20_load_malecns_subset.ipynb",
            "21_scaling_bottlenecks.ipynb",
            "22_closed_loop_world.ipynb",
            "23_cpu_gpu_fpga_benchmark.ipynb",
        ],
        "en": [
            "19_what_is_connectome.ipynb",
            "20_load_malecns_subset.ipynb",
            "21_scaling_bottlenecks.ipynb",
            "22_closed_loop_world.ipynb",
            "23_cpu_gpu_fpga_benchmark.ipynb",
        ],
    }
    for language in ("zh", "en"):
        trace = (ROOT / "docs" / language / "TRACE.md").read_text(encoding="utf-8")
        for number in range(19, 24):
            assert f"LSN-{number:03d}" in trace
        for filename in expected_files[language]:
            assert filename in trace
