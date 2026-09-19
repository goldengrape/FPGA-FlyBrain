# Exercise Notebook Design Specification

## 1. Purpose

FPGA FlyBrain exercises are not bare code-completion files. They are self-contained electronic workbooks that can be read, run, checked, and reflected on in one place.

Lesson Notebooks teach concepts. Exercise Notebooks ask the learner to turn those concepts into executable understanding through code, hand calculation, prediction, and explanation. A learner should not have to jump among a README, a starter Python file, and a test file just to discover what an assignment is asking.

This specification applies primarily to Python exercises. RTL lessons use the same teaching structure with compile, simulation, lint, and waveform checks instead.

## 2. Core principles

Every Exercise Notebook must:

1. **Stand on its own.** Opening the Notebook alone should reveal which lesson it belongs to, what is being practiced, why it matters, and what completion means.
2. **State the task before the code.** Background, requirements, and constraints come before TODO cells.
3. **Avoid turning tests into hints.** Student-facing Notebooks do not directly show assert statements, concrete grader vectors, or full grading logic.
4. **Provide immediate feedback.** After a small task, the learner can check the current implementation in the active Jupyter kernel.
5. **Separate execution checks from explanation.** Automatic checks validate behavior; Human Check prompts validate the learner's ability to explain concepts and boundaries.
6. **Keep interfaces stable.** Function names, arguments, and return values are part of the course contract unless the assignment explicitly says otherwise.
7. **Do not treat visibility as a security boundary.** This is an open-source self-study course. External graders exist to keep grading logic out of the visible workbook, not to prevent a determined learner from reading repository source.

## 3. Student-facing Notebook structure

Python exercises follow this general order:

1. Title and corresponding lesson
2. Why this exercise exists
3. What you will complete
4. Rules and constraints
5. Hand-work / prediction / small example
6. Student code cell
7. Check your implementation
8. Human Check
9. Optional extension

Not every task must mechanically use all nine headings, but the information must be present and preserve the sequence: explain → implement → check → explain again.

### 3.1 State the semantic contract before showing code

**A function signature is not a substitute for assignment prose.** Before the learner sees the code, the workbook must explain in natural language what the function means in the current model.

For every function the learner must implement, state at least:

- **Role**: what step of the model or data flow the function performs;
- **Inputs**: what each argument means in the course context, not only its Python type;
- **Outputs**: how many results are produced and what each result represents;
- **Return order**: for tuples / multiple values, explain item 1, item 2, item 3, and so on;
- **Time/state meaning**: when state, next state, candidate, or events belong to different stages or time steps, say so explicitly;
- **Side effects**: whether inputs such as lists or state objects may be modified.

For example, do not rely only on:

~~~python
def lif_step(...) -> tuple[float, bool]:
    ...
~~~

Explain first:

> Return `(next_v, spike)`.  
> `next_v` is the membrane voltage stored for the next time step after this update.  
> `spike` is a Boolean indicating whether this update emits a spike.

The learner should understand the assignment even if they are not yet comfortable reading Python type annotations such as `tuple[float, bool]`.

### 3.2 Student code cells

TODO regions should stay small and contain only what the lesson actually asks the learner to implement. Boilerplate, I/O, testing infrastructure, and unrelated course machinery should stay outside the TODO.

Example:

~~~python
def threshold_reached(value: int, threshold: int) -> bool:
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO")
    # YOUR CODE ENDS HERE
~~~

### 3.3 Check cells

The Notebook does not contain pytest test functions. It imports an external grader and passes the learner's current in-kernel functions to it.

Example:

~~~python
from exercises.grader.lesson05 import check

check(
    gate_not=gate_not,
    gate_and=gate_and,
    gate_or=gate_or,
    threshold_reached=threshold_reached,
    spike_enabled=spike_enabled,
)
~~~

The grader therefore checks the implementation that the learner has just executed in the current kernel. There is no need to export the Notebook to a Python module or restart the kernel.

## 4. Grader design

Graders live under exercises/grader/ and each lesson exposes a simple public check(...) entry point.

A grader should accept callables or other required objects defined in the current Notebook, run enough checks to decide whether the lesson contract is satisfied, catch internal assertions and exceptions, print concise student-readable results, and avoid revealing concrete test vectors, expected values, or internal assertion expressions.

Recommended output:

~~~text
Lesson 05 checks

✓ Boolean logic
✓ Threshold behavior
✗ Enable behavior

