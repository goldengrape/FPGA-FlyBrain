# From Zero to an FPGA FlyBrain — Learning and Implementation Roadmap

> This is the human-facing high-level roadmap. The authoritative task order, IDs, and acceptance criteria live in [RMD](RMD.md).

## Goal
Start from an inspectable LIF neuron and progressively build an event-driven FPGA neural system that can ultimately run a target network constrained by the real MaleCNS connectome, with correctness and performance compared against software references.

## Engineering principles
1. Build the software reference before RTL.
2. Prove the small-scale architecture before scaling it up.
3. Treat computation separately from storage and data movement.
4. Introduce only one major unfamiliar concept per learning slice; add a bridge when the jump is too large.
5. Use AI aggressively for implementation friction, while keeping architecture and acceptance criteria under human control.

## Stage 0 — Turn a neuron into an inspectable program
- Python LIF float reference.
- Fixed random seeds; record membrane-voltage and spike trajectories.
- Basic physiological/mathematical sanity checks.

Completion feeling: you can see one neuron firing by explicit, repeatable rules.

## Stage 1 — Learn fixed point before writing RTL
- Emulate bit width, Q-format, rounding, and saturation in Python.
- Compare float and fixed-point error and spike timing.
- Freeze the first neuron semantics.

Completion feeling: you understand why hardware numbers are not “infinite-precision real values.”

## Stage 2 — Cross from program variables to digital state
- combinational adder;
- clocked counter;
- accumulator + threshold;
- read waveforms and understand registers, clocks, combinational logic, and sequential logic.

Completion feeling: you understand for the first time how “state in a program” becomes “state in a circuit.”

## Stage 3 — First SystemVerilog neuron
- Implement `lif_neuron_engine`.
- Compare Python fixed-point vectors against RTL.
- Use a testbench and waveform to explain input, state, threshold, spike, and reset.

Completion feeling: the same neuron exists in both Python and digital hardware and produces matching results.

## Stage 4 — Use a small amount of hardware to simulate many neurons
- neuron state RAM;
- scheduler / time multiplexing;
- scale from 128 to 1K neurons;
- measure cycles/update and RAM usage.

Completion feeling: you understand why 166K virtual neurons do not require 166K complete physical neuron circuits.

## Stage 5 — Turn a neuron array into an event computer
First trace the complete event journey with only four neurons:

```text
spike(source)
→ queue
→ connectivity lookup
→ (target, weight)
→ target update
```

Then introduce:
- sparse adjacency / CSR-like images;
- spike FIFO;
- synapse reader;
- synapse engine;
- target accumulator.

Completion feeling: a small network processes only actual spikes instead of scanning every connection.

## Stage 6 — Enter a real FPGA for the first time

The reference board is frozen to the **AMD Kria KV260 Vision AI Starter Kit**. Keep the synthesis dry run before buying hardware; after purchase, do not compress “board bring-up” into a single step. Follow the zero-experience Physical Lab sequence:

1. **LAB-HW-00**: complete vendor-toolchain preflight and freeze/verify Vivado, JTAG driver, and KV260 board files;
2. **LAB-HW-01**: identify the real KV260, connectors, SW2 SOM reset, and carrier revision;
3. **LAB-HW-02**: power correctly, distinguish J12 board power from J4 USB/JTAG/UART, and enumerate a real target;
4. **LAB-HW-03**: first synthesis → implementation → bitstream → program;
5. **LAB-HW-04**: connect logical ports and clock/design-local reset to real board resources/constraints;
6. **LAB-HW-05**: complete PS/Linux first boot using microSD + UART without simultaneously learning the runtime transport;
7. **LAB-HW-06**: real KV260 PS/runtime-host ↔ PL minimal loopback;
8. **LAB-HW-07**: map neuron-state RAM onto real on-chip BRAM resources;
9. **LAB-HW-08**: move the verified small FlyBrain network onto KV260 and compare replay against the Python fixed reference.

Completion feeling: the learner can start from an unconfigured development environment and powered-off board, complete toolchain preflight, connect it, discover the target, build/program it, boot PS/Linux, observe physical evidence, and perform host readback, and prove that a small FlyBrain network is actually running on FPGA.

See `KV260_REFERENCE_PLATFORM.md` and `PHYSICAL_FPGA_LABS.md`.

## Stage 7 — Understand why memory becomes the bottleneck
Build memory-hierarchy and bandwidth intuition first, then connect real DDR/AXI.

Physical Labs:

1. **LAB-HW-09**: use the KV260 platform infrastructure for DDR write → read → integrity compare, then measure sequential/random-like access;
2. **LAB-HW-10**: under the same workload, compare small/scattered and burst-oriented transfer latency/effective bandwidth;
3. only after integrity and measurement are stable, move the synapse store from on-chip memory to DDR;
4. then measure bandwidth, latency, and synaptic events/s.

The learner does not implement a DDR PHY/controller, and a full AXI master from scratch is not a prerequisite for the first DDR lab.

Completion feeling: the learner has real KV260 measurements rather than only a toy cost model and can explain why modern AI hardware is often data-movement limited.

## Stage 8 — Run real connectome data for the first time
- MaleCNS converter;
- versioned binary image + manifest/checksum;
- start with a real subgraph of roughly 1K neurons;
- software-vs-FPGA differential test.

Completion feeling: you are no longer running a handwritten toy graph; you are running real biological connectivity data.

## Stage 9 — Scale toward the full target network
Scale in steps:

```text
1K → 10K → 50K → full target
```

Continuously measure:
- DDR bandwidth;
- FIFO depth;
- bank conflicts;
- hotspots;
- FPGA resources;
- real-time factor.

Only after the baseline is correct should you optimize with lazy updates, caching, banking, or multiple synapse engines.

## Stage 10 — Give the FlyBrain a world
The host handles:
- sensory encoding;
- experiment control;
- visualization;
- output decoding.

The FPGA continuously runs the neural system.

Start with a simple 2D environment before moving to a virtual body, game, or robot.

The final benchmark can compare CPU / GPU / FPGA under the same model, data, and inputs for:
- latency;
- throughput;
- memory traffic;
- power / energy efficiency.

## Five learning platforms
```text
1. Computational neuron
2. Digital neuron
3. Event neural network
4. Real FPGA and external memory
5. Real MaleCNS connectome
```

Each platform must end with something visible and testable rather than merely “a body of theory completed.”
