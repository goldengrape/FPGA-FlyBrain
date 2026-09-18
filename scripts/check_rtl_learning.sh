#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${RTL_LEARNING_BUILD_DIR:-${ROOT_DIR}/build/rtl-learning}"

require_tool() {
    local tool="$1"
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "ERROR: required tool '$tool' was not found in PATH." >&2
        return 1
    fi
}

for tool in iverilog vvp verilator yosys; do
    require_tool "$tool"
done

mkdir -p "${BUILD_DIR}/lesson06" "${BUILD_DIR}/lesson08"

echo "== Tool versions =="
iverilog -V 2>&1 | sed -n '1p'
verilator --version
yosys -V

echo
echo "== Lesson 6: Icarus compile + self-checking simulation =="
iverilog -g2012 \
    -o "${BUILD_DIR}/lesson06/clocked_accumulator.vvp" \
    "${ROOT_DIR}/rtl/learning/clocked_accumulator.sv" \
    "${ROOT_DIR}/tb/learning/clocked_accumulator_tb.sv"
vvp "${BUILD_DIR}/lesson06/clocked_accumulator.vvp"

echo
echo "== Lesson 6: Verilator lint =="
verilator --lint-only --timing -Wall -Wno-TIMESCALEMOD \
    "${ROOT_DIR}/rtl/learning/clocked_accumulator.sv" \
    "${ROOT_DIR}/tb/learning/clocked_accumulator_tb.sv"

echo
echo "== Lesson 6: Yosys synthesis sanity =="
yosys -q -p "read_verilog -sv ${ROOT_DIR}/rtl/learning/clocked_accumulator.sv; hierarchy -check -top clocked_accumulator; proc; opt; check"

echo
echo "== Lesson 8: Icarus compile + self-checking simulation =="
iverilog -g2012 \
    -o "${BUILD_DIR}/lesson08/tutorial_if_neuron.vvp" \
    "${ROOT_DIR}/rtl/learning/tutorial_if_neuron.sv" \
    "${ROOT_DIR}/tb/learning/tutorial_if_neuron_tb.sv"
(
    cd "${BUILD_DIR}/lesson08"
    vvp ./tutorial_if_neuron.vvp
)

VCD_PATH="${BUILD_DIR}/lesson08/tutorial_if_neuron.vcd"
if [[ ! -s "${VCD_PATH}" ]]; then
    echo "ERROR: expected non-empty waveform was not generated: ${VCD_PATH}" >&2
    exit 1
fi
echo "Waveform: ${VCD_PATH} ($(wc -c < "${VCD_PATH}") bytes)"

echo
echo "== Lesson 8: Verilator lint =="
verilator --lint-only --timing -Wall -Wno-TIMESCALEMOD \
    "${ROOT_DIR}/rtl/learning/tutorial_if_neuron.sv" \
    "${ROOT_DIR}/tb/learning/tutorial_if_neuron_tb.sv"

echo
echo "== Lesson 8: Yosys synthesis sanity =="
yosys -q -p "read_verilog -sv ${ROOT_DIR}/rtl/learning/tutorial_if_neuron.sv; hierarchy -check -top tutorial_if_neuron; proc; opt; check"

echo
echo "PASS: all RTL learning checks completed successfully."
