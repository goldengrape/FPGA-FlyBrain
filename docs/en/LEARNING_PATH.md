# LEARNING_PATH — Learning Architecture

## 0. Purpose

`RMD.md` answers “in what order do we build the system?” This document answers “in what conceptual order does a student learn?” The two paths run in parallel but do not replace each other.

The teaching surface has three layers:

```text
LEARNING_PATH.md
    ↓ defines concept order and learning objectives
Jupyter Notebook lessons
    ↓ explanation + experiment + AI collaboration + human check
formal engineering files (python/ rtl/ tb/ tests/)
    ↓ testable, reusable implementations that can enter CI
```

**Core boundary: a Notebook is an executable textbook and laboratory, not the source of truth for the formal implementation.** Mature algorithms, RTL, tests, and interfaces must move into ordinary source files.

## 1. Teaching design principles

### LP-1 One major unfamiliar concept per lesson
Follow the `Learning Independence Axiom` in ADD. If a lesson requires two or more major concepts the learner has not yet mastered, split it or insert a bridge lesson.

### LP-2 Start from what the learner already knows
Prefer:

```text
known neurophysiology → mathematical abstraction → executable experiment → hardware concept → formal engineering implementation
```

rather than teaching all of digital logic, HDL, or computer architecture up front.

### LP-3 AI lowers implementation friction but does not own the model
A Notebook may contain an explicit `AI Task` for generating boilerplate, tests, or explanations. It must be followed by a `Human Check` requiring the learner to explain state, inputs, outputs, timing, and the test oracle.

### LP-4 Every lesson produces something observable
At least one of: a numerical trace, waveform, event sequence, resource report, bandwidth measurement, on-board output, or visualization.

### LP-5 Every lesson has an engineering handoff
A mature Notebook experiment must migrate into a formal source path. The Notebook should then import/call the formal module rather than maintain a permanent duplicate implementation.

## 2. Standard Notebook structure

1. **What you already know** — begin from physiology or mathematical intuition.
2. **Question for this lesson** — one concrete problem.
3. **One new concept** — the primary unfamiliar concept for the lesson.
4. **Minimal model** — the smallest useful mathematical/hardware abstraction.
5. **Run** — executable experiment.
6. **Observe** — the trace, waveform, or event to inspect.
7. **AI Task** — implementation work that may be delegated to AI.
8. **Human Check** — questions the learner must answer without outsourcing understanding.
9. **Engineering Handoff** — formal source/test path and RMD slice.
10. **Exit Ticket** — criteria required before the next lesson.

## 3. First lesson set: from membrane potential to digital state

| Lesson | Notebook | Primary new concept | RMD | Engineering output |
|---|---|---|---|---|
| LSN-001 | `lessons/en/01_membrane_to_lif.ipynb` | A model is a purposeful simplification | RMD-001 | `python/reference/lif_float.py` |
| LSN-002 | `lessons/en/02_float_to_fixed.ipynb` | Finite-width numerical representation | RMD-002 | `python/reference/lif_fixed.py` + numeric decision |
| LSN-003 | `lessons/en/03_freeze_neuron_semantics.ipynb` | Freeze semantics before hardware implementation | RMD-003 | MDD/TDD/TRACE spec checkpoint |
| LSN-004 | `lessons/en/04_state_and_clock.ipynb` | Digital state and the clock | RMD-003A | Preparation and explanation for three micro hardware experiments |

### LSN-001 — From membrane potential to LIF
Starting knowledge: membrane potential, threshold, action potential, refractory period.  
Question: what is the minimum neuronal behavior we need to preserve to study network computation?  
Exit: explain the physiological and computational meaning of `V`, input, threshold, spike, and reset, and run a deterministic LIF trace.

### LSN-002 — From floating point to finite width
Starting point: a working LIF model.  
Question: why can real digital hardware not assume that `V` is an infinite-precision real number?  
Exit: explain scale, quantization, rounding, and saturation, and compare at least two width choices for their effect on spike timing.

### LSN-003 — Freeze neuron semantics
Starting point: both float and fixed-point behavior have been observed.  
Question: if AI, Python, and RTL each implement a different interpretation of LIF, which one is correct?  
Exit: define the inputs, state, outputs, update ordering, threshold/reset/refractory behavior, and numeric semantics for one update; commit the specification before RTL begins.

### LSN-004 — State and clock
Starting point: the learner understands that software variables retain values but has not learned RTL.  
Question: how can a circuit “remember” the previous membrane potential?  
Exit: explain combinational vs sequential logic, register vs clock edge, and map `variable → register`, `if → comparator/control`, and `loop → parallel/time-multiplex`.

## 4. Later learning platforms

### Platform 2: Digital neuron
SystemVerilog, testbench, waveform, and the first RTL neuron; maps to RMD-004~005A.

### Platform 3: Event neural network
RAM, time multiplexing, four-neuron event walk-through, sparse adjacency, FIFO, and event routing; maps to RMD-006~011.

### Platform 4: Physical FPGA and memory
Synthesis, bitstream, host↔FPGA, memory hierarchy, DDR, the required AXI subset, and bandwidth; maps to RMD-011A~016.

### Platform 5: Real connectome
MaleCNS converter, real subsets, scaling, the full network, closed loop, and benchmarks; maps to RMD-017~028.

## 5. Relationship between Notebooks and formal code

Notebooks may contain:
- small demonstration code;
- parameter sweeps;
- plots and waveform presentation;
- AI prompts and critique;
- experiment control and benchmark analysis.

Notebooks must not remain the only home for:
- the `lif_float` implementation;
- RTL modules;
- test oracles;
- interface or numeric specifications.

When an experiment matures:

```text
Notebook prototype
      ↓
formal source module
      ↓
unit test / oracle
      ↓
Notebook imports formal module for demonstration
```

## 6. Bilingual maintenance

- English and Chinese lessons share the same `LSN-*`, `RMD-*`, `FR/DP`, and `T-*` IDs.
- Code cells should remain identical whenever practical; translate the narrative and questions, not the engineering semantics.
- Any lesson-structure change should update both `LEARNING_PATH.md` files and the matching bilingual Notebooks in the same change.

## 7. Current teaching status

- Learning Architecture: defined.
- LSN-001~004: first executable Notebook versions being established.
- First formal implementation: still `RMD-001`; it is not yet declared complete.
