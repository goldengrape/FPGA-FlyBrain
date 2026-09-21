# MDD — Building Blocks / 模块设计文档

## 0. 目的
定义当前系统的模块边界、接口、数据和契约。模块划分服务于实现和验证，不追求过度细分。

本文件受 [文档优先与规范治理](DOCUMENT_AUTHORITY.md) 约束：正式 module/interface/semantic contract 先在文档中明确，再由 TDD 固化 oracle，最后进入实现；现有 RTL/Python 行为不能自动反向定义本文件。

## 1. 系统拓扑
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

## 2. 核心数据类型
### `neuron_state_t`
- `membrane_v`
- `refractory_count`
- optional `last_update_time`
- optional flags

### `spike_event_t`
- `source_neuron_id`
- `timestamp` / `step_id`（按执行模型选择）

### `synapse_record_t`
- `target_neuron_id`
- `weight`
- optional delay/type flags（初版可不启用）

### `source_index_t`
- `start_offset`
- `fanout_count`

## 3. 模块
### MOD-001 `python_float_reference`
职责：定义最清晰的模型语义。  
输入：模型参数、初始状态、输入事件。  
输出：状态轨迹、spike 轨迹。  
契约：可读性优先，不作为性能实现。

### MOD-002 `python_fixed_reference`
职责：模拟 FPGA 采用的位宽、舍入、饱和和溢出规则。  
契约：RTL 的直接 oracle。

### MOD-003 `lif_neuron_engine`
职责：读取 `neuron_state + input_accum`，执行一次状态更新并产生 `spike_flag`。  
不负责：查突触、DDR、感觉编码。

### MOD-004 `neuron_state_store`
职责：保存大量虚拟神经元状态；支持 banked 访问。  
初版：BRAM/behavioral memory。  
后期：BRAM/URAM + arbitration。

LAB-HW-07 提供的是一个**教学 slice**，不等于正式 MOD-004 已完成：只实现一个 1024 × 32-bit single-port state memory、synchronous read，并通过 AXI BRAM Controller 暴露给 KV260 PS。固定 4 KiB geometry 与 `0xA0000000` platform mapping 只用于教学 memory boundary，不冻结最终 neuron-state record、banking、arbitration 或正式 MOD-004 interface。

### MOD-005 `spike_fifo`
职责：缓存待处理 spike events。  
契约：明确 full/empty/backpressure。

### MOD-006 `source_index_store`
职责：`source neuron ID → synapse range`。

### MOD-007 `synapse_reader`
职责：根据 range 从片上或 DDR 读取 synapse records。  
契约：以流式 valid/ready 风格输出。

### MOD-008 `synapse_engine`
职责：将 synapse record 转换为 target weighted event。

### MOD-009 `target_accumulator`
职责：汇总对目标神经元的输入；处理并发冲突。  
初版：串行/单事件。  
后期：banked accumulator。

### LAB-HW-08 teaching replay boundary

LAB-HW-08 新增 `kv260_small_replay_engine` 与 dual-access teaching state/trace store，只作为 Lesson-12 四神经元 event machine 的**板级 replay harness**。

它把 queue → source lookup → weighted event → target accumulator 的简化教学形式组合起来，但**不**把它们升级成正式 `MOD-005~009`。具体边界：

- 四神经元 source index 与 4 条 synapse record 是 compiled fixture constant；
- target state 是 32-bit integer teaching accumulator，不是正式 `neuron_state_t`；
- threshold crossing 完全按 Lesson 12 将 teaching accumulator reset；
- host 与 engine 不做 concurrent BRAM arbitration；只有 `busy=0` 时 host 才允许访问；
- replay engine 把 spike/event trace 写入同一个 4 KiB teaching memory window 的 reserved word；
- 本 Lab 不冻结正式 `IF-SPIKE-QUEUE`、`IF-SYNAPSE-STREAM`、最终 fixed-point LIF、DDR backend 或 programmable network loader。

这个 harness 只证明一个窄结论：已经验证过 event causality 的教学小网络，在 reference board PL 上执行时产生相同 deterministic trace。

### MOD-010 `host_if`
职责：装载参数、输入刺激、读取 spike/telemetry。  
初版：仿真接口。  
板上：AXI-lite + DMA/streaming，视平台而定。

### MOD-011 `connectome_converter`
职责：将 MaleCNS 原始数据转成版本化 FPGA binary image。  
输出：neuron metadata、source index、synapse records、manifest/checksum。

### MOD-012 `sensory_encoder`
职责：把外部环境输入映射成指定感觉神经元刺激。  
必须显式记录人工假设。

