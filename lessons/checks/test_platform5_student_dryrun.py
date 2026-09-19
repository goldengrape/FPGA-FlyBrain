"""Student-path execution checks for Platform 5 lessons."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

EXAMPLES = [
    (
        "19_what_is_connectome.ipynb",
        (
            "neurons: 3",
            "directed edges: 3",
            "in-degree: {101: 0, 205: 1, 330: 2}",
            "out-degree: {101: 2, 205: 1, 330: 0}",
        ),
    ),
    (
        "20_load_malecns_subset.ipynb",
        (
            '"source_release": "teaching-fixture-v1"',
            '"converter_version": "teaching-converter-v1"',
            '"byte_count": 8',
            "same image: True",
            "software checksum:",
            "FPGA replay checksum:",
        ),
    ),
    (
        "21_scaling_bottlenecks.ipynb",
        (
            "small bottleneck: lookup utilization: 0.45",
            "medium bottleneck: memory utilization: 0.95",
            "large bottleneck: fifo utilization: 0.95",
        ),
    ),
    (
        "22_closed_loop_world.ipynb",
        (
            "0 right 1 1",
            "2 right 1 3",
            "position trace: [0, 1, 2, 3, 3, 3]",
        ),
    ),
    (
        "23_cpu_gpu_fpga_benchmark.ipynb",
        (
            "CPU-teaching events/s = 2000000 J/event = 0.00002000",
            "GPU-teaching events/s = 5000000 J/event = 0.00002400",
            "FPGA-teaching events/s = 4000000 J/event = 0.00000450",
        ),
    ),
]


def _code_cells(language: str, name: str) -> list[str]:
    path = ROOT / "lessons" / language / name
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return [
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    ]


@pytest.mark.parametrize("language", ["zh", "en"])
@pytest.mark.parametrize(("name", "expected"), EXAMPLES)
def test_platform5_example_cells_execute_as_students_see_them(
    language, name, expected, capsys
):
    namespace: dict[str, object] = {}
    for code in _code_cells(language, name):
        exec(compile(code, f"<{language}/{name}>", "exec"), namespace)
    output = capsys.readouterr().out
    for marker in expected:
        assert marker in output
