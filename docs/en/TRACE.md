# TRACE — Project Map / Traceability Matrix

## 0. Document information
- Project: FPGA FlyBrain / From Membrane Potential to Silicon
- Revision: v0.3-r4
- Date: 2026-09-18
- Purpose: synchronize ADD's product/process FR split, RMD bridge slices, and the new Learning Architecture / Notebook teaching layer.

## 1. Purpose
Link user needs → functional requirements → design parameters → teaching artifacts / modules → tests → implementation tasks so humans and AI do not drift during long-term iteration.

## 2. Top-level traceability
| User task | Product / Process FR | DP | Module(s) / Process | Test(s) | RMD |
|---|---|---|---|---|---|
| U1 Understand a minimal neuron | FR1 | DP1 | LSN-001/002 + MOD-001/002 | T-001~006 | 001~003 |
| U2 Use AI while remaining able to explain the result | PFR1/PFR2 | PDP1/PDP2 | Notebook AI Task/Human Check + bridge slices | explanation checkpoints + module tests | all relevant |
| U3 Build multi-neuron and event networks | FR3/FR4/FR5 | DP3/DP4/DP5 | MOD-004~009 | T-007~013 | 006~011 + 007A |
| U4 Run on FPGA | FR2/FR3/FR5/FR6 | DP2/DP3/DP5/DP6 | MOD-003/010/014 | L3~L5 + board replay | 011A~016 |
| U5 Import real MaleCNS data | FR7 | DP7 | MOD-011 | T-014/015 | 017~021 |
| U6 Build a layered verification chain | PFR4 | PDP4 | LSN-002/003 + float/fixed/RTL/FPGA oracle chain | L0~L7 | all relevant |
| U7 Learn Axiomatic Design and traceability | PFR2/PFR3 | PDP2/PDP3 | docs/ + lessons/ + exercises/ + CI checks | trace checks + checkpoints | all |
| U8 Become able to enter AI-hardware work | FR2~FR8 + PFR1~4 | DP2~DP8 + PDP1~4 | full learning + engineering system | T-016 + P-001~008 + explanation | 003A~028 |

