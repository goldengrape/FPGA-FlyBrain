"""End-to-end student workbook flow for Platform 5 exercises."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.start_exercise import create_work_copy


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
def test_platform5_student_visible_code_cells_compile(language, name):
    for index, code in enumerate(_code_cells(_template(language, name))):
        compile(code, f"<student-code/{language}/{name}/{index}>", "exec")


@pytest.mark.parametrize("language", ["zh", "en"])
@pytest.mark.parametrize("name", EXERCISES)
def test_platform5_student_workbook_runs_from_personal_work_copy(
    language, name, tmp_path, monkeypatch, capsys
):
    lesson = name[:2]
    fake_repo = tmp_path / "repo"
    template = fake_repo / "exercises" / language / name
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(_template(language, name).read_text(encoding="utf-8"), encoding="utf-8")

    work_copy, created = create_work_copy(fake_repo, lesson, language)
    assert created
    assert work_copy == fake_repo / "exercises" / "work" / language / name

    # The grader bootstrap in the workbook searches upward for exercises/grader.
    # Point execution at the real repository so the same import path a learner
    # sees is exercised, while the personal workbook itself remains a temp copy.
    monkeypatch.chdir(ROOT)
    namespace: dict[str, object] = {}

    for index, code in enumerate(_code_cells(work_copy)):
        if "YOUR CODE STARTS HERE" in code:
            code = REFERENCE_IMPLEMENTATIONS[name]
        exec(
            compile(code, f"<student-flow/{language}/{name}/{index}>", "exec"),
            namespace,
        )

    output = capsys.readouterr().out
    assert "3 / 3 groups passed" in output
