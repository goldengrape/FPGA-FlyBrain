# RMD — Build Path / 实施路线

## 0. 文档信息
- 项目：FPGA果蝇 / From Membrane Potential to Silicon
- 修订：v0.3-r2
- 日期：2026-09-19
- 目的：根据 Learning Independence Axiom 压平学习曲线；保留已有 RMD 编号，并用字母后缀插入 bridge slice，避免破坏既有追踪。

## 1. 总原则
每个 slice 必须：
1. 目标小而明确。
2. 有测试 oracle。
3. 有可运行/可观察产物。
4. 有 Git checkpoint 或 spec checkpoint。
5. 不提前引入当前 slice 不需要的复杂度。
6. 最多引入一个主要陌生概念，或一个不可分割的紧密概念簇。
7. AI 可以生成代码；学习者必须能解释输入、状态、输出、时序和验收标准。
8. 遵守 [文档优先与规范治理](DOCUMENT_AUTHORITY.md)：涉及 contract 的 slice 先更新中英文文档与 oracle / TRACE，再进入实现；RMD 不得用“现有代码已经这样写”代替 specification decision。

## 2. 五个平台
```text
平台 1 计算神经元
Python / LIF / fixed point

平台 2 数字神经元
clock / register / RTL / waveform

平台 3 事件神经网络
RAM / sparse graph / FIFO / event routing

平台 4 真实硬件与内存
FPGA / host transport / DDR / AXI / bandwidth

平台 5 真实连接组
MaleCNS / scaling / closed loop / benchmark
```

# 平台 1 — 我理解一个神经元如何成为计算

### RMD-001 Python LIF float reference
主要新概念：**模型是有目的的简化**。  
产物：`python/reference/lif_float.py`  
测试：T-001~T-004。  
完成：给定输入可输出膜电位轨迹和 spike，并能解释每一项生理学含义。

### RMD-002 Fixed-point exploration
主要新概念：**有限位宽数值表示**。  
产物：`python/reference/lif_fixed.py`。  
比较多个 Q-format、rounding、saturation/overflow 策略。  
测试：T-005~T-006。

### RMD-003 First spec checkpoint
冻结 v0 neuron semantics；更新 MDD 数值接口、TDD oracle、TRACE。  
Git checkpoint：`spec: freeze v0 neuron semantics`。

**平台 1 完成标志：** 屏幕上的神经元按可重复规则放电，float 与 fixed-point 差异可测。

## Bridge 1 — 从程序变量到数字状态
### RMD-003A Digital Hardware Bridge
主要新概念：**硬件状态与时钟**。

只做三个微实验：
1. combinational adder；
2. clocked counter；
3. accumulator + threshold。

建立对应关系：
```text
Python variable  → register / RAM state
if               → comparator + mux/control
loop             → parallel hardware 或 time multiplexing
function/module  → hardware module + interface contract
```

完成：能从 waveform 指出状态何时改变，并解释 combinational 与 sequential 的区别。

# 平台 2 — 我理解计算如何成为数字电路

### RMD-004 SystemVerilog single neuron
主要新概念：**用 RTL 描述已知状态机/数据通路**。  
产物：`rtl/neuron/lif_neuron_engine.sv`。  
测试：Python fixed-point vector → RTL compare。  
约束：不得在 RTL 中重新发明 neuron semantics。

### RMD-005 Testbench + waveform lesson
主要新概念：**仿真与 testbench 是硬件的可执行实验**。  
产物：`tb/lif_neuron_engine_tb.sv`。

### RMD-005A RTL explanation checkpoint
学习者必须不用 AI 解释：哪些是 state、哪些是 combinational path、bit width 的理由、输入在哪个 clock edge 生效、测试失败时先查哪个层级。

**平台 2 完成标志：** RTL waveform 与 Python fixed-point reference 在规定测试上匹配。

# 平台 3 — 我理解很多神经元如何成为一台事件计算机

### RMD-006 128-neuron time multiplexing
主要新概念：**一个物理计算单元轮流服务大量虚拟状态**。  
产物：state RAM + scheduler。

### RMD-007 1K-neuron simulation
主要新概念：**吞吐量和资源使用成为架构指标**。  
测量：cycles per neuron update、RAM usage。

## Bridge 2 — 从“神经元数组”到“事件传播”
### RMD-007A Four-neuron event walk-through
主要新概念：**事件携带 source，系统据此查找下游连接**。

使用 4 个神经元、3–6 条手写连接，观察：
`spike(source)` → queue → lookup → `(target, weight)` → target update。

完成：在进入正式 CSR/FIFO RTL 与接口实现前，能口头描述一个 spike 从 source 到 target 的完整旅程。教学 Notebook 可以先用小型 Python 模型分别认识 queue/backpressure 与 sparse lookup，再回到本 checkpoint 做端到端整合。

### RMD-008 Sparse adjacency image
主要新概念：**稀疏图的数据表示**。  
Host 生成 source index + synapse records。

### RMD-009 Spike FIFO
主要新概念：**事件排队与流控**。  
测试：ordering、full/empty、backpressure。

