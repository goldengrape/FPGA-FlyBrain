#!/usr/bin/env python3
"""Create a Git-ignored working copy of an FPGA FlyBrain exercise notebook."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


EXERCISE_FILES = {
    "01": "01_membrane_to_lif.ipynb",
    "02": "02_float_to_fixed.ipynb",
    "03": "03_freeze_neuron_semantics.ipynb",
    "04": "04_state_and_clock.ipynb",
    "05": "05_logic_building_blocks.ipynb",
    "06": "06_what_is_rtl.ipynb",
    "07": "07_first_rtl_neuron.ipynb",
    "08": "08_testbench_waveform_simulation.ipynb",
    "09": "09_time_multiplex_many_neurons.ipynb",
    "10": "10_spike_fifo_backpressure.ipynb",
    "11": "11_sparse_synapse_lookup.ipynb",
    "12": "12_one_spike_journey.ipynb",
    "13": "13_simulation_is_not_chip.ipynb",
    "14": "14_what_is_fpga_board.ipynb",
    "15": "15_host_talks_to_fpga.ipynb",
    "16": "16_data_movement_cost.ipynb",
    "17": "17_external_memory_ddr.ipynb",
    "18": "18_axi_subset.ipynb",
    "19": "19_what_is_connectome.ipynb",
    "20": "20_load_malecns_subset.ipynb",
    "21": "21_scaling_bottlenecks.ipynb",
    "22": "22_closed_loop_world.ipynb",
    "23": "23_cpu_gpu_fpga_benchmark.ipynb",
}


def normalize_lesson(value: str) -> str:
    value = value.strip().lower()
    if value == "all":
        return value

    if value.startswith("lesson"):
        value = value.removeprefix("lesson")

    if not value.isdigit():
        raise ValueError(f"Unknown lesson: {value!r}")

    lesson = f"{int(value):02d}"
    if lesson not in EXERCISE_FILES:
        available = ", ".join(EXERCISE_FILES)
        raise ValueError(
            f"Lesson {lesson} has no Python Exercise Notebook. "
            f"Available: {available}, or 'all'."
        )
    return lesson


def create_work_copy(
    repo_root: Path,
    lesson: str,
    language: str,
) -> tuple[Path, bool]:
    """Return (destination, created). Existing student work is never overwritten."""
    filename = EXERCISE_FILES[lesson]
    source = repo_root / "exercises" / language / filename
    destination = repo_root / "exercises" / "work" / language / filename

    if not source.is_file():
        raise FileNotFoundError(f"Official exercise template not found: {source}")

    if destination.exists():
        return destination, False

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination, True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a personal, Git-ignored working copy of an Exercise Notebook. "
            "Existing work is never overwritten."
        )
    )
    parser.add_argument(
        "lesson",
        help="Lesson number such as 01 or 11, or 'all'.",
    )
    parser.add_argument(
        "--lang",
        choices=("zh", "en"),
        default="zh",
        help="Exercise language (default: zh).",
    )
    args = parser.parse_args()

    try:
        lesson = normalize_lesson(args.lesson)
    except ValueError as exc:
        parser.error(str(exc))

    repo_root = Path(__file__).resolve().parents[1]
    lessons = list(EXERCISE_FILES) if lesson == "all" else [lesson]

    created = 0
    existing = 0

    for item in lessons:
        destination, was_created = create_work_copy(repo_root, item, args.lang)
        relative = destination.relative_to(repo_root)

        if was_created:
            created += 1
            print(f"Created: {relative}")
        else:
            existing += 1
            print(f"Already exists, kept unchanged: {relative}")

    print()
    if created:
        print("Open the file(s) above in JupyterLab and do your work there.")
    if existing:
        print("Existing student work was not overwritten.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
