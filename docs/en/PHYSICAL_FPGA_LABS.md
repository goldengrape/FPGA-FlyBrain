# PHYSICAL_FPGA_LABS — Physical FPGA Lab Teaching Standard

## 0. Goal

A Concept Lesson answers why a hardware concept is needed and what it means. A Physical Lab answers how a learner performs it on a real KV260 and leaves reviewable evidence.

Physical Labs target a learner with **zero previous FPGA, embedded-Linux, or vendor-FPGA-toolchain experience**. They must not assume that Vivado, cable drivers, board files, cables, power, JTAG, UART, microSD, Linux boot, programming, or constraints are already familiar.

See [KV260_REFERENCE_PLATFORM.md](KV260_REFERENCE_PLATFORM.md).

## 1. Relationship between lessons and labs

```text
Concept Lesson
    ↓ establish model, terms, expectation
Physical Lab
    ↓ real setup / connection / build / program / boot / run / observe
Evidence
    ↓ report / readback / serial log / photo / hash / measurement
Human Check
    ↓ learner explains what happened
Engineering Handoff
```

A Physical Lab is not a copy of the concept lesson with screenshots added. It owns real-device operation, troubleshooting, and evidence capture.

## 2. Required structure of every lab

Each Physical Lab includes at least:

1. **What should be on the desk**: board, power supply, cables, SD card/peripherals;
2. **Preflight check**: power state, correct connector, voltage/safety boundaries, required software versions;
3. **One primary new physical operation**;
4. **Connection Map**: inline SVG plus official connector names for the path used in this lab;
5. **Build / Program / Boot / Run**: explicitly separated when applicable;
6. **Expected Evidence**: what success looks like, not merely “no error”;
7. **If it does not work**: a layered troubleshooting tree;
8. **Human Check**: what the current evidence proves and does not prove;
9. **Save Evidence**: board revision, tool version, Git commit, artifact hash, and experimental output.

Screenshots may help locate UI elements, but they are never the only specification. Critical buttons/commands, inputs, outputs, and pass criteria must also exist as searchable text.

## 3. Failure-layer order

Physical labs debug in this order instead of immediately editing RTL:

```text
vendor toolchain / driver / board files
  ↓
power
  ↓
physical connection / cable
  ↓
target enumeration / JTAG
  ↓
synthesis / implementation
  ↓
constraints / timing
  ↓
programming
  ↓
PS boot / UART / Linux
  ↓
runtime I/O / host transport
  ↓
FlyBrain core behavior
```

Evidence proves only the relevant layer and explicitly connected contracts. “Program succeeded” does not prove the neuron algorithm is correct, and “Linux booted” does not prove that the PS↔PL transport is correct.

## 4. Reset layers must stay distinct

KV260 exposes reset mechanisms at different levels. The course must distinguish:

- **SW2 / SOM reset**: a board/SOM-level hard reset; it resets the SOM and is not automatically the same thing as a SystemVerilog module's `rst_n`;
- **PS/platform reset**: reset generated/distributed by platform infrastructure;
- **FlyBrain design-local reset**: the logical reset contract of a specific RTL block.

Before LAB-HW-04 freezes the design-local reset source, course material must not say or imply that pressing SW2 is equivalent to asserting a neuron's RTL `rst_n`. If a lab uses SW2, it proves only SOM-level reset. A local PL-design reset must name its actual source and polarity.

## 5. KV260 Physical Lab path

### LAB-HW-00 — Vendor toolchain preflight

**Primary new operation:** verify the vendor toolchain on the development host without powering a board or writing RTL.

The learner only handles development-host setup:

- install the course-frozen AMD Vivado version;
- install/verify the JTAG cable driver;
- install/verify the course-frozen KV260 board files / board flow;
- record OS, Vivado version, and board-file/platform version;
- run course-provided version and board-definition checks.

This lab does not connect the board, generate a bitstream, or teach AXI.