### RMD-010 Synapse reader + engine
主要新概念：**从稀疏连接记录形成 weighted event stream**。

### RMD-011 Small event-driven SNN
集成前面模块，不新增主要概念。  
规模：100–1000 neurons。

**平台 3 完成标志：** 小网络只靠 spike event 自主传播活动，而不扫描所有连接。

# Bridge 3 — 从仿真里的硬件到真的 FPGA

### RMD-011A FPGA toolchain dry run（无需买板）
主要新概念：**synthesis 与 simulation 回答不同问题**。  
综合 counter/accumulator，阅读基础 resource/timing report；不学习 AXI/DDR。

### RMD-012 Select reference board and create platform shell

reference board 冻结为 **AMD Kria KV260 Vision AI Starter Kit**。正式实体教学从这里开始使用 board-specific facts，但 FlyBrain core 保持板卡无关。

对应 Physical Lab：

- **LAB-HW-00**：vendor toolchain preflight；在不连接板卡时先冻结/验证 Vivado version、JTAG cable driver、KV260 board files / board flow；
- **LAB-HW-01**：board orientation；识别 K26 SOM、carrier、J12 power、J4 UART/JTAG、microSD、Ethernet、SW2 SOM reset、carrier revision；
- **LAB-HW-02**：正确供电并完成 target enumeration；把 power/cable/JTAG 问题与 RTL 问题分层。

通过标准：
- development host 的 vendor toolchain preflight 有文本证据；
- 学生能从未上电状态开始正确连接 KV260；
- development host 能稳定发现目标；
- 记录 board revision、tool version、board-file/platform version、target identification；
- 规划中的 `boards/kv260/` platform shell 边界清楚，不把 pin/platform IP 写进 core RTL。

### RMD-012A First physical proof

主要新概念：**bitstream 把 RTL 变成真实芯片中的实现；logical port 还需要 board/constraint mapping 才有物理意义。**

对应：

- **LAB-HW-03**：最小 RTL 完成 synthesis → implementation → timing → bitstream → program；
- **LAB-HW-04**：clock/design-local reset/一个安全 physical I/O 的 constraint 与实体行为。

通过标准至少包括：
- build/implementation 无阻断错误；
- bitstream/build artifact hash；
- programming success；
- 与实际 programming path 匹配的 configuration evidence；
- 至少一个能证明“这是我们的设计在运行，而不是只有板卡上电”的可观察结果；
- 实体/可读 input 或 local reset source 与预期输出一致；
- 学生能区分 SW2 SOM-level hard reset 与 FlyBrain design-local reset。

**DS34 不作为通用 JTAG programming oracle。** 只有 PS 实际加载 PL 时，才按其 PS-done 语义使用 DS34；Vivado/JTAG direct program 以 device programming status + design observable output 为主要证据。

第一次 Physical Lab 不同时学习 AXI、DDR 或 FlyBrain network。

### RMD-012B PS/Linux runtime-host bridge → Host ↔ FPGA minimal loopback

host↔PL 前先拆出一个独立 bridge，避免 Linux boot、serial console 与 runtime transport 同时第一次出现。

对应：

- **LAB-HW-05**：starter Linux image → microSD → UART console → PS boot/login；只证明 KV260 PS/Linux runtime host 自己能启动；
- **LAB-HW-06**：在 LAB-HW-05 已通过后，再做真实 PS/runtime host ↔ PL minimal loopback。

LAB-HW-05 通过标准：
- starter Linux image 的 version/checksum 有记录；
- UART boot log 可保存；
- 能进入 shell 并记录 kernel/OS identification；
- 学生能解释 development host 与 runtime host/PS 的区别。

LAB-HW-06 冻结最小 semantic contract：

```text
write value → PL stores/processes → read back result
```

具体 runtime transport（如 AXI-Lite/UIO/XRT 等）在 Lab prose 与 TDD oracle 审批后选择；选择标准是最小稳定路径，而不是提前教授完整 AXI。

LAB-HW-06 通过标准：
- write/readback 可重复；
- PL state/operation 与顺序 contract 一致；
- host script 自检失败时能区分 Linux/transport failure 与 core behavior failure。

### RMD-013 Run small network on FPGA

先用 **LAB-HW-07** 把 L9 的抽象 neuron state memory 映射到真实片上 BRAM resource，再用 **LAB-HW-08** 迁移平台 3 已验证的小网络。

LAB-HW-07 只学习本设计需要的 address/read/write/synchronous-read behavior 与 resource report，不展开 BRAM primitive 全参数。

LAB-HW-08 使用同一 fixed input/seed，把 KV260 输出与 Python fixed-point reference 做 L5 replay。

通过标准：
- 多地址 neuron state read/write 正确；
- synthesis/resource report 确认预期的 on-chip memory resource；
- 小网络 spike/state trace 与 reference 在冻结 contract 下匹配；
- 保存 bitstream、network fixture、input fixture、输出 hash/trace 与 Git commit。

# Bridge 4 — 内存不是“一个很大的 RAM”

