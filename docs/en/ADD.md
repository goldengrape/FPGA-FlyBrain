# ADD — Design Split / Axiomatic Design Document

## 0. Document information
- Project: FPGA FlyBrain / From Membrane Potential to Silicon
- Revision: v0.3-r1
- Date: 2026-09-16
- Purpose of this revision: separate the FlyBrain product system from the learning/engineering process, verify a lower-triangular decoupled product matrix, and apply Axiomatic Design to the learning curve itself.

## 1. Design principles
1. **Independence Axiom**: preserve the independence of Functional Requirements (FRs) as far as practical.
2. **Information Axiom**: among designs that satisfy independence, prefer the simpler path with a higher probability of successful implementation.
3. **Do not fake zero coupling**: never create meaningless modules merely to make the matrix look diagonal; necessary coupling must be recorded and protected by tests.
4. **Separate levels**: product-system FRs are not mixed with teaching, AI collaboration, verification, or traceability process FRs.
5. **Learning Independence Axiom (project extension)**: one learning slice should introduce at most one major unfamiliar concept, or one inseparable concept cluster. If a task requires two or more still-unmastered concepts, insert a bridge slice.

# Part A — FlyBrain product system

## 2. Top-level system FR / DP
| ID | Functional Requirement (FR) | Design Parameter (DP) |
|---|---|---|
| FR1 | Define executable and repeatable neuron-computation semantics | DP1 Python float LIF reference + versioned neuron semantics |
| FR2 | Map defined neuron semantics into deterministic digital computation | DP2 fixed-point spec + RTL neuron engine |
| FR3 | Manage many virtual neuron states with limited hardware | DP3 banked neuron-state memory + scheduler/time multiplexing |
| FR4 | Represent and sequentially read sparse synaptic connectivity | DP4 versioned adjacency/CSR-like synapse image |
| FR5 | Propagate only when spikes actually occur | DP5 spike FIFO + event router + synapse engine |
| FR6 | Support a synapse set larger than on-chip SRAM | DP6 external DDR access layer + burst-oriented layout |
| FR7 | Convert real MaleCNS data into a network consumable by the system | DP7 host-side converter + manifest/checksum + binary image |
| FR8 | Close an observable loop between the neural system and a host environment | DP8 sensory encoder + host/FPGA transport + output decoder |

## 3. System design matrix
`X` means a functional dependency; `.` means no direct dependency.

```text
          DP1 DP2 DP3 DP4 DP5 DP6 DP7 DP8
FR1        X   .   .   .   .   .   .   .
FR2        X   X   .   .   .   .   .   .
FR3        .   X   X   .   .   .   .   .
FR4        .   .   .   X   .   .   .   .
FR5        .   .   .   X   X   .   .   .
FR6        .   .   .   X   X   X   .   .
FR7        .   .   .   X   .   X   X   .
FR8        .   .   .   .   X   X   X   X
```

### 3.1 Classification
All non-zero terms lie on or below the main diagonal. The matrix is therefore a **strict lower-triangular decoupled design**, more precisely two blocks that can be solved in sequence.

Recommended implementation order:

```text
DP1 → DP2 → DP3

DP4 → DP5 → DP6 → DP7 → DP8
```

DP1–DP3 form the neuron-computation/state block. DP4–DP8 form the connectivity/event/large-data/closed-loop block. They connect later through stable interfaces.

### 3.2 Meaning of independence
- DP1 does not need to know future neuron count, DDR, or MaleCNS details.
- DP2 implements frozen neuron semantics and does not redefine the model.
- DP3 solves state scaling without knowing where synapses originate.
- DP4 defines a consumable sparse-connectivity representation without prescribing the event pipeline.
- DP5 consumes a standardized connectivity stream without being tied to a particular storage medium.
- DP6 can move the connectivity backend from on-chip memory to DDR without changing neuron semantics.
- DP7 converts real data into the image required by the DP4/DP6 contracts without changing the FPGA core.
- DP8 builds the closed loop only on stable sensory-input and neural-output interfaces.

## 4. Subsystem FR / DP
### A. Neuron subsystem
FR-N1 store membrane voltage and required internal state.  
FR-N2 accept input and update state according to frozen semantics.  
FR-N3 detect threshold crossing and emit a spike.  
FR-N4 support refractory/reset behavior.

DP-N1 neuron state record  
DP-N2 arithmetic pipeline  
DP-N3 comparator + spike flag  
DP-N4 refractory counter/FSM

### B. Event subsystem
FR-E1 accept a spike.  
FR-E2 locate the source neuron's connectivity range.  
FR-E3 sequentially read target synapses.  
FR-E4 emit weighted target events.

