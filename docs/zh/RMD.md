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

教学 transport 现在冻结为最小、可检查的 KV260 路径：

```text
Ubuntu/Python on PS
  → fixed /dev/mem MMIO
  → PS M_AXI_HPM0_FPD
  → AXI SmartConnect
  → dual-channel AXI GPIO @ 0xA0010000
  → kv260_loopback_transform
```

AXI GPIO 只承担 adapter：Channel 1 `GPIO_DATA`（`+0x0`）保存 32-bit host write，PL 教学 core 计算 `(write + 1) mod 2^32`，Channel 2 `GPIO2_DATA`（`+0x8`）暴露结果。hardware address 与 AMD/Xilinx K26 `base_gpio_bram` reference 一致。课程 helper 不允许指定任意 physical address。

这条 `/dev/mem` path 只冻结为 **LAB-HW-06 的教学 transport**，不定义后续 MOD-010 的最终 software stack。如果受支持的 Ubuntu image 按 policy 阻止访问，不降低系统安全设置；保存 evidence、保持 T-HW-006 阻塞，并在后续仓库修订 transport。

LAB-HW-06 通过标准：
- 保存 build/DRC/timing 与 direct-JTAG programming evidence；
- 固定 vector set 连续运行两轮，`write → expected → read` 全部一致，包括 32-bit wraparound；
- self-checking host script 能区分 Linux/transport failure 与 core-behavior mismatch；
- 保存 runtime trace、bitstream/script hash、Git commit、OS/image identity 与 board/carrier revision。

### RMD-013 Run small network on FPGA

分成两个互相独立的 Physical Lab slice。

**LAB-HW-07 — BRAM neuron state** 只冻结后续 network 所需的 memory substrate：

- 1024 × 32-bit state word；
- PS-visible 4 KiB window，base 为 `0xA0000000`；
- PS `M_AXI_HPM0_FPD` → SmartConnect → AXI BRAM Controller → teaching state-store RTL；
- native synchronous read；
- block-RAM synthesis intent，以及 RAMB18/RAMB36 非零的 resource oracle；
- 固定 multi-address write/read/rewrite self-check。

LAB-HW-07 **不**声明完整 MOD-004 已完成。它只是 board-level teaching slice，用一个简单 memory geometry 证明 address/read/write/synchronous-read/resource 这些概念。banking、arbitration、更宽 neuron record、ECC 与最终正式 state layout 留给后续设计。

**LAB-HW-08 — Small FlyBrain replay** 再把 Lesson 12 已经教过的四神经元 event machine 原样迁移到 KV260，不改变教学 semantics。事实源是 versioned JSON fixture，Python replay oracle 从该 fixture 计算。

冻结 replay：
- source index `[(0,2), (2,1), (3,1), (4,0)]`；
- records `[(1,+2), (2,+1), (3,+2), (3,+1)]`；
- thresholds `[99,2,1,3]`；
- initial state `[0,0,0,0]`、initial queue `[0]`；
- expected spike order `[0,1,2,3]`、expected final state `[0,0,0,0]`；
- 固定 4 KiB state/trace BRAM window：`0xA0000000`；
- 固定 AXI-GPIO control/status：`0xA0010000`；
- host 只能在 PL replay engine idle 时访问 BRAM。

replay 不只比较 final state，还逐项比较 spike order 与每个 weighted event。Lesson-12 fixture 完全 deterministic，不使用 PRNG；未来只有 stochastic replay 才要求 seed。

这是 **teaching event machine 的 L5 board replay**，不是 Python fixed-point LIF oracle，也不代表正式 MOD-004~009 完成。它保留 Lesson 12 的边界：leak、refractory、最终 fixed-point LIF numerics、concurrent target-write conflict 与正式 valid/ready timing 都不属于这个教学 machine。

通过标准：
- LAB-HW-07 multi-address state read/write 与 block-RAM resource proof 保持不变；
- versioned fixture 与 Python oracle 能复现 Lesson-12 expected spike order/event trace；
- open-source RTL simulation 与同一 fixture-derived expected trace 匹配；
- 真实 KV260 的 spike/state/event readback 与同一 Python oracle 匹配；
- 保存 fixture/oracle/bitstream hash、build/program log、output trace、Git commit、OS/image identity、board/carrier revision。

# Bridge 4 — 内存不是“一个很大的 RAM”

