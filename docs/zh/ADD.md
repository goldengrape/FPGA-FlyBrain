# ADD — Design Split / 公理设计文档

## 0. 文档信息
- 项目：FPGA果蝇 / From Membrane Potential to Silicon
- 修订：v0.3-r1
- 日期：2026-09-16
- 本次修订目的：严格区分 FlyBrain 产品系统与学习/工程过程；验证系统矩阵为下三角（decoupled）；把学习曲线本身纳入公理设计约束。

## 1. 设计原则
1. **Independence Axiom**：尽量保持 Functional Requirements（FR）独立。
2. **Information Axiom**：在满足独立性的方案中，优先选择更简单、成功概率更高的方案。
3. **不伪造零耦合**：不为了让矩阵好看而制造无意义模块；必要耦合必须记录并由测试保护。
4. **层级分离**：运行系统的 FR 与教学、AI 协作、验证、追踪等过程 FR 不放在同一设计矩阵中。
5. **Learning Independence Axiom（本项目教学扩展）**：一个学习 slice 最多引入一个主要陌生概念，或一个必须同时出现的紧密概念簇；若完成任务依赖两个以上尚未掌握的新概念，必须增加 bridge slice。

# Part A — FlyBrain 产品系统

## 2. 系统顶层 FR / DP
| ID | Functional Requirement (FR) | Design Parameter (DP) |
|---|---|---|
| FR1 | 定义可执行、可重复的神经元计算语义 | DP1 Python float LIF reference + versioned neuron semantics |
| FR2 | 将已定义的神经元语义映射为确定性的数字计算 | DP2 fixed-point spec + RTL neuron engine |
| FR3 | 用有限硬件资源管理大量虚拟神经元状态 | DP3 banked neuron-state memory + scheduler/time multiplexing |
| FR4 | 表示并可顺序读取稀疏突触连接 | DP4 versioned adjacency/CSR-like synapse image |
| FR5 | 仅对发生的 spike 执行下游传播 | DP5 spike FIFO + event router + synapse engine |
| FR6 | 支持超出片上 SRAM 的突触规模 | DP6 external DDR access layer + burst-oriented layout |
| FR7 | 把真实 MaleCNS 数据装载为系统可消费的网络 | DP7 host-side converter + manifest/checksum + binary image |
| FR8 | 让神经系统与电脑环境形成可观察的闭环 | DP8 sensory encoder + host/FPGA transport + output decoder |

## 3. 系统设计矩阵
`X` 表示功能依赖，`.` 表示无直接依赖。

```text
          DP1 DP2 DP3 DP4 DP5 DP6 DP7 DP8
FR1        X   .   .   .   .   .   .   .
FR2        X   X   .   .   .   .   .   .
FR3        .   X   X   .   .   .   .   .
FR4        .   .   .   X   .   .   .   .
FR5        .   .   .   X   X   .   .   .
FR6        .   .   .   X   X   X   .   .
FR7        .   .   .   X   .   X   X   .
FR8        .   .   .   .   X   X   X   X
```

### 3.1 判定
所有非零项均位于主对角线或其下方，因此为**严格下三角形式的 decoupled design**，更准确地说包含两个可顺序求解的块。

推荐顺序：

```text
DP1 → DP2 → DP3

DP4 → DP5 → DP6 → DP7 → DP8
```

DP1–DP3 是“神经元计算/状态”块；DP4–DP8 是“连接/事件/大规模数据/闭环”块。后期通过稳定接口连接。

### 3.2 独立性含义
- DP1 不需要知道未来神经元数量、DDR 或 MaleCNS。
- DP2 只实现冻结的神经元语义，不重新定义模型。
- DP3 只解决状态规模，不理解突触来源。
- DP4 只定义连接图的可消费表示。
- DP5 消费标准化连接流，不绑死存储介质。
- DP6 可把连接流从片上存储替换为 DDR，而不改变神经元语义。
- DP7 把真实数据转换为 DP4/DP6 契约所需的 image，不改变 FPGA 核心。
- DP8 只在稳定感觉输入/神经输出接口上构造闭环。

## 4. 子系统 FR / DP
### A. Neuron subsystem
FR-N1 保存膜电位和必要内部状态。  
FR-N2 接收输入并按冻结语义更新状态。  
FR-N3 阈值判断并产生 spike。  
FR-N4 支持 refractory/reset。

DP-N1 neuron state record  
DP-N2 arithmetic pipeline  
DP-N3 comparator + spike flag  
DP-N4 refractory counter/FSM

### B. Event subsystem
FR-E1 接收 spike。  
FR-E2 找到 source 的连接范围。  
FR-E3 顺序读取目标突触。  
FR-E4 生成 target weighted event。