## 3. Teaching-artifact traceability
| Lesson | Primary objective | FR / PFR | Test / Check | RMD | Notebook |
|---|---|---|---|---|---|
| LSN-001 | Abstract executable LIF behavior from neurophysiology | FR1/DP1 | T-001~004 + Human Check | RMD-001 | `lessons/en/01_membrane_to_lif.ipynb` |
| LSN-002 | Understand how fixed-point/quantization changes behavior | FR1/FR2 + PFR4 | T-005~006 + Human Check | RMD-002 | `lessons/en/02_float_to_fixed.ipynb` |
| LSN-003 | Freeze testable neuron semantics | PFR3/PFR4 | semantic ambiguity tests + spec checkpoint | RMD-003 | `lessons/en/03_freeze_neuron_semantics.ipynb` |
| LSN-004 | Build intuition for registers, clocks, combinational and sequential logic | PFR1; prepares FR2/DP2 | explanation checkpoint | RMD-003A | `lessons/en/04_state_and_clock.ipynb` |
| LSN-005 | Build minimal Boolean decisions | PFR1; prepares FR2/DP2 | `exercises/en/05_logic_building_blocks.ipynb` (grader: `exercises/grader/lesson05.py`) + Human Check | RMD-003A | `lessons/en/05_logic_building_blocks.ipynb` |
| LSN-006 | Understand RTL/HDL/SystemVerilog/module/port | PFR1; prepares FR2/DP2 | teaching RTL simulation + Human Check | prepares RMD-004 | `lessons/en/06_what_is_rtl.ipynb` |
| LSN-007 | Known neuron contract → combinational + sequential RTL | FR2/DP2 + PFR4 | Python oracle + RTL review | RMD-004 teaching precursor | `lessons/en/07_first_rtl_neuron.ipynb` |
| LSN-008 | Verify RTL with testbench/waveform/simulation | PFR4/PDP4 | self-checking testbench + explanation | RMD-005/005A | `lessons/en/08_testbench_waveform_simulation.ipynb` |
| LSN-009 | Understand how one physical engine time-multiplexes many virtual neuron states | FR3/DP3 + PFR1 | `exercises/en/09_time_multiplex_many_neurons.ipynb` (grader: `exercises/grader/lesson09.py`) + Human Check | RMD-006/007 teaching precursor | `lessons/en/09_time_multiplex_many_neurons.ipynb` |
| LSN-010 | Understand bounded-FIFO ordering and backpressure | FR4/DP4 + PFR4 | `exercises/en/10_spike_fifo_backpressure.ipynb` (grader: `exercises/grader/lesson10.py`); prepares T-007/008 | RMD-007A/009 teaching precursor | `lessons/en/10_spike_fifo_backpressure.ipynb` |
| LSN-011 | Locate exact real synapse ranges with a sparse source index | FR4/DP4 + PFR4 | `exercises/en/11_sparse_synapse_lookup.ipynb` (grader: `exercises/grader/lesson11.py`); prepares T-009 | RMD-008 | `lessons/en/11_sparse_synapse_lookup.ipynb` |
| LSN-012 | Compose queue → lookup → weighted event → target update | FR4/FR5 + DP4/DP5 + PFR4 | `exercises/en/12_one_spike_journey.ipynb` (grader: `exercises/grader/lesson12.py`); prepares T-010~013 | RMD-007A/010/011 teaching integration | `lessons/en/12_one_spike_journey.ipynb` |
| LSN-013 | Separate simulation, synthesis, implementation, and timing, then perform a Yosys dry run | FR2 + PFR1/PFR4 | Yosys synthesis dry run + timing summary + Human Check | RMD-011A | `lessons/en/13_simulation_is_not_chip.ipynb` |
| LSN-014 | Understand the relationship between FPGA chip, development board, clock/reset, and I/O | FR2 + PFR1 | `exercises/en/14_what_is_fpga_board.ipynb` (grader: `exercises/grader/lesson14.py`) + Human Check | RMD-012/012A | `lessons/en/14_what_is_fpga_board.ipynb` |
| LSN-015 | Build the two-domain host/programmable-logic model and a minimal roundtrip | FR2/FR6 + PFR1 | `exercises/en/15_host_talks_to_fpga.ipynb` (grader: `exercises/grader/lesson15.py`) + Human Check | RMD-012B/013 | `lessons/en/15_host_talks_to_fpga.ipynb` |
| LSN-016 | Distinguish latency, throughput, and bandwidth and compare compute/data-movement costs | FR5/FR6 + PFR1 | `exercises/en/16_data_movement_cost.ipynb` (grader: `exercises/grader/lesson16.py`) + Human Check | RMD-013A | `lessons/en/16_data_movement_cost.ipynb` |
| LSN-017 | Understand external DDR, bursts, and access-pattern cost | FR6/DP6 + PFR1 | `exercises/en/17_external_memory_ddr.ipynb` (grader: `exercises/grader/lesson17.py`) + Human Check | RMD-014 | `lessons/en/17_external_memory_ddr.ipynb` |
| LSN-018 | Learn the minimal AXI transaction/beat and VALID/READY handshake subset | FR6/DP6 + PFR4 | `exercises/en/18_axi_subset.ipynb` (grader: `exercises/grader/lesson18.py`) + Human Check | RMD-014A/015/016 | `lessons/en/18_axi_subset.ipynb` |

Principle: Notebooks may prototype and demonstrate, but formal algorithms, RTL, interfaces, and oracles remain authoritative in `python/`, `rtl/`, MDD, TDD, and other engineering sources.

## 4. Key trace examples
### TRACE-N-001 — Neuron semantics to RTL
Requirement: the neuron accumulates input and emits a spike on threshold crossing.  
FR: FR1/FR2  
DP: DP1/DP2  
Teaching: LSN-001~008  
Modules: MOD-001, MOD-002, MOD-003  
Tests: T-001~T-006  
Tasks: RMD-001, 002, 003, 003A, 004, 005, 005A

### TRACE-E-001 — Event-driven propagation
Requirement: only downstream connections of an actual spike are processed.  
FR: FR4/FR5  
DP: DP4/DP5  
Modules: MOD-005, 006, 007, 008  
Tests: T-007~T-010  
Tasks: RMD-007A, 008~011

### TRACE-H-001 — First real FPGA
Requirement: a small network already verified in simulation can move to a real FPGA, with host input and output readback.  
FR: FR2/FR3/FR5  
DP: DP2/DP3/DP5  
Modules: MOD-003/004/005/010  
Tests: synthesis report + loopback + L5 replay  
Tasks: RMD-011A, 012, 012A, 012B, 013

### TRACE-M-001 — External synapse memory
Requirement: synapses larger than on-chip SRAM can live in DDR without changing upper-layer synapse-stream semantics.  
FR: FR6  
DP: DP6  
Modules: MOD-010/014  
Tests: integrity + on-chip/DDR differential + bandwidth benchmark  
Tasks: RMD-013A, 014, 014A, 015, 016