### MOD-013 `output_decoder`
职责：读取 descending/output neuron 活动并转成行为/控制信号。  
必须显式记录人工假设。

### MOD-014 `telemetry`
职责：性能计数、spike rate、队列深度、错误状态。  
原则：不可改变模型结果。

## 4. 接口规范（第一阶段）
### IF-NEURON-UPDATE
输入：
- `valid`
- `neuron_id`
- `neuron_state`
- `input_current`
- `model_params`

输出：
- `valid`
- `neuron_id`
- `updated_state`
- `spike`

### IF-SPIKE-QUEUE
输入：`push_valid, spike_event`  
输出：`pop_valid, spike_event`  
控制：`full, empty, ready`

### IF-SYNAPSE-STREAM
输出：`valid, source_id, target_id, weight, last`  
消费端：`ready`

## 5. 数值规范
第一版建议：
- `membrane_v`：signed fixed-point，具体 Q-format 由 RMD-002 实验确定。
- `weight`：signed fixed-point。
- accumulator：比 weight/v 更宽，避免短时间内溢出。
- saturation / wraparound 必须明确；默认优先 saturation。

任何位宽决策必须先进入 TDD 做误差实验，再固化 RTL。

## 6. 硬件平台抽象

第一套完整实体教学 reference board 冻结为 **AMD Kria KV260 Vision AI Starter Kit**，但 core RTL 仍不得绑定单一板卡。

平台边界：

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

平台相关内容放在 `boards/<board>/`。KV260 第一版规划：

```text
boards/
  kv260/
    README.md
    rtl/            # board/platform shell only
    constraints/    # XDC / board-flow glue as approved by the Lab
    scripts/        # build/program/runtime helpers
    evidence/       # ignored/generated evidence manifests, not source of truth
```

边界规则：

- `rtl/neuron/`、`rtl/event/`、`rtl/memory/` 不得出现 KV260 connector/pin 名称；
- JTAG/UART、PS/Linux boot/runtime、DDR controller、Vivado board flow、pin constraints 都属于 platform layer；
- `MOD-010 host_if` 的**逻辑语义**是装载参数/刺激与读取 spike/telemetry；LAB-HW-06 现在只冻结一条**教学 transport**：PS `M_AXI_HPM0_FPD` → SmartConnect → `0xA0010000` dual-channel AXI GPIO，并由 fixed-address、root-only 的 `/dev/mem` helper 访问。这不冻结后续正式 MOD-010 software stack；driver/UIO/XRT 或其他受支持路径可以替换教学 transport，而不改变逻辑 contract；
- board-specific convenience 不得反向改变 `IF-NEURON-UPDATE`、`IF-SPIKE-QUEUE`、`IF-SYNAPSE-STREAM`；
- Physical Lab 需要的板卡事实以 `KV260_REFERENCE_PLATFORM.md` 与 AMD 官方 board docs 为依据。

## 7. 双语仓库结构

### 7.1 当前实际结构

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
    en/             # LAB-HW-00~07 已实现
    zh/
    checks/
  boards/
    kv260/
      README.md
      rtl/          # LAB-HW-03/04/06/07 board-specific teaching RTL
      tb/           # open-source self-checking teaching testbench
      constraints/  # 冻结的 Bank 45 XDC mapping
      scripts/      # preflight、discovery、build、program helper
      runtime/      # LAB-HW-05~07 boot/MMIO/state-memory checker
      evidence/     # versioned template + 默认忽略的本地生成 evidence
  rtl/
    learning/
  tb/
    learning/
  scripts/
  .github/workflows/
```

### 7.2 规划中的正式工程目录

以下目录或更深层内容属于后续 RMD slice 的**规划态**，尚未因为出现在 MDD 中就视为已实现：

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
    platform/       # 后续 host↔PL / DDR platform integration
tests/
data/
okf/
.vibe/
```

当前 `labs/` 与 `boards/kv260/` 已实现 LAB-HW-00~07 的教学/support slice。LAB-HW-07 新增 1024 × 32-bit synchronous teaching state store、AXI-BRAM platform build path、runtime multi-address checker 与 resource oracle；这不代表正式 MOD-004 或 MOD-010、通用 KV260 platform shell、MOD-003 或后续正式硬件模块已经完成。

当前的 `rtl/learning/` 与 `tb/learning/` 是教学 artifact，不等同于正式 `MOD-003` 等模块已经完成。

中英文文档必须共享同一套 FR/DP/MOD/T/RMD ID；设计含义改变时两种语言同步更新。
