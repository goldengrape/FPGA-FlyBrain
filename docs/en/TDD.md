# TDD — Check Plan / Test and Verification Document

## 0. Principles
- Define the oracle before writing the implementation.
- Never claim a test passed unless the exact command actually ran successfully.
- The Python float reference is the conceptual oracle; the Python fixed-point reference is the direct RTL oracle.
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
Replay fixed seeds and input events, capture outputs, and compare against RTL simulation and Python references.

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

## 3. Performance metrics
- **P-001** max clock frequency
- **P-002** synaptic events / second
- **P-003** spikes / second
- **P-004** average / 99th-percentile event latency
- **P-005** DDR bandwidth utilization
- **P-006** BRAM/URAM/DSP/LUT usage
- **P-007** power estimate / measured board power
- **P-008** real-time factor

## 4. Learning verification
At the end of each chapter, the learner should be able to answer:
1. What practical problem did the newly introduced hardware concept solve?
2. Which state is stored, and where?
3. Which module or reference defines the truth for this behavior?
4. When a test fails, should debugging start from the model, interface, or implementation?
5. Did this slice introduce multiple still-unmastered major concepts? If yes, return to ADD/RMD and split the slice.

## 5. Additional rules for AI-generated code
- When AI writes RTL, it must also provide an interface explanation and a testbench/test-vector plan.
- Critical arithmetic requires a bit-level reference; “looks reasonable” is not acceptable.
- Before AI changes a public interface, update MDD/TRACE.
- Before AI changes model semantics, update URD/ADD/TDD; do not silently change RTL to make a test pass.
- Any AI claim about passing tests, timing closure, or performance must be backed by the corresponding command, waveform, report, or benchmark evidence.

## 6. Minimal CI (future)
- Python tests
- lint/format
- RTL compile
- fast RTL unit tests
- trace-consistency check
- bilingual-ID consistency check

A full FPGA build does not need to run on every CI invocation; it can be reserved for checkpoints or nightly builds.
