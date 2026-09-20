# TRACE — Project Map / 追踪矩阵

## 0. 文档信息
- 项目：FPGA果蝇 / From Membrane Potential to Silicon
- 修订：v0.3-r9
- 日期：2026-09-20
- 目的：同步 ADD 的产品/过程 FR 分层、RMD bridge slices，以及新的 Learning Architecture / Notebook 教学层。

## 1. 目的
把用户需求 → 功能需求 → 设计参数 → 教学 artifact / 模块 → 测试 → 实施任务串起来，防止 AI 和人类在长期迭代中漂移。

## 2. 顶层追踪
| User task | Product / Process FR | DP | Module(s) / Process | Test(s) | RMD |
|---|---|---|---|---|---|
| U1 理解最小神经元 | FR1 | DP1 | LSN-001/002 + MOD-001/002 | T-001~006 | 001~003 |
| U2 AI辅助实现且可理解 | PFR1/PFR2 | PDP1/PDP2 | Notebook AI Task/Human Check + bridge slices | explanation checkpoints + module tests | all relevant |
| U3 多神经元与事件网络 | FR3/FR4/FR5 | DP3/DP4/DP5 | MOD-004~009 | T-007~013 | 006~011 + 007A |
| U4 FPGA 上运行 | FR2/FR3/FR5/FR6 | DP2/DP3/DP5/DP6 | MOD-003/004/005/010/014 + KV260 platform shell | L3~L5 + T-HW-001~011 + board replay | 011A~016 |
| U5 导入真实 MaleCNS | FR7 | DP7 | MOD-011 | T-014/015 | 017~021 |
| U6 建立验证链 | PFR4 | PDP4 | LSN-002/003 + float/fixed/RTL/FPGA oracle chain | L0~L7 | all relevant |
| U7 公理设计与追踪 | PFR2/PFR3 | PDP2/PDP3 | docs/ + lessons/ + exercises/ + CI checks | trace checks + checkpoints | all |
| U8 进入 AI hardware | FR2~FR8 + PFR1~4 | DP2~DP8 + PDP1~4 | full learning + engineering system | T-016 + P-001~008 + explanation | 003A~028 |

