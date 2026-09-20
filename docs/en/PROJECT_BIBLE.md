# Project Bible — From Membrane Potential to Silicon: Building a FlyBrain on FPGA

- Working version: v0.3
- Synchronized baseline: ADD/RMD v0.3-r1
- Audience: medical, biology, neuroscience, and biomedical-engineering students entering neuromorphic computing and AI hardware

## 1. Mission
This project takes a learner with university-level life-science knowledge but almost no computer-hardware background from “I understand how a neuron fires” to the point where they can understand, design, implement, and verify an FPGA neuromorphic computer running a network constrained by a real Drosophila connectome.

The same system grows throughout the project:

```text
one LIF neuron
→ many neurons
→ sparse synapses
→ spike events
→ FPGA
→ external memory
→ real MaleCNS subgraph
→ full target network
→ closed-loop environment
```

The goal is not to claim reproduction of a complete biological fly brain. The engineering target is a **verifiable, measurable spiking neural network constrained by real MaleCNS connectivity and running on FPGA**.

## 2. Target learner
The assumed learner is a second- or third-year undergraduate in medicine, biology, neuroscience, biomedical engineering, or a related discipline.

Expected background:
- membrane potential, action potentials, threshold, refractory period, synapses, excitation/inhibition;
- basic calculus, vectors, and matrices;
- a vague familiarity with binary logic such as AND/OR/NOT.

Not required beforehand: SystemVerilog, FPGA, computer architecture, AXI/DDR/DMA, neuromorphic computing, or AI-chip design.

## 3. Graduate profile
The learner does not need to become a professional chip designer by the end. They should, however, be able to decompose a neural-computation problem into questions such as:

```text
Where is the state?
Where does data come from?
How is it stored?
How is it moved?
Which unit computes it?
How is work parallelized?
How is correctness verified?
Where is the bottleneck?
```

They should have hands-on intuition for registers, RAM/BRAM, FIFO, pipelines, fixed point, DDR bandwidth, sparse/event-driven computation, FPGA accelerators, and neuromorphic hardware; and they should be able to complete the basic bring-up path on the **AMD Kria KV260 Vision AI Starter Kit**, from target discovery and first bitstream through physical I/O, host↔PL loopback, and small FlyBrain replay.

## 4. Three-layer translation
Important ideas should be described in three languages at once:

| Biology | Mathematics | Hardware |
|---|---|---|
| membrane potential | state variable V | register / RAM state |
| synaptic strength | weight | fixed-point value |
| action potential | threshold event | comparator + spike flag |
| refractory period | state constraint | counter / FSM |
| neural connectivity | sparse graph | adjacency / CSR-like image |
| spike | discrete event | FIFO message |
| neural network | dynamical system | memory + compute + event router |

The ability to translate between these three layers is the central skill of the project.

## 5. AI-assisted engineering, not AI-replaced thinking
AI / vibe coding is used from the first chapter.

AI may help with:
- boilerplate code;
- testbench generation;
- tool-error explanation;
- documentation maintenance;
- differential-test scripts;
- implementation research;
- experiment data-processing code.

The human must own:
- requirements;
- model assumptions;
- FR/DP decomposition;
- module boundaries and interfaces;
- test oracles;
- performance trade-offs;
- the decision to accept or reject a result.

Core rule: **AI may write large portions of the code, but it may not own the model for the learner.**

Any AI claim such as “tests pass,” “timing closes,” or “performance improved” requires actual command output, waveforms, reports, or benchmark evidence.

## 6. Axiomatic Design as the engineering spine
The project uses the basic language of Axiomatic Design:
- Functional Requirement (FR): what the system must accomplish;
- Design Parameter (DP): the design choice used to satisfy it;
- Constraint (C): a boundary that may not be violated.

Two core ideas guide design:
1. preserve FR independence as far as practical;
2. among independent-enough solutions, prefer simpler designs with a clearer path to success.

