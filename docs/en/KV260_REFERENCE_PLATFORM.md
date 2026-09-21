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
- **SW2** is a SOM-level reset; it resets the SOM and **must not be treated automatically as the local `rst_n` of a FlyBrain RTL module**;
- SOM **DS34** is the PS done LED and indicates that **the PS successfully loaded a PL design**; it is not a universal “FPGA configured” indicator for every programming path;
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

Each lab will re-check its exact bill of materials. Before touching the real board, complete **LAB-HW-00 vendor-toolchain preflight** so Vivado, the JTAG cable driver, and KV260 board files are separated from physical-board failures. This documentation pass freezes these categories:

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

A separate **PS/Linux first-boot bridge** belongs between them: starter Linux image → microSD → UART console → boot/login. The learner proves that the PS/Linux runtime host can boot before learning the PS↔PL loopback; Linux boot, serial-console use, and the runtime transport must not arrive for the first time in the same lab.

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

## 7. What the implemented Physical-Lab slice now freezes — and what remains provisional

The documentation-first decision has now advanced through the implemented **LAB-HW-00~10** teaching slice.

The repository now freezes:

- reference target part: `xck26-sfvc784-2LV-c`;
- LAB-HW-03 board-visible logical output and Bank 45 XDC mapping;
- LAB-HW-04 PS `pl_clk0` / `pl_resetn0` clock-reset teaching path;
- direct Vivado/JTAG programming for LAB-HW-03/04/06/07/08/10;
- LAB-HW-05 Ubuntu Server 24.04 LTS first-boot/UART path;
- LAB-HW-06 PS `M_AXI_HPM0_FPD` → AXI GPIO teaching loopback;
- LAB-HW-07 4 KiB BRAM teaching state path;
- LAB-HW-08 deterministic four-neuron board replay;
- LAB-HW-09 64 MiB PS/Linux-managed system-memory integrity sanity path;
- KV260/K26 external system memory: 4 GB DDR4;
- LAB-HW-10 control path: PS `M_AXI_HPM0_FPD` → AXI CDMA `S_AXI_LITE` at **`0xA0020000`**;
- LAB-HW-10 data path: AXI CDMA `M_AXI` → PS **`S_AXI_HP0_FPD`** → DDR;
- LAB-HW-10 AXI CDMA teaching configuration: Simple DMA, 128-bit data, max burst 64, 64-bit addressing, DRE disabled;
- LAB-HW-10 first mapped PL-DDR aperture: `HP0_DDR_LOW`;
- LAB-HW-10 non-coherent buffer contract: course-approved u-dma-buf, at least 2 MiB, physical address from sysfs, device opened with `O_SYNC`;
- LAB-HW-10 workload: identical 256 KiB payload, contiguous = one request, small/scattered = 1024 × 256-byte requests in a fixed permutation;
- LAB-HW-10 benchmark oracle: two batches per pattern, each 5 warm-ups + 20 measured samples, byte-integrity gates, raw samples + median/min/max, and ≤10% inter-batch median drift;
- LAB-HW-10 measurement scope: end-to-end software-controlled DMA workload including Python register programming/polling. It is not a peak-DDR or pure AXI bus-efficiency specification measurement.

The following are **not yet promoted to tested physical facts**:

- the exact physically observed visible-polarity details for the early Bank 45 marker;
- Vivado 2026.1 as the tested/supported course baseline rather than the current authoring candidate;
- a trusted expected SHA-256 for the LAB-HW-05 Ubuntu archive;
- whether the selected Ubuntu 24.04 image/kernel permits the fixed `/dev/mem` teaching mappings used by LAB-HW-06~08/10;
- a real-KV260 T-HW-007/008/009/010 physical PASS;
- a real Vivado LAB-HW-08 or LAB-HW-10 full build on the target device;
- whether the selected course Ubuntu/kernel image provides the required u-dma-buf buffer/cache contract and whether its physical placement lies in the first `HP0_DDR_LOW` aperture;
- whether the live LAB-HW-05 boot firmware leaves the required `S_AXI_HP0_FPD` runtime path usable after direct PL JTAG programming without a PS reinitialization sequence;
- the final formal MOD-004~010 implementations, formal DDR-backed synapse store, production DMA/buffer API, coherent-memory strategy, and final performance claims.

Those remaining facts are promoted only after the matching real-KV260 dry run records T-HW evidence for a specific Git commit, bitstream where applicable, software/buffer-provider identity, and raw evidence.

The implemented board-support code lives under `boards/kv260/`. FlyBrain core RTL still must not depend on KV260 connector names, package pins, Vivado project layout, Linux device paths, or teaching-only AXI CDMA/u-dma-buf choices.

## 8. Reference-board decision

This document resolves the former URD Q1:

> **The first and fully supported reference development board for FPGA-FlyBrain is the AMD Kria KV260 Vision AI Starter Kit.**

Other boards may later receive porting guides, but the first course release does not maintain multiple zero-experience physical-board walkthroughs.