### TRACE-C-001 — MaleCNS import
Requirement: real MaleCNS data can be converted into a reproducible FPGA-consumable format.  
FR: FR7  
DP: DP7  
Module: MOD-011  
Tests: T-014/T-015 + manifest/checksum  
Tasks: RMD-017~020


### TRACE-IO-001 — Sensory-input and behavioral-output closed loop
Requirement: external-environment inputs can map to sensory neurons and neural outputs can decode into behavior/control while the host/FPGA boundary remains observable.  
FR: FR8  
DP: DP8  
Modules: MOD-010, MOD-012, MOD-013, MOD-014  
Tests: interface/closed-loop replay + telemetry consistency; full-system determinism is covered by T-016  
Tasks: RMD-023~025

### TRACE-F-001 — Full-system reproducible replay
Requirement: the same versioned model, network image, initial state, and input events produce repeatable results; if the model includes noise, fix the PRNG seed.  
FR: FR2~FR8 + PFR4  
DP: DP2~DP8 + PDP4  
Modules: the complete formal system module set  
Test: T-016  
Tasks: RMD-021, RMD-025, RMD-027

### TRACE-P-001 — Performance metrics and benchmarks
Requirement: after correctness is frozen, measure throughput, latency, bandwidth, resources, and power reproducibly.  
FR: FR2~FR8  
DP: corresponding implementation DPs  
Modules: whichever formal MOD-003~014 components are involved in the current benchmark  
Tests/metrics: P-001~P-008  
Tasks: RMD-016, RMD-019, RMD-021, RMD-028

### TRACE-L-001 — Learning independence
Requirement: a learning task should not require multiple still-unmastered concepts at the same time.  
FR: PFR1  
DP: PDP1  
Implementation: `LEARNING_PATH.md` + `LSN-*` Notebooks + RMD bridge slices  
Check: every lesson/slice names one major new concept; split when multiple unknown dependencies appear.  
Tasks: RMD-003A, 007A, 011A, 012A, 012B, 013A, 014A

## 5. Document authority
- URD: users, scope, and success definition.
- ADD: product/process FR/DP, matrices, and coupling.
- MDD: modules and interfaces.
- TDD: oracles and tests.
- RMD: engineering implementation order.
- LEARNING_PATH: conceptual teaching order and lesson-design rules.
- `lessons/`: student-facing executable textbook/lab layer; it does not replace formal engineering specifications.
- TRACE: links across documents, lessons, and implementation.

Change routing:
- user goal changes → URD
- system decomposition or learning-independence rule changes → ADD
- module/interface changes → MDD
- correctness definition changes → TDD
- engineering implementation order changes → RMD
- teaching concept order or lesson structure changes → LEARNING_PATH + matching Notebook
- any ID/link changes → TRACE

## 6. Bilingual traceability rules
- `docs/zh/` and `docs/en/`, and `lessons/zh/` and `lessons/en/`, share the same ID namespace.
- A translation must not invent a new FR, DP, PFR, PDP, MOD, T, P, RMD, or LSN ID.
- Code cells should remain identical whenever practical; language versions primarily translate narrative and questions.
- Design or teaching meaning changes must be synchronized in both languages within the same change cycle.
- A future automated check should compare ID sets and Notebook pairs across languages.

## 7. Current status
- URD: initialized
- ADD: revised; product matrix lower-triangular / decoupled
- MDD: initialized; review again when first interfaces freeze
- TDD: initialized
- RMD: revised with four bridge zones
- LEARNING_PATH: initialized bilingually
- LSN-001~004: first bilingual executable lesson block established
- LSN-005~008: second bilingual lesson block established; `rtl/learning/` and `tb/learning/` do not declare MOD-003 complete
- LSN-009~012: third bilingual lesson block established; Python teaching models do not declare MOD-004~009 complete
- LSN-013~018: fourth bilingual lesson block established; synthesis/board/host/DDR/AXI teaching experiments do not declare the corresponding formal MODs or physical-platform implementation complete
- TRACE: synchronized across engineering and teaching paths through LSN-018
- First formal implementation slice: not started

## 8. Events that require a TRACE update
- first freeze of an `IF-NEURON-*` interface;
- when LSN-001~004 move from prototype code to importing formal `python/`/`rtl/` modules;
- first addition or removal of a MOD or LSN ID;
- final FPGA board selection;
- freezing the MaleCNS binary-image schema;
- any RMD renumbering.