## 3. 教学 artifact 追踪
| Lesson | 主要目标 | FR / PFR | Test / Check | RMD | Notebook |
|---|---|---|---|---|---|
| LSN-001 | 从神经生理抽象出可执行 LIF | FR1/DP1 | T-001~004 + Human Check | RMD-001 | `lessons/zh/01_membrane_to_lif.ipynb` |
| LSN-002 | 理解 fixed-point/quantization 对行为的影响 | FR1/FR2 + PFR4 | T-005~006 + Human Check | RMD-002 | `lessons/zh/02_float_to_fixed.ipynb` |
| LSN-003 | 冻结可测试的 neuron semantics | PFR3/PFR4 | semantic ambiguity tests + spec checkpoint | RMD-003 | `lessons/zh/03_freeze_neuron_semantics.ipynb` |
| LSN-004 | 建立 register/clock/combinational/sequential 直觉 | PFR1；准备 FR2/DP2 | explanation checkpoint | RMD-003A | `lessons/zh/04_state_and_clock.ipynb` |
| LSN-005 | Boolean logic 最小组合判断 | PFR1；准备 FR2/DP2 | `exercises/zh/05_logic_building_blocks.ipynb`（grader: `exercises/grader/lesson05.py`）+ Human Check | RMD-003A | `lessons/zh/05_logic_building_blocks.ipynb` |
| LSN-006 | 理解 RTL/HDL/SystemVerilog/module/port | PFR1；准备 FR2/DP2 | `exercises/zh/06_what_is_rtl.ipynb`（grader: `exercises/grader/lesson06.py`）+ compile-only RTL check + Human Check | 准备 RMD-004 | `lessons/zh/06_what_is_rtl.ipynb` |
| LSN-007 | 已知 neuron contract → combinational + sequential RTL | FR2/DP2 + PFR4 | `exercises/zh/07_first_rtl_neuron.ipynb`（grader: `exercises/grader/lesson07.py`）+ RTL review + Human Check | RMD-004 教学前置 | `lessons/zh/07_first_rtl_neuron.ipynb` |
| LSN-008 | testbench/waveform/simulation 验证 RTL | PFR4/PDP4 | `exercises/zh/08_testbench_waveform_simulation.ipynb`（grader: `exercises/grader/lesson08.py`）+ self-checking testbench/VCD + Human Check | RMD-005/005A | `lessons/zh/08_testbench_waveform_simulation.ipynb` |
| LSN-009 | 理解一个物理 engine 如何 time-multiplex 多个虚拟 neuron state | FR3/DP3 + PFR1 | `exercises/zh/09_time_multiplex_many_neurons.ipynb`（grader: `exercises/grader/lesson09.py`）+ Human Check | RMD-006/007 教学前置 | `lessons/zh/09_time_multiplex_many_neurons.ipynb` |
| LSN-010 | 理解 bounded FIFO ordering 与 backpressure | FR4/DP4 + PFR4 | `exercises/zh/10_spike_fifo_backpressure.ipynb`（grader: `exercises/grader/lesson10.py`）；T-007/008 前置 | RMD-007A/009 教学前置 | `lessons/zh/10_spike_fifo_backpressure.ipynb` |
| LSN-011 | 用 sparse source index 精确定位真实 synapse range | FR4/DP4 + PFR4 | `exercises/zh/11_sparse_synapse_lookup.ipynb`（grader: `exercises/grader/lesson11.py`）；T-009 前置 | RMD-008 | `lessons/zh/11_sparse_synapse_lookup.ipynb` |
| LSN-012 | 串起 queue → lookup → weighted event → target update | FR4/FR5 + DP4/DP5 + PFR4 | `exercises/zh/12_one_spike_journey.ipynb`（grader: `exercises/grader/lesson12.py`）；T-010~013 前置 | RMD-007A/010/011 教学整合 | `lessons/zh/12_one_spike_journey.ipynb` |
| LSN-013 | 区分 simulation、synthesis、implementation 与 timing，并完成 Yosys dry run | FR2 + PFR1/PFR4 | Yosys synthesis dry run + timing summary + Human Check | RMD-011A | `lessons/zh/13_simulation_is_not_chip.ipynb` |
| LSN-014 | 理解 FPGA 芯片与开发板、clock/reset/I/O 的关系 | FR2 + PFR1 | `exercises/zh/14_what_is_fpga_board.ipynb`（grader: `exercises/grader/lesson14.py`）+ Human Check | RMD-012/012A | `lessons/zh/14_what_is_fpga_board.ipynb` |
| LSN-015 | 建立 host 与 programmable logic 两个执行域及最小往返语义 | FR2/FR6 + PFR1 | `exercises/zh/15_host_talks_to_fpga.ipynb`（grader: `exercises/grader/lesson15.py`）+ Human Check | RMD-012B/013 | `lessons/zh/15_host_talks_to_fpga.ipynb` |
| LSN-016 | 区分 latency、throughput、bandwidth，并比较 compute/data-movement 成本 | FR5/FR6 + PFR1 | `exercises/zh/16_data_movement_cost.ipynb`（grader: `exercises/grader/lesson16.py`）+ Human Check | RMD-013A | `lessons/zh/16_data_movement_cost.ipynb` |
| LSN-017 | 理解外部 DDR、burst 与访问模式成本 | FR6/DP6 + PFR1 | `exercises/zh/17_external_memory_ddr.ipynb`（grader: `exercises/grader/lesson17.py`）+ Human Check | RMD-014 | `lessons/zh/17_external_memory_ddr.ipynb` |
| LSN-018 | 掌握 AXI transaction/beat 与 VALID/READY handshake 的最小子集 | FR6/DP6 + PFR4 | `exercises/zh/18_axi_subset.ipynb`（grader: `exercises/grader/lesson18.py`）+ Human Check | RMD-014A/015/016 | `lessons/zh/18_axi_subset.ipynb` |
| LSN-019 | 把 connectome 区分为 neuron ID、directed edge、metadata 与 dynamic state | FR7/DP7 + PFR1 | `exercises/zh/19_what_is_connectome.ipynb`（grader: `exercises/grader/lesson19.py`）+ Human Check | RMD-017 | `lessons/zh/19_what_is_connectome.ipynb` |
| LSN-020 | 用 manifest/checksum/provenance 建立 network image contract，并明确 teaching fixture ≠ 正式 MaleCNS artifact | FR7/DP7 + PFR4 | `exercises/zh/20_load_malecns_subset.ipynb`（grader: `exercises/grader/lesson20.py`）；T-014/015 教学前置 | RMD-017/018 | `lessons/zh/20_load_malecns_subset.ipynb` |
| LSN-021 | 用 demand/capacity utilization 识别会随 scale 移动的 bottleneck | FR7 + PFR4 | `exercises/zh/21_scaling_bottlenecks.ipynb`（grader: `exercises/grader/lesson21.py`）+ synthetic scale dry run | RMD-019~022 | `lessons/zh/21_scaling_bottlenecks.ipynb` |
| LSN-022 | 建立 closed-loop feedback，并把 sensory/output mapping 的人工假设显式化 | FR8/DP8 + PFR4 | `exercises/zh/22_closed_loop_world.ipynb`（grader: `exercises/grader/lesson22.py`）；T-016 教学前置 | RMD-023~025 | `lessons/zh/22_closed_loop_world.ipynb` |
| LSN-023 | 冻结 CPU/GPU/FPGA benchmark comparability contract，再计算 throughput/energy metric | FR2~FR8 + PFR4 | `exercises/zh/23_cpu_gpu_fpga_benchmark.ipynb`（grader: `exercises/grader/lesson23.py`）；P-001~008 教学前置 | RMD-028 | `lessons/zh/23_cpu_gpu_fpga_benchmark.ipynb` |

