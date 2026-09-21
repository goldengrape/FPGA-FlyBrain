# MDD — Building Blocks / Module Design Document

## 0. Purpose
Define the current module boundaries, interfaces, data structures, and contracts. Module boundaries exist to support implementation and verification; avoid over-decomposition.

This document follows [Documentation-First Specification Governance](DOCUMENT_AUTHORITY.md): formal module/interface/semantic contracts are documented first, translated into TDD oracles second, and implemented last. Existing RTL/Python behavior does not automatically redefine this document.

## 1. System topology
```text
Host / Python
  ├─ connectome converter
  ├─ sensory encoder
  ├─ control/telemetry
  └─ reference model
          │
          ▼
      Host-FPGA I/O
          │
          ▼
┌─────────────────────────────┐
│ FPGA                        │
│  spike_fifo                 │
│      ↓                      │
│  event_router               │
│      ↓                      │
│  synapse_reader ── DDR      │
│      ↓                      │
│  synapse_engine             │
│      ↓                      │
│  accumulator/banked state   │
│      ↓                      │
│  neuron_engine              │
│      ↓                      │
│  output spike / telemetry   │
└─────────────────────────────┘
```

## 2. Core data types
### `neuron_state_t`
- `membrane_v`
- `refractory_count`
- optional `last_update_time`
- optional flags

### `spike_event_t`
- `source_neuron_id`
- `timestamp` / `step_id` depending on the execution model

### `synapse_record_t`
- `target_neuron_id`
- `weight`
- optional delay/type flags, disabled in the first version if unnecessary

### `source_index_t`
- `start_offset`
- `fanout_count`

## 3. Modules
### MOD-001 `python_float_reference`
Responsibility: define the clearest version of model semantics.  
Inputs: model parameters, initial state, input events.  
Outputs: state trajectory and spike trajectory.  
Contract: readability first; not a performance implementation.

### MOD-002 `python_fixed_reference`
Responsibility: emulate FPGA bit widths, rounding, saturation, and overflow behavior.  
Contract: direct oracle for RTL.

### MOD-003 `lif_neuron_engine`
Responsibility: consume `neuron_state + input_accum`, execute one state update, and emit `spike_flag`.  
Not responsible for synapse lookup, DDR, or sensory encoding.

### MOD-004 `neuron_state_store`
Responsibility: store many virtual-neuron states and support banked access.  
Initial: BRAM/behavioral memory.  
Later: BRAM/URAM + arbitration.

LAB-HW-07 provides a **teaching slice**, not the completed formal MOD-004: one 1024 × 32-bit single-port state memory with synchronous read, exposed to the KV260 PS through an AXI BRAM Controller. Its fixed 4 KiB geometry and `0xA0000000` platform mapping teach the memory boundary; they do not freeze the final neuron-state record, banking scheme, arbitration, or formal MOD-004 interface.

### MOD-005 `spike_fifo`
Responsibility: buffer pending spike events.  
Contract: explicit full/empty/backpressure behavior.

### MOD-006 `source_index_store`
Responsibility: map `source neuron ID → synapse range`.

### MOD-007 `synapse_reader`
Responsibility: read synapse records from on-chip memory or DDR for a specified range.  
Contract: streaming valid/ready style output.

### MOD-008 `synapse_engine`
Responsibility: convert a synapse record into a weighted target event.

### MOD-009 `target_accumulator`
Responsibility: accumulate target-neuron inputs and handle update conflicts.  
Initial: serial/single-event handling.  
Later: banked accumulator.

### LAB-HW-08 teaching replay boundary

LAB-HW-08 adds `kv260_small_replay_engine` and a dual-access teaching state/trace store only as a **board replay harness** for the exact Lesson-12 four-neuron event machine.

It composes simplified teaching forms of queue → source lookup → weighted event → target accumulator, but it does **not** promote them to formal `MOD-005~009` implementations. In particular:

- the four-neuron source index and four synapse records are compiled fixture constants;
- target state is a 32-bit integer teaching accumulator, not formal `neuron_state_t`;
- threshold crossing resets that teaching accumulator exactly as Lesson 12 specifies;
- host and engine do not arbitrate concurrent BRAM access; host access is allowed only while `busy=0`;
- the replay engine writes spike/event traces into reserved words of the same 4 KiB teaching memory window;
- no formal `IF-SPIKE-QUEUE`, `IF-SYNAPSE-STREAM`, final fixed-point LIF, DDR backend, or programmable network loader is frozen by this Lab.

The harness exists to prove one narrow statement: a previously verified event-causality teaching network produces the same deterministic trace when executed in PL on the reference board.

### MOD-010 `host_if`
Responsibility: load parameters, deliver stimuli, and read spikes/telemetry.  
Initial: simulation interface.  
On hardware: AXI-Lite + DMA/streaming as appropriate for the platform.

### MOD-011 `connectome_converter`
Responsibility: convert raw MaleCNS data into a versioned FPGA binary image.  
Outputs: neuron metadata, source index, synapse records, manifest/checksum.

### MOD-012 `sensory_encoder`
Responsibility: map external-environment inputs onto selected sensory-neuron stimulation.  
All manual assumptions must be documented explicitly.

