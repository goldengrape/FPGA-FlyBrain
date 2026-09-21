# KV260 board-support layer

This directory contains the board-specific support used by the FPGA-FlyBrain Physical Lab track for the **AMD Kria KV260 Vision AI Starter Kit**.

The FlyBrain core remains board-independent. KV260 connector names, Vivado board definitions, JTAG/UART handling, constraints, and later PS/PL runtime integration belong here.

## Current batch

The board-support layer now implements **LAB-HW-00~09**:

- `scripts/check_vivado.tcl` — LAB-HW-00 vendor-toolchain preflight;
- `scripts/detect_target.tcl` — LAB-HW-02 JTAG target discovery;
- `rtl/kv260_marker_top.sv` + `scripts/build_lab03_marker.tcl` — LAB-HW-03 first bitstream;
- `rtl/kv260_blink_core.sv` + `scripts/build_lab04_blink.tcl` — LAB-HW-04 clock/reset/I/O proof;
- `constraints/bank45_gpio.xdc` — reviewed Bank 45 logical-port → K26 package-pin mapping;
- `runtime/ubuntu24_image.json`, `hash_image.py`, and `collect_boot_info.sh` — LAB-HW-05 image/UART evidence helpers;
- `rtl/kv260_loopback_transform.sv` + `scripts/build_lab06_loopback.tcl` — LAB-HW-06 PS↔PL MMIO loopback design;
- `runtime/loopback_mmio.py` — LAB-HW-06 self-checking runtime-host helper;
- `rtl/kv260_neuron_state_store.sv` + `scripts/build_lab07_bram_state.tcl` — LAB-HW-07 1024 × 32-bit synchronous BRAM state store and AXI-BRAM build path;
- `runtime/state_bram_mmio.py` — LAB-HW-07 multi-address/rewrite state-memory checker;
- `fixtures/lab08_four_neuron_replay_v1.json` + `runtime/lab08_replay_reference.py` — LAB-HW-08 frozen Lesson-12 replay fixture and deterministic Python oracle;
- `rtl/kv260_replay_state_store.sv` + `rtl/kv260_small_replay_engine.sv` + `scripts/build_lab08_small_replay.tcl` — LAB-HW-08 shared BRAM + fixed four-neuron PL replay path;
- `runtime/small_replay_mmio.py` — LAB-HW-08 fixed-address differential runtime checker;
- `runtime/ddr_integrity.py` — LAB-HW-09 fixed 64 MiB OS-managed external-memory integrity checker and host-path timing observer;
- `scripts/program_bitstream.tcl` — shared direct-JTAG programming helper;
- `evidence/manifest.example.json` — T-HW-011 evidence checklist/template.

PL→DDR AXI/burst measurement belongs to LAB-HW-10 and is not implemented by this stage. LAB-HW-09 validates only PS/Linux-managed external-memory integrity and host-path observations; it does not freeze a raw DDR address, DMA path, PL AXI master, or formal DDR-backed synapse store.

## Authoring baseline

The current lab prose selects **Vivado 2026.1** as the **authoring candidate baseline**. The preflight script rejects another release during this batch so documentation and scripts do not silently drift.

This is not yet a declaration that Vivado 2026.1 is the physically validated course-support baseline. That promotion requires a real-KV260 dry run and retained evidence.

This repository has not yet recorded a real-KV260 physical PASS for LAB-HW-00~09. Cloud CI validates notebook/helper/RTL/runtime contracts only and must not be interpreted as physical T-HW evidence. LAB-HW-09 requires no new Vivado build.

## LAB-HW-00

From a shell where Vivado is available:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-00-vivado-preflight.log \
  -source boards/kv260/scripts/check_vivado.tcl
```

The script exits non-zero when:

- Vivado does not match the 2026.1 authoring candidate; or
- no installed board part contains `kv260`.

Cable-driver installation is an OS/vendor setup step. Physical cable operation is first proven by LAB-HW-02 target discovery.

## LAB-HW-02

With the KV260 correctly powered and J4 connected to the development host:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-02-target-detection.log \
  -source boards/kv260/scripts/detect_target.tcl
```

The script exits non-zero when the local hardware server cannot be reached, no hardware target can be opened, or no XCK26 FPGA device is discovered. A PS debug object such as `arm_dap_1` does not satisfy the KV260 FPGA-device oracle by itself.

## Evidence boundary