**Pass evidence:** tool/version/board-definition preflight passes and textual output is saved. The exact Vivado version and commands are frozen in this lab's prose only after a real-KV260 dry run.

### LAB-HW-01 — Board orientation

**Primary new operation:** identify the real interfaces without powering the board or writing RTL.

The learner identifies:

- K26 SOM and carrier card;
- J12 12 V power input;
- J4 FTDI USB UART/JTAG;
- J11 microSD;
- J10 Ethernet;
- SW2 SOM-level reset;
- at least one later I/O/expansion path;
- carrier revision marking according to the real board and official interface figure.

**Pass evidence:** a completed board inventory recording the actual carrier revision and a correct explanation that SW2 is a SOM reset, not the default FlyBrain local RTL reset.

### LAB-HW-02 — Power + target detection

**Primary new operation:** power the board correctly and let the LAB-HW-00-verified tools enumerate a real target.

This lab does not change FlyBrain RTL and does not teach AXI.

The learner separates:

- 12 V board power;
- J4 USB data/JTAG/UART;
- development host;
- target device.

**Pass evidence:** stable target enumeration plus target identification. Detection failures are debugged through power → USB/JTAG → driver/tool instead of editing RTL.

### LAB-HW-03 — First bitstream

**Primary new operation:** take minimal RTL through synthesis → implementation → bitstream → program.

The first implementation uses a PL proof that is observable and supported by the official board flow/schematic. The exact user output and constraints are frozen when the lab prose is implemented; this standards document does not guess a pin.

**Pass evidence includes at least:**

- no blocking implementation/timing error;
- bitstream hash;
- programming success;
- **configuration evidence appropriate to the actual programming path**;
- at least one observable result demonstrating that the learner's design, not merely board power, is active.

**DS34 is not a universal JTAG-programming oracle.** AMD defines DS34 as the PS done indication that the PS successfully loaded a PL design. It may be evidence only when the lab's actual configuration path matches that meaning. If LAB-HW-03 configures PL directly through Vivado/JTAG, use Vivado/device programming status plus the design's own observable output as the primary evidence.

### LAB-HW-04 — Constraints + clock/reset/I/O

**Primary new operation:** connect logical RTL ports to physical board resources through board/constraint mapping.

Teach only what this lab needs:

- clock source / period;
- design-local reset semantics;
- one safe board-visible I/O;
- I/O-standard / voltage boundary.

This lab must freeze the source and polarity of the local reset used by this design and repeat that SW2 is a SOM-level hard reset, not automatically a module reset.

**Pass evidence:** the course-frozen physical/readable input or local-reset source changes the output as specified; the learner can explain why an RTL port name has no intrinsic physical-pin meaning and can distinguish SOM reset from design-local reset.

### LAB-HW-05 — PS/Linux first boot + UART console

**Prerequisite:** LAB-HW-00~04.

**Primary new operation:** boot the KV260 PS/runtime host independently, without simultaneously learning the PS↔PL transport.

The learner:

- obtains and verifies the course-frozen starter Linux image;
- writes the image to microSD;
- uses the course-specified UART-console path;
- boots the KV260;
- observes the boot log and completes first login / shell check;
- distinguishes the development host from the KV260 PS/Linux runtime host.

This lab does not require host↔PL register readback and does not teach full AXI.

**Pass evidence:** image/version/checksum, UART boot log, kernel/OS identification, and one simple shell-command result are saved. The learner can explain why “JTAG programs PL” and “PS/Linux boots” are different paths.

### LAB-HW-06 — Real host↔PL loopback

**Prerequisites:** LSN-015 and LAB-HW-05.

**Primary new operation:** after PS/Linux boot is understood, let the KV260 runtime host control PL.

The minimum semantics remain those introduced in Lesson 15:

```text
write value → PL stores/processes → read back result
```

The semantic contract is frozen first; RMD-012B then selects the smallest stable KV260 runtime transport. Full AXI is not made a prerequisite merely to get the first loopback working.

