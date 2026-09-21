# TRACE — Project Map / Traceability Matrix

## 0. Document information
- Project: FPGA FlyBrain / From Membrane Potential to Silicon
- Revision: v0.3-r8
- Date: 2026-09-20
- Purpose: synchronize ADD's product/process FR split, RMD bridge slices, and the new Learning Architecture / Notebook teaching layer.

## 1. Purpose
Link user needs → functional requirements → design parameters → teaching artifacts / modules → tests → implementation tasks so humans and AI do not drift during long-term iteration.

## 2. Top-level traceability
| User task | Product / Process FR | DP | Module(s) / Process | Test(s) | RMD |
|---|---|---|---|---|---|
| U1 Understand a minimal neuron | FR1 | DP1 | LSN-001/002 + MOD-001/002 | T-001~006 | 001~003 |
| U2 Use AI while remaining able to explain the result | PFR1/PFR2 | PDP1/PDP2 | Notebook AI Task/Human Check + bridge slices | explanation checkpoints + module tests | all relevant |
| U3 Build multi-neuron and event networks | FR3/FR4/FR5 | DP3/DP4/DP5 | MOD-004~009 | T-007~013 | 006~011 + 007A |
| U4 Run on FPGA | FR2/FR3/FR5/FR6 | DP2/DP3/DP5/DP6 | MOD-003/004/005/010/014 + KV260 platform shell | L3~L5 + T-HW-001~011 + board replay | 011A~016 |
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
| LSN-006 | Understand RTL/HDL/SystemVerilog/module/port | PFR1; prepares FR2/DP2 | `exercises/en/06_what_is_rtl.ipynb` (grader: `exercises/grader/lesson06.py`) + compile-only RTL check + Human Check | prepares RMD-004 | `lessons/en/06_what_is_rtl.ipynb` |
| LSN-007 | Known neuron contract → combinational + sequential RTL | FR2/DP2 + PFR4 | `exercises/en/07_first_rtl_neuron.ipynb` (grader: `exercises/grader/lesson07.py`) + RTL review + Human Check | RMD-004 teaching precursor | `lessons/en/07_first_rtl_neuron.ipynb` |
| LSN-008 | Verify RTL with testbench/waveform/simulation | PFR4/PDP4 | `exercises/en/08_testbench_waveform_simulation.ipynb` (grader: `exercises/grader/lesson08.py`) + self-checking testbench/VCD + Human Check | RMD-005/005A | `lessons/en/08_testbench_waveform_simulation.ipynb` |
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
| LSN-019 | Separate connectome neuron IDs, directed edges, metadata, and dynamic state | FR7/DP7 + PFR1 | `exercises/en/19_what_is_connectome.ipynb` (grader: `exercises/grader/lesson19.py`) + Human Check | RMD-017 | `lessons/en/19_what_is_connectome.ipynb` |
| LSN-020 | Build a manifest/checksum/provenance network-image contract while keeping teaching fixture ≠ formal MaleCNS artifact explicit | FR7/DP7 + PFR4 | `exercises/en/20_load_malecns_subset.ipynb` (grader: `exercises/grader/lesson20.py`); prepares T-014/015 | RMD-017/018 | `lessons/en/20_load_malecns_subset.ipynb` |
| LSN-021 | Use demand/capacity utilization to identify a bottleneck that can move with scale | FR7 + PFR4 | `exercises/en/21_scaling_bottlenecks.ipynb` (grader: `exercises/grader/lesson21.py`) + synthetic scale dry run | RMD-019~022 | `lessons/en/21_scaling_bottlenecks.ipynb` |
| LSN-022 | Build closed-loop feedback while making manual sensory/output mappings explicit | FR8/DP8 + PFR4 | `exercises/en/22_closed_loop_world.ipynb` (grader: `exercises/grader/lesson22.py`); prepares T-016 | RMD-023~025 | `lessons/en/22_closed_loop_world.ipynb` |
| LSN-023 | Freeze a CPU/GPU/FPGA benchmark comparability contract before calculating throughput/energy metrics | FR2~FR8 + PFR4 | `exercises/en/23_cpu_gpu_fpga_benchmark.ipynb` (grader: `exercises/grader/lesson23.py`); prepares P-001~008 | RMD-028 | `lessons/en/23_cpu_gpu_fpga_benchmark.ipynb` |

### 3.1 KV260 Physical Lab traceability

`LAB-HW-*` does not replace LSN lessons. It turns Platform 4 concepts into real KV260 operations and evidence.

