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
Do a synthesis dry run before buying hardware.

After the board arrives:
1. counter / observable register;
2. minimal host ↔ FPGA loopback;
3. move the already-verified small network onto FPGA.

Completion feeling: the circuit that used to exist only in simulation is now physically running inside the chip.

## Stage 7 — Understand why memory becomes the bottleneck
Build intuition for memory hierarchy and bandwidth before touching DDR/AXI.

Compare:
- sequential access;
- random access;
- burst access.

Then implement:
- DDR read/write integrity tests;
- AXI bursts;
- move the synapse store from on-chip memory to DDR;
- measure bandwidth, latency, and synaptic events/s.

Completion feeling: you understand why modern AI hardware is often limited by data movement rather than by the arithmetic itself.

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