**Pass evidence:** write, PL-state change, and readback ordering match the contract; a self-checking script detects wrong values/order and distinguishes Linux/transport failures from core-behavior failures.

### LAB-HW-07 — BRAM neuron state

**Primary new operation:** map Lesson 9's abstract `state[address]` onto real FPGA on-chip memory.

Require only:

- role difference between register arrays and block RAM;
- address;
- read/write;
- actual synchronous-read behavior used by this design;
- confirmation of memory resources in synthesis/resource reports.

Primitive parameters, ECC, and complex multi-port arbitration are deferred.

**Pass evidence:** multi-address state read/write is correct and the resource report matches the intended mapping.

### LAB-HW-08 — Small FlyBrain replay

**Primary new operation:** move an already verified small network onto KV260 without redefining the algorithm.

Use the same fixed input/seed:

```text
Python fixed reference
        ↕ compare
KV260 FlyBrain small network
```

**Pass evidence:** spike/state replay matches the frozen reference contract, with bitstream, network fixture, input fixture, and output hash/trace recorded.

### LAB-HW-09 — DDR integrity

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

**Pass evidence:** integrity PASS + transfer size + elapsed time + effective bandwidth, with access pattern recorded. Any integrity failure blocks performance conclusions.

### LAB-HW-10 — AXI/burst measurement

**Prerequisites:** LSN-018 and LAB-HW-09.

**Primary new operation:** compare effective bandwidth/latency for small/scattered versus contiguous/burst-oriented paths on real hardware.

Using and measuring the platform path is mandatory. Writing a full AXI master from scratch is optional.

Default measurement protocol (lab prose may be stricter with evidence, but not vaguer):

- same bitstream, data volume, payload, and measurement boundary;
- perform **5 warm-up runs**, excluded from statistics;
- at least **20 measured repetitions** for each access pattern;
- use the **median** as the primary result and retain min/max plus all raw samples;
- repeat another measurement batch in the same session; the two batch medians should differ by **≤10%**. If they differ by more than 10%, report “measurement unstable” and make no performance conclusion;
- state the workload contract, timer boundaries, and whether host/software overhead is included.

**Pass evidence:** at least two access patterns satisfy the reproducible-benchmark protocol; results must not claim “AXI/FPGA is faster” without a workload contract.

## 6. Content intentionally not taught in the first physical track

The first Physical Lab track does not systematically teach:

- internal JTAG protocol state machines;
- boot-firmware internals;
- Linux kernel/driver development;
- DDR PHY training;
- full AXI channel/ordering/outstanding/coherency behavior;
- all Vivado IP Integrator features;
- advanced floorplanning/timing closure;
- a complete clock-domain-crossing curriculum.

Add a bridge lab only when FlyBrain actually requires one and the existing abstraction no longer suffices.

## 7. Assessment and evidence

Physical Labs do not force every task into a Python grader. Formal evidence may include:

- toolchain/version preflight logs;
- parsed Vivado reports;
- programming/target logs;
- UART boot logs;
- terminal readback;
- self-checking host scripts;
- hardware output traces;
- photos as supplemental evidence;
- resource/timing summaries;
- bitstream/build manifests;
- differential replay reports;
- bandwidth raw samples + summaries.

Automatable pieces remain in CI. Steps requiring a real KV260 belong in a physical checkpoint/hardware runner; ordinary CI must not pretend that board verification occurred.

## 8. Documentation-first implementation order

This revision first completes:

1. URD / ADD / LEARNING_PATH / ROADMAP;
2. RMD / MDD / TDD / TRACE;
3. KV260 reference-platform and Physical-Lab standards.

Only then may the project:

4. author `labs/zh/` and `labs/en/`;
5. freeze the exact Vivado version, board files, pins/constraints, starter Linux image, and host transport in LAB-HW-00/02/03/05/06 prose;
6. implement `boards/kv260/`, RTL/platform scripts;
7. dry-run every lab on a real KV260;
8. add automatable pieces to CI.

No lab enters board-specific implementation before its documentation and oracle are approved.
