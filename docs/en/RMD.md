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

The teaching transport is now frozen to the smallest inspectable KV260 path:

```text
Ubuntu/Python on PS
  → fixed /dev/mem MMIO
  → PS M_AXI_HPM0_FPD
  → AXI SmartConnect
  → dual-channel AXI GPIO @ 0xA0010000
  → kv260_loopback_transform
```

AXI GPIO is the adapter: Channel 1 `GPIO_DATA` at `+0x0` stores the 32-bit host write, the PL teaching core computes `(write + 1) mod 2^32`, and Channel 2 `GPIO2_DATA` at `+0x8` exposes the result. The hardware address follows AMD/Xilinx's K26 `base_gpio_bram` reference. The course helper does not expose arbitrary physical addresses.

This `/dev/mem` path is frozen for **LAB-HW-06 teaching only**; it does not define the final MOD-010 software stack. If the supported Ubuntu image blocks this access by policy, do not weaken security. Preserve the evidence, leave T-HW-006 blocked, and revise the repository transport in a later change.

LAB-HW-06 pass criteria:
- build/DRC/timing and direct-JTAG programming evidence are retained;
- two rounds of the fixed vector set produce the expected `write → expected → read` trace, including 32-bit wraparound;
- the self-checking host script distinguishes Linux/transport failures from core-behavior mismatch;
- runtime trace, bitstream/script hashes, Git commit, OS/image identity, and board/carrier revision are recorded.

### RMD-013 Run small network on FPGA

Implement this in two independent Physical Lab slices.

**LAB-HW-07 — BRAM neuron state** freezes only the memory substrate needed by the later network:

- 1024 × 32-bit state words;
- 4 KiB PS-visible window at `0xA0000000`;
- PS `M_AXI_HPM0_FPD` → SmartConnect → AXI BRAM Controller → teaching state-store RTL;
- synchronous native reads;
- block-RAM synthesis intent and a non-zero RAMB18/RAMB36 resource oracle;
- fixed multi-address write/read/rewrite self-check.

LAB-HW-07 does **not** declare full MOD-004 complete. It is a board-level teaching slice that proves the address/read/write/synchronous-read/resource concepts with one simple memory geometry. Banking, arbitration, wider neuron records, ECC, and the final formal state layout remain later design work.

**LAB-HW-08 — Small FlyBrain replay** then moves the already taught Lesson-12 four-neuron event machine onto KV260 without changing its teaching semantics. The source-of-truth fixture is versioned JSON and the Python replay oracle is derived from that fixture.

Freeze this replay:
- source index `[(0,2), (2,1), (3,1), (4,0)]`;
- records `[(1,+2), (2,+1), (3,+2), (3,+1)]`;
- thresholds `[99,2,1,3]`;
- initial state `[0,0,0,0]`, initial queue `[0]`;
- expected spike order `[0,1,2,3]`, expected final state `[0,0,0,0]`;
- fixed 4 KiB state/trace BRAM window at `0xA0000000`;
- fixed AXI-GPIO control/status block at `0xA0010000`;
- host BRAM access only while the PL replay engine is idle.

The replay compares not only final state but also spike order and every weighted event. The deterministic Lesson-12 fixture has no PRNG; a seed is required only for a future stochastic replay.

This is an L5 board replay of a **teaching event machine**, not the Python fixed-point LIF oracle and not completion of formal MOD-004~009. It deliberately preserves Lesson 12's warning that leak, refractory behavior, final fixed-point LIF numerics, concurrent target-write conflicts, and formal valid/ready timing remain outside that teaching machine.

Pass criteria:
- LAB-HW-07 multi-address state read/write and block-RAM resource proof remain intact;
- the versioned fixture and Python oracle reproduce the Lesson-12 expected spike order and event trace;
- open-source RTL simulation matches the same fixture-derived expected trace;
- physical KV260 spike/state/event readback matches the same Python oracle;
- fixture/oracle/bitstream hashes, build/program logs, output trace, Git commit, OS/image identity, and board/carrier revision are recorded.

# Bridge 4 — Memory is not “one very large RAM”

### RMD-013A Memory hierarchy & bandwidth bridge
Major new concept: **moving data can cost more than arithmetic**.  
First compare sequential, random, and batched/burst-like access and distinguish latency from throughput. Concept lessons may start with models; real measurements are produced by LAB-HW-09/10.

### RMD-014 DDR hello-world

Major new concept: **external memory has its own latency/control path, and correctness must be established before performance**.

