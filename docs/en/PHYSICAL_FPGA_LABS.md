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

- use the current **authoring candidate** AMD Vivado version named by the lab;
- install/verify the JTAG cable driver;
- install/verify the matching KV260 board files / board flow;
- record OS, Vivado version, and board-file/platform version;
- run course-provided version and board-definition checks.

This lab does not connect the board, generate a bitstream, or teach AXI.

**Pass evidence:** tool/version/board-definition preflight passes and textual output is saved. A candidate version may be named during authoring so the prose/scripts do not drift, but it becomes the **tested course-support baseline only after a real-KV260 dry run** with retained evidence.

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

**Primary new operation:** take a tiny RTL design with no clock/reset/AXI/Linux dependency through synthesis → implementation → bitstream → JTAG programming.

The first teaching implementation is now frozen as a **Bank 45 GPIO marker**:

- top module: `kv260_marker_top`;
- logical output: `bank45_gpio[4:0]`;
- fixed logical pattern: `5'b10101`;
- target part: `xck26-sfvc784-2LV-c`;
- physical mapping comes from `boards/kv260/constraints/bank45_gpio.xdc`;
- the XDC is grounded in the AMD/Xilinx Board Store KV260 carrier `bank45_gpio` 5-bit LED-class interface and the K26 SOM `part0_pins.xml` package-pin mapping.

Frozen package pins:

| logical bit | K26 SOM signal | package pin | I/O standard |
|---|---|---|---|
| `bank45_gpio[0]` | SOM240 D18 | J11 | LVCMOS33 |
| `bank45_gpio[1]` | SOM240 B17 | J10 | LVCMOS33 |
| `bank45_gpio[2]` | SOM240 B18 | K13 | LVCMOS33 |
| `bank45_gpio[3]` | SOM240 A15 | F11 | LVCMOS33 |
| `bank45_gpio[4]` | SOM240 C24 | A12 | LVCMOS33 |

Learners do **not** need to understand those constraints yet; the XDC is treated as a course-provided board adapter. LAB-HW-04 explains why RTL ports need physical mapping and why these pins are used.

The build helper emits the bitstream, utilization report, and timing summary into a fixed build directory. The programming helper accepts only an existing bitstream and requires an `xck26*` device on the JTAG chain before programming.

**Pass evidence includes:**

- synthesis/implementation/DRC complete; because this marker is intentionally clockless, the build explicitly reports `TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS` and retains a timing summary rather than claiming timing closure;
- bitstream SHA-256;
- Vivado/JTAG programming success;
- `xck26*` target identification;
- a stable, repeatable marker state on the Bank 45 LED-class output, with photo/observation retained;
- current Git commit and carrier revision.

**Physical-polarity boundary:** Board Store data establishes that these five signals are an LED-class `bank45_gpio` output and establishes the pin mapping. Before a real-KV260 dry run, the course does not invent a silkscreen LED designator or visual polarity. The learner records the actual visible state; physical designator/polarity becomes a tested fact only after the real dry run.

**DS34 is not a universal JTAG-programming oracle.** AMD defines DS34 as the PS-done indication when the PS successfully loaded a PL design. LAB-HW-03 uses direct Vivado/JTAG programming, so the primary evidence is Vivado/device programming status plus the design's Bank 45 observable output.

### LAB-HW-04 — Constraints + clock/reset/I/O

**Primary new operation:** after the learner can already generate/program a bitstream, connect logical RTL to a physical board resource through explicit clock/reset/platform glue and constraints.

The first teaching implementation is frozen as a **PS-clock/reset-driven PL blink proof**:

- the PS is used only as platform infrastructure; Linux/AXI is not introduced;
- Zynq UltraScale+ MPSoC `pl_clk0` supplies the PL clock, taught as nominal 100 MHz;
- PS `pl_resetn0` feeds `proc_sys_reset`;
- `proc_sys_reset/peripheral_aresetn` is the frozen **design-local active-low reset**;
- `kv260_blink_core` divides the clock with a counter and drives a visible periodic change on `bank45_gpio[0]`, while the remaining bits keep a marker;
- the physical output reuses LAB-HW-03's `bank45_gpio.xdc`, so this lab adds clock/reset/constraint interpretation instead of a second peripheral.

The lab must distinguish three reset layers:

1. **SW2** — SOM-level hard reset;
2. **PS `pl_resetn0`** — platform reset source;
3. **`peripheral_aresetn`** — synchronized design-local reset delivered to `kv260_blink_core.resetn`.

It is valid to say SW2 is upstream of the system reset sequence; it is **not** valid to say SW2 is the RTL module's `resetn`.

Teach only the constraints needed here:

- a logical RTL port has no intrinsic package pin;
- `PACKAGE_PIN` maps the port to the K26 package;
- `IOSTANDARD LVCMOS33` follows the Board Store constraint for these Bank 45 carrier signals;
- the clock arrives through the internal PS→PL clock path, so no fake external clock constraint is attached to `bank45_gpio`.

**Pass evidence:**

- synthesis/implementation complete, a real clock plus setup/hold timing paths are present, and worst setup/hold slack are both non-negative;
- blink bitstream hash and programming log;
- periodic activity on `bank45_gpio[0]` with the other marker bits stable;
- the learner can explain at least one logical-bit → package-pin XDC mapping;
- the learner can distinguish `pl_resetn0`, `peripheral_aresetn`, and SW2;
- resource/timing report, Git commit, board/carrier revision are recorded in the T-HW-011 evidence manifest.



