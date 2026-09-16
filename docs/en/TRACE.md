# TRACE — Project Map / Traceability Matrix

## 0. Document information
- Project: FPGA FlyBrain / From Membrane Potential to Silicon
- Revision: v0.3-r1
- Date: 2026-09-16
- Purpose: synchronize ADD's product-FR/process-FR split and the new RMD learning-bridge slices.

## 1. Purpose
Link user needs → functional requirements → design parameters → modules → tests → implementation tasks so that humans and AI do not drift during long-term iteration.

## 2. Top-level traceability
| User task | Product / Process FR | DP | Module(s) / Process | Test(s) | RMD |
|---|---|---|---|---|---|
| U1 Understand a minimal neuron | FR1 | DP1 | MOD-001/002 | T-001~006 | 001~003 |
| U2 Use AI while remaining able to explain the result | PFR1/PFR2 | PDP1/PDP2 | bridge slices + AI workflow | explanation checkpoints + module tests | all relevant |
| U3 Build multi-neuron and event networks | FR3/FR4/FR5 | DP3/DP4/DP5 | MOD-004~009 | T-007~013 | 006~011 + 007A |
| U4 Run on FPGA | FR2/FR3/FR5/FR6 | DP2/DP3/DP5/DP6 | MOD-003/010/014 | L3~L5 + board replay | 011A~016 |
| U5 Import real MaleCNS data | FR7 | DP7 | MOD-011 | T-014/015 | 017~021 |
| U6 Build a layered verification chain | PFR4 | PDP4 | float/fixed/RTL/FPGA oracle chain | L0~L7 | all relevant |
| U7 Learn Axiomatic Design and traceability | PFR2/PFR3 | PDP2/PDP3 | docs/ + .vibe/ + okf/ | trace checks + checkpoints | all |
| U8 Become able to enter AI-hardware work | FR2~FR8 + PFR1~4 | DP2~DP8 + PDP1~4 | full system | performance + explanation | 003A~028 |

## 3. Key trace examples
### TRACE-N-001 — Neuron semantics to RTL
Requirement: the neuron accumulates input and emits a spike on threshold crossing.  
FR: FR1/FR2  
DP: DP1/DP2  
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

### TRACE-L-001 — Learning independence
Requirement: a learning task should not require multiple still-unmastered concepts at the same time.  
FR: PFR1  
DP: PDP1  
Implementation: RMD bridge slices + chapter structure  
Check: every slice names its `major new concept`; split slices when multiple unknown dependencies appear.  
Tasks: RMD-003A, 007A, 011A, 012A, 012B, 013A, 014A

## 4. Document authority
- URD: users, scope, and success definition.
- ADD: product/process FR/DP, matrices, and coupling.
- MDD: modules and interfaces.
- TDD: oracles and tests.
- RMD: implementation and learning order.
- TRACE: cross-document links.

Change routing:
- user goal changes → URD
- system decomposition or learning-independence rule changes → ADD
- module/interface changes → MDD
- correctness definition changes → TDD
- implementation/teaching order changes → RMD
- any ID/link changes → TRACE

## 5. Bilingual traceability rules
- `docs/zh/` and `docs/en/` share the same ID namespace.
- A translation must not invent a new FR, DP, MOD, T, P, or RMD ID.
- When design meaning changes, update the source-of-truth text and synchronize the other language in the same change set.
- A future automated check should compare the ID sets found in both languages.

## 6. Current status
- URD: initialized
- ADD: revised; product matrix lower-triangular / decoupled
- MDD: initialized; review again when first interfaces freeze
- TDD: initialized
- RMD: revised with four bridge zones
- TRACE: synchronized with ADD/RMD revision
- First implementation slice: not started

## 7. Events that require a TRACE update
- first freeze of an `IF-NEURON-*` interface;
- first addition or removal of a MOD ID;
- final FPGA board selection;
- freezing the MaleCNS binary-image schema;
- any RMD renumbering.
