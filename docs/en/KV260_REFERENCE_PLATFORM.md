# KV260_REFERENCE_PLATFORM — KV260 Reference Hardware Platform

## 0. Role of this document

This document freezes the **reference development board for physical FPGA teaching** in FPGA-FlyBrain. It does not replace AMD's official manuals. It defines how this project uses the board, what evidence every physical lab must record, and which board-specific details must stay outside the FlyBrain core RTL.

**Reference board: AMD Kria KV260 Vision AI Starter Kit.**

Other boards may be added later, but the first complete beginner physical path is guaranteed only for KV260. Concept lessons remain board-neutral where practical; `LAB-HW-*` Physical Labs may explicitly use KV260 interfaces, tools, and board files.

## 1. Why freeze a reference board

Understanding FPGA concepts can remain board-neutral. A first real FPGA experience cannot be reduced to abstract instructions. A learner with zero FPGA experience needs to know:

- where power is connected;
- which USB interface carries JTAG/UART;
- how the development computer confirms that a target exists;
- which Vivado board definition to select;
- how a bitstream reaches the PL;
- where reset, I/O, DDR, and the host/PS live on this board;
- how to distinguish power, connection, toolchain, constraint, programming, and runtime failures.

The course therefore uses:

```text
board-neutral core concepts
        +
KV260 reference physical path
        +
platform shell isolation
```

rather than claiming generic board support at the cost of an unusable beginner tutorial.

## 2. KV260 baseline confirmed by AMD documentation

Physical labs are authored against the AMD **Kria KV260 Vision AI Starter Kit User Guide (UG1089)**, KV260 Data Sheet (DS986), Vivado Board Flow documentation, and matching board files.

The current official documentation confirms:

- the starter kit consists of a **K26 SOM + carrier card + thermal solution**;
- the board requires a **12 V / 3 A** supply through **J12**; the starter-kit box itself does not include the power adapter;
- carrier-card **J4** provides integrated FTDI USB 2.0 UART + JTAG;
- **J3** provides direct JTAG bypassing the FTDI device;
- **J11** is the microSD interface;
- **J10** is 1 Gb/s Ethernet;
- **SW2** resets the SOM;
- SOM **DS34** is the PS done LED and indicates successful loading of a PL design;
- KV260 carrier-card revisions 1.0 and 2.0 both exist, with some revision-specific differences;
- Vivado provides a **KV260 Starter Kit** board flow using SOM/companion-card metadata for fixed platform resources and associated constraints;
- AMD's software getting-started path uses a starter Linux image on microSD; later host↔PL labs will distinguish the external development computer from the PS/Linux runtime host on the KV260.

Official entry points:

- UG1089: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit
- Interfaces: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Interfaces
- Powering: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Powering-the-Starter-Kit-and-Power-Budgets
- Vivado Board Flow: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Vivado-Board-Flow
- Software Getting Started: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Software-Getting-Started

## 3. Learner hardware preparation

Each lab will re-check its exact bill of materials. This documentation pass freezes these categories:

- KV260 Vision AI Starter Kit;
- a power supply meeting the official 12 V / 3 A requirement;
- microSD card for the official Linux / later PS runtime path;
- a USB data cable suitable for J4;
- a development computer running the course-supported AMD Vivado toolchain;
- for later Pmod I/O labs, only course-listed 3.3 V compatible devices/modules.

**A connected USB cable must not be treated as proof that the board is powered.** KV260 board power and JTAG/UART data connectivity are separate paths.

## 4. Distinguish the two host roles

KV260 is a SoC FPGA platform. Physical teaching must separate two easily confused roles.

### Development host

The external computer that:

- edits RTL;
- runs Vivado;
- performs synthesis / implementation / bitstream generation;
- discovers and configures the target over JTAG;
- collects build reports.

### Runtime host / PS

The Arm processing system on the K26, later typically running Linux, that handles:

- runtime control;
- host↔PL register/message exchange;
- files, networking, and experiment control;
- later data loading and telemetry.

Physical Labs must not blur “the development PC programs the device over JTAG” with “runtime software controls PL through the PS↔PL path.”

## 5. Platform abstraction boundary

FlyBrain core RTL must not know KV260 connector names, pins, Linux device paths, or Vivado project layout.

Planned boundary:

```text
FlyBrain core RTL
      │ stable logical interfaces
      ▼
KV260 platform shell
  ├─ clock/reset adaptation
  ├─ board-visible I/O
  ├─ PS↔PL control path
  ├─ on-chip memory mapping
  └─ DDR/platform integration
      │
      ▼
KV260 board files / constraints / build scripts
```

Board-specific implementation belongs under the planned:

```text
boards/kv260/
```

KV260 pins and platform IP must not leak into core modules such as `rtl/neuron/` or `rtl/event/`.

## 6. Carrier revision and evidence

Every physical lab must record:

- board model: KV260;
- carrier revision (Rev. 1.0 / Rev. 2.0 or actual marking);
- Vivado/tool version;
- board-file/platform version when identifiable;
- bitstream or build-artifact hash;
- Git commit;
- experiment date;
- photos, terminal/readback, reports, or waveform evidence required by the pass criterion.

If a step is revision-specific, the lab must state that explicitly.

## 7. What this documentation pass does not freeze

This is a **documentation-first** revision. Board code is not written yet, so this pass does not freeze:

- a specific PL user-output pin;
- exact XDC pin assignments;
- whether the final host↔PL implementation uses AXI-Lite, UIO, XRT, or another runtime transport;
- the DDR access software stack;
- the exact Vivado supported version.

Those decisions are made only after the matching `LAB-HW-*` prose and TDD oracle are reviewed. Implementations should prefer AMD's official board flow and must not change the FlyBrain core contract merely because one demo path is convenient.

## 8. Reference-board decision

This document resolves the former URD Q1:

> **The first and fully supported reference development board for FPGA-FlyBrain is the AMD Kria KV260 Vision AI Starter Kit.**

Other boards may later receive porting guides, but the first course release does not maintain multiple zero-experience physical-board walkthroughs.
