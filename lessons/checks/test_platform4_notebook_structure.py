"""Structural regression tests for the Platform 4 lesson notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LESSONS = [
    "13_simulation_is_not_chip.ipynb",
    "14_what_is_fpga_board.ipynb",
    "15_host_talks_to_fpga.ipynb",
    "16_data_movement_cost.ipynb",
    "17_external_memory_ddr.ipynb",
    "18_axi_subset.ipynb",
]

FIRST_USE_TERMS = {
    "13_simulation_is_not_chip.ipynb": (
        "Register-Transfer Level",
        "Field-Programmable Gate Array",
    ),
    "14_what_is_fpga_board.ipynb": ("Field-Programmable Gate Array",),
    "15_host_talks_to_fpga.ipynb": (
        "Field-Programmable Gate Array",
        "programmable logic",
    ),
    "16_data_movement_cost.ipynb": ("throughput",),
    "17_external_memory_ddr.ipynb": (
        "Double Data Rate Synchronous Dynamic Random-Access Memory",
        "Field-Programmable Gate Array",
    ),
    "18_axi_subset.ipynb": (
        "Advanced eXtensible Interface",
        "System on Chip",
        "Field-Programmable Gate Array",
    ),
}


def _read(language: str, name: str):
    path = ROOT / "lessons" / language / name
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


def test_platform4_lessons_are_bilingual_and_structurally_aligned():
    for name in LESSONS:
        zh = _read("zh", name)
        en = _read("en", name)
        assert zh["nbformat"] == 4
        assert en["nbformat"] == 4
        assert [c["cell_type"] for c in zh["cells"]] == [
            c["cell_type"] for c in en["cells"]
        ], f"{name} has drifted zh/en cell structure"


def test_platform4_lessons_keep_core_teaching_sections():
    required_zh = ("概念账本", "AI Task", "Human Check", "Engineering Handoff", "Project Trace", "Exit Ticket")
    required_en = ("Concept ledger", "AI Task", "Human Check", "Engineering Handoff", "Project Trace", "Exit Ticket")

    for name in LESSONS:
        zh = _markdown(_read("zh", name))
        en = _markdown(_read("en", name))
        for marker in required_zh:
            assert marker in zh, f"zh/{name} is missing {marker}"
        for marker in required_en:
            assert marker in en, f"en/{name} is missing {marker}"


def test_primary_first_use_terms_are_expanded_near_lesson_start():
    for name, terms in FIRST_USE_TERMS.items():
        for language in ("zh", "en"):
            notebook = _read(language, name)
            opening = "\n".join(
                "".join(cell.get("source", []))
                for cell in notebook["cells"][:2]
            )
            for term in terms:
                assert term in opening, f"{language}/{name} does not expand {term} near first use"


def test_lesson13_performs_real_yosys_synthesis_dry_run():
    for language in ("zh", "en"):
        code = _code(_read(language, "13_simulation_is_not_chip.ipynb"))
        assert 'shutil.which("yosys")' in code
        assert "clocked_accumulator.sv" in code
        assert "read_verilog -sv" in code
        assert "stat; check" in code


def test_lesson17_does_not_borrow_axi_transaction_vocabulary_early():
    for language in ("zh", "en"):
        notebook = _read(language, "17_external_memory_ddr.ipynb")
        early = "\n".join(
            "".join(cell.get("source", []))
            for cell in notebook["cells"][:5]
        ).lower()
        assert "transaction" not in early
        assert "beat" not in early


def test_lesson18_states_valid_and_payload_stability_rule():
    zh = _markdown(_read("zh", "18_axi_subset.ipynb"))
    en = _markdown(_read("en", "18_axi_subset.ipynb"))
    assert "VALID 不能自行撤掉" in zh
    assert "payload/control" in zh and "保持稳定" in zh
    assert "must not withdraw VALID" in en
    assert "payload/control" in en and "remain stable" in en


def _numbered_sections(notebook):
    sections = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "markdown":
            continue
        first = "".join(cell.get("source", [])).splitlines()[0]
        match = __import__("re").match(r"^## (\d+)\. ", first)
        if match:
            sections.append((int(match.group(1)), first))
    return sections


def test_platform4_numbered_sections_are_unique_and_monotonic():
    for language in ("zh", "en"):
        for name in LESSONS:
            sections = _numbered_sections(_read(language, name))
            numbers = [number for number, _ in sections]
            assert numbers == list(range(1, len(numbers) + 1)), (
                f"{language}/{name} numbered sections are out of order or duplicated: {numbers}"
            )


def test_lesson13_student_flow_keeps_run_observe_try_exercise_order():
    expected = {
        "zh": {
            4: "Yosys",
            5: "Observe",
            6: "timing",
            7: "Run",
            8: "Observe",
            9: "Try It",
            10: "作业",
            11: "AI Task",
            12: "Human Check",
            13: "Engineering Handoff",
            14: "Project Trace",
            15: "Exit Ticket",
        },
        "en": {
            4: "Yosys",
            5: "Observe",
            6: "timing",
            7: "Run",
            8: "Observe",
            9: "Try It",
            10: "Exercise",
            11: "AI Task",
            12: "Human Check",
            13: "Engineering Handoff",
            14: "Project Trace",
            15: "Exit Ticket",
        },
    }
    for language in ("zh", "en"):
        sections = dict(_numbered_sections(_read(language, "13_simulation_is_not_chip.ipynb")))
        for number, marker in expected[language].items():
            assert marker.lower() in sections[number].lower()