### LAB-HW-05 — PS/Linux first boot + UART console

**Prerequisite:** LAB-HW-00~04.

**Primary new operation:** boot the KV260 PS/runtime host independently, without simultaneously learning the PS↔PL transport.

The Stage-2 authoring image is frozen to the current AMD/Canonical Kria K26 Ubuntu Server image:

- distribution: **Ubuntu Server 24.04 LTS**;
- image archive: `iot-limerick-kria-classic-server-2404-classic-24.04-x07-20250423.img.xz`;
- source page: Canonical **Install Ubuntu on AMD** / Kria K26;
- target: KV260/KR260/KD240 unified Kria image;
- microSD guidance: 16 GB UHS-1 or larger;
- flashing tool for the beginner path: **Raspberry Pi Imager**, matching the current AMD Kria guide.

The exact download identity is versioned in `boards/kv260/runtime/ubuntu24_image.json`. The repository records the image filename/source now, but does **not** invent an upstream SHA-256 value that the visible Canonical download index does not publish. The learner computes the downloaded archive SHA-256 with the course helper and records it. Until a controlled course download promotes an expected SHA-256 into that manifest, T-HW-005 may be exercised but must not be labeled a fully frozen image-hash PASS.

The physical boot path is:

- microSD in J11;
- J4 FTDI USB for the UART console;
- J12 12 V / 3 A power;
- UART: **115200 baud, 8 data bits, no parity, 1 stop bit, no flow control**;
- initial Ubuntu login: `ubuntu` / `ubuntu`, followed by the required first-login password change.

The learner retains the complete UART transcript from power-on through login, then records:

```bash
uname -a
cat /etc/os-release
cat /proc/device-tree/model; echo
sudo xmutil boardid
sudo xmutil bootfw_status
```

A successful Linux boot does not prove that custom PL is loaded. Likewise, Vivado/JTAG programming PL does not prove that Linux booted. These are separate paths.

Boot firmware is **observed first, not casually rewritten as part of the main exercise**. If current firmware prevents the supported Ubuntu image from booting, follow the AMD boot-firmware update/recovery instructions as a troubleshooting branch and retain that evidence.

Before removing power, run:

```bash
sudo shutdown -h now
```

**Pass evidence:** exact image filename, computed archive SHA-256, flashing method, UART settings/port, UART boot log, kernel/OS/model output, boot-firmware status, current Git commit, board/carrier revision, and a clean shutdown record. Formal image-hash PASS remains blocked while the course expected SHA-256 field is null.

### LAB-HW-06 — Real host↔PL loopback

**Prerequisites:** LSN-015 and LAB-HW-05.

**Primary new operation:** after PS/Linux boot is understood, let the KV260 runtime host control a real PL register path without turning this first roundtrip into a full AXI course.

The Stage-2 authoring transport is frozen to the smallest inspectable path:

```text
Ubuntu/Python on PS
  → /dev/mem MMIO
  → PS M_AXI_HPM0_FPD
  → AXI SmartConnect
  → dual-channel AXI GPIO @ 0xA0010000
  → kv260_loopback_transform
```

AXI GPIO is used as a teaching adapter rather than asking the learner to write an AXI slave. The only register-map facts required here are taken from AMD PG144:

- Channel 1 `GPIO_DATA`: base + `0x0000`; configured as 32-bit output;
- Channel 2 `GPIO2_DATA`: base + `0x0008`; configured as 32-bit input.

The frozen PL behavior is:

```text
write_value = host writes GPIO_DATA
read_value  = (write_value + 1) mod 2^32
host reads GPIO2_DATA
```

The Vivado address is frozen to **0xA0010000**, matching the address region used by AMD/Xilinx's K26 starter-kit `base_gpio_bram` reference for AXI GPIO. Full AXI channel/ordering details remain deferred to Lesson 18/LAB-HW-10.

The Stage-2 deployment sequence deliberately keeps the two execution domains visible:

1. PS/Linux is already booted from LAB-HW-05.
2. On the runtime host, unload an active Kria application firmware if one is present: `sudo xmutil unloadapp`.
3. On the development host, build and direct-JTAG program the dedicated LAB-HW-06 bitstream.
4. Without power-cycling the board, run `boards/kv260/runtime/loopback_mmio.py` on the PS/Linux side as root.
5. The self-checking script writes a fixed vector set, reads the transformed result, and fails on any mismatch.

The initial runtime access implementation uses Python `mmap` over `/dev/mem` because it keeps the software side small and exposes the MMIO boundary directly. This is an **authoring-candidate transport until the real Ubuntu 24.04 dry run passes**. If the supported image blocks this MMIO path by policy, that is a transport failure to record and revise (for example to UIO); learners must not weaken system security merely to force a PASS.

**Pass evidence:** LAB-HW-06 bitstream SHA-256, build/timing reports, JTAG program log, fixed base address/register offsets, runtime script version/hash, every write/expected/read triple, final `STATUS=PASS`, Git commit, OS/image identity, and board/carrier revision. A failure before the first MMIO read is classified separately from a wrong PL result.



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