| Lab | Objective | Primary test | RMD | Artifact |
|---|---|---|---|---|
| LAB-HW-00 | vendor-toolchain preflight | T-HW-001/T-HW-011 | RMD-012 | `labs/en/00_vendor_toolchain_preflight.ipynb` |
| LAB-HW-01 | identify real KV260, interfaces, SW2 SOM reset, carrier revision | T-HW-011 (inventory/evidence) | RMD-012 | `labs/en/01_board_orientation.ipynb` |
| LAB-HW-02 | power + JTAG target discovery | T-HW-002/T-HW-011 | RMD-012 | `labs/en/02_power_target_detection.ipynb` |
| LAB-HW-03 | first bitstream build/program | T-HW-003/T-HW-011 | RMD-012A | `labs/en/03_first_bitstream.ipynb` + `boards/kv260/rtl/kv260_marker_top.sv` |
| LAB-HW-04 | clock/design-local reset/I/O constraints | T-HW-004/T-HW-011 | RMD-012A | `labs/en/04_clock_reset_io.ipynb` + `boards/kv260/rtl/kv260_blink_core.sv` |
| LAB-HW-05 | PS/Linux first boot + UART console | T-HW-005/T-HW-011 | RMD-012B | `labs/en/05_ps_linux_first_boot.ipynb` + `boards/kv260/runtime/` |
| LAB-HW-06 | real host↔PL loopback | T-HW-006/T-HW-011 | RMD-012B | `labs/en/06_host_pl_loopback.ipynb` + `boards/kv260/rtl/kv260_loopback_transform.sv` + `boards/kv260/runtime/loopback_mmio.py` |
| LAB-HW-07 | BRAM neuron-state store | T-HW-007/T-HW-011 | RMD-013 | `labs/en/07_bram_neuron_state.ipynb` + `boards/kv260/rtl/kv260_neuron_state_store.sv` + `boards/kv260/runtime/state_bram_mmio.py` |
| LAB-HW-08 | small FlyBrain FPGA replay | T-HW-008/T-HW-011 | RMD-013 | `labs/en/08_small_flybrain_replay.ipynb` + `boards/kv260/fixtures/lab08_four_neuron_replay_v1.json` + `boards/kv260/rtl/kv260_small_replay_engine.sv` + `boards/kv260/runtime/small_replay_mmio.py` |
| LAB-HW-09 | DDR integrity + real measurement | T-HW-009/T-HW-011 | RMD-014 | planned `labs/en/09_*` |
| LAB-HW-10 | AXI/burst measurement | T-HW-010/T-HW-011 | RMD-014A | planned `labs/en/10_*` |

Physical-Lab specification sources:
- `docs/en/KV260_REFERENCE_PLATFORM.md`
- `docs/en/PHYSICAL_FPGA_LABS.md`

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
Requirement: a zero-FPGA-experience learner can take KV260 from vendor-toolchain preflight and correct connection/target discovery through first bitstream, physical I/O, PS/Linux first boot, host↔PL loopback, and migration of an already simulation-verified small network.  
FR: FR2/FR3/FR5  
DP: DP2/DP3/DP5  
Modules: MOD-003/004/005/010 + KV260 platform shell  
Teaching: LAB-HW-00~08  
Tests: T-HW-001~008 + T-HW-011 + L5 replay  
Tasks: RMD-011A, 012, 012A, 012B, 013

### TRACE-M-001 — External synapse memory
Requirement: synapses larger than on-chip SRAM can live in DDR without changing upper-layer synapse-stream semantics.  
FR: FR6  
DP: DP6  
Modules: MOD-010/014  
Teaching: LAB-HW-09/10  
Tests: T-HW-009/010/011 + integrity + on-chip/DDR differential + bandwidth benchmark  
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
- LSN-013~018: fourth bilingual lesson block established; concept Notebooks do not declare the physical-platform implementation complete
- Reference board: **AMD Kria KV260 Vision AI Starter Kit** is frozen
- LAB-HW-00~10: Physical Lab teaching structure, RMD mappings, and T-HW oracles are frozen; **LAB-HW-00~08** now have bilingual Notebooks and CI contract checks; LAB-HW-08 adds the versioned Lesson-12 four-neuron fixture, deterministic Python replay oracle, fixed PL replay engine, shared BRAM trace, and differential runtime checker. No real-KV260 T-HW-008 pass or real Vivado LAB-HW-08 full build is claimed; LAB-HW-09~10 remain pending
- LSN-019~023: fifth bilingual lesson block established; connectome teaching fixtures, synthetic scale/benchmark numbers, and the toy closed loop do not declare RMD-017~028 formal data artifacts, full-system implementation, or real performance results complete
- TRACE: synchronized across engineering and teaching paths through LSN-023
- First formal implementation slice: not started

## 8. Events that require a TRACE update
- first freeze of an `IF-NEURON-*` interface;
- when LSN-001~004 move from prototype code to importing formal `python/`/`rtl/` modules;
- first addition or removal of a MOD or LSN ID;
- any change to the reference board, carrier-revision policy, or supported physical tool flow;
- freezing the MaleCNS binary-image schema;
- any RMD renumbering.