### 3.1 KV260 Physical Lab 追踪

`LAB-HW-*` 不替代 LSN；它们把 Platform 4 的概念落实为真实 KV260 操作与 evidence。

| Lab | 目标 | 主要 Test | RMD | Artifact |
|---|---|---|---|---|
| LAB-HW-00 | vendor toolchain preflight | T-HW-001/T-HW-011 | RMD-012 | `labs/zh/00_vendor_toolchain_preflight.ipynb` |
| LAB-HW-01 | 认识 KV260 实体、接口、SW2 SOM reset、carrier revision | T-HW-011（inventory/evidence） | RMD-012 | `labs/zh/01_board_orientation.ipynb` |
| LAB-HW-02 | power + JTAG target discovery | T-HW-002/T-HW-011 | RMD-012 | `labs/zh/02_power_target_detection.ipynb` |
| LAB-HW-03 | first bitstream build/program | T-HW-003/T-HW-011 | RMD-012A | `labs/zh/03_first_bitstream.ipynb` + `boards/kv260/rtl/kv260_marker_top.sv` |
| LAB-HW-04 | clock/design-local reset/I/O constraints | T-HW-004/T-HW-011 | RMD-012A | `labs/zh/04_clock_reset_io.ipynb` + `boards/kv260/rtl/kv260_blink_core.sv` |
| LAB-HW-05 | PS/Linux first boot + UART console | T-HW-005/T-HW-011 | RMD-012B | `labs/zh/05_ps_linux_first_boot.ipynb` + `boards/kv260/runtime/ubuntu24_image.json` |
| LAB-HW-06 | real host↔PL loopback | T-HW-006/T-HW-011 | RMD-012B | `labs/zh/06_host_pl_loopback.ipynb` + `boards/kv260/scripts/build_lab06_loopback.tcl` + `boards/kv260/runtime/loopback_mmio.py` |
| LAB-HW-07 | BRAM neuron-state store | T-HW-007/T-HW-011 | RMD-013 | planned `labs/zh/07_*` |
| LAB-HW-08 | small FlyBrain FPGA replay | T-HW-008/T-HW-011 | RMD-013 | planned `labs/zh/08_*` |
| LAB-HW-09 | DDR integrity + real measurement | T-HW-009/T-HW-011 | RMD-014 | planned `labs/zh/09_*` |
| LAB-HW-10 | AXI/burst measurement | T-HW-010/T-HW-011 | RMD-014A | planned `labs/zh/10_*` |

