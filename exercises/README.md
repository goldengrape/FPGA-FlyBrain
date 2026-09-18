# FPGA FlyBrain Exercise Workbooks

[简体中文](README.zh-CN.md)

Python exercises use Jupyter Notebooks. Each workbook should stand on its own: explain why the task exists, what must be completed, and which constraints apply before presenting a small TODO region, an automatic check, and a Human Check.

See the full specification: [Exercise Notebook Design](../docs/en/EXERCISE_DESIGN.md).

## Student workflow

From the repository root:

~~~bash
uv sync --group dev
uv run jupyter lab
~~~

Then open the corresponding Notebook under exercises/en/.

The normal flow is:

~~~text
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
~~~

Student-facing Notebooks **do not directly show grading asserts, concrete grader vectors, or the complete grading logic**. A check cell passes the functions defined in the current Jupyter kernel to the external grader under exercises/grader/.

The grader reports conceptual groups rather than failing vectors, for example:

~~~text
Lesson 05 checks

✓ Boolean gates
✓ Threshold behavior
✗ Enable behavior

2 / 3 groups passed
~~~

Failure output may indicate which concept to revisit, but it does not print the exact failing input and expected answer.

## Python exercise index

| Lesson | Exercise Notebook | Main practice |
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

Lessons 6–8 focus on SystemVerilog, testbenches, and waveforms and continue to use the RTL learning check:

~~~bash
./scripts/check_rtl_learning.sh
~~~

Any future dedicated workbooks for Lessons 6–8 should follow the same rules: state the task before code, do not leak grading answers, and pair automatic checks with Human Checks.

## For maintainers

Student-facing grader implementations live under exercises/grader/.

Maintainer tests live under exercises/checks/. The current entry point is:

~~~bash
uv run pytest   exercises/checks/test_graders.py   exercises/checks/test_notebook_structure.py -q
~~~

test_graders.py checks that graders accept reference implementations and reject representative conceptual mistakes. test_notebook_structure.py checks that bilingual Notebooks parse, retain TODOs, use external graders, and do not embed test functions or asserts in student code cells.

The GitHub Actions Python exercise infrastructure workflow runs these checks automatically.

The project does not currently use nbgrader or testbook. They will be reconsidered only when a concrete new requirement appears.
