"""End-to-end student workbook flow for Platform 5 exercises."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

EXERCISES = [
    "19_what_is_connectome.ipynb",
    "20_load_malecns_subset.ipynb",
    "21_scaling_bottlenecks.ipynb",
    "22_closed_loop_world.ipynb",
    "23_cpu_gpu_fpga_benchmark.ipynb",
]

REFERENCE_IMPLEMENTATIONS = {
    "19_what_is_connectome.ipynb": """
def degree_summary(neuron_ids, edges):
    incoming = {neuron_id: 0 for neuron_id in neuron_ids}
    outgoing = {neuron_id: 0 for neuron_id in neuron_ids}
    for source, target in edges:
        outgoing[source] += 1
        incoming[target] += 1
    return incoming, outgoing
""",
    "20_load_malecns_subset.ipynb": """
import hashlib

def image_manifest(payload, schema_version, source_release, converter_version):
    return {
        "schema_version": schema_version,
        "source_release": source_release,
        "converter_version": converter_version,
        "byte_count": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
""",
    "21_scaling_bottlenecks.ipynb": """
def bottleneck(stage_demand, stage_capacity):
    utilization = {
        stage: stage_demand[stage] / stage_capacity[stage]
        for stage in stage_demand
    }
    return utilization, max(utilization, key=utilization.get)
""",
    "22_closed_loop_world.ipynb": """
def closed_loop_trace(initial_position, target_position, steps):
    position = initial_position
    trace = [position]
    for _ in range(steps):
        if position < target_position:
            position += 1
        elif position > target_position:
            position -= 1
        trace.append(position)
    return trace
""",
    "23_cpu_gpu_fpga_benchmark.ipynb": """
def benchmark_metrics(events, seconds, watts):
    throughput = events / seconds
    energy_per_event = watts * seconds / events
    return throughput, energy_per_event
""",
}


def _notebook(language: str, name: str):
    path = ROOT / "exercises" / language / name
    return json.loads(path.read_text(encoding="utf-8"))


def _code_cells(language: str, name: str) -> list[str]:
    notebook = _notebook(language, name)
    return [
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    ]


@pytest.mark.parametrize("language", ["zh", "en"])
@pytest.mark.parametrize("name", EXERCISES)
def test_platform5_student_visible_code_cells_compile(language, name):
    for index, code in enumerate(_code_cells(language, name)):
        compile(code, f"<student-code/{language}/{name}/{index}>", "exec")


@pytest.mark.parametrize("language", ["zh", "en"])
@pytest.mark.parametrize("name", EXERCISES)
def test_platform5_student_workbook_runs_with_reference_solution(
    language, name, monkeypatch, capsys
):
    monkeypatch.chdir(ROOT)
    namespace: dict[str, object] = {}

    for index, code in enumerate(_code_cells(language, name)):
        if "YOUR CODE STARTS HERE" in code:
            code = REFERENCE_IMPLEMENTATIONS[name]
        exec(
            compile(code, f"<student-flow/{language}/{name}/{index}>", "exec"),
            namespace,
        )

    output = capsys.readouterr().out
    assert "3 / 3 groups passed" in output