7 / 8 checks passed
~~~

A conceptual hint such as “check behavior when enable is off” is acceptable. Printing the exact failing input and expected result is not.

The grader does not teach the assignment, expose the full test suite inside the Notebook, prove conceptual understanding, or prevent a learner from intentionally opening grader source.

## 5. Testing the graders

Graders are course infrastructure and must themselves be tested with ordinary pytest tests under exercises/checks/.

Maintainer tests should verify at least:

1. a correct reference implementation passes;
2. representative incorrect implementations are rejected, such as > instead of >=, FIFO overwrite on full, or an incorrect sparse range.

These pytest tests are maintainer-facing and are not shown as part of the student workbook.

At the current stage the project does not introduce nbgrader or testbook. They may be reconsidered only when there is a concrete teacher-release, student-submission, or full-Notebook execution requirement.

## 6. Human Check

Each exercise includes at least one prompt that cannot be answered merely by seeing “tests passed,” for example:

- hand-calculate a state update;
- explain why a boundary condition matters;
- state what a data structure stores and what it does not store;
- predict the effect of a parameter change, then run it;
- distinguish old state, candidate state, and stored state within one cycle.

AI may help explain errors, compare implementations, or generate extra practice, but the learner should attempt Human Check prompts independently first.

## 7. File layout

Python exercises migrate to:

~~~text
exercises/
├── README.md
├── README.zh-CN.md
├── grader/
│   ├── __init__.py
│   ├── lesson01.py
│   ├── lesson02.py
│   ├── lesson03.py
│   ├── lesson04.py
│   ├── lesson05.py
│   ├── lesson09.py
│   ├── lesson10.py
│   ├── lesson11.py
│   ├── lesson12.py
│   ├── lesson13.py
│   ├── lesson14.py
│   ├── lesson15.py
│   ├── lesson16.py
│   ├── lesson17.py
│   └── lesson18.py
├── checks/
│   └── ...
├── en/
│   └── ...
└── zh/
    ├── 01_membrane_to_lif.ipynb
    ├── 02_float_to_fixed.ipynb
    ├── 03_freeze_neuron_semantics.ipynb
    ├── 04_state_and_clock.ipynb
    ├── 05_logic_building_blocks.ipynb
    ├── 09_time_multiplex_many_neurons.ipynb
    ├── 10_spike_fifo_backpressure.ipynb
    ├── 11_sparse_synapse_lookup.ipynb
    ├── 12_one_spike_journey.ipynb
    ├── 13_simulation_is_not_chip.ipynb
    ├── 14_what_is_fpga_board.ipynb
    ├── 15_host_talks_to_fpga.ipynb
    ├── 16_data_movement_cost.ipynb
    ├── 17_external_memory_ddr.ipynb
    └── 18_axi_subset.ipynb
~~~

Exercise Notebook names should match their lesson counterparts whenever practical.

Lessons 6–8 focus on SystemVerilog, testbenches, and waveforms, so they are not forced into Python exercise Notebooks. Their HDL exercises will follow the same workbook principles later.

Lessons 13–18 enter physical-hardware and external-memory topics, but their formal workbooks deliberately remain board-independent semantic/performance models. Physical-board steps, DDR controllers, and platform-specific procedures belong to the matching RMD engineering labs rather than becoming coursework prerequisites.

## 8. Definition of done

A Python exercise migration is complete only when:

- the Notebook is understandable on its own;
- every learner-implemented function has a natural-language semantic contract before its code, stating role, inputs, outputs, return order, and any necessary time/state meaning;
- TODOs remain unsolved and do not leak answers;
- the Notebook does not directly show assert statements or full grader vectors;
- the grader can check the current in-kernel implementation;
- failure messages do not reveal the answer;
- the grader has maintainer pytest coverage;
- Human Check prompts match the lesson's primary concept;
- README paths and running instructions are updated;
- Chinese and English versions preserve the same structure and requirements.

## 9. Current decision

As of 2026-09-18 the project uses:

~~~text
Lesson Notebook
    → textbook chapter

Exercise Notebook
    → formal workbook

external grader
    → immediate student checks without showing asserts

pytest
    → maintainer validation of graders and course rules

Human Check
    → conceptual explanation
~~~

The project does not currently introduce nbgrader, testbook, or Notebook-output-snapshot grading as the primary mechanism. Those tools should be added only in response to a concrete need, rather than as up-front infrastructure.