This maps to **LAB-HW-09** as a PS/Linux-managed external-memory sanity slice. The board has 4 GB DDR4 system memory, but this Lab does not yet add PL→DDR AXI traffic.

Freeze the first physical DDR operation as:

```text
OS-managed anonymous mapping
→ prefault 64 MiB
→ deterministic contiguous 1 MiB chunks
→ write
→ read
→ byte-for-byte compare
→ SHA-256 compare
→ integrity PASS
→ only then report host-path timing observations
```

This design intentionally avoids a raw physical DDR address, custom DMA driver, AXI master, or CDMA setup. Those are separate dependencies and move to LAB-HW-10 / RMD-015.

The timing observations in LAB-HW-09 are descriptive evidence for this userspace path only. They are not a peak-DDR or PL/AXI bandwidth benchmark.

Pass criteria:
- 64 MiB allocation and 1 MiB chunk geometry are frozen;
- every regenerated expected chunk matches readback byte-for-byte;
- expected and observed SHA-256 match;
- deliberate corruption in CI/dry-run produces `DDR_INTEGRITY_MISMATCH`, `PERFORMANCE_BLOCKED=1`, and no accepted bandwidth result;
- successful physical runs record board/OS/kernel/memory identity plus write/read timer boundaries, elapsed times, and host-path effective bandwidth;
- no bitstream is required;
- T-HW-009 physical PASS requires a real KV260 PS/Linux run.

### RMD-014A AXI burst practical bridge

Major new concept: **transaction granularity and access ordering change effective DMA throughput even when total bytes and hardware are held constant**.

This maps to **LAB-HW-10**. The Lab uses AMD AXI CDMA rather than requiring the learner to hand-write a complete AXI master.

Freeze the first real PL→DDR benchmark as:

```text
PS/Linux programs AXI CDMA
        ↓
AXI CDMA M_AXI
        ↓
PS S_AXI_HP0_FPD
        ↓
DDR
```

The buffer contract is intentionally explicit because `S_AXI_HP0_FPD` is non-coherent. Physical runs use a course-approved u-dma-buf allocation opened with `O_SYNC`; ordinary cached Python memory is not accepted as a DMA buffer.

Workload contract:
- one bitstream and one 2 MiB-or-larger DMA-safe buffer;
- 256 KiB deterministic payload;
- contiguous pattern = one 256 KiB CDMA request;
- small/scattered pattern = 1024 × 256-byte requests in a frozen deterministic permutation;
- timer includes Python register programming/polling plus DMA completion;
- both patterns must pass byte-for-byte integrity before and after benchmark batches.

Default benchmark protocol:
- 5 warm-up runs excluded from statistics;
- 20 measured repetitions per pattern;
- median as primary result, retain min/max and every raw sample;
- repeat a second batch in the same session;
- median difference between batches must be ≤10% for both patterns;
- unstable measurements retain evidence but support no performance conclusion.

This is an end-to-end **software-controlled DMA workload** comparison, not a peak-DDR specification measurement and not a CPU/GPU/FPGA benchmark.

Pass criteria:
- AXI CDMA build contract uses 128-bit data, max burst 64, Simple DMA, and `S_AXI_HP0_FPD`;
- fixed control base `0xA0020000`;
- DMA-safe buffer/cache-mode preflight passes;
- identical source/destination payload checks pass for both patterns;
- all raw samples and two batch summaries are retained;
- both patterns satisfy the ≤10% stability gate;
- only then may the contiguous/scattered median ratio be reported;
- physical T-HW-010 PASS requires real KV260 evidence.

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

## 4. Current execution status

RMD-001, RMD-002, and RMD-003 remain semantic/numeric prerequisites for the **formal product implementation** to advance through later MOD/RMD items. The teaching track has already progressed under explicitly marked teaching-artifact and Physical-Lab boundaries, so the early-stage instruction not to start the FPGA toolchain or acquire hardware no longer describes the current repository.

At the current revision:

1. LSN-001~023 and their Exercise paths are established and continuously checked by Python/RTL CI;
2. LAB-HW-00~10 have bilingual Notebooks, KV260 board-support/runtime helpers, and CI contract checks;
3. that teaching completeness does **not** mean formal MOD-003~014 product implementation is complete;
4. the highest-priority physical work is a complete real-KV260 instructor dry run: validate the Vivado authoring candidate, freeze the LAB-HW-05 image identity/hash, verify HW-05→06 and HW-09→10, especially u-dma-buf/HP0 DDR placement and LAB-HW-10 AXI CDMA;
5. until real-board evidence exists, cloud CI, dry runs, and generic OSS synthesis must not be reported as T-HW physical PASS.
