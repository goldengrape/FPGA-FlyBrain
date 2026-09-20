# KV260 board-support layer

This directory contains the board-specific support used by the FPGA-FlyBrain Physical Lab track for the **AMD Kria KV260 Vision AI Starter Kit**.

The FlyBrain core remains board-independent. KV260 connector names, Vivado board definitions, JTAG/UART handling, constraints, and later PS/PL runtime integration belong here.

## Current batch

This first batch supports LAB-HW-00~02 only:

- `scripts/check_vivado.tcl` — LAB-HW-00 vendor-toolchain preflight;
- `scripts/detect_target.tcl` — LAB-HW-02 JTAG target discovery.

There is intentionally no XDC, PL design, PS/Linux runtime code, or DDR/AXI implementation in this batch. Those belong to later labs after their prose/oracles are approved.

## Authoring baseline

The current lab prose selects **Vivado 2026.1** as the **authoring candidate baseline**. The preflight script rejects another release during this batch so documentation and scripts do not silently drift.

This is not yet a declaration that Vivado 2026.1 is the physically validated course-support baseline. That promotion requires a real-KV260 dry run and retained evidence.

This repository has not yet recorded a real-KV260 physical pass for this batch. Cloud CI validates notebook/script contracts only and must not be interpreted as `T-HW-002` board evidence.

## LAB-HW-00

From a shell where Vivado is available:

```bash
vivado -mode batch -nolog -nojournal \
  -source boards/kv260/scripts/check_vivado.tcl \
  | tee lab-hw-00-vivado-preflight.txt
```

The script exits non-zero when:

- Vivado does not match the 2026.1 authoring candidate; or
- no installed board part contains `kv260`.

Cable-driver installation is an OS/vendor setup step. Physical cable operation is first proven by LAB-HW-02 target discovery.

## LAB-HW-02

With the KV260 correctly powered and J4 connected to the development host:

```bash
vivado -mode batch -nolog -nojournal \
  -source boards/kv260/scripts/detect_target.tcl \
  | tee lab-hw-02-target-detection.txt
```

The script exits non-zero when the local hardware server cannot be reached, no hardware target can be opened, or no XCK26 FPGA device is discovered. A PS debug object such as `arm_dap_1` does not satisfy the KV260 FPGA-device oracle by itself.

## Evidence boundary

These scripts print machine-searchable `KEY=VALUE` lines so saved logs can later feed an evidence manifest. They do not claim algorithm correctness, bitstream correctness, or a board pass by themselves.
