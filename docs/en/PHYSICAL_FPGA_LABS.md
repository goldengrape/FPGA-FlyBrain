# PHYSICAL_FPGA_LABS — Physical FPGA Lab Teaching Standard

## 0. Goal

A Concept Lesson answers why a hardware concept is needed and what it means. A Physical Lab answers how a learner performs it on a real KV260 and leaves reviewable evidence.

Physical Labs target a learner with **zero previous FPGA experience**. They must not assume that vendor UI, cables, power, JTAG, board files, programming, or constraints are already familiar.

See [KV260_REFERENCE_PLATFORM.md](KV260_REFERENCE_PLATFORM.md).

## 1. Relationship between lessons and labs

```text
Concept Lesson
    ↓ establish model, terms, expectation
Physical Lab
    ↓ real connection / build / program / observe
Evidence
    ↓ report / readback / photo / hash / measurement
Human Check
    ↓ learner explains what happened
Engineering Handoff
```

A Physical Lab is not a copy of the concept lesson with screenshots added. It owns real-device operation, troubleshooting, and evidence capture.

## 2. Required structure of every lab

Each Physical Lab includes at least:

1. **What should be on the desk**: board, power supply, cables, SD card/peripherals;
2. **Preflight check**: power state, correct connector, voltage and safety boundaries;
3. **One primary new physical operation**;
4. **Connection Map**: inline SVG plus official connector names for the path used in this lab;
5. **Build / Program / Run**: explicitly separated stages;
6. **Expected Evidence**: what success looks like, not merely “no error”;
7. **If it does not work**: a layered troubleshooting tree;
8. **Human Check**: what the current evidence proves and does not prove;
9. **Save Evidence**: board revision, tool version, Git commit, artifact hash, and experimental output.

Screenshots may help locate UI elements, but they are never the only specification. Critical buttons/commands, inputs, outputs, and pass criteria must also exist as searchable text.

## 3. Failure-layer order

Physical labs debug in this order instead of immediately editing RTL:

```text
power
  ↓
physical connection / cable
  ↓
target enumeration / driver / JTAG
  ↓
board selection / toolchain
  ↓
synthesis / implementation
  ↓
constraints / timing
  ↓
programming
  ↓
runtime I/O / host transport
  ↓
FlyBrain core behavior
```

Evidence proves only the relevant layer and explicitly connected contracts. For example, “program succeeded” does not prove the neuron algorithm is correct.

## 4. KV260 Physical Lab path

### LAB-HW-00 — Board orientation

**Primary new operation:** identify the real interfaces without powering the board or writing RTL.

The learner identifies:

- K26 SOM and carrier card;
- J12 12 V power input;
- J4 FTDI USB UART/JTAG;
- J11 microSD;
- J10 Ethernet;
- SW2 reset;
- at least one later I/O/expansion path;
- carrier revision marking according to the real board and official interface figure.

**Pass evidence:** a completed board inventory recording the actual carrier revision.

### LAB-HW-01 — Power + target detection

**Primary new operation:** power the board correctly and let the development tools enumerate a real target.

This lab does not change FlyBrain RTL and does not teach AXI.

The learner separates:

- 12 V board power;
- J4 USB data/JTAG/UART;
- development host;
- target device.

**Pass evidence:** stable target enumeration plus recorded tool version and target identification. Detection failures are debugged through power → USB/JTAG → driver/tool first.

### LAB-HW-02 — First bitstream

**Primary new operation:** take minimal RTL through synthesis → implementation → bitstream → program.

The first implementation uses a PL proof that is observable and supported by the official board flow/schematic. The exact user output and constraints are frozen when the lab prose is implemented; this standards document does not guess a pin.

**Pass evidence includes at least:**

- no blocking implementation/timing error;
- bitstream hash;
- programming success;
- KV260 PL configuration-status evidence;
- at least one observable result demonstrating that the learner's design, not merely board power, is active.

### LAB-HW-03 — Constraints + clock/reset/I/O

**Primary new operation:** connect logical RTL ports to physical board resources through board/constraint mapping.

Teach only what this lab needs:

- clock source / period;
- reset semantics;
- one safe board-visible I/O;
- I/O-standard / voltage boundary.