These scripts print machine-searchable `KEY=VALUE` lines so saved logs can later feed an evidence manifest. They do not claim algorithm correctness, bitstream correctness, or a board pass by themselves.


## LAB-HW-03

Build:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-03-build.log \
  -source boards/kv260/scripts/build_lab03_marker.tcl
```

Program:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-03-program.log \
  -source boards/kv260/scripts/program_bitstream.tcl \
  -tclargs build/kv260/lab-hw-03/kv260_marker_top.bit
```

The marker is deliberately clockless: `bank45_gpio[4:0] = 5'b10101`. The build writes DRC/timing/resource reports and must print `TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS`; it does not claim timing closure for a design with no clocked timing path.

## LAB-HW-04

Build:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-04-build.log \
  -source boards/kv260/scripts/build_lab04_blink.tcl
```

Program:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-04-program.log \
  -source boards/kv260/scripts/program_bitstream.tcl \
  -tclargs build/kv260/lab-hw-04/kv260_blink.bit
```

Clock/reset contract:

- clock: PS `pl_clk0` (nominal 100 MHz);
- platform reset source: PS `pl_resetn0`;
- design-local reset: `proc_sys_reset/peripheral_aresetn` → `kv260_blink_core.resetn`;
- SW2 remains a SOM-level hard reset and is not the module reset wire;
- the build stops at routed implementation, requires real setup/hold timing paths, and rejects negative setup or hold slack before writing the bitstream.

The shared `program_bitstream.tcl` enumerates hardware targets first and requires **exactly one** XCK26 target/device pair. If multiple KV260/XCK26 targets are attached, it fails with `AMBIGUOUS_KV260_FPGA_DEVICE` instead of guessing which board to program.

## LAB-HW-05

Image identity:

```bash
python boards/kv260/runtime/hash_image.py \
  /path/to/iot-limerick-kria-classic-server-2404-classic-24.04-x07-20250423.img.xz
```

The current manifest intentionally has `expected_sha256: null`. A local hash is recorded, but formal image-hash PASS remains blocked until a controlled course download freezes the expected hash.

After Ubuntu boots on the PS, collect evidence with:

```bash
bash boards/kv260/runtime/collect_boot_info.sh
```

The main Lab path observes boot firmware first; firmware update/recovery is a documented troubleshooting branch, not an unrecorded default action.

## LAB-HW-06

Build the dedicated loopback bitstream on the development host:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-06-build.log \
  -source boards/kv260/scripts/build_lab06_loopback.tcl
```

With LAB-HW-05 Linux already running, unload an active Kria application firmware if one is present:

```bash
sudo xmutil unloadapp
```

Then direct-JTAG program the LAB-HW-06 bitstream from the development host:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-06-program.log \
  -source boards/kv260/scripts/program_bitstream.tcl \
  -tclargs build/kv260/lab-hw-06/kv260_loopback.bit
```

Frozen hardware path:

- PS `M_AXI_HPM0_FPD` → AXI SmartConnect → dual-channel AXI GPIO;
- AXI GPIO base: `0xA0010000`;
- Channel 1 `GPIO_DATA`: `+0x0000`, 32-bit host write;
- Channel 2 `GPIO2_DATA`: `+0x0008`, 32-bit host read;
- PL operation: `read = (write + 1) mod 2^32`.

The address follows AMD/Xilinx's K26 `base_gpio_bram` reference design. AXI GPIO is a teaching adapter; learners are not asked to implement an AXI slave in this Lab.

Host-side oracle without hardware:

```bash
python boards/kv260/runtime/loopback_mmio.py --dry-run
```

Physical runtime-host check on PS/Linux:

```bash
sudo python3 /tmp/loopback_mmio.py \
  --json-out /tmp/lab-hw-06-trace.json
```

The physical helper maps only the frozen `0xA0010000` region and intentionally has no arbitrary `--base` option. If Ubuntu policy rejects the `/dev/mem` mapping, retain the failure evidence and keep T-HW-006 blocked; do not weaken system security to force a PASS. The long-term MOD-010 software stack may later use UIO, XRT, a driver, or another supported transport without changing the semantic contract.

## LAB-HW-07

Native state-store semantics can be checked without Vivado:

```bash
iverilog -g2012 \
  -s kv260_neuron_state_store_tb \
  -o /tmp/lab07_state \
  boards/kv260/rtl/kv260_neuron_state_store.sv \
  boards/kv260/tb/kv260_neuron_state_store_tb.sv
vvp /tmp/lab07_state
```

