# FPGA FlyBrain exercises and checks

The Python-exercise lessons use one consistent homework pattern: **fixed function signatures + small TODO regions + public pytest checks + a Human Check**.

The purpose is not to test Python cleverness. It is to verify that you can translate the lesson's model rules into a testable function. Keep function names, arguments, and return shapes unchanged unless a lesson explicitly asks otherwise; the interface is part of the specification.

## Running the checks

```bash
uv sync --group dev
uv run pytest exercises/checks/check_lesson01.py -q
```

The files are intentionally named `check_lessonXX.py` instead of ordinary `test_*.py`. Unfinished student exercises therefore do not get collected by a normal project test run; they run only when explicitly requested.

The checks are public. Read them. The course treats tests as executable specifications, not as hidden answers.

Passing the automated checks means your code satisfies the behavior covered by the current public tests. It does not by itself demonstrate conceptual understanding. Each lesson also has a Human Check that you should be able to explain in your own words without having AI answer it for you.

AI may help explain failures, compare implementations, propose extra tests, or review code. If AI writes a TODO region, you should still complete the Human Check and manually work through at least one test case.

## Python exercise lessons

| Lesson | Starter | Check | Main target |
|---|---|---|---|
| 01 | `lesson01_lif.py` | `check_lesson01.py` | leak, integration, `>=` threshold, reset |
| 02 | `lesson02_fixed_point.py` | `check_lesson02.py` | signed range, rounding, quantization, saturation |
| 03 | `lesson03_semantics.py` | `check_lesson03.py` | frozen semantics and distinguishing probes |
| 04 | `lesson04_state_clock.py` | `check_lesson04.py` | combinational next-state logic and clocked state |
| 05 | `lesson05_logic.py` | `check_lesson05.py` | Boolean gates, threshold boundary, enable logic |
| 09 | `lesson09_time_multiplexing.py` | `check_lesson09.py` | addressed state and round-robin service |
| 10 | `lesson10_fifo.py` | `check_lesson10.py` | FIFO ordering, full/empty, backpressure |
| 11 | `lesson11_sparse_graph.py` | `check_lesson11.py` | source index and exact sparse ranges |
| 12 | `lesson12_event_journey.py` | `check_lesson12.py` | one source spike to weighted target events |

Run a selected lesson explicitly, or run the current Python exercise set with:

```bash
uv run pytest \
  exercises/checks/check_lesson01.py \
  exercises/checks/check_lesson02.py \
  exercises/checks/check_lesson03.py \
  exercises/checks/check_lesson04.py \
  exercises/checks/check_lesson05.py \
  exercises/checks/check_lesson09.py \
  exercises/checks/check_lesson10.py \
  exercises/checks/check_lesson11.py \
  exercises/checks/check_lesson12.py -q
```

Starter files initially raise `NotImplementedError`, so failures before completing the TODO regions are expected.

### Lesson 1
Implement `leak_step(...)` and `lif_step(...)`. Human Check: manually evaluate `V=-60, V_rest=-70, alpha=0.9, input=11, threshold=-50` and explain why it is a threshold boundary case.

### Lesson 2
Implement `signed_limits(...)` and `quantize(...)` using Python `round()` and saturation. Human Check: explain the range-versus-precision tradeoff when `total_bits` stays fixed while `frac_bits` increases.

### Lesson 3
Implement the frozen `lif_step_v0(...)` contract, then construct one case that distinguishes `>=` from `>` and one that distinguishes `alpha * v + current` from `alpha * (v + current)`. The checker validates the property of your cases rather than requiring predetermined numbers.

### Lesson 4
Implement `combinational_step(...)`, `clock_edge(...)`, and the clocked update in `run_clocked_accumulator(...)`. Human Check: explain how `candidate_state=4` and `state_after=0` can both be correct in the same cycle.


### Lesson 5
Implement NOT / AND / OR plus threshold and enable logic. Human Check: explain why `candidate == threshold` is the most direct probe for `>=` versus `>`.

### Lesson 9
Implement addressed state updates and one round-robin service pass. Human Check: explain why the address selects state but is not itself neuron state, and how one physical engine can serve many virtual neurons.

### Lesson 10
Implement bounded FIFO push/pop. Human Check: explain why a full queue must produce backpressure rather than overwrite an older spike.

### Lesson 11
Build a project-style `(start,count)` source index plus contiguous synapse records. Human Check: reconstruct every source range by hand, including a source with zero fanout.

### Lesson 12
Process one source spike through exactly its sparse synapse range. Human Check: distinguish what is stored in the spike queue, source index, synapse record, and target accumulator.

Lessons 6–8 use HDL compile/simulation/lint checks rather than Python TODO exercises; see `./scripts/check_rtl_learning.sh`.