Physical Lab 规范来源：
- `docs/zh/KV260_REFERENCE_PLATFORM.md`
- `docs/zh/PHYSICAL_FPGA_LABS.md`

原则：Notebook 可以 prototype/展示，但正式算法、RTL、接口与 oracle 的事实来源仍在 `python/`、`rtl/`、MDD、TDD 等正式工程位置。

## 4. 关键需求追踪示例
### TRACE-N-001 — 神经元语义到 RTL
需求：神经元能累积输入并跨阈值产生 spike。  
FR：FR1/FR2  
DP：DP1/DP2  
教学：LSN-001~008  
模块：MOD-001, MOD-002, MOD-003  
测试：T-001~T-006  
任务：RMD-001, 002, 003, 003A, 004, 005, 005A

### TRACE-E-001 — 事件驱动传播
需求：只为发生的 spike 处理其下游连接。  
FR：FR4/FR5  
DP：DP4/DP5  
模块：MOD-005, 006, 007, 008  
测试：T-007~T-010  
任务：RMD-007A, 008~011

### TRACE-H-001 — 首次真实 FPGA
需求：零 FPGA 经验学习者能在 KV260 上从 vendor toolchain preflight、正确连接/target discovery 走到 first bitstream、physical I/O、PS/Linux first boot、host↔PL loopback，并把已在仿真验证的小网络迁移到真实 FPGA。  
FR：FR2/FR3/FR5  
DP：DP2/DP3/DP5  
模块：MOD-003/004/005/010 + KV260 platform shell  
教学：LAB-HW-00~08  
测试：T-HW-001~008 + T-HW-011 + L5 replay  
任务：RMD-011A, 012, 012A, 012B, 013

### TRACE-M-001 — 外部突触内存
需求：超出片上 SRAM 的突触可放入 DDR，而不改变上层 synapse stream 语义。  
FR：FR6  
DP：DP6  
模块：MOD-010/014  
教学：LAB-HW-09/10  
测试：T-HW-009/010/011 + integrity + on-chip/DDR differential + bandwidth benchmark  
任务：RMD-013A, 014, 014A, 015, 016

### TRACE-C-001 — MaleCNS 导入
需求：真实 MaleCNS 数据可转成 FPGA 可消费、可复现的格式。  
FR：FR7  
DP：DP7  
模块：MOD-011  
测试：T-014/T-015 + manifest/checksum  
任务：RMD-017~020


### TRACE-IO-001 — 感觉输入与行为输出闭环
需求：外部环境输入可映射到感觉神经元，神经输出可解码为行为/控制，同时保持 host/FPGA 边界可观察。  
FR：FR8  
DP：DP8  
模块：MOD-010, MOD-012, MOD-013, MOD-014  
测试：接口/闭环 replay + telemetry consistency；完整系统确定性由 T-016 覆盖  
任务：RMD-023~025

### TRACE-F-001 — 全系统可重复回放
需求：同一版本模型、网络 image、初始状态与输入事件应产生可重复结果；若模型含噪声则固定 PRNG seed。  
FR：FR2~FR8 + PFR4  
DP：DP2~DP8 + PDP4  
模块：全系统正式模块集合  
测试：T-016  
任务：RMD-021, RMD-025, RMD-027

### TRACE-P-001 — 性能指标与 benchmark
需求：正确性冻结后，对吞吐、延迟、带宽、资源与功耗进行可重复测量。  
FR：FR2~FR8  
DP：对应实现 DP  
模块：MOD-003~014 中当前 benchmark 涉及的正式模块  
测试/指标：P-001~P-008  
任务：RMD-016, RMD-019, RMD-021, RMD-028

