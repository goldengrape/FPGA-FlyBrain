# TDD — Check Plan / Test and Verification Document

## 0. Principles
- Follow [Documentation-First Specification Governance](DOCUMENT_AUTHORITY.md): start from an approved requirement/semantic/interface contract, translate it into an oracle, and only then write implementation.
- Define the oracle before writing the implementation.
- Never claim a test passed unless the exact command actually ran successfully.
- Once the corresponding model semantics are frozen, the Python float reference is the conceptual oracle and the Python fixed-point reference is the direct RTL oracle. Reference models themselves must conform to the approved documented contract.
- Keep unit, integration, and performance testing separate.

## 1. Verification layers
### L0 Mathematical / physiological sanity checks
Verify no-input decay, accumulation under sustained input, threshold crossing, reset, and refractory behavior.

### L1 Python float reference
Verify state trajectories and spike timestamps under deterministic inputs.

### L2 Python fixed-point reference
Test:
- quantization error
- overflow/saturation
- effect of Q-format on spike timing

Pass criterion: after selecting a Q-format, error is acceptable on the defined test set and no undefined overflow behavior remains.

### L3 RTL unit simulation
Modules: `lif_neuron_engine`, FIFO, `synapse_reader`, `synapse_engine`, accumulator.  
Oracle: Python fixed-point vectors or directly constructed expected values.

### L4 RTL integration simulation
Scenario: small networks of roughly 10–1000 neurons.  
Compare spike sequences event-by-event or step-by-step; compare neuron-state checksums where useful.

### L5 FPGA board verification
The reference board is KV260. Complete vendor-toolchain preflight / target-discovery / programming / physical-I/O / PS/Linux-boot / host-loopback `T-HW-*` checkpoints first, then replay fixed seeds and input events, capture outputs, and compare against RTL simulation and Python references.

### L6 Connectome subset verification
Choose a real subgraph of roughly 1K neurons. The exact same binary image is consumed by software and FPGA implementations.

### L7 Full-scale performance / correctness
- target scale around 166.7K neurons
- full connectivity image loaded
- long-run stability
- output statistics compared with a software baseline

## 2. Key test oracles
- **T-001** LIF no-input decay
- **T-002** threshold crossing
- **T-003** reset after spike
- **T-004** refractory behavior
- **T-005** signed excitatory/inhibitory weight
- **T-006** fixed-point saturation
- **T-007** FIFO ordering
- **T-008** FIFO backpressure
- **T-009** source index → exact synapse range
- **T-010** synapse-stream ordering / last marker
- **T-011** target accumulation correctness
- **T-012** small-network known spike sequence
- **T-013** random seeded network differential test
- **T-014** DDR image checksum + manifest match
- **T-015** real-subset differential test
- **T-016** full-system replay determinism; if the model includes noise, fix the PRNG seed

## 3. KV260 physical-board checkpoints

These `T-HW-*` items are physical-lab oracles. They do not replace T-001~T-016 model/algorithm correctness tests. Ordinary cloud CI without a real KV260 must never mark them as passed.

- **T-HW-001 Vendor toolchain preflight**: the course-frozen Vivado version, JTAG cable driver, and KV260 board files/board flow work on the development host; retain OS, tool version, board-file/platform version, and preflight output.
- **T-HW-002 Target discovery**: with the KV260 correctly powered, the development host reliably enumerates the target through the course-specified JTAG path; record board/carrier revision and target identification.
- **T-HW-003 First bitstream program**: the frozen clockless `kv260_marker_top` completes synthesis/implementation/DRC for `xck26-sfvc784-2LV-c`, produces a bitstream, and programs successfully through Vivado/JTAG; `bank45_gpio[4:0]` has logical value `5'b10101` under the frozen Bank 45 XDC. Because this proof contains no clocked timing path, the build must state `TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS` rather than pretending to prove timing closure. Retain the timing summary, bitstream SHA-256, `xck26*` target identification, program log, and a real visible marker observation. DS34 is not the primary oracle for direct JTAG programming.
- **T-HW-004 Physical clock/reset/I/O**: `pl_clk0` (nominal 100 MHz) drives `kv260_blink_core`; PS `pl_resetn0` feeds `proc_sys_reset`, whose `peripheral_aresetn` is the design-local active-low reset. The implemented design must contain a real clock and at least one setup timing path; the worst setup slack must be non-negative or the build is FAIL. The Bank 45 XDC logical-port→package-pin mapping must match the frozen table; `bank45_gpio[0]` shows periodic activity while the remaining marker bits stay stable. Wrong constraints, held reset, missing clock, no setup timing path, or negative setup slack must block PASS. SW2 proves only SOM-level hard reset and is not automatically equivalent to module reset.
- **T-HW-005 PS/Linux first boot**: the course-frozen starter Linux image is version/checksum verified and written to microSD; KV260 boots through the course-specified UART console, produces a boot log, and reaches a shell; the learner distinguishes the development host from the runtime host/PS.
- **T-HW-006 Host↔PL loopback**: after T-HW-005 passes, the runtime host writes PL state/operations and reads results back in a fixed sequence; a self-checking script detects wrong values/order and distinguishes Linux/transport failure from core-behavior failure.
- **T-HW-007 BRAM neuron-state store**: state read/write is correct across multiple addresses, and synthesis/resource reports show the intended on-chip-memory mapping.
- **T-HW-008 Small FlyBrain replay**: for a fixed network image / seed / input, KV260 spike/state traces match the Python fixed-point reference under the frozen contract.
- **T-HW-009 DDR integrity**: a known payload reads back byte-for-byte or with the approved checksum; any integrity failure blocks performance claims.
- **T-HW-010 AXI/burst measurement**: with the same bitstream, data volume, payload, and measurement boundary, each access pattern gets 5 warm-up runs followed by at least 20 measured repetitions; use the median as the primary result and retain all raw samples plus min/max. A second batch in the same session should differ from the first batch median by ≤10%; otherwise label the result `measurement unstable` and make no performance conclusion.
- **T-HW-011 Hardware evidence manifest**: every physical checkpoint records Git commit, board model/revision, development-host OS, tool version, board/platform version when known, Linux-image/version when PS boot is involved, bitstream SHA-256 and/or build hash when applicable, test input, output summary, retained artifact paths, and date. These are explicit manifest fields, not information hidden only inside free-form notes.

