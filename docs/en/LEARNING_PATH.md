# LEARNING_PATH — Learning Architecture

## 0. What this document is for

`RMD.md` answers “in what order do we build the system?” This document answers “in what conceptual order does a student learn?” The two paths are traceable to each other, but neither replaces the other.

The typical learner has taken basic university physiology and understands membrane potential, action potentials, and synapses, but has little or no digital-hardware background. Therefore the course must not treat abbreviations such as `FPGA`, `LIF`, `RTL`, `FIFO`, or `AXI` as assumed knowledge.

The teaching surface has three layers:

```text
LEARNING_PATH.md
    ↓ defines concept order, terminology order, and learning objectives
Jupyter Notebook lessons
    ↓ textbook-style explanation + laboratory-style execution + AI collaboration + human checks
formal engineering files (python/ rtl/ tb/ tests/)
    ↓ testable, reusable implementations that can enter CI
```

**Core boundary: a Notebook is an executable textbook plus laboratory, not the sole source of truth for the formal implementation.** Mature algorithms, RTL, tests, and interfaces move into ordinary source files; the Notebook then imports/calls them for teaching experiments.

---

## 1. Learner promise

The course assumes the learner:

- broadly understands membrane potential, action potential, threshold, synapse, excitation/inhibition, and refractory period;
- knows basic algebra, introductory calculus, vectors, and matrices;
- may have heard of AND / OR / NOT but is not expected to know digital-circuit design;
- is **not expected** to know FPGA, HDL, RTL, SystemVerilog, RAM, FIFO, DDR, AXI, or computer architecture;
- may learn Python as the course proceeds.

If a concept is not in the assumed knowledge above, the course must explain it the first time it is used.

---

## 2. Terminology and abbreviation rules

### LP-T1 Expand every abbreviation on first use

The first use of an abbreviation must follow this pattern:

> **English Full Name (ABBR)**: a one-sentence plain-language definition, followed by why the learner needs it now.

Examples:

> **Field-Programmable Gate Array (FPGA)**: a chip whose digital circuitry can be configured after manufacturing to implement our own hardware design. This project will eventually turn neuron computation into real digital circuits inside an FPGA.

> **Leaky Integrate-and-Fire (LIF)**: a neuron model that keeps only a few behaviors: membrane state decays, inputs accumulate, and crossing a threshold emits a spike and resets the state.

Only after that may the lesson use `FPGA` or `LIF` alone.

### LP-T2 No acronym waterfalls

If a paragraph contains several unfamiliar abbreviations, split it. A lesson has one primary new concept; supporting terms may appear, but each must be introduced explicitly.

### LP-T3 Each Notebook should remain readable on its own

Even if an abbreviation was introduced in the previous lesson, the first appearance in the current lesson should include a brief reminder.

### LP-T4 Project IDs must not compete with teaching

`FR1`, `DP2`, `RMD-003A`, and `T-006` are traceability IDs, not learner concepts. They belong in a **Project Trace** section near the end of the lesson, not in the opening screen.

### LP-T5 The global glossary is backup, not an excuse

`docs/en/GLOSSARY.md` is a reference, but “look it up in the glossary” never replaces first-use explanation.

---

## 3. Teaching design principles

### LP-1 One major unfamiliar concept per lesson
Follow the `Learning Independence Axiom` in ADD. If a lesson requires two or more still-unmastered major concepts, split the lesson or insert a bridge lesson.

### LP-2 Start from what the learner already knows
Prefer:

```text
known neurophysiology
    ↓
one concrete question
    ↓
mathematical/computational abstraction
    ↓
executable experiment
    ↓
one new hardware concept
    ↓
formal engineering implementation
```

rather than teaching all of digital logic, HDL, or computer architecture up front.

### LP-3 Build intuition, then define, then code
A new term should not appear “incidentally” inside code. Preferred order:

1. why the problem appears;
2. an intuitive analogy;
3. a precise definition;
4. the smallest example;
5. code or circuit;
6. observation;
7. return to the definition and explain the result.

### LP-4 AI lowers implementation friction but does not own the model
A Notebook may include an `AI Task` for boilerplate, tests, or explanations. It must be followed by a `Human Check` that requires the learner to explain state, inputs, outputs, timing, and the test oracle.

### LP-5 Every lesson produces something observable
At least one of: a numerical trace, plot, waveform, event sequence, resource report, bandwidth measurement, on-board output, or visualization.

