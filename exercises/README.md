# FPGA FlyBrain Exercise Workbooks

[简体中文](README.zh-CN.md)

Python exercises use Jupyter Notebooks. Each workbook should stand on its own: explain why the task exists, what must be completed, and which constraints apply before presenting a small TODO region, an automatic check, and a Human Check.

See the full specification: [Exercise Notebook Design](../docs/en/EXERCISE_DESIGN.md).

## Student workflow

### 1. Do not edit the official starter in place

`exercises/zh/` and `exercises/en/` contain the Git-tracked **official exercise templates**. They may change as the course evolves, so they are not the right place for long-lived personal answers.

Student work belongs under:

```text
exercises/work/
├── zh/
└── en/
```

The entire `exercises/work/` directory is ignored by Git, so normal `git status`, commits, and `git pull` do not treat your answers as course source files.

### 2. Start an exercise with one command

From the repository root:

```bash
uv sync --group dev
uv run python scripts/start_exercise.py 01 --lang en
```

This creates:

```text
exercises/work/en/01_membrane_to_lif.ipynb
```

Then launch:

```bash
uv run jupyter lab
```

In JupyterLab, open the copy under **`exercises/work/en/`**, not the official starter under `exercises/en/`.

Other examples:

```bash
# Lesson 11 in English
uv run python scripts/start_exercise.py 11 --lang en

# Lesson 1 in Chinese
uv run python scripts/start_exercise.py 01

# Create all current English Python exercises
uv run python scripts/start_exercise.py all --lang en

# Create all current Chinese Python exercises
uv run python scripts/start_exercise.py all
```

The helper **never overwrites an existing student copy**. Running the same command again reports:

```text
Already exists, kept unchanged: exercises/work/en/01_membrane_to_lif.ipynb
```

so it is safe to rerun.

### 3. Normal exercise flow

```text
official starter
  ↓ copied once by start_exercise.py
personal work notebook
  ↓
read the task
  ↓
predict / hand-calculate
  ↓
complete the TODO
  ↓
run “Check your implementation”
  ↓
revise if needed
  ↓
complete the Human Check
```

Student-facing Notebooks **do not directly show grading asserts, concrete grader vectors, or the complete grading logic**. A check cell passes functions from the current Jupyter kernel to the external grader under `exercises/grader/`.

### 4. Course updates do not overwrite your answers

Later you can update the repository normally:

```bash
git pull
```

Git updates the official templates and course source. Your `exercises/work/` directory is untracked, so course updates do not create Notebook merge conflicts with your answers.

If an official starter changes, you may keep using your existing work copy. To start again from a newer starter, first back up or rename your old work file, then run `start_exercise.py` again. The helper never deletes or overwrites existing work.

### 5. If you already edited an official Notebook

If you started before the `exercises/work/` workflow existed and your answers are still in a tracked file such as:

```text
exercises/en/01_membrane_to_lif.ipynb
```

first run:

```bash
uv run python scripts/start_exercise.py 01 --lang en
```

The helper copies your **current local version**, including your answers, into `exercises/work/en/`. After verifying that personal copy, restore the official starter:

```bash
git restore exercises/en/01_membrane_to_lif.ipynb
```

Your answers and course source are now separated.

## Python exercise index

The links below point to official starters for reading and version tracking. When doing an exercise, use `start_exercise.py` to create a personal `work/` copy.

| Lesson | Official Exercise Notebook | Main practice |
|---|---|---|
| 01 | [One LIF membrane update](en/01_membrane_to_lif.ipynb) | leak, integration, threshold, reset |
| 02 | [Finite-width values](en/02_float_to_fixed.ipynb) | signed range, rounding, quantization, saturation |
| 03 | [Explicit LIF specification](en/03_freeze_neuron_semantics.ipynb) | frozen semantics, boundaries, counterexamples |
| 04 | [Next state and register state](en/04_state_and_clock.ipynb) | combinational next-state, clock edge, state history |
| 05 | [Logic gates, comparison, and enable](en/05_logic_building_blocks.ipynb) | Boolean logic, threshold, enable |
| 09 | [One engine serving many states](en/09_time_multiplex_many_neurons.ipynb) | addressed state, round robin |
| 10 | [Bounded FIFO and backpressure](en/10_spike_fifo_backpressure.ipynb) | FIFO ordering, full/empty, retry |
| 11 | [Sequential sparse lookup representation](en/11_sparse_synapse_lookup.ipynb) | source index, contiguous records, zero fanout |
| 12 | [The journey of one source spike](en/12_one_spike_journey.ipynb) | source range, weighted event, target accumulator |
| 13 | [Read a timing budget](en/13_simulation_is_not_chip.ipynb) | critical path, slack, timing pass/fail |
| 14 | [Turn a board clock into an observable tick](en/14_what_is_fpga_board.ipynb) | board clock, counter width, observable tick |
| 15 | [Model a host ↔ programmable-logic roundtrip](en/15_host_talks_to_fpga.ipynb) | persistent PL state, readback ordering |
| 16 | [Identify compute / data-movement bottleneck](en/16_data_movement_cost.ipynb) | latency, bandwidth, simple cost model |
| 17 | [Estimate sequential/random burst cost](en/17_external_memory_ddr.ipynb) | burst grouping, setup cost, access pattern |
| 18 | [Identify VALID/READY accepted beats](en/18_axi_subset.ipynb) | handshake, stall, accepted beat |
| 19 | [Compute connectome in/out degree](en/19_what_is_connectome.ipynb) | directed graph structure, zero-degree neurons |
| 20 | [Build a minimal image manifest](en/20_load_malecns_subset.ipynb) | schema version, byte count, SHA-256 integrity |
| 21 | [Identify the highest-utilization stage](en/21_scaling_bottlenecks.ipynb) | utilization, scale-dependent bottleneck |
| 22 | [Generate a closed-loop position trace](en/22_closed_loop_world.ipynb) | feedback, target-reaching trace |
| 23 | [Calculate throughput and energy per event](en/23_cpu_gpu_fpga_benchmark.ipynb) | benchmark metrics, duration-aware energy |

Lessons 13–18 enter FPGA-board, host, DDR, and AXI topics, but their formal workbooks remain **board-independent** Python/reasoning exercises. Physical-board labs are engineering extensions of the matching RMD slices, so hardware purchase does not block course progress.

Lessons 19–23 enter connectome integrity, scaling, closed-loop experiments, and benchmarking. Their official exercises use teaching fixtures and synthetic measurements so full MaleCNS downloads, a finished converter, GPU access, and a physical FPGA are not prerequisites for learning the contracts.

Lessons 6–8 focus on SystemVerilog, testbenches, and waveforms and continue to use the RTL learning check:

```bash
./scripts/check_rtl_learning.sh
```

## For maintainers

Student-facing grader implementations live under `exercises/grader/`.

Maintainer tests live under `exercises/checks/`. The current entry point is:

```bash
uv run pytest \
  exercises/checks/test_graders.py \
  exercises/checks/test_notebook_structure.py \
  exercises/checks/test_start_exercise.py \
  lessons/checks/test_platform4_notebook_structure.py \
  lessons/checks/test_platform4_student_dryrun.py \
  lessons/checks/test_platform5_notebook_structure.py \
  lessons/checks/test_platform5_student_dryrun.py -q
```

`test_start_exercise.py` verifies lesson selection, work-copy paths, and the guarantee that existing student answers are never overwritten.

The GitHub Actions Python exercise infrastructure workflow runs the exercise-infrastructure checks automatically.

The project does not currently use nbgrader or testbook. They will be reconsidered only when a concrete new requirement appears.