The current FlyBrain product system is structured as a lower-triangular decoupled design. Cross-cutting mechanisms such as verification, AI collaboration, Git, and TRACE are kept in a separate process FR/DP layer instead of being mixed into the product matrix.

## 7. Learning Independence Axiom
We apply the same independence idea to curriculum design:

> A learning slice should introduce at most one major unfamiliar concept. If success requires several still-unknown concepts at once, insert a bridge slice.

The route therefore includes explicit bridges for:
- Python → RTL: Digital Hardware Bridge;
- multi-neuron → event-driven: four-neuron event walkthrough;
- simulation → FPGA: synthesis, first bitstream, host/FPGA loopback;
- **KV260 Physical Lab Track**: board orientation → target detection → first bitstream → constraints/I/O → host loopback → BRAM → small-network replay;
- FPGA → DDR/AXI: memory hierarchy and bandwidth bridge.

Bridge chapters are first-class course material, not remedial appendices.

## 8. Engineering document system
`docs/` is the source of truth. The project follows [Documentation-First Specification Governance](DOCUMENT_AUTHORITY.md): **update documentation first, then test oracles / TRACE, and code or RTL last.** Existing implementation behavior does not automatically define requirements, interfaces, or model semantics.

- URD: why, for whom, and what success means;
- ADD: FR/DP, design matrices, coupling;
- MDD: modules, interfaces, and data contracts;
- TDD: correctness, oracles, and tests;
- RMD: safest implementation/learning order;
- TRACE: links requirements → design → modules → tests → tasks.

Future `okf/` content is an AI retrieval layer, while `.vibe/` stores machine-readable trace state. Neither may silently invent requirements. Design changes start in `docs/`.

**Diagram specification**: Architecture diagrams, timing/state graphs, and teaching workflows should use Markdown **inline SVG**; do not add new Mermaid or hand-aligned ASCII diagrams. SVG remains reviewable text, works with Git diff, and can be checked in PDF visual CI. Physical Labs may use official board photos/screenshots to help locate connectors, but critical connections, commands, and pass criteria must also exist in searchable text/structural diagrams.

## 9. Standard chapter pattern
Each chapter should begin from an actual problem and answer, in order:

1. **Biology problem** — what is happening?
2. **Computational model** — what is the smallest useful mathematical description?
3. **Hardware problem** — what must the machine store, move, or compute?
4. **Minimum new knowledge** — what one concept is needed now?
5. **Design Split** — are FRs/DPs sufficiently independent?
6. **Build** — human + AI implementation.
7. **Test** — what is the oracle?
8. **Measure** — error, throughput, resources, or power.
9. **Explain-back** — can the learner explain the system without AI?
10. **Git checkpoint** — preserve a reproducible state.

## 10. Biological realism as an experimental axis
The baseline uses LIF and does not pretend that LIF is a complete biological neuron.

Future complexity may be added in stages:

```text
LIF
→ refractory/adaptation
→ conductance-based synapse
→ short-term plasticity
→ STDP
→ neuron classes
→ neuromodulation
```

Every added biological mechanism should be evaluated on two axes: how much useful behavior/predictive power it adds, and how much hardware cost it introduces.

## 11. Explicit non-goals
The current project does not attempt to:
- prove or reproduce consciousness;
- equate a connectome with a complete brain;
- teach all of neuroscience, semiconductor physics, or SystemVerilog;
- optimize for maximum performance in the first implementation cycle;
- require expensive HBM FPGA hardware at the start;
- create meaningless modules just to beautify an ADD matrix.

## 12. What success really means
The full MaleCNS target is the north star, not the only success criterion.

If a life-science student reaches the middle of the project and can already reason about registers, BRAM, FIFO, pipelines, memory bandwidth, sparse accelerators, hardware mapping, and verification, the project has already achieved substantial value.

The final artifact is a machine; the deeper outcome is a new way to think:

```text
cell
→ dynamical system
→ network
→ graph computation
→ digital logic
→ memory system
→ parallel architecture
→ AI hardware
```