Build the KV260 bitstream:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-07-build.log \
  -source boards/kv260/scripts/build_lab07_bram_state.tcl
```

Frozen memory geometry:

- `1024 × 32-bit` state words;
- `4096` bytes / 4 KiB;
- PS-visible base `0xA0000000`;
- word `i` lives at byte offset `4*i`;
- PS `M_AXI_HPM0_FPD` → SmartConnect → AXI BRAM Controller → `kv260_neuron_state_store`;
- synchronous native read, read-first on same-cycle read/write;
- at least one RAMB18/RAMB36 primitive required before bitstream generation.

Host oracle without physical hardware:

```bash
python boards/kv260/runtime/state_bram_mmio.py --dry-run
```

After programming the LAB-HW-07 bitstream, run on PS/Linux:

```bash
sudo python3 /tmp/state_bram_mmio.py \
  --json-out /tmp/lab-hw-07-trace.json
```

The checker writes separated low/middle/high addresses, reads them back, rewrites selected locations, and verifies that untouched locations keep their state. As in LAB-HW-06, `/dev/mem` is a fixed teaching transport. If Ubuntu policy rejects the mapping, retain the evidence and keep T-HW-007 blocked rather than weakening system security.

## LAB-HW-08

The replay source of truth is:

`fixtures/lab08_four_neuron_replay_v1.json`

Generate the deterministic Python oracle:

```bash
python boards/kv260/runtime/lab08_replay_reference.py \
  --fixture boards/kv260/fixtures/lab08_four_neuron_replay_v1.json
```

Run the open-source PL replay simulation:

```bash
iverilog -g2012 \
  -s kv260_small_replay_engine_tb \
  -o /tmp/lab08_replay \
  boards/kv260/rtl/kv260_replay_state_store.sv \
  boards/kv260/rtl/kv260_small_replay_engine.sv \
  boards/kv260/tb/kv260_small_replay_engine_tb.sv
vvp /tmp/lab08_replay
```

Build:

```bash
vivado -mode batch -nojournal \
  -log lab-hw-08-build.log \
  -source boards/kv260/scripts/build_lab08_small_replay.tcl
```

The fixed replay path uses:

- `0xA0000000`: 4 KiB shared state/trace BRAM;
- `0xA0010000`: dual-channel AXI GPIO control/status;
- control bit 0: start;
- status bit 0: busy, bit 1: done, bit 2: engine error;
- status bits 7:4: spike count;
- status bits 15:8: weighted-event count.

The host must not access the shared BRAM while `busy=1`. This deliberately avoids adding concurrent BRAM arbitration to the Lab.

Dry-run the differential checker:

```bash
python boards/kv260/runtime/small_replay_mmio.py \
  --fixture boards/kv260/fixtures/lab08_four_neuron_replay_v1.json \
  --dry-run
```

After programming the LAB-HW-08 bitstream, copy the fixture plus the two runtime Python files to PS/Linux and run the same checker with sudo. A physical T-HW-008 PASS requires real-board differential evidence; CI success is not a substitute.

## LAB-HW-09

LAB-HW-09 deliberately needs no new PL bitstream. It validates the K26 external system-memory substrate from PS/Linux while keeping Linux in control of memory ownership.

Dry-run the integrity oracle on any host:

```bash
python boards/kv260/runtime/ddr_integrity.py \
  --dry-run \
  --json-out /tmp/lab-hw-09-dry-run.json
```

Prove that corruption blocks performance output:

```bash
python boards/kv260/runtime/ddr_integrity.py \
  --dry-run \
  --inject-corruption-for-test
```

Physical KV260 run:

```bash
python3 /tmp/ddr_integrity.py \
  --physical \
  --json-out /tmp/lab-hw-09-trace.json
```

Physical mode freezes:

- 64 MiB OS-managed anonymous mapping;
- 1 MiB contiguous chunks;
- deterministic SHAKE256 chunk-index payload;
- prefault before timed payload copies;
- byte-for-byte readback plus expected/observed SHA-256;
- performance output only after integrity PASS;
- board/kernel/OS/memory snapshot;
- host-path write/read elapsed time and MiB/s observations.

The reported MiB/s values are not peak DDR or PL/AXI bandwidth. LAB-HW-10 owns the first PL→DDR AXI/burst measurement.
