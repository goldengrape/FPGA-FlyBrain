# KV260 board-support layer

This directory contains the board-specific support used by the FPGA-FlyBrain Physical Lab track for the **AMD Kria KV260 Vision AI Starter Kit**.

The FlyBrain core remains board-independent. KV260 connector names, Vivado board definitions, JTAG/UART handling, constraints, and later PS/PL runtime integration belong here.

## Current batch

The board-support layer now implements **LAB-HW-00~04**:

- `scripts/check_vivado.tcl` — LAB-HW-00 vendor-toolchain preflight;
- `scripts/detect_target.tcl` — LAB-HW-02 JTAG target discovery;
- `rtl/kv260_marker_top.sv` + `scripts/build_lab03_marker.tcl` — LAB-HW-03 first bitstream;
- `rtl/kv260_blink_core.sv` + `scripts/build_lab04_blink.tcl` — LAB-HW-04 clock/reset/I/O proof;
- `constraints/bank45_gpio.xdc` — reviewed Bank 45 logical-port → K26 package-pin mapping;
- `scripts/program_bitstream.tcl` — shared direct-JTAG programming helper;
- `evidence/manifest.example.json` — T-HW-011 evidence checklist/template.

PS/Linux runtime, host↔PL transport, BRAM network state, DDR, and AXI belong to LAB-HW-05~10 and are not implemented by this stage.

## Authoring baseline

The current lab prose selects **Vivado 2026.1** as the **authoring candidate baseline**. The preflight script rejects another release during this batch so documentation and scripts do not silently drift.

This is not yet a declaration that Vivado 2026.1 is the physically validated course-support baseline. That promotion requires a real-KV260 dry run and retained evidence.

This repository has not yet recorded a real-KV260 physical pass for this batch. Cloud CI validates notebook/script contracts only and must not be interpreted as `T-HW-002` board evidence.

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