### 3.1 Minimum physical evidence

“No tool error” is not a pass criterion. A board test needs at least one direct evidence source:

- toolchain/version preflight log;
- target/program log;
- UART boot log;
- physical/readable I/O observation;
- host readback;
- hardware trace;
- resource/timing report;
- differential replay report;
- DDR integrity/bandwidth raw samples + summary.

A photo may supplement evidence that a real board visibly changed, but it never replaces a machine-readable oracle.

### 3.2 Default performance-measurement protocol

Unless a lab justifies a stricter protocol with real evidence, board-level performance comparisons default to:

1. pass correctness / integrity first;
2. fix bitstream, data volume, payload, and timer boundaries;
3. exclude 5 warm-up runs from statistics;
4. measure each access pattern at least 20 times;
5. report the median as the primary value and retain raw samples plus min/max;
6. repeat a second measurement batch in the same session; the two batch medians must differ by ≤10% to call the result reproducible;
7. state whether host/software overhead is included in the timer.

If item 6 fails, the result may be reported only as an unstable observation, not as evidence for a “faster/slower” engineering conclusion.

### 3.3 Hardware runner / CI boundary

- A full Vivado + physical-board run is not required on every normal CI commit.
- Automatable HDL, report parsers, and host self-check scripts belong in ordinary CI.
- `T-HW-*` steps that require a real KV260 run as a manual physical checkpoint or controlled hardware runner.
- PRs/documentation must not say “board verified” unless physical evidence actually exists for a specific commit/artifact.

## 4. Performance metrics
- **P-001** max clock frequency
- **P-002** synaptic events / second
- **P-003** spikes / second
- **P-004** average / 99th-percentile event latency
- **P-005** DDR bandwidth utilization
- **P-006** BRAM/URAM/DSP/LUT usage
- **P-007** power estimate / measured board power
- **P-008** real-time factor

## 5. Learning verification
At the end of each chapter, the learner should be able to answer:
1. What practical problem did the newly introduced hardware concept solve?
2. Which state is stored, and where?
3. Which module or reference defines the truth for this behavior?
4. When a test fails, should debugging start from the model, interface, or implementation?
5. Did this slice introduce multiple still-unmastered major concepts? If yes, return to ADD/RMD and split the slice.

## 6. Additional rules for AI-generated code
- When AI writes RTL, it must also provide an interface explanation and a testbench/test-vector plan.
- Critical arithmetic requires a bit-level reference; “looks reasonable” is not acceptable.
- Before AI changes a public interface, update MDD/TRACE.
- Before AI changes model semantics, update URD/ADD/TDD; do not silently change RTL to make a test pass.
- Any AI claim about passing tests, timing closure, or performance must be backed by the corresponding command, waveform, report, or benchmark evidence.

## 7. Minimal CI (partially implemented)

Current status:
- Python tests: **implemented** (Python exercise infrastructure)
- RTL compile: **implemented**
- fast RTL unit tests: **implemented**, including teaching-boundary characterization
- Verilator RTL lint: **implemented**
- Yosys synthesis sanity: **implemented**
- lint/format: **partially implemented**; there is no unified Python format/lint gate yet
- trace-consistency check: **not yet automated**
- bilingual-ID consistency check: **partially automated**; Exercise Notebooks and LAB-HW-00~04 enforce bilingual cell-structure/ID consistency
- KV260 Physical Lab contract checks: **implemented for LAB-HW-00~04**; CI checks bilingual Notebook structure, frozen XDC/board-helper contracts, LAB-HW-03/04 open-source RTL behavior, and Tcl helper paths where they can be exercised without Vivado. It does not claim physical-board verification or a real Vivado full build.

A full FPGA build does not need to run on every CI invocation; it can be reserved for checkpoints or nightly builds. Physical KV260 `T-HW-*` results must also follow the physical-evidence boundary in Section 3.2.