DP-E1 spike FIFO  
DP-E2 source index table  
DP-E3 synapse memory reader  
DP-E4 synapse pipeline

### C. Memory subsystem
FR-M1 keep frequently accessed state on chip.  
FR-M2 keep large synapse data externally.  
FR-M3 preserve efficient sequential/burst access.  
FR-M4 control hotspots, bank conflicts, and arbitration.

DP-M1 banked BRAM/URAM  
DP-M2 DDR image  
DP-M3 burst-oriented layout  
DP-M4 banking/cache/arbitration

# Part B — Learning, AI collaboration, and verification process

## 5. Process FR / DP
These FRs do not belong to the FlyBrain product itself and are therefore excluded from the product matrix.

| ID | Process Functional Requirement | Process Design Parameter |
|---|---|---|
| PFR1 | Let a beginner progress without being hit by multiple unfamiliar concepts at once | PDP1 bridge-first learning slices + one-major-concept rule |
| PFR2 | Use AI/vibe coding aggressively while keeping human ownership of requirements, models, architecture, and acceptance criteria | PDP2 AI collaboration contract + guarded CHECKPOINTs |
| PFR3 | Keep requirements, design, code, and tests traceable over long iterations | PDP3 URD/ADD/MDD/TDD/RMD/TRACE + Git checkpoints + OKF-derived context |
| PFR4 | Preserve correctness across Python, fixed point, RTL, and hardware | PDP4 layered oracle: float → fixed-point → RTL simulation → FPGA replay |

The process matrix is diagonal:

```text
          PDP1 PDP2 PDP3 PDP4
PFR1        X    .    .    .
PFR2        .    X    .    .
PFR3        .    .    X    .
PFR4        .    .    .    X
```

## 6. Learning Independence Axiom — operating rules
### LI-1 One major new concept per slice
- Learn fixed point in Python before using it in RTL.
- Learn clock/register behavior with tiny circuits before writing LIF RTL.
- Understand event queuing in a tiny network before introducing CSR and large-scale propagation.
- Do not learn AXI during the first FPGA bring-up.
- Build memory-hierarchy and bandwidth intuition before DDR/AXI.

### LI-2 Insert a bridge slice when
- success requires two or more still-unmastered concepts at the same time;
- the learner can copy AI-generated code but cannot explain state, input, output, or timing;
- a test failure cannot be localized to one layer;
- toolchain complexity hides the algorithm/hardware concept being learned.

### LI-3 Each learning platform must have a visible completion point
1. Computational neuron — membrane voltage and spikes are visible on screen.
2. Digital neuron — RTL waveform matches the Python reference.
3. Event neural network — a small network propagates spikes on its own.
4. Real hardware and memory — FPGA runs in real time and bandwidth/latency can be measured.
5. Real connectome — MaleCNS subsets and eventually the full network can be loaded, run, and verified.

## 7. Accepted Coupling
### AC-001 Verification cross-cuts all product FRs
Verification naturally spans all implementation layers. It is therefore treated as PFR4/PDP4 rather than a product FR, and test logic remains separate from synthesizable RTL.

### AC-002 DDR layout affects synapse-engine throughput
Memory layout and event-pipeline performance cannot be fully independent. Control: define a stable `synapse stream` contract and benchmark sequential/random/burst access plus at least two record layouts before full MaleCNS scale.

### AC-003 Teaching order constrains implementation order
The project explicitly accepts “understandability before premature performance optimization.” Performance work starts after correctness is frozen.

### AC-004 Host/FPGA boundary depends on platform capabilities
Different SoC FPGAs expose different ARM, DDR, and transport paths. DP8 therefore targets a stable host/FPGA message contract rather than a board-specific API.

## 8. Current design decisions
D-001 Baseline neuron: LIF.  
D-002 Primary hardware numeric representation: fixed point.  
D-003 Scaling strategy: time multiplexing.  
D-004 Network propagation: sparse adjacency + spike events.  
D-005 Large connectivity store: external DDR.  
D-006 Host handles conversion, environment, and visualization; FPGA handles the neural-compute core.  
D-007 AI may write substantial implementation and test code but may not bypass FR/DP, interface, oracle, or CHECKPOINT decisions.  
D-008 Product ADD and learning/engineering-process ADD are maintained as separate layers.  
D-009 The teaching route follows the Learning Independence Axiom.

## 9. Current conclusion
- FlyBrain product matrix: **passes lower-triangular / decoupled check**.
- Process matrix: **diagonal / uncoupled**.
- Remaining performance/platform coupling is explicitly recorded and guarded by contracts and benchmarks.
