# RMD — Build Path / Implementation Route

## 0. Document information
- Project: FPGA FlyBrain / From Membrane Potential to Silicon
- Revision: v0.3-r1
- Date: 2026-09-16
- Purpose: flatten the learning curve according to the Learning Independence Axiom while preserving existing RMD numbering. Bridge slices use letter suffixes so earlier trace links do not break.

## 1. General rules
Every slice must:
1. have a small, explicit goal;
2. have a test oracle;
3. produce something runnable or observable;
4. end with a Git or specification checkpoint;
5. avoid complexity not required by the current slice;
6. introduce at most one major unfamiliar concept, or one inseparable concept cluster;
7. allow AI-generated implementation while requiring the learner to explain inputs, state, outputs, timing, and acceptance criteria;
8. follow [Documentation-First Specification Governance](DOCUMENT_AUTHORITY.md): slices that change a contract update bilingual documentation and oracle / TRACE before implementation; RMD must not substitute “the current code already does this” for a specification decision.

## 2. Five learning platforms
```text
Platform 1 Computational neuron
Python / LIF / fixed point

Platform 2 Digital neuron
clock / register / RTL / waveform

Platform 3 Event neural network
RAM / sparse graph / FIFO / event routing

Platform 4 Real hardware and memory
FPGA / host transport / DDR / AXI / bandwidth

Platform 5 Real connectome
MaleCNS / scaling / closed loop / benchmark
```

# Platform 1 — I understand how a neuron becomes computation

### RMD-001 Python LIF float reference
Major new concept: **a model is a purposeful simplification**.  
Deliverable: `python/reference/lif_float.py`.  
Tests: T-001~T-004.  
Done when: given an input sequence, the model emits membrane-voltage and spike trajectories and the learner can explain the physiological meaning of each term.

### RMD-002 Fixed-point exploration
Major new concept: **finite-width numeric representation**.  
Deliverable: `python/reference/lif_fixed.py`.  
Compare Q-formats, rounding, saturation, and overflow strategies.  
Tests: T-005~T-006.

### RMD-003 First spec checkpoint
Freeze v0 neuron semantics; update the numeric interface in MDD, TDD oracles, and TRACE.  
Git checkpoint: `spec: freeze v0 neuron semantics`.

**Platform 1 completion:** the neuron fires by repeatable rules on screen, and float-vs-fixed differences are measurable.

## Bridge 1 — From program variables to digital state
### RMD-003A Digital Hardware Bridge
Major new concept: **hardware state and clocking**.

Only three micro-experiments:
1. combinational adder;
2. clocked counter;
3. accumulator + threshold.

Build these mappings:
```text
Python variable  → register / RAM state
if               → comparator + mux/control
loop             → parallel hardware or time multiplexing
function/module  → hardware module + interface contract
```

Done when: the learner can point to a waveform and explain exactly when state changes, and can distinguish combinational from sequential behavior.

# Platform 2 — I understand how computation becomes digital circuitry

### RMD-004 SystemVerilog single neuron
Major new concept: **describing a known state machine/datapath in RTL**.  
Deliverable: `rtl/neuron/lif_neuron_engine.sv`.  
Test: Python fixed-point vector → RTL compare.  
Constraint: RTL must not redefine neuron semantics.

### RMD-005 Testbench + waveform lesson
Major new concept: **simulation and testbenches are executable hardware experiments**.  
Deliverable: `tb/lif_neuron_engine_tb.sv`.

### RMD-005A RTL explanation checkpoint
Without AI, the learner must explain: which signals are state, which paths are combinational, why bit widths were chosen, at which clock edge an input takes effect, and which layer should be debugged first when a test fails.

**Platform 2 completion:** RTL waveforms match the Python fixed-point reference on the defined tests.

# Platform 3 — I understand how many neurons become an event computer

### RMD-006 128-neuron time multiplexing
Major new concept: **one physical compute unit can serve many virtual states over time**.  
Deliverable: state RAM + scheduler.

### RMD-007 1K-neuron simulation
Major new concept: **throughput and resource use become architecture metrics**.  
Measure cycles per neuron update and RAM usage.

## Bridge 2 — From a neuron array to event propagation
### RMD-007A Four-neuron event walk-through
Major new concept: **an event carries a source identity, which is used to find downstream connections**.

Use only four neurons and 3–6 handwritten edges. Observe:
`spike(source)` → queue → lookup → `(target, weight)` → target update.

Done when: before entering formal CSR/FIFO RTL and interface implementation, the learner can verbally trace one spike from source to target. Teaching Notebooks may first introduce queue/backpressure and sparse lookup separately with small Python models, then return to this checkpoint for end-to-end integration.

### RMD-008 Sparse adjacency image
Major new concept: **data representation for a sparse graph**.  
The host emits source index + synapse records.

### RMD-009 Spike FIFO
Major new concept: **event queuing and flow control**.  
Tests: ordering, full/empty, backpressure.