### RMD-013A Memory hierarchy & bandwidth bridge
主要新概念：**数据移动成本可以高于算术成本**。  
先比较 sequential、random、batched/burst-like access，理解 latency 与 throughput。概念 Lesson 可以先用模型；真实 measurement 由 LAB-HW-09/10 完成。

### RMD-014 DDR hello-world

主要新概念：**外部存储有自己的 latency/control path，而且必须先证明 correctness，再谈 performance**。

对应 **LAB-HW-09**，先做 PS/Linux 管理的 external-memory sanity slice。板上有 4 GB DDR4 system memory，但本 Lab 暂时不加入 PL→DDR AXI traffic。

第一套 physical DDR 操作冻结为：

```text
OS-managed anonymous mapping
→ prefault 64 MiB
→ deterministic contiguous 1 MiB chunks
→ write
→ read
→ byte-for-byte compare
→ SHA-256 compare
→ integrity PASS
→ only then report host-path timing observations
```

这种设计刻意避开 raw physical DDR address、custom DMA driver、AXI master 与 CDMA setup；这些是不同依赖，留到 LAB-HW-10 / RMD-015。

LAB-HW-09 的 timing 只是这个 userspace path 的 descriptive evidence，不是 peak DDR，也不是 PL/AXI bandwidth benchmark。

通过标准：
- 冻结 64 MiB allocation 与 1 MiB chunk geometry；
- 每个 regenerated expected chunk 与 readback byte-for-byte 一致；
- expected / observed SHA-256 一致；
- CI/dry-run 的 deliberate corruption 必须得到 `DDR_INTEGRITY_MISMATCH`、`PERFORMANCE_BLOCKED=1`，且没有可接受的 bandwidth result；
- 成功 physical run 保存 board/OS/kernel/memory identity，以及 write/read timer boundary、elapsed time 与 host-path effective bandwidth；
- 本 Lab 不需要 bitstream；
- T-HW-009 physical PASS 必须来自真实 KV260 PS/Linux run。

### RMD-014A AXI burst practical bridge

主要新概念：**即使 total bytes 与 hardware 完全相同，transaction granularity 与 access ordering 仍会改变 effective DMA throughput**。

对应 **LAB-HW-10**。本 Lab 使用 AMD AXI CDMA，不要求学生手写完整 AXI master。

第一套真实 PL→DDR benchmark 冻结为：

```text
PS/Linux programs AXI CDMA
        ↓
AXI CDMA M_AXI
        ↓
PS S_AXI_HP0_FPD
        ↓
DDR
```

因为 `S_AXI_HP0_FPD` 是 non-coherent，buffer contract 必须显式冻结。physical run 使用 course-approved u-dma-buf allocation，并以 `O_SYNC` 打开；普通 cached Python memory 不能直接当 DMA buffer。

workload contract：
- 同一 bitstream + 一个至少 2 MiB 的 DMA-safe buffer；
- 256 KiB deterministic payload；
- contiguous pattern = 1 次 256 KiB CDMA request；
- small/scattered pattern = 冻结 deterministic permutation 下的 1024 × 256-byte request；
- timer 包含 Python register programming/polling + DMA completion；
- benchmark 前后两种 pattern 都必须 byte-for-byte integrity PASS。

默认 benchmark protocol：
- 5 次 warm-up，不进统计；
- 每种 pattern 20 次 measured repetition；
- median 为主结果，保留 min/max 与全部 raw sample；
- 同一 session 再重复第二批；
- 两批 median 的差异对两种 pattern 都必须 ≤10%；
- measurement unstable 时保留 evidence，但不能支持 performance conclusion。

这是 end-to-end **software-controlled DMA workload** comparison，不是 peak-DDR specification measurement，也不是 CPU/GPU/FPGA benchmark。

通过标准：
- AXI CDMA build contract：128-bit data、max burst 64、Simple DMA、`S_AXI_HP0_FPD`；
- control base 固定为 `0xA0020000`；
- DMA-safe buffer/cache-mode preflight PASS；
- 两种 pattern 的 source/destination payload integrity 全部 PASS；
- 保存所有 raw sample 与两批 summary；
- 两种 pattern 都通过 ≤10% stability gate；
- 只有这时才允许报告 contiguous/scattered median ratio；
- physical T-HW-010 PASS 必须来自真实 KV260 evidence。

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
