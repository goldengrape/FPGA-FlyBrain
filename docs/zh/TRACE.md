# TRACE — Project Map / 追踪矩阵

## 0. 文档信息
- 项目：FPGA果蝇 / From Membrane Potential to Silicon
- 修订：v0.3-r3
- 日期：2026-09-18
- 目的：同步 ADD 的产品/过程 FR 分层、RMD bridge slices，以及新的 Learning Architecture / Notebook 教学层。

## 1. 目的
把用户需求 → 功能需求 → 设计参数 → 教学 artifact / 模块 → 测试 → 实施任务串起来，防止 AI 和人类在长期迭代中漂移。

## 2. 顶层追踪
| User task | Product / Process FR | DP | Module(s) / Process | Test(s) | RMD |
|---|---|---|---|---|---|
| U1 理解最小神经元 | FR1 | DP1 | LSN-001/002 + MOD-001/002 | T-001~006 | 001~003 |
| U2 AI辅助实现且可理解 | PFR1/PFR2 | PDP1/PDP2 | Notebook AI Task/Human Check + bridge slices | explanation checkpoints + module tests | all relevant |
| U3 多神经元与事件网络 | FR3/FR4/FR5 | DP3/DP4/DP5 | MOD-004~009 | T-007~013 | 006~011 + 007A |
| U4 FPGA 上运行 | FR2/FR3/FR5/FR6 | DP2/DP3/DP5/DP6 | MOD-003/010/014 | L3~L5 + board replay | 011A~016 |
| U5 导入真实 MaleCNS | FR7 | DP7 | MOD-011 | T-014/015 | 017~021 |
| U6 建立验证链 | PFR4 | PDP4 | LSN-002/003 + float/fixed/RTL/FPGA oracle chain | L0~L7 | all relevant |
| U7 公理设计与追踪 | PFR2/PFR3 | PDP2/PDP3 | docs/ + lessons/ + .vibe/ + okf/ | trace checks + checkpoints | all |
| U8 进入 AI hardware | FR2~FR8 + PFR1~4 | DP2~DP8 + PDP1~4 | full learning + engineering system | T-016 + P-001~008 + explanation | 003A~028 |

## 3. 教学 artifact 追踪
| Lesson | 主要目标 | FR / PFR | Test / Check | RMD | Notebook |
|---|---|---|---|---|---|
| LSN-001 | 从神经生理抽象出可执行 LIF | FR1/DP1 | T-001~004 + Human Check | RMD-001 | `lessons/zh/01_membrane_to_lif.ipynb` |
| LSN-002 | 理解 fixed-point/quantization 对行为的影响 | FR1/FR2 + PFR4 | T-005~006 + Human Check | RMD-002 | `lessons/zh/02_float_to_fixed.ipynb` |
| LSN-003 | 冻结可测试的 neuron semantics | PFR3/PFR4 | semantic ambiguity tests + spec checkpoint | RMD-003 | `lessons/zh/03_freeze_neuron_semantics.ipynb` |
| LSN-004 | 建立 register/clock/combinational/sequential 直觉 | PFR1；准备 FR2/DP2 | explanation checkpoint | RMD-003A | `lessons/zh/04_state_and_clock.ipynb` |
| LSN-005 | Boolean logic 最小组合判断 | PFR1；准备 FR2/DP2 | `exercises/zh/05_logic_building_blocks.ipynb`（grader: `exercises/grader/lesson05.py`）+ Human Check | RMD-003A | `lessons/zh/05_logic_building_blocks.ipynb` |
| LSN-006 | 理解 RTL/HDL/SystemVerilog/module/port | PFR1；准备 FR2/DP2 | teaching RTL simulation + Human Check | 准备 RMD-004 | `lessons/zh/06_what_is_rtl.ipynb` |
| LSN-007 | 已知 neuron contract → combinational + sequential RTL | FR2/DP2 + PFR4 | Python oracle + RTL review | RMD-004 教学前置 | `lessons/zh/07_first_rtl_neuron.ipynb` |
| LSN-008 | testbench/waveform/simulation 验证 RTL | PFR4/PDP4 | self-checking testbench + explanation | RMD-005/005A | `lessons/zh/08_testbench_waveform_simulation.ipynb` |
| LSN-009 | 理解一个物理 engine 如何 time-multiplex 多个虚拟 neuron state | FR3/DP3 + PFR1 | `exercises/zh/09_time_multiplex_many_neurons.ipynb`（grader: `exercises/grader/lesson09.py`）+ Human Check | RMD-006/007 教学前置 | `lessons/zh/09_time_multiplex_many_neurons.ipynb` |
| LSN-010 | 理解 bounded FIFO ordering 与 backpressure | FR4/DP4 + PFR4 | `exercises/zh/10_spike_fifo_backpressure.ipynb`（grader: `exercises/grader/lesson10.py`）；T-007/008 前置 | RMD-007A/009 教学前置 | `lessons/zh/10_spike_fifo_backpressure.ipynb` |
| LSN-011 | 用 sparse source index 精确定位真实 synapse range | FR4/DP4 + PFR4 | `exercises/zh/11_sparse_synapse_lookup.ipynb`（grader: `exercises/grader/lesson11.py`）；T-009 前置 | RMD-008 | `lessons/zh/11_sparse_synapse_lookup.ipynb` |
| LSN-012 | 串起 queue → lookup → weighted event → target update | FR4/FR5 + DP4/DP5 + PFR4 | `exercises/zh/12_one_spike_journey.ipynb`（grader: `exercises/grader/lesson12.py`）；T-010~013 前置 | RMD-007A/010/011 教学整合 | `lessons/zh/12_one_spike_journey.ipynb` |

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
需求：已在仿真验证的小网络能迁移到真实 FPGA，且 host 可输入/读取结果。  
FR：FR2/FR3/FR5  
DP：DP2/DP3/DP5  
模块：MOD-003/004/005/010  
测试：synthesis report + loopback + L5 replay  
任务：RMD-011A, 012, 012A, 012B, 013

### TRACE-M-001 — 外部突触内存
需求：超出片上 SRAM 的突触可放入 DDR，而不改变上层 synapse stream 语义。  
FR：FR6  
DP：DP6  
模块：MOD-010/014  
测试：integrity + on-chip/DDR differential + bandwidth benchmark  
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
- TRACE：已同步工程路径与教学路径
- First formal implementation slice：not started

## 8. 下一次必须同步 TRACE 的触发条件
- 第一次冻结 `IF-NEURON-*` 接口；
- LSN-001~004 从 prototype 切换为 import 正式 `python/`/`rtl/` 模块时；
- 第一次新增或删除 MOD / LSN 编号；
- 选择最终 FPGA 板卡后；
- MaleCNS binary image schema 冻结后；
- 任意 RMD 编号发生重排时。