### RMD-013A Memory hierarchy & bandwidth bridge
主要新概念：**数据移动成本可以高于算术成本**。  
先比较 sequential、random、batched/burst-like access，理解 latency 与 throughput。概念 Lesson 可以先用模型；真实 measurement 由 LAB-HW-09/10 完成。

### RMD-014 DDR hello-world

主要新概念：**外部存储具有独立访问延迟与控制路径**。

对应 **LAB-HW-09**：通过 KV260 平台已有 controller/IP 完成：

```text
known payload → DDR write → DDR read → byte/checksum compare → measurement
```

不手写 DDR PHY/controller。

通过标准：
- integrity PASS；
- transfer size、elapsed time、access pattern、effective bandwidth 有记录；
- 错误数据必须先使 integrity fail，不能用性能数字掩盖 correctness failure。

### RMD-014A AXI burst practical bridge

主要新概念：**用标准总线事务批量搬运连续数据**。

对应 **LAB-HW-10**：只学习本项目需要的 AXI subset，在真实 KV260 上比较 small/scattered 与 burst-oriented transfer。第一次必做目标是“使用 + 测量”；从零实现完整 AXI master 只作为可选挑战。

measurement 默认 protocol：
- 同一 bitstream、data volume、payload 与 measurement boundary；
- 5 次 warm-up 不计入统计；
- 每种 access pattern 至少 20 次 measured repetitions；
- 主结果取 median，并保存全部 raw samples 与 min/max；
- 同一 session 再做第二批 measurement，两批 median 相对差异 ≤10% 才可称可重复；否则标记 `measurement unstable`；
- 明确 timer 是否包含 host/software overhead。

通过标准：
- 至少两种 access pattern 满足可重复 measurement protocol；
- workload contract 写清楚，不从单个数字泛化“AXI/FPGA 更快”。

### RMD-015 Move synapse store to DDR
替换存储后端，不改变 `IF-SYNAPSE-STREAM`。  
测试：同一网络片上/DDR 结果一致。

### RMD-016 Throughput baseline
测 P-001~P-008 中当前可测项目。

**平台 4 完成标志：** 学生能够从一台尚未配置好 vendor toolchain 的 development host 与一块未上电的 KV260 开始，独立完成 toolchain preflight、board orientation、target discovery、bitstream build/program、physical I/O、PS/Linux first boot、host↔PL loopback、BRAM state、small-network replay、DDR integrity 与真实 bandwidth measurement；FPGA 网络使用外部内存，并能解释和测量内存瓶颈。

# 平台 5 — 我可以运行真实神经系统数据

### RMD-017 MaleCNS converter v1
主要新概念：**科学数据需要转换成稳定、版本化的硬件 image**。  
输出 manifest/checksum + binary image。

### RMD-018 1K real subset
把真实 connectome 第一次送入已验证系统；软件与 FPGA differential test。

### RMD-019 10K / 50K scaling
主要新概念：**性能瓶颈随规模变化**。  
定位 DDR、FIFO、bank conflict、hotspot。

### RMD-020 Full MaleCNS image
装载完整目标数据。

### RMD-021 Full network execution
完成 correctness + stability + performance 报告。

### RMD-022 Event-driven optimization
baseline 正确后才优化：lazy membrane update、cache、banking、多 synapse engines 等。

### RMD-023 Sensory encoder v1
人工映射必须文档化，明确实验事实与工程假设。

### RMD-024 Output decoder v1
输出 descending neurons → 简单行为。

### RMD-025 Closed-loop demo
先用二维简化环境，再考虑游戏/机器人。

### RMD-026 Chapterize each build slice
每个 slice 对应一章/实验；bridge slice 也是正式教学内容。

### RMD-027 Public reproducibility pass
在新机器上按 README 从零复现。

### RMD-028 CPU/GPU/FPGA benchmark
同模型、同数据、同输入，对比延迟、吞吐、内存流量与功耗。

**平台 5 完成标志：** 真实 MaleCNS 数据可转换、加载并在 FPGA 上运行；闭环输入输出与性能验证可重复。

## 3. 学习曲线风险表
| 跃迁 | 原风险 | 修订后的缓冲 |
|---|---|---|
| Python → RTL | 同时遇到 clock/register/HDL/waveform/bit width | RMD-003A 三个微型数字硬件实验 |
| 多神经元 → event-driven | sparse graph/FIFO/router 同时出现 | RMD-007A 四神经元事件传播 |
| Simulation → FPGA | vendor toolchain、power/cable/JTAG、bitstream、constraint、PS/Linux、host I/O 同时出现 | RMD-011A + LAB-HW-00~08 分成 toolchain preflight、board orientation、target discovery、first bitstream、physical I/O、PS boot、loopback、BRAM、small replay |
| FPGA → DDR/AXI | memory hierarchy、DDR、AXI、bandwidth 同时出现 | RMD-013A + LAB-HW-09/10 分成 integrity 与 measurement |

## 4. 当前第一批只执行的任务
1. RMD-001 Python LIF float reference
2. RMD-002 Fixed-point exploration
3. RMD-003 Freeze v0 neuron semantics

前三项完成前，不启动 FPGA 工具链和硬件购买。`RMD-003A` 是下一批第一项。
