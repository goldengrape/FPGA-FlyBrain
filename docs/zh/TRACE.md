# TRACE — Project Map / 追踪矩阵

## 0. 文档信息
- 项目：FPGA果蝇 / From Membrane Potential to Silicon
- 修订：v0.3-r1
- 日期：2026-09-16
- 目的：同步 ADD 的产品 FR / Process FR 分层，以及 RMD 新增的学习桥接 slice。

## 1. 目的
把用户需求 → 功能需求 → 设计参数 → 模块 → 测试 → 实施任务串起来，防止 AI 和人类在长期迭代中漂移。

## 2. 顶层追踪
| User task | Product / Process FR | DP | Module(s) / Process | Test(s) | RMD |
|---|---|---|---|---|---|
| U1 理解最小神经元 | FR1 | DP1 | MOD-001/002 | T-001~006 | 001~003 |
| U2 AI辅助实现且可理解 | PFR1/PFR2 | PDP1/PDP2 | bridge slices + AI workflow | explanation checkpoints + module tests | all relevant |
| U3 多神经元与事件网络 | FR3/FR4/FR5 | DP3/DP4/DP5 | MOD-004~009 | T-007~013 | 006~011 + 007A |
| U4 FPGA 上运行 | FR2/FR3/FR5/FR6 | DP2/DP3/DP5/DP6 | MOD-003/010/014 | L3~L5 + board replay | 011A~016 |
| U5 导入真实 MaleCNS | FR7 | DP7 | MOD-011 | T-014/015 | 017~021 |
| U6 建立验证链 | PFR4 | PDP4 | float/fixed/RTL/FPGA oracle chain | L0~L7 | all relevant |
| U7 公理设计与追踪 | PFR2/PFR3 | PDP2/PDP3 | docs/ + .vibe/ + okf/ | trace checks + checkpoints | all |
| U8 进入 AI hardware | FR2~FR8 + PFR1~4 | DP2~DP8 + PDP1~4 | full system | performance + explanation | 003A~028 |

## 3. 关键需求追踪示例
### TRACE-N-001 — 神经元语义到 RTL
需求：神经元能累积输入并跨阈值产生 spike。  
FR：FR1/FR2  
DP：DP1/DP2  
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

### TRACE-L-001 — 学习独立性
需求：一个学习任务不应同时依赖多个尚未掌握的新概念。  
FR：PFR1  
DP：PDP1  
实现：RMD bridge slices + chapter structure  
检查：每个 slice 标记 `主要新概念`；出现多重未知依赖时拆分。  
任务：RMD-003A, 007A, 011A, 012A, 012B, 013A, 014A

## 4. 文档权威关系
- URD：用户、范围、成功定义。
- ADD：产品 FR/DP、过程 FR/DP、矩阵与耦合。
- MDD：模块与接口。
- TDD：oracle 与测试。
- RMD：实现与学习顺序。
- TRACE：跨文档链接。

变更路由：
- 用户目标变了 → URD
- 系统拆分或学习独立性规则变了 → ADD
- 接口/模块变了 → MDD
- 正确性的定义变了 → TDD
- 实施/教学顺序变了 → RMD
- 任一 ID/link 变了 → TRACE

## 5. 双语追踪规则
- `docs/zh/` 与 `docs/en/` 共享同一套 ID。
- 翻译不得自行新增 FR、DP、MOD、T、P 或 RMD ID。
- 设计含义变化时，先修改 source-of-truth 版本，再同步另一语言；最终提交必须两边一致。
- 后续可加入自动化脚本检查两种语言出现的 ID 集合是否一致。

## 6. 当前状态
- URD：initialized
- ADD：revised; product matrix lower-triangular / decoupled
- MDD：initialized; first interfaces freeze 后复查
- TDD：initialized
- RMD：revised with four bridge zones
- TRACE：synchronized with ADD/RMD revision
- First implementation slice：not started

## 7. 下一次必须同步 TRACE 的触发条件
- 第一次冻结 `IF-NEURON-*` 接口；
- 第一次新增或删除 MOD 编号；
- 选择最终 FPGA 板卡后；
- MaleCNS binary image schema 冻结后；
- 任意 RMD 编号发生重排时。
