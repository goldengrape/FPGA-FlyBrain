#!/usr/bin/env bash
set -euo pipefail

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: required tool not found: $1" >&2
    exit 2
  }
}

need verilator
need yosys

echo "== KV260 RTL static checks =="
verilator --version
yosys -V

# These are teaching RTL blocks, not the Vivado block-design wrappers.
# Keep waivers narrow and documented:
# - state stores intentionally ignore upper address bits outside their 4 KiB window;
# - replay_state_store is a true-dual-port BRAM inference pattern written from two
#   clocked processes. LAB-HW-08 wires both ports to the same clock and forbids
#   host Port-A access while the engine owns Port B.
verilator --lint-only -Wall boards/kv260/rtl/kv260_marker_top.sv
verilator --lint-only -Wall boards/kv260/rtl/kv260_blink_core.sv
verilator --lint-only -Wall boards/kv260/rtl/kv260_loopback_transform.sv
verilator --lint-only -Wall -Wno-UNUSEDSIGNAL \
  boards/kv260/rtl/kv260_neuron_state_store.sv
verilator --lint-only -Wall -Wno-UNUSEDSIGNAL -Wno-MULTIDRIVEN \
  boards/kv260/rtl/kv260_replay_state_store.sv
verilator --lint-only -Wall -Wno-UNUSEDSIGNAL \
  boards/kv260/rtl/kv260_small_replay_engine.sv

synth_check() {
  local top="$1"
  local file="$2"
  echo "== Yosys: ${top} =="
  yosys -q -p "read_verilog -sv ${file}; hierarchy -check -top ${top}; proc; opt; check"
}

synth_check kv260_marker_top boards/kv260/rtl/kv260_marker_top.sv
synth_check kv260_blink_core boards/kv260/rtl/kv260_blink_core.sv
synth_check kv260_loopback_transform boards/kv260/rtl/kv260_loopback_transform.sv
synth_check kv260_neuron_state_store boards/kv260/rtl/kv260_neuron_state_store.sv
synth_check kv260_replay_state_store boards/kv260/rtl/kv260_replay_state_store.sv
synth_check kv260_small_replay_engine boards/kv260/rtl/kv260_small_replay_engine.sv

echo "PASS: KV260 teaching RTL static checks completed successfully."