DP-E1 spike FIFO  
DP-E2 source index table  
DP-E3 synapse memory reader  
DP-E4 synapse pipeline

### C. Memory subsystem
FR-M1 片上保存高频访问状态。  
FR-M2 外部保存大规模突触。  
FR-M3 保证顺序/burst 访问效率。  
FR-M4 控制热点、bank conflict 和仲裁。

DP-M1 banked BRAM/URAM  
DP-M2 DDR image  
DP-M3 burst-oriented layout  
DP-M4 banking/cache/arbitration

# Part B — 学习、AI 协作与验证过程

## 5. Process FR / DP
这些 FR 不属于 FlyBrain 本体，因此不放进产品系统矩阵。

| ID | Process Functional Requirement | Process Design Parameter |
|---|---|---|
| PFR1 | 初学者能在不同时遭遇多个陌生概念的情况下前进 | PDP1 bridge-first learning slices + one-major-concept rule |
| PFR2 | 充分利用 AI/vibe coding，同时由人保持需求、模型、架构与验收标准所有权 | PDP2 AI collaboration contract + guarded CHECKPOINTs |
| PFR3 | 长期迭代中保持需求、设计、代码、测试可追踪 | PDP3 URD/ADD/MDD/TDD/RMD/TRACE + Git checkpoints + OKF derived context |
| PFR4 | 跨 Python、fixed-point、RTL、板上实现保持正确性 | PDP4 layered oracle: float → fixed-point → RTL simulation → FPGA replay |

过程矩阵是对角设计：

```text
          PDP1 PDP2 PDP3 PDP4
PFR1        X    .    .    .
PFR2        .    X    .    .
PFR3        .    .    X    .
PFR4        .    .    .    X
```

## 6. Learning Independence Axiom 操作规则
### LI-1 每个 slice 只允许一个主要新概念
- fixed-point 先在 Python 中掌握，再进入 RTL；
- clock/register 先通过微型电路掌握，再写 LIF RTL；
- FIFO 先在极小网络中看懂，再引入 CSR/大规模传播；
- 第一次上板不同时学习 AXI；
- DDR/AXI 前先建立 memory hierarchy 与 bandwidth 直觉。

### LI-2 以下情况必须插入 bridge slice
- 成功需要同时理解两个以上尚未掌握的新概念；
- 学生只能复制 AI 代码，不能解释状态、输入、输出或时序；
- test failure 无法归因到单一层级；
- 新工具链问题掩盖正在学习的算法/硬件概念。

### LI-3 五个平台都必须有可见完成感
1. 计算神经元：屏幕上看到膜电位与 spike。
2. 数字神经元：RTL waveform 与 Python reference 一致。
3. 事件神经网络：小网络自主传播 spike。
4. 真实硬件与内存：FPGA 实时运行并能测 bandwidth/latency。
5. 真实连接组：MaleCNS 子图到完整网络可加载、运行、验证。

## 7. Accepted Coupling
### AC-001 Verification cross-cuts all product FRs
验证天然横跨所有实现层，因此移出产品矩阵，作为 PFR4/PDP4；测试逻辑与 synthesizable RTL 分离。

### AC-002 DDR layout affects synapse engine throughput
内存布局与事件流水的性能不可完全独立。控制：定义稳定 `synapse stream` contract，并在完整 MaleCNS 前 benchmark sequential/random/burst 与至少两个 record layout。

### AC-003 Teaching order constrains implementation order
教学项目接受“可理解性优先于过早性能最优”；性能优化在正确性冻结后进行。

### AC-004 Host/FPGA boundary depends on platform capabilities
不同 SoC FPGA 的 ARM、DDR、transport 路径不同。控制：DP8 面向稳定 host/FPGA message contract，不把核心绑定到特定板卡 API。

## 8. 当前设计决策
D-001 基础神经元：LIF。  
D-002 主硬件数值：fixed-point。  
D-003 规模扩展：time multiplexing。  
D-004 网络传播：稀疏 adjacency + spike events。  
D-005 大连接表：外部 DDR。  
D-006 主机负责数据转换、环境与可视化；FPGA 负责神经计算核心。  
D-007 AI 可写大量实现与测试代码，但不能绕过 FR/DP、接口、oracle 与 CHECKPOINT。  
D-008 产品系统 ADD 与学习/工程过程 ADD 分层维护。  
D-009 教学路线遵守 Learning Independence Axiom。

## 9. 本轮结论
- FlyBrain 产品系统矩阵：**通过下三角 / decoupled 检查**。
- 过程矩阵：**对角 / uncoupled**。
- 性能与平台耦合：已记录为 Accepted Coupling，并由 benchmark/contract 守护。