### RMD-010 Synapse reader + engine
Major new concept: **turning sparse connection records into a weighted event stream**.

### RMD-011 Small event-driven SNN
Integrate previous modules without introducing a new major concept.  
Scale: roughly 100–1000 neurons.

**Platform 3 completion:** a small network propagates activity only through spike events instead of scanning every connection.

# Bridge 3 — From simulated hardware to a real FPGA

### RMD-011A FPGA toolchain dry run — no board required
Major new concept: **synthesis and simulation answer different questions**.  
Synthesize a counter/accumulator and read basic resource and timing reports. Do not learn AXI or DDR yet.

### RMD-012 Select board and create platform shell
Only now purchase hardware. Default candidate: a KV260-class SoC FPGA; keep the platform interface replaceable.

### RMD-012A First physical proof
Major new concept: **a bitstream turns RTL into a real implementation inside the chip**.  
Use a counter / LED or another observable register.

### RMD-012B Host ↔ FPGA minimal loopback
Major new concept: **the host and programmable logic are separate execution domains**.  
Minimal experiment: host writes a value → FPGA accumulator/register → host reads it back. Do not dive deeply into AXI yet.

### RMD-013 Run small network on FPGA
Move the already-verified Platform 3 network onto hardware and perform L5 replay.

# Bridge 4 — Memory is not “one very large RAM”

### RMD-013A Memory hierarchy & bandwidth bridge
Major new concept: **moving data can cost more than arithmetic**.  
First compare sequential, random, and batched/burst-like access and distinguish latency from throughput.

### RMD-014 DDR hello-world
Major new concept: **external memory has its own latency and control path**.  
Use platform-provided controllers/IP for stable read/write + integrity tests. Do not hand-build a DDR PHY/controller.

### RMD-014A AXI burst practical bridge
Major new concept: **moving contiguous data efficiently through standardized bus transactions**.  
Learn only the AXI mental model/subset needed by this project. Compare small/random transactions with bursts.

### RMD-015 Move synapse store to DDR
Replace the storage backend without changing `IF-SYNAPSE-STREAM`.  
Test: identical network results with on-chip versus DDR storage.

### RMD-016 Throughput baseline
Measure the currently available subset of P-001~P-008.

**Platform 4 completion:** the FPGA network uses external memory, and the learner can explain and measure how memory becomes a bottleneck.

# Platform 5 — I can run real neural-system data

### RMD-017 MaleCNS converter v1
Major new concept: **scientific data must be converted into a stable, versioned hardware image**.  
Output: manifest/checksum + binary image.

### RMD-018 1K real subset
Feed a real connectome subset into the already-verified system for the first time; run software-vs-FPGA differential tests.

### RMD-019 10K / 50K scaling
Major new concept: **performance bottlenecks move with scale**.  
Locate DDR, FIFO, bank-conflict, and hotspot limits.

### RMD-020 Full MaleCNS image
Load the full target dataset.

### RMD-021 Full network execution
Produce correctness + stability + performance reports.

### RMD-022 Event-driven optimization
Optimize only after the baseline is correct: lazy membrane update, cache, banking, multiple synapse engines, etc.

### RMD-023 Sensory encoder v1
All manual mappings must be documented, separating experimental facts from engineering assumptions.

### RMD-024 Output decoder v1
Map descending-neuron outputs to simple behavior.

### RMD-025 Closed-loop demo
Start with a simple 2D environment before games or robotics.

### RMD-026 Chapterize each build slice
Each slice becomes a chapter/experiment; bridge slices are first-class teaching material, not remedial appendices.

### RMD-027 Public reproducibility pass
Reproduce the project from scratch on a fresh machine using the README.

### RMD-028 CPU/GPU/FPGA benchmark
Use the same model, data, and inputs to compare latency, throughput, memory traffic, and power.

**Platform 5 completion:** real MaleCNS data can be converted, loaded, and run on FPGA; closed-loop I/O and performance verification are reproducible.

## 3. Learning-curve risk table
| Transition | Original risk | Buffer introduced |
|---|---|---|
| Python → RTL | clock/register/HDL/waveform/bit width arrive together | RMD-003A three micro hardware experiments |
| Multi-neuron → event-driven | sparse graph/FIFO/router arrive together | RMD-007A four-neuron event walkthrough |
| Simulation → FPGA | toolchain/bitstream/host I/O arrive together | RMD-011A, 012A, 012B separated |
| FPGA → DDR/AXI | memory hierarchy/DDR/AXI/bandwidth arrive together | RMD-013A, 014, 014A layered |

## 4. Current first execution batch
1. RMD-001 Python LIF float reference
2. RMD-002 Fixed-point exploration
3. RMD-003 Freeze v0 neuron semantics

Do not start the FPGA toolchain or buy hardware before these three tasks are complete. `RMD-003A` is the first task in the next batch.
