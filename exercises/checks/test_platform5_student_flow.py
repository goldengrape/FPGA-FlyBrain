"""End-to-end student check-cell flow for Platform 5 exercises."""

from __future__ import annotations

import hashlib
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


def _notebook(language: str, name: str):
    path = ROOT / "exercises" / language / name
    return json.loads(path.read_text(encoding="utf-8"))


def _check_cell(language: str, name: str) -> str:
    notebook = _notebook(language, name)
    code_cells = [
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    ]
    return code_cells[-1]


def degree_summary(neuron_ids, edges):
    incoming = {neuron_id: 0 for neuron_id in neuron_ids}
    outgoing = {neuron_id: 0 for neuron_id in neuron_ids}
    for source, target in edges:
        outgoing[source] += 1
        incoming[target] += 1
    return incoming, outgoing


def image_manifest(payload, schema_version):
    return {
        "schema_version": schema_version,
        "byte_count": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def bottleneck(stage_demand, stage_capacity):
    utilization = {
        stage: stage_demand[stage] / stage_capacity[stage]
        for stage in stage_demand
    }
    return utilization, max(utilization, key=utilization.get)


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


def benchmark_metrics(events, seconds, watts):
    throughput = events / seconds
    energy_per_event = watts * seconds / events
    return throughput, energy_per_event


REFERENCES = {
    "19_what_is_connectome.ipynb": {"degree_summary": degree_summary},
    "20_load_malecns_subset.ipynb": {"image_manifest": image_manifest},
    "21_scaling_bottlenecks.ipynb": {"bottleneck": bottleneck},
    "22_closed_loop_world.ipynb": {"closed_loop_trace": closed_loop_trace},
    "23_cpu_gpu_fpga_benchmark.ipynb": {"benchmark_metrics": benchmark_metrics},
}


@pytest.mark.parametrize("language", ["zh", "en"])
@pytest.mark.parametrize("name", EXERCISES)
def test_platform5_student_check_cell_accepts_reference_implementation(
    language, name, monkeypatch, capsys
):
    monkeypatch.chdir(ROOT)
    namespace = dict(REFERENCES[name])
    check_code = _check_cell(language, name)
    exec(compile(check_code, f"<exercise-check/{language}/{name}>", "exec"), namespace)
    output = capsys.readouterr().out
    assert "3 / 3 groups passed" in output
