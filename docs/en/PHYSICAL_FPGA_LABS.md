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

The LAB-HW-06 teaching transport is frozen to the smallest inspectable path:

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

The initial runtime access implementation uses Python `mmap` over `/dev/mem` because it keeps the software side small and exposes the MMIO boundary directly. This fixed-address `/dev/mem` path is the **teaching transport for LAB-HW-06**, not a promise that later MOD-010 software will use `/dev/mem`. The helper does not expose an arbitrary base-address option. If the supported Ubuntu image blocks this MMIO path by policy, that is a transport failure: retain the evidence, keep T-HW-006 blocked, and revise the repository transport later. Learners must not weaken system security merely to force a PASS.

**Pass evidence:** LAB-HW-06 bitstream SHA-256, build/timing reports, JTAG program log, fixed base address/register offsets, runtime script version/hash, every write/expected/read triple, final `STATUS=PASS`, Git commit, OS/image identity, and board/carrier revision. A failure before the first MMIO read is classified separately from a wrong PL result.



### LAB-HW-07 — BRAM neuron state

**Prerequisites:** LSN-009, LAB-HW-06, and the LAB-HW-06 PS/Linux runtime path.

**Primary new operation:** turn Lesson 9's abstract `state[address]` into a real, addressable on-chip Block RAM (BRAM) state store on KV260.

Freeze the teaching memory before adding a network:

- state word: **32 bits**;
- depth: **1024 words**;
- total logical capacity: **4096 bytes (4 KiB)**;
- word index: `0..1023`;
- PS-visible base: **`0xA0000000`**;
- byte offset for state word `i`: `4 * i`;
- physical path: PS `M_AXI_HPM0_FPD` → SmartConnect → AXI BRAM Controller → `kv260_neuron_state_store`;
- native memory behavior: synchronous read, with the teaching RTL using read-first semantics on a same-cycle read/write;
- implementation intent: `(* ram_style = "block" *)`, with the Vivado resource oracle requiring at least one RAMB18/RAMB36 primitive.

The base address follows AMD/Xilinx's K26 `base_gpio_bram` reference, which maps its BRAM controller at `0xA0000000`. The runtime helper reuses the LAB-HW-06 fixed `/dev/mem` teaching transport, but maps only this 4 KiB state window.

Two different proofs are required and must not be confused:

1. **Cycle-level proof:** the SystemVerilog testbench demonstrates synchronous native BRAM behavior. A new address is presented before the clock edge; valid read data appears only after the clocked memory operation.
2. **Board-level proof:** PS/Linux writes distinct 32-bit state words to multiple word indices and reads them back through the AXI BRAM Controller. This proves addressable physical memory, not a one-cycle host-software latency claim.

The physical self-check uses separated addresses including low, middle, and last locations; it then rewrites selected locations and verifies that untouched locations retain their values. Address aliasing, wrong data, and transport failures are distinct failures.

Do **not** add the LAB-HW-08 network, spike replay, DDR, performance measurement, ECC, complicated dual-port arbitration, or manual BRAM primitive instantiation here.

**Pass evidence:** LAB-HW-07 bitstream SHA-256; Vivado build/program logs; DRC/timing reports; resource report showing non-zero block-RAM primitives; frozen base/window/word geometry; runtime helper hash; every address/write/read triple; rewrite-and-neighbor-preservation trace; final `STATUS=PASS`; Git commit; OS/image identity; board/carrier revision. Cloud simulation/resource-contract checks do not substitute for real T-HW-007 board evidence.

### LAB-HW-08 — Small FlyBrain replay

**Prerequisites:** LSN-012, LAB-HW-06, LAB-HW-07, and the frozen Platform-3 teaching-event semantics from Lesson 12.

**Primary new operation:** execute the already taught four-neuron event-driven network in PL, then compare its complete trace against a deterministic Python replay oracle without changing the teaching algorithm.

The Lab reuses the exact Lesson-12 network:

- four neurons;
- source index: `[(0,2), (2,1), (3,1), (4,0)]`;
- synapse records: `[(1,+2), (2,+1), (3,+2), (3,+1)]`;
- thresholds: `[99, 2, 1, 3]`;
- initial accumulator state: `[0,0,0,0]`;
- initial input queue: `[0]`;
- threshold crossing enqueues the target and resets its teaching accumulator to zero;
- expected spike order: `[0,1,2,3]`;
- expected final state: `[0,0,0,0]`.

This is the Lesson-12 **teaching event machine**, not the formal LIF numeric model. Therefore LAB-HW-08 must not relabel its simple integer threshold semantics as `MOD-003` or as the final `MOD-004~009` implementation. L5 here means **board-level replay of a frozen teaching network**.

Freeze the replay artifacts:

- versioned fixture: `boards/kv260/fixtures/lab08_four_neuron_replay_v1.json`;
- Python oracle: `boards/kv260/runtime/lab08_replay_reference.py`;
- PL engine: `kv260_small_replay_engine`;
- shared 4 KiB state/trace BRAM window at `0xA0000000`;
- fixed AXI GPIO control/status block at `0xA0010000`;
- host may access the shared BRAM window only while the engine reports `busy=0`; no concurrent host/engine arbitration is taught here.

The PL replay writes machine-readable evidence into BRAM:

- word `0..3`: accumulator state;
- word `16..19`: emitted spike order;
- word `20`: spike count;
- word `32..35`: weighted-event trace;
- word `36`: weighted-event count.

Each event-trace word encodes source, target, signed 8-bit weight, pre-reset accumulator-after-add, and whether that target spiked. The host checker computes the oracle from the fixture first, launches the PL engine, reads back spike/state/event traces, and compares every field.

The deterministic fixture uses no PRNG. A seed becomes mandatory only when a future replay contract is stochastic; do not invent a meaningless seed merely to satisfy wording.

Do **not** introduce DDR, performance claims, a real MaleCNS image, final LIF numerics, concurrent BRAM arbitration, or a general programmable network loader here.

**Pass evidence:** fixture SHA-256, Python-oracle SHA-256, bitstream SHA-256, build/program logs, DRC/timing/resource reports, exact control/status contract, complete Python expected trace, complete PL readback trace, differential result `STATUS=PASS`, Git commit, OS/image identity, and board/carrier revision. Ordinary CI may prove oracle/RTL/host-checker agreement but cannot claim physical T-HW-008 PASS.

### LAB-HW-09 — DDR integrity

**Course sequence:** after LAB-HW-08.  
**Operational prerequisites:** LSN-016, LSN-017, and the LAB-HW-05 PS/Linux boot path.

**Primary new operation:** prove that a deterministic payload can survive a large write/read roundtrip through the K26 system-memory path before introducing a PL AXI master, DMA engine, or burst benchmark.

The KV260/K26 provides 4 GB DDR4 system memory. This Lab deliberately uses an **OS-managed anonymous memory mapping on PS/Linux** instead of guessing a physical DDR address with `/dev/mem`. That keeps Linux memory ownership intact and isolates the new concept: external-memory integrity.

Freeze the physical sanity contract:

- test allocation: **64 MiB**;
- chunk size: **1 MiB**;
- access pattern: contiguous sequential chunks only;
- payload: deterministic, chunk-indexed bytes generated from the fixed LAB-HW-09 seed string;
- pages are prefaulted before the timed payload write;
- every read chunk is compared byte-for-byte with the regenerated expected chunk;
- expected and observed SHA-256 values must match;
- any mismatch immediately sets `PERFORMANCE_BLOCKED=1` and no bandwidth result is accepted;
- physical mode must run on PS/Linux and record board model, kernel, OS identity, `MemTotal`, `MemAvailable`, and swap information;
- no root privilege and no fixed physical DDR address are required.

The script records two **host-path observations** after integrity succeeds:

- timed payload-copy write elapsed time / effective write bandwidth;
- timed contiguous read elapsed time / effective read bandwidth.

These numbers include the PS/Linux/userspace memory path and are **not** a claim about peak DDR bandwidth, PL bandwidth, AXI burst efficiency, or hardware-only latency. The reproducible multi-pattern benchmark belongs to LAB-HW-10.

The order is mandatory:

```text
verify runtime environment
→ allocate + prefault OS-managed memory
→ deterministic payload write
→ byte-for-byte readback
→ SHA-256 compare
→ integrity PASS
→ only then report host-path timing observations
```

A corruption-injection mode exists only for CI/dry-run to prove that a single modified byte blocks all performance conclusions.

Do **not** add a PL AXI master, AXI CDMA, DMA driver, reserved physical DDR region, random/scattered comparison, burst tuning, cache/coherency claims, DDR PHY training, or synapse-store migration here. Those would couple HW-09 to HW-10/RMD-015.

**Pass evidence:** `ddr_integrity.py` SHA-256; fixed 64 MiB/1 MiB geometry; payload seed/algorithm identifier; board model; kernel/OS identity; memory snapshot; expected/observed SHA-256; byte-compare result; integrity `STATUS=PASS`; write/read timer boundaries and elapsed time; observed host-path effective bandwidth; access-pattern label; Git commit/date. No bitstream is required for this Lab. Ordinary CI dry-run cannot claim physical T-HW-009 PASS.

### LAB-HW-10 — AXI/burst measurement

**Prerequisites:** LSN-018, LAB-HW-09 integrity PASS, and the earlier PS/Linux + JTAG programming path.

**Primary new operation:** use a real programmable-logic AXI master path into K26 DDR, then compare two transaction granularities with the same bitstream, payload, byte count, buffer, and timer boundary.