**Pass evidence:** physical input/reset changes a physical/readable output as specified, and the learner can explain why an RTL port name has no intrinsic physical-pin meaning.

### LAB-HW-04 — Real host↔PL loopback

**Prerequisite:** LSN-015.

**Primary new operation:** distinguish JTAG programming from runtime control of PL by the KV260 PS/runtime host.

The minimum semantics remain those introduced in Lesson 15:

```text
write value → PL stores/processes → read back result
```

The semantic contract is frozen first; RMD-012B then selects the smallest stable KV260 runtime transport. Full AXI is not made a prerequisite merely to get the first loopback working.

**Pass evidence:** write, PL-state change, and readback ordering match the contract and can be repeated with self-checking error paths.

### LAB-HW-05 — BRAM neuron state

**Primary new operation:** map Lesson 9's abstract `state[address]` onto real FPGA on-chip memory.

Require only:

- role difference between register arrays and block RAM;
- address;
- read/write;
- actual synchronous-read behavior used by this design;
- confirmation of memory resources in synthesis/resource reports.

Primitive parameters, ECC, and complex multi-port arbitration are deferred.

**Pass evidence:** multi-address state read/write is correct and the resource report matches the intended mapping.

### LAB-HW-06 — Small FlyBrain replay

**Primary new operation:** move an already verified small network onto KV260 without redefining the algorithm.

Use the same fixed input/seed:

```text
Python fixed reference
        ↕ compare
KV260 FlyBrain small network
```

**Pass evidence:** spike/state replay matches the frozen reference contract, with bitstream, network fixture, input fixture, and output hash/trace recorded.

### LAB-HW-07 — DDR integrity

**Prerequisites:** LSN-016 and LSN-017.

**Primary new operation:** perform stable external-memory read/write through the KV260 platform infrastructure without implementing a DDR PHY/controller.

Order:

```text
known payload
→ write
→ read
→ byte-for-byte/checksum compare
→ only then measure
```

**Pass evidence:** integrity PASS + transfer size + elapsed time + effective bandwidth, with access pattern recorded.

### LAB-HW-08 — AXI/burst measurement

**Prerequisites:** LSN-018 and LAB-HW-07.

**Primary new operation:** compare effective bandwidth/latency for small/scattered versus contiguous/burst-oriented paths on real hardware.

Using and measuring the platform path is mandatory. Writing a full AXI master from scratch is optional.

**Pass evidence:** a reproducible benchmark with the same data volume, explicit measurement window, and at least two access patterns; results must not claim “AXI/FPGA is faster” without a workload contract.

## 5. Content intentionally not taught in the first physical track

The first Physical Lab track does not systematically teach:

- internal JTAG protocol state machines;
- DDR PHY training;
- full AXI channel/ordering/outstanding/coherency behavior;
- all Vivado IP Integrator features;
- boot-firmware internals;
- advanced floorplanning/timing closure;
- a complete clock-domain-crossing curriculum.

Add a bridge lab only when FlyBrain actually requires one and the existing abstraction no longer suffices.

## 6. Assessment and evidence

Physical Labs do not force every task into a Python grader. Formal evidence may include:

- parsed Vivado reports;
- programming/target logs;
- terminal readback;
- self-checking host scripts;
- hardware output traces;
- photos as supplemental evidence;
- resource/timing summaries;
- bitstream/build manifests;
- differential replay reports;
- bandwidth measurements.

Automatable pieces remain in CI. Steps requiring a real KV260 belong in a physical checkpoint/hardware runner; ordinary CI must not pretend that board verification occurred.

## 7. Documentation-first implementation order

This revision first completes:

1. URD / ADD / LEARNING_PATH / ROADMAP;
2. RMD / MDD / TDD / TRACE;
3. KV260 reference-platform and Physical-Lab standards.

Only then may the project:

4. author `labs/zh/` and `labs/en/`;
5. freeze the exact Vivado flow, board pins/constraints, and host transport;
6. implement `boards/kv260/`, RTL/platform scripts;
7. dry-run every lab on a real KV260;
8. add automatable pieces to CI.

No lab enters board-specific implementation before its documentation and oracle are approved.
