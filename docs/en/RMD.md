# RMD — Build Path / Implementation Route

## 0. Document information
- Project: FPGA FlyBrain / From Membrane Potential to Silicon
- Revision: v0.3-r2
- Date: 2026-09-19
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

### RMD-012 Select reference board and create platform shell

The reference board is frozen to the **AMD Kria KV260 Vision AI Starter Kit**. Physical teaching becomes board-specific here, while FlyBrain core RTL remains board-independent.

Physical Labs:

- **LAB-HW-00**: vendor-toolchain preflight; before connecting a board, freeze/verify Vivado version, JTAG cable driver, and KV260 board files / board flow;
- **LAB-HW-01**: board orientation; identify K26 SOM, carrier, J12 power, J4 UART/JTAG, microSD, Ethernet, SW2 SOM reset, and carrier revision;
- **LAB-HW-02**: correct power-up and target enumeration; isolate power/cable/JTAG failures from RTL failures.

Pass criteria:
- vendor-toolchain preflight has textual evidence;
- learner can connect the KV260 correctly from a powered-off state;
- development host can discover the target reliably;
- board revision, tool version, board-file/platform version, and target identification are recorded;
- the planned `boards/kv260/` platform-shell boundary is clear and board pins/platform IP do not leak into core RTL.

### RMD-012A First physical proof

Major new concept: **a bitstream turns RTL into a real implementation, and a logical port needs board/constraint mapping before it has physical meaning.**

Physical Labs:

- **LAB-HW-03**: minimal RTL through synthesis → implementation → timing → bitstream → program;
- **LAB-HW-04**: constraints and physical behavior for clock/design-local reset/one safe board-visible I/O.

Pass evidence includes:
- no blocking build/implementation error;
- bitstream/build-artifact hash;
- programming success;
- configuration evidence appropriate to the actual programming path;
- at least one observable result proving that the learner's design is active rather than merely board power;
- real/readable input or local-reset source produces the specified output behavior;
- learner distinguishes SW2 SOM-level hard reset from the FlyBrain design-local reset.

**DS34 is not a universal JTAG-programming oracle.** Use DS34 with its PS-done meaning only when the PS actually loads PL; Vivado/JTAG direct programming uses device programming status plus the design's own observable output as primary evidence.

The first physical proof does not simultaneously teach AXI, DDR, or the FlyBrain network.

### RMD-012B PS/Linux runtime-host bridge → Host ↔ FPGA minimal loopback

Insert a separate bridge before host↔PL so Linux boot, serial-console use, and the runtime transport do not all arrive for the first time together.

Physical Labs:

- **LAB-HW-05**: starter Linux image → microSD → UART console → PS boot/login; prove only that the KV260 PS/Linux runtime host can boot;
- **LAB-HW-06**: after LAB-HW-05 passes, perform the real PS/runtime-host ↔ PL minimal loopback.

LAB-HW-05 pass criteria:
- starter Linux image version/checksum recorded;
- UART boot log retained;
- shell reached with kernel/OS identification;
- learner distinguishes development host from runtime host/PS.

LAB-HW-06 freezes the semantic contract first:

```text
write value → PL stores/processes → read back result
```

The exact runtime transport (for example AXI-Lite/UIO/XRT or another supported path) is selected only after the Lab prose and TDD oracle are reviewed. Prefer the smallest stable path rather than using the first loopback to teach full AXI.

LAB-HW-06 pass criteria:
- write/readback is repeatable;
- PL state/operation ordering matches the contract;
- a self-checking host script distinguishes Linux/transport failure from core-behavior failure.

### RMD-013 Run small network on FPGA

Use **LAB-HW-07** first to map Lesson 9's abstract neuron-state memory onto real on-chip BRAM resources, then use **LAB-HW-08** to move the already-verified Platform 3 network onto hardware.

LAB-HW-07 teaches only the address/read/write/synchronous-read behavior and resource-report interpretation needed by this design; it does not teach every BRAM primitive parameter.

LAB-HW-08 uses the same fixed input/seed and compares KV260 output against the Python fixed-point reference for L5 replay.

Pass criteria:
- multi-address neuron-state read/write is correct;
- synthesis/resource report confirms the intended on-chip memory resource;
- small-network spike/state trace matches the frozen reference contract;
- bitstream, network fixture, input fixture, output hash/trace, and Git commit are recorded.

# Bridge 4 — Memory is not “one very large RAM”

### RMD-013A Memory hierarchy & bandwidth bridge
Major new concept: **moving data can cost more than arithmetic**.  
First compare sequential, random, and batched/burst-like access and distinguish latency from throughput. Concept lessons may start with models; real measurements are produced by LAB-HW-09/10.

### RMD-014 DDR hello-world

Major new concept: **external memory has its own latency and control path**.

This maps to **LAB-HW-09** using KV260 platform-provided controllers/IP:

```text
known payload → DDR write → DDR read → byte/checksum compare → measurement
```

Do not implement a DDR PHY/controller.

Pass criteria:
- integrity PASS;
- transfer size, elapsed time, access pattern, and effective bandwidth are recorded;
- corrupted data must fail integrity before any performance result is accepted.

### RMD-014A AXI burst practical bridge

Major new concept: **move contiguous data efficiently through standardized bus transactions**.

This maps to **LAB-HW-10**. Learn only the project-required AXI subset and compare small/scattered versus burst-oriented transfers on a real KV260. The required objective is “use + measure”; implementing a complete AXI master from scratch is optional.

Default measurement protocol:
- same bitstream, data volume, payload, and measurement boundary;
- 5 warm-up runs excluded from statistics;
- at least 20 measured repetitions per access pattern;
- median as the primary result, retaining all raw samples plus min/max;
- repeat a second batch in the same session; the two medians must differ by ≤10% to call the measurement reproducible, otherwise label it `measurement unstable`;
- state whether host/software overhead is inside the timer.

Pass criteria:
- at least two access patterns satisfy the reproducible-measurement protocol;
- workload contract is explicit and no single measurement is generalized into “AXI/FPGA is faster.”

### RMD-015 Move synapse store to DDR
Replace the storage backend without changing `IF-SYNAPSE-STREAM`.  
Test: identical network results with on-chip versus DDR storage.

### RMD-016 Throughput baseline
Measure the currently available subset of P-001~P-008.

**Platform 4 completion:** the learner can start from a development host whose vendor toolchain is not yet configured and a powered-off KV260, then independently complete toolchain preflight, board orientation, target discovery, bitstream build/program, physical I/O, PS/Linux first boot, host↔PL loopback, BRAM state, small-network replay, DDR integrity, and real bandwidth measurement. The FPGA network uses external memory, and the learner can explain and measure the memory bottleneck.

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
| Simulation → FPGA | vendor toolchain, power/cable/JTAG, bitstream, constraints, PS/Linux, and host I/O arrive together | RMD-011A + LAB-HW-00~08 split toolchain preflight, board orientation, target discovery, first bitstream, physical I/O, PS boot, loopback, BRAM, and small replay |
| FPGA → DDR/AXI | memory hierarchy/DDR/AXI/bandwidth arrive together | RMD-013A + LAB-HW-09/10 split integrity from measurement |

## 4. Current first execution batch
1. RMD-001 Python LIF float reference
2. RMD-002 Fixed-point exploration
3. RMD-003 Freeze v0 neuron semantics

Do not start the FPGA toolchain or buy hardware before these three tasks are complete. `RMD-003A` is the first task in the next batch.