### LP-6 Every lesson has an engineering handoff
A mature Notebook experiment migrates into formal source. The Notebook later imports the formal module rather than maintaining a shadow implementation.

### LP-7 Every lesson maintains a concept ledger
Each Notebook should state:

- **already known before this lesson**;
- **first learned in this lesson**;
- **preview only — not yet required**.

This prevents preview terms from quietly becoming assumed knowledge.

### LP-8 Use declarative diagram syntax (Mermaid), avoid ASCII art

All conceptual flows, dataflow graphs, state transition diagrams, clock timing relationships, and hardware block diagrams must be expressed using declarative diagram code (primarily Mermaid fenced blocks: ```` ```mermaid ````). Do not draw diagrams by manually aligning spaces, hyphens, and slashes as ASCII art.

**Engineering rationale:**

1. **Rendering stability**: ASCII art relies on rigid monospace fonts and breaks easily across operating systems, mobile viewports, variable-width fonts, and screen readers;
2. **Native vector rendering**: Modern JupyterLab 4, GitHub web viewer, and modern IDEs natively render Mermaid into crisp vector diagrams without extra plugins;
3. **Traceability and Git diffs**: Declarative diagrams represent graph structure and semantics (`A --> B`). Modifying nodes or connections produces minimal, readable Git diffs, avoiding full-block whitespace realignments;
4. **Human-AI collaboration**: Structured diagram code is precise and easy for both humans and AI to inspect, edit, and validate programmatically.

---

## 4. Recommended Notebook structure

1. **Welcome and where we are**.
2. **What you already know**.
3. **One question for today**.
4. **Term cards** for first-use vocabulary.
5. **Intuitive model**.
6. **Precise model/definition**.
7. **Read the minimal code or circuit line by line**.
8. **Run**.
9. **Observe** — explicitly tell the learner what to look for.
10. **Try It** — change one thing, predict first, then run.
11. **AI Task**.
12. **Human Check**.
13. **Engineering Handoff**.
14. **Project Trace** — LSN/RMD/FR/DP/T IDs, placed near the end.
15. **Exit Ticket**.

Notebook Markdown is textbook content, not decoration between code cells.

---

## 5. First lesson set: from membrane potential to digital state

| Lesson | Notebook | Primary new concept | Engineering mapping |
|---|---|---|---|
| LSN-001 | `lessons/en/01_membrane_to_lif.ipynb` | Scientific models are purposeful simplifications; meet LIF | RMD-001 |
| LSN-002 | `lessons/en/02_float_to_fixed.ipynb` | Finite-width numerical representation | RMD-002 |
| LSN-003 | `lessons/en/03_freeze_neuron_semantics.ipynb` | Freeze testable semantics before implementation | RMD-003 |
| LSN-004 | `lessons/en/04_state_and_clock.ipynb` | Digital state and the clock | RMD-003A |

### LSN-001 — From membrane potential to LIF
Explain what a Jupyter Notebook is, briefly introduce FPGA as the destination, then fully unpack **Leaky Integrate-and-Fire (LIF)** word by word. The learner is not expected to understand FPGA internals yet.

### LSN-002 — From floating point to finite width
Explain bit, binary, floating point, fixed point, quantization, rounding, overflow, and saturation before the width experiments. State clearly that Python `float` is also finite precision.

### LSN-003 — Freeze neuron semantics
Explain specification, semantics, and test oracle. Use minimal counterexamples such as `>=` versus `>` and update ordering to show that sharing the name “LIF” does not guarantee identical behavior.

### LSN-004 — State and clock
Start from “how does a software variable remember a value?” Introduce combinational logic, state/register, clock/clock edge, and next state. SystemVerilog and RTL are previews only, not mastery targets in this lesson.

---

## 6. Planned concept path for later lessons

The sequence below is a teaching plan; these Notebooks are not all created yet.

### Platform 2: from digital state to the first RTL neuron

| Planned lesson | First-use concepts | Engineering mapping |
|---|---|---|
| LSN-005 Digital logic building blocks | bit, Boolean logic, AND/OR/NOT, comparator | RMD-003A |
| LSN-006 What is RTL? | Register-Transfer Level, HDL, SystemVerilog, module/port | prepares RMD-004 |
| LSN-007 First RTL neuron | combinational path, sequential update, `always_comb`/`always_ff` | RMD-004 teaching precursor |
| LSN-008 How do we know hardware is correct? | testbench, waveform, simulation | RMD-005/005A |

### Platform 3: many neurons become an event computer

| Planned lesson | First-use concepts | Engineering mapping |
|---|---|---|
| LSN-009 One compute unit serves many neurons | time multiplexing; memory/address/RAM as supporting terms | RMD-006/007 |
| LSN-010 Why spikes need a queue | bounded FIFO and backpressure | RMD-007A/009 |
| LSN-011 Do not scan every synapse | sparse graph, adjacency list, CSR-like source index | RMD-008 |
| LSN-012 The complete journey of one spike | event-driven computation; integrate queue/lookup/weighted events | RMD-007A/010/011 |

> **Teaching order and RMD engineering implementation order do not have to match step-for-step.** LSN-010/011 isolate queue/backpressure and sparse lookup with Python first; LSN-012 then performs the RMD-007A-style end-to-end integration. RMD-007A still precedes formal MOD-006/007/005 RTL implementation.

### Platform 4: from simulation to real FPGA and external memory

| Lesson | First-use concepts | Engineering mapping |
|---|---|---|
| LSN-013 Simulation is not a chip | synthesis, implementation, timing, bitstream | RMD-011A |
| LSN-014 What is an FPGA board? | FPGA, I/O, clock/reset, development board | RMD-012/012A |
| LSN-015 How does the computer talk to the FPGA? | host, CPU, SoC, programmable logic | RMD-012B/013 |
| LSN-016 Why moving data can be harder than adding | memory hierarchy, latency, throughput, bandwidth | RMD-013A |
| LSN-017 What is external memory? | DDR, burst, random vs sequential access | RMD-014 |
| LSN-018 Learn only the AXI we need | Advanced eXtensible Interface (AXI), transaction, valid/ready | RMD-014A/015/016 |

### Platform 5: real connectome and full system

| Planned lesson | First-use concepts | Engineering mapping |
|---|---|---|
| LSN-019 What is a connectome? | connectome, neuron ID, edge, metadata | RMD-017 |
| LSN-020 First real MaleCNS subset | manifest, checksum, differential test | RMD-018 |
| LSN-021 What changes when scale grows? | bottleneck, utilization, hotspot | RMD-019~022 |
| LSN-022 Give the fly a world | sensory encoder, decoder, closed loop | RMD-023~025 |
| LSN-023 Run the same experiment on three machines | CPU, GPU, FPGA, latency/throughput/power | RMD-028 |

---

## 7. Relationship between Notebooks and formal code

Notebooks may contain:
- full teaching narrative;
- small demonstration code;
- parameter sweeps;
- plots, waveforms, and visualization;
- AI prompts and critique;
- experiment control and benchmark analysis.

Notebooks must not remain the only home for:
- `lif_float`;
- RTL modules;
- test oracles;
- interface/numeric specifications.

When mature:

```text
Notebook prototype
      ↓
formal source module
      ↓
unit test / oracle
      ↓
Notebook imports formal module for teaching and experiments
```

---

## 8. Bilingual maintenance

- English and Chinese lessons share the same `LSN-*`, `RMD-*`, `FR/DP`, and `T-*` IDs.
- Code cells should remain identical whenever practical; translate narrative and questions without changing engineering semantics.
- Abbreviation full names must match across languages.
- Any lesson-structure change updates both `LEARNING_PATH.md` files and the matching bilingual Notebooks in the same change set.

## 9. Current teaching status

- Learning Architecture: defined and through its first curriculum audit.
- LSN-001~004: being revised from experiment skeletons into textbook-quality executable lessons, with first-use terminology and project IDs moved to the end.
- LSN-005~008: the second bilingual lesson block is established; teaching RTL lives in `rtl/learning/` and does not replace formal `MOD-003`.
- LSN-009~012: the third bilingual Notebook block is established; small Python event-machine experiments teach time multiplexing, FIFO/backpressure, sparse lookup, and the event-driven causal chain without declaring MOD-004~009 complete.
- LSN-013~018: the fourth bilingual Notebook block is established; formal exercises remain board-independent, while physical FPGA/DDR labs remain engineering extensions of RMD-012A~016.
- First formal implementation remains `RMD-001`; it is not yet declared complete.
