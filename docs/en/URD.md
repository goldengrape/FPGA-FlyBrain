# URD — Idea Brief / User Requirements Document

## 0. Document information
- Project: FPGA FlyBrain / From Membrane Potential to Silicon
- Version: v0.3-r1
- Status: Reference board frozen; physical-lab documentation pass
- Purpose: define why the project exists, who it is for, and what counts as success.

## 1. Vision
Provide a learning and engineering path for university students with a life-science or medical background but little computer-hardware training. The project uses a real Drosophila connectome as the long-running theme, AI-assisted engineering as the working method, and FPGA as the target hardware.

The learner starts from familiar neurophysiology and progressively translates “how a neuron fires” into a mathematical model, digital logic, hardware modules, a sparse event-driven architecture, and finally an FPGA implementation of a spiking network constrained by the Drosophila MaleCNS connectivity. The host computer provides sensory input, reads outputs, visualizes activity, and controls experiments.

## 2. Target learner
Typical learner: second- or third-year undergraduate in medicine, biology, neuroscience, biomedical engineering, or a related field.

### Assumed background
- Understands membrane potential, action potential, threshold, refractory period, synapses, excitation and inhibition.
- Knows basic algebra, calculus, vectors, matrices, and matrix multiplication.
- Has seen basic digital logic such as AND / OR / NOT, without needing fluency.
- May have no prior FPGA, HDL, computer architecture, or embedded-system experience; the course must support a learner receiving an FPGA development board for the first time.
- May have weak programming experience; Python can be learned incrementally as needed.

### Not assumed
- Verilog/SystemVerilog
- FPGA toolchains
- computer architecture
- AXI / DDR / DMA
- neuromorphic computing
- SNN hardware design

## 3. Core user tasks
- **U1** Understand a minimal LIF neuron starting from familiar neurophysiology.
- **U2** Use AI to help produce Python references, SystemVerilog RTL, testbenches, and documentation while remaining able to explain the physical, mathematical, and hardware meaning of the result.
- **U3** Grow one neuron into multiple neurons, sparse synapses, event queues, and an event-driven network.
- **U4** Run the network on FPGA and observe, verify, and measure it.
- **U5** Import a real MaleCNS subgraph and eventually scale to the full target network.
- **U6** Build a Python float → Python fixed-point → RTL/FPGA verification chain.
- **U7** Learn to derive FRs/DPs, analyze coupling, define module contracts and test oracles, and maintain implementation order and traceability.
- **U8** Reach the point where FPGA accelerators, SNN accelerators, sparse accelerators, and neuromorphic hardware literature become approachable.

## 4. Success criteria
### Learning success
- Explain why registers, RAM, FIFO, pipelines, fixed point, DDR bandwidth, and event-driven computation appear in this project.
- Independently explain the state, inputs, outputs, and timing of a LIF neuron RTL implementation.
- Starting from an unconfigured reference board, correctly power/connect it, discover the target, build/program a bitstream, verify minimal physical I/O, complete a host↔PL readback, and distinguish connection/build/program/runtime failures by layer.
- Draft simple FR/DP pairs and a small design matrix for a functional requirement.

### Engineering success
- Runnable Python LIF reference model.
- Simulatable single-neuron SystemVerilog implementation.
- Time-multiplexed multi-neuron implementation.
- Sparse synapse store, spike FIFO, event routing, and synapse engine.
- A repeatably built, programmed, and verified FPGA implementation on the reference AMD Kria KV260 Vision AI Starter Kit, with board/tool/artifact evidence retained.
- External-memory support.
- Real MaleCNS subgraph implementation.
- Ultimately, a full target MaleCNS model with the host handling sensory I/O and visualization.

### Verification success
- Critical arithmetic can be compared with a Python fixed-point reference.
- Each major module has a testbench and a clear test oracle.
- Major build slices have repeatable commands and Git checkpoints.
- Major requirements trace to design, modules, tests, and implementation tasks.

## 5. Current scope
### In scope
LIF / simplified spiking neurons, Python reference models, SystemVerilog RTL, FPGA simulation and board deployment, a zero-experience KV260 Physical Lab path, sparse connectivity, event-driven spike processing, BRAM/URAM/DDR organization, MaleCNS conversion and execution, AI-assisted engineering / vibe coding, Axiomatic Design, testing, traceability, Git checkpoints, and a public educational project.

### Out of scope
Claims of reproducing a complete biological fly brain or consciousness, full Hodgkin–Huxley-level biophysical simulation, analog IC design, transistor/process design, custom ASIC tape-out, medical-device or clinical deployment, and adding STDP, complex neuromodulation, or a full body model in the first implementation cycle.

## 6. Constraints
- **C1** New hardware concepts should be introduced by an actual engineering need in the current build.
- **C2** AI may generate code, but the human owns the model, requirements, interfaces, architecture, and acceptance criteria.
- **C3** “It runs” is never a substitute for verification.
- **C4** Do not create meaningless modules merely to make an Axiomatic Design matrix look diagonal.
- **C5** Keep documents small and useful; future ideas go to a parking lot.
- **C6** Hardware purchase is deferred until simulation stages pass.
- **C7** The first complete physical teaching path freezes the **AMD Kria KV260 Vision AI Starter Kit** as the reference board. FlyBrain core logic and stable interfaces remain portable; board-specific content is isolated in the platform shell and Physical Labs.

## 7. Assumptions
- **A1** MaleCNS data remains publicly accessible during the project.
- **A2** The baseline model uses a simplified LIF neuron rather than full biophysical realism.
- **A3** Fixed point is the primary FPGA numeric representation; floating point is used for software reference.
- **A4** Early phases may use AI to generate substantial boilerplate and testbench code, but all critical modules require explanation and verification.

## 8. Open questions and resolved decisions

**Resolved:**
- **Q1** The first complete board-teaching path is locked to the **AMD Kria KV260 Vision AI Starter Kit**. Other boards may later receive porting guides, but the first course release does not maintain multiple zero-experience board walkthroughs.

**Still open:**
- **Q2** For the full MaleCNS model, use fixed time steps with sparse propagation or eventually implement lazy/event-driven neuron updates?
- **Q3** Publication language? Current decision: GitHub engineering documents are maintained in both English and Chinese.
- **Q4** Final closed-loop demo: virtual body, simple game, or custom 2D environment?

## 9. North star
> Enable a life-science student to translate neurophysiology into a verifiable, runnable, measurable digital hardware system and use that experience to enter the world of AI hardware.