### MOD-013 `output_decoder`
Responsibility: read descending/output-neuron activity and map it to behavior/control signals.  
All manual assumptions must be documented explicitly.

### MOD-014 `telemetry`
Responsibility: performance counters, spike rate, queue depth, and error status.  
Rule: telemetry must not alter model results.

## 4. First-stage interface specifications
### IF-NEURON-UPDATE
Inputs:
- `valid`
- `neuron_id`
- `neuron_state`
- `input_current`
- `model_params`

Outputs:
- `valid`
- `neuron_id`
- `updated_state`
- `spike`

### IF-SPIKE-QUEUE
Input: `push_valid, spike_event`  
Output: `pop_valid, spike_event`  
Control: `full, empty, ready`

### IF-SYNAPSE-STREAM
Output: `valid, source_id, target_id, weight, last`  
Consumer: `ready`

## 5. Numeric specification
Initial direction:
- `membrane_v`: signed fixed point; exact Q-format chosen by RMD-002 experiments.
- `weight`: signed fixed point.
- accumulator: wider than weight/voltage to reduce short-window overflow risk.
- saturation vs wraparound must be explicit; prefer saturation initially.

Any bit-width decision must first be evaluated in TDD experiments before RTL is frozen.

## 6. Hardware-platform abstraction

The first complete physical-teaching reference board is frozen to the **AMD Kria KV260 Vision AI Starter Kit**, while core RTL remains board-independent.

Platform boundary:

```text
core RTL / stable FlyBrain interfaces
              │
              ▼
        platform shell
  ├─ clock/reset adaptation
  ├─ board-visible I/O
  ├─ PS↔PL runtime control path
  ├─ on-chip memory mapping
  └─ DDR/platform integration
              │
              ▼
   KV260 board files / constraints
   build/program/runtime scripts
```

Platform-specific material lives under `boards/<board>/`. The first KV260 plan is:

```text
boards/
  kv260/
    README.md
    rtl/            # board/platform shell only
    constraints/    # XDC / board-flow glue approved by the Lab
    scripts/        # build/program/runtime helpers
    evidence/       # ignored/generated evidence manifests, not a source of truth
```

Boundary rules:

- `rtl/neuron/`, `rtl/event/`, and `rtl/memory/` must not contain KV260 connector/pin names;
- JTAG/UART, PS/Linux boot/runtime, DDR controller, Vivado board flow, and pin constraints belong to the platform layer;
- the **logical contract** of `MOD-010 host_if` is parameter/stimulus loading plus spike/telemetry readback. LAB-HW-06 now freezes one **teaching transport** only: PS `M_AXI_HPM0_FPD` → SmartConnect → dual-channel AXI GPIO at `0xA0010000`, accessed by a fixed-address root-only `/dev/mem` helper. This does not freeze the later production MOD-010 software stack; a driver/UIO/XRT or other supported path may replace the teaching transport without changing the logical contract;
- board-specific convenience must not redefine `IF-NEURON-UPDATE`, `IF-SPIKE-QUEUE`, or `IF-SYNAPSE-STREAM`;
- Physical Lab board facts are grounded in `KV260_REFERENCE_PLATFORM.md` and AMD official board documentation.

## 7. Bilingual repository layout

### 7.1 Current repository structure

```text
FPGA-FlyBrain/
  README.md
  README.zh-CN.md
  docs/
    en/
    zh/
  lessons/
    en/
    zh/
    checks/
  exercises/
    en/
    zh/
    grader/
    checks/
  labs/
    en/             # LAB-HW-00~07 implemented
    zh/
    checks/
  boards/
    kv260/
      README.md
      rtl/          # LAB-HW-03/04/06/07 board-specific teaching RTL
      tb/           # open-source self-checking teaching testbenches
      constraints/  # frozen Bank 45 XDC mapping
      scripts/      # preflight, discovery, build, and program helpers
      runtime/      # LAB-HW-05~07 boot/MMIO/state-memory checkers
      evidence/     # versioned template + ignored generated local evidence
  rtl/
    learning/
  tb/
    learning/
  scripts/
  .github/workflows/
```

### 7.2 Planned formal-engineering directories

The following directories or deeper contents are **planned** for later RMD slices. Their presence in MDD does not mean they are already implemented:

```text
python/
  reference/
  connectome/
rtl/
  neuron/
  event/
  memory/
  top/
boards/
  kv260/
    platform/       # later host↔PL / DDR platform integration
tests/
data/
okf/
.vibe/
```

Current `labs/` and `boards/kv260/` implement the LAB-HW-00~07 teaching/support slice. LAB-HW-07 adds a 1024 × 32-bit synchronous teaching state store, AXI-BRAM platform build path, runtime multi-address checker, and resource oracle. This does not declare formal MOD-004 or MOD-010, the general KV260 platform shell, MOD-003, or any later formal hardware module complete.

Current `rtl/learning/` and `tb/learning/` are teaching artifacts and do not declare formal modules such as `MOD-003` complete.

English and Chinese documents share the same FR/DP/MOD/T/RMD IDs. Any design-meaning change must be reflected in both languages.