The Lab uses AMD AXI Central Direct Memory Access (AXI CDMA) in **Simple DMA mode** so the learner uses a real AXI4 master without implementing the complete AXI master state machine from scratch.

Freeze the hardware teaching path:

```text
PS/Linux
  ├─ /dev/mem control MMIO
  │    ↓
  │  PS M_AXI_HPM0_FPD
  │    ↓
  │  AXI CDMA S_AXI_LITE @ 0xA0020000
  │
  └─ DMA-safe source/destination buffer in DDR
             ↑
             │ AXI CDMA M_AXI, 128 bit, max burst 64
             │
       PS S_AXI_HP0_FPD
             │
             ↓
           DDR4
```

The selected `S_AXI_HP0_FPD` path is **non-coherent**. Therefore this Lab does not use an ordinary cached Python allocation as a DMA buffer. The physical checker requires a course-approved **u-dma-buf** device (`/dev/udmabuf0`) of at least 2 MiB and opens it with `O_SYNC`; the physical address is read from the driver's sysfs interface. If that buffer provider or cache mode is unavailable on the selected Ubuntu/kernel combination, T-HW-010 remains blocked. Do not guess a physical address and do not weaken kernel security to force a result.

The course does not teach kernel-driver implementation here. u-dma-buf is a buffer-provider prerequisite, analogous to the vendor toolchain prerequisite: the learner uses it and records its identity, but does not modify its source.

Freeze the AXI CDMA build contract:

- target: KV260 / K26, part `xck26-sfvc784-2LV-c`;
- control path: PS `M_AXI_HPM0_FPD` → SmartConnect → AXI CDMA `S_AXI_LITE`;
- control base: **`0xA0020000`**;
- data path: AXI CDMA `M_AXI` → PS **`S_AXI_HP0_FPD`** → DDR;
- AXI CDMA mode: Simple DMA only; Scatter/Gather disabled;
- data width: **128 bits**;
- maximum burst length: **64 beats**;
- address width: **64 bits**;
- DRE disabled; all course source/destination addresses and lengths are naturally aligned;
- mapped DDR aperture for this first measurement: `HP0_DDR_LOW` only. The physical helper rejects a DMA buffer outside that aperture rather than silently depending on a different address map;
- routed implementation must pass DRC plus setup/hold timing before bitstream generation.

Freeze the workload:

- DMA buffer provider size: at least **2 MiB**;
- source region offset: **0 MiB**;
- destination region offset: **1 MiB**;
- payload per repetition: **256 KiB**;
- deterministic payload: SHAKE256-derived bytes;
- **contiguous pattern:** one 256 KiB CDMA request;
- **small/scattered pattern:** 1024 × 256-byte CDMA requests covering the same 256 KiB in the deterministic permutation `block = (257*i + 17) mod 1024`;
- the destination must match the source byte-for-byte before performance measurement and after every measured batch.

This is an **end-to-end software-controlled DMA workload comparison**. The timer includes Python register programming and polling plus the AXI/CDMA/DDR transfer. Therefore a result is not a pure bus-efficiency measurement and must not be generalized into a peak-DDR claim.

Measurement protocol, fixed for both patterns:

1. same bitstream, DMA buffer, payload, total 256 KiB, and timer boundary;
2. run an integrity precheck for the pattern;
3. perform **5 warm-up repetitions**, excluded from statistics;
4. perform **20 measured repetitions** and retain every raw elapsed time;
5. use the **median** as the primary result; also retain min/max;
6. run a second batch in the same session with the same 5 + 20 protocol;
7. verify destination integrity after each batch;
8. compute relative difference between the two batch medians for each pattern;
9. require **≤10%** median difference for both patterns to call the benchmark reproducible;
10. if either pattern exceeds 10%, report `MEASUREMENT_UNSTABLE`, retain the raw evidence, and make no performance conclusion.

Only after both integrity and stability gates pass may the checker report the contiguous/scattered median ratio as an observation for this workload.

Do **not** add Scatter/Gather descriptors, interrupts, multiple outstanding masters, HPC/CCI coherency tuning, cache-policy experiments, a custom Linux DMA driver, a hand-written AXI master, formal synapse-store migration, or a CPU/GPU/FPGA comparison here. Those are later engineering topics.

**Pass evidence:** LAB-HW-10 bitstream SHA-256; Vivado build/program logs; DRC/timing/resource reports; AXI CDMA configuration; fixed control address; buffer-provider identity, size, physical base, and cache-mode contract; deterministic payload hash; pre/post integrity evidence; all warm-up/measured raw samples; two batch medians/min/max per pattern; stability percentages; stable ratio when allowed; helper SHA-256; Git commit; OS/kernel; board/carrier revision; experiment date. Ordinary CI dry-run validates the benchmark logic only and cannot claim physical T-HW-010 PASS.


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