### TRACE-L-001 — 学习独立性
需求：一个学习任务不应同时依赖多个尚未掌握的新概念。  
FR：PFR1  
DP：PDP1  
实现：`LEARNING_PATH.md` + `LSN-*` Notebook + RMD bridge slices  
检查：每课/每 slice 标记主要新概念；出现多重未知依赖时拆分。  
任务：RMD-003A, 007A, 011A, 012A, 012B, 013A, 014A

## 5. 文档权威关系
- URD：用户、范围、成功定义。
- ADD：产品 FR/DP、过程 FR/DP、矩阵与耦合。
- MDD：模块与接口。
- TDD：oracle 与测试。
- RMD：工程实现顺序。
- LEARNING_PATH：教学概念顺序与 lesson 设计规则。
- `lessons/`：学生可执行教材与实验，不替代正式工程规范。
- TRACE：跨文档、课程、实现的链接。

变更路由：
- 用户目标变了 → URD
- 系统拆分或学习独立性规则变了 → ADD
- 接口/模块变了 → MDD
- 正确性的定义变了 → TDD
- 工程实施顺序变了 → RMD
- 教学概念顺序/lesson 结构变了 → LEARNING_PATH + 对应 Notebook
- 任一 ID/link 变了 → TRACE

## 6. 双语追踪规则
- `docs/zh/` 与 `docs/en/`、`lessons/zh/` 与 `lessons/en/` 共享同一套 ID。
- 翻译不得自行新增 FR、DP、PFR、PDP、MOD、T、P、RMD 或 LSN ID。
- 代码 cell 尽量保持一致；语言版本主要翻译叙事和问题。
- 设计或教学含义变化时，中英文最终必须在同一变更周期内同步。
- 后续加入自动化脚本检查两种语言出现的 ID 集合与 Notebook 对是否一致。

## 7. 当前状态
- URD：initialized
- ADD：revised; product matrix lower-triangular / decoupled
- MDD：initialized; first interfaces freeze 后复查
- TDD：initialized
- RMD：revised with four bridge zones
- LEARNING_PATH：initialized bilingually
- LSN-001~004：第一组双语可执行 Notebook 已建立
- LSN-005~008：第二组双语课程已建立；`rtl/learning/` 与 `tb/learning/` 不代表 MOD-003 已完成
- LSN-009~012：第三组双语课程已建立；Python teaching models 不代表 MOD-004~009 已完成
- LSN-013~018：第四组双语课程已建立；概念 Notebook 不代表实体平台实现已完成
- Reference board：**AMD Kria KV260 Vision AI Starter Kit** 已冻结
- LAB-HW-00~10：Physical Lab 教学结构、RMD 映射与 T-HW oracle 已冻结；**LAB-HW-00~06** 已建立双语 Notebook 与 CI contract checks。LAB-HW-05 加入 Ubuntu/UART evidence helper；LAB-HW-06 加入 authoring-candidate PS/Linux `/dev/mem` MMIO ↔ dual-channel AXI GPIO transport、loopback RTL/build helper 与 self-checking runtime script。当前不宣称真实 KV260、Ubuntu expected hash、`/dev/mem` policy compatibility 或真实 Vivado full build 已通过；LAB-HW-07~10 仍待实现
- LSN-019~023：第五组双语课程已建立；connectome teaching fixture、synthetic scale/benchmark 与 toy closed loop 不代表 RMD-017~028 的正式数据 artifact、全系统实现或真实性能结论已完成
- TRACE：已同步工程路径与教学路径至 LSN-023
- First formal implementation slice：not started

## 8. 下一次必须同步 TRACE 的触发条件
- 第一次冻结 `IF-NEURON-*` 接口；
- LSN-001~004 从 prototype 切换为 import 正式 `python/`/`rtl/` 模块时；
- 第一次新增或删除 MOD / LSN 编号；
- reference board、carrier-revision policy 或支持的 physical tool flow 发生变化时；
- MaleCNS binary image schema 冻结后；
- 任意 RMD 编号发生重排时。
