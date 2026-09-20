# PHYSICAL_FPGA_LABS — 实体 FPGA 实验教学规范

## 0. 目标

Concept Lesson 回答“为什么需要这个硬件概念、它是什么”；Physical Lab 回答“学生怎样在真实 KV260 上完成它，并留下可审查证据”。

Physical Lab 面向 **从未接触过 FPGA、嵌入式 Linux 或厂商 FPGA 工具链的学习者**。不能把 Vivado、cable driver、board file、线缆、供电、JTAG、UART、microSD、Linux boot、programming、constraint 等操作假设成常识。

参考平台见 [KV260_REFERENCE_PLATFORM.md](KV260_REFERENCE_PLATFORM.md)。

## 1. Lesson 与 Lab 的关系

```text
Concept Lesson
    ↓ 建立模型、术语、预期
Physical Lab
    ↓ 真实 setup / connection / build / program / boot / run / observe
Evidence
    ↓ report / readback / serial log / photo / hash / measurement
Human Check
    ↓ 学生解释发生了什么
Engineering Handoff
```

Physical Lab **不是**把现有 Lesson 复制一遍加上截图；它承担真实设备操作、故障定位和证据采集。

## 2. 每个 Lab 的固定结构

每份 Physical Lab 至少包含：

1. **今天桌上应该有什么**：板卡、电源、线缆、SD 卡/外围器件；
2. **开始前检查**：断电/供电、接口、电压、安全边界、所需软件版本；
3. **今天只学习一个主要新操作**；
4. **Connection Map**：使用 inline SVG + 官方接口名称标明这次真正要接的路径；
5. **Build / Program / Boot / Run**：按本 Lab 实际涉及的阶段明确分开；
6. **Expected Evidence**：成功时应该看到什么，而不是只写“无报错”；
7. **If it does not work**：按层级提供 troubleshooting tree；
8. **Human Check**：要求解释当前证据能证明什么、不能证明什么；
9. **Save Evidence**：记录 board rev、tool version、Git commit、artifact hash 与实验输出。

截图可以辅助定位 UI，但不能成为唯一规范。关键按钮/命令、输入、输出与通过标准必须有可搜索的文字版本。

## 3. 故障分层

实体实验默认按下面顺序定位，不让学生一上来改 RTL：

```text
vendor toolchain / driver / board files
  ↓
power
  ↓
physical connection / cable
  ↓
target enumeration / JTAG
  ↓
synthesis / implementation
  ↓
constraints / timing
  ↓
programming
  ↓
PS boot / UART / Linux
  ↓
runtime I/O / host transport
  ↓
FlyBrain core behavior
```

一个证据只能证明其所在层及明确关联的 contract。例如“Vivado 显示 program succeeded”不能证明 neuron algorithm 正确；“Linux 启动成功”也不能证明 PS↔PL transport 正确。

## 4. Reset 层级必须分清

KV260 上存在不同层级的 reset。课程必须明确区分：

- **SW2 / SOM reset**：board/SOM 级 hard reset；用于复位整个 SOM，不自动等于某个 SystemVerilog module 的 `rst_n`；
- **PS/platform reset**：由平台基础设施产生或分发的 reset；
- **FlyBrain design-local reset**：某个 RTL block 的逻辑 reset contract。

在 LAB-HW-04 真正冻结 design-local reset source 之前，教材不得写成“按 SW2 就等于给 neuron RTL 拉低 `rst_n`”。如果某次实验使用 SW2，只能说明它执行 SOM-level reset；若要控制局部 PL design reset，必须明确说明实际来源与极性。

## 5. KV260 Physical Lab 路径

### LAB-HW-00 — Vendor toolchain preflight / 先把开发环境准备正确

**主要新操作：** 在不上电、不写 RTL 的情况下确认厂商工具链本身可用。

学生只处理 development host：

- 使用本 Lab 指定的当前 AMD Vivado **authoring candidate** 版本；
- 安装/验证 JTAG cable driver；
- 安装/验证与该版本匹配的 KV260 board files / board flow；
- 记录 OS、Vivado version、board-file/platform version；
- 运行课程给出的版本与 board-definition 自检命令。

本 Lab 不连接板卡、不生成 bitstream、不学习 AXI。

**通过证据：** tool/version/board-definition preflight 全部通过，并保存文本输出。authoring 阶段可以先指定 candidate version，防止教材/脚本静默漂移；但只有真实 KV260 dry run 留下 evidence 后，才能把它升级为**已测试的课程支持 baseline**。

### LAB-HW-01 — Board orientation / 第一次认识 KV260

**主要新操作：** 在不上电、不写 RTL 的情况下识别实体接口。

学生必须能指出：

- K26 SOM 与 carrier card；
- J12 12 V power input；
- J4 FTDI USB UART/JTAG；
- J11 microSD；
- J10 Ethernet；
- SW2 SOM-level reset；
- 至少一种后续可用 I/O/expansion path；
- carrier revision 标识位置（以实际板卡/官方图为准）。

**通过证据：** 一张按课程模板完成的 board inventory，记录实际 carrier revision，并能说明 SW2 是 SOM reset、不是默认的 FlyBrain local RTL reset。

### LAB-HW-02 — Power + target detection / 让开发电脑看见板子

**主要新操作：** 正确供电并让已通过 LAB-HW-00 的开发工具枚举真实 target。

本 Lab 不修改 FlyBrain RTL，不学习 AXI。

学生区分：

- 12 V board power；
- J4 USB data/JTAG/UART；
- development host；
- target device。

**通过证据：** 工具能够稳定枚举目标；记录 target identification。若板未被识别，按 power → cable/JTAG → driver/tool 的路径排查，而不是改 RTL。

### LAB-HW-03 — First bitstream / 第一次配置 PL

**主要新操作：** 从最小 RTL 完整经过 synthesis → implementation → bitstream → program。

第一版实现选择一个由官方 board flow / schematic 支持、容易观察的 PL proof。具体用户输出与约束在写 Lab prose 时冻结，不在本规范阶段猜 pin。

**通过证据至少包括：**

- implementation/timing 没有阻断性错误；
- bitstream hash；
- programming success；
- **与实际 programming path 对应的 configuration evidence**；
- 至少一个能说明“这是我们的设计，不只是板卡上电”的可观察结果。

**DS34 不是通用 JTAG programming oracle。** AMD 对 DS34 的语义是 PS done：表示 PS 已成功加载 PL design。只有当本实验实际采用的路径与该语义一致时，DS34 才能作为证据；如果 LAB-HW-03 使用 Vivado/JTAG 直接配置 PL，应使用 Vivado/device programming status 与该设计自己的可观察输出作为主要证据。

### LAB-HW-04 — Constraints + clock/reset/I/O / 逻辑 port 连接到真实世界

**主要新操作：** 理解 logical RTL port 与 physical board resource 之间需要 board/constraint mapping。

只教当前实验需要的：

- clock source / period；
- design-local reset semantics；
- 一个安全的 board-visible I/O；
- I/O standard / voltage boundary。

本 Lab 必须明确冻结“这个实验中的 local reset 到底从哪里来、极性是什么”，并再次说明 SW2 是 SOM-level hard reset，不能未经设计就等同于 module reset。

**通过证据：** 课程冻结的实体/可读 input 或 local reset source 能以预期方式改变输出；学生能够解释“RTL port 名称本身为什么没有物理 pin 含义”，并区分 SOM reset 与 design-local reset。

### LAB-HW-05 — PS/Linux first boot + UART console / 第一次启动 runtime host

**前置：** LAB-HW-00~04。

**主要新操作：** 让 KV260 的 PS/runtime host 独立启动起来，不同时学习 PS↔PL transport。

学生完成：

- 按课程冻结来源获取并校验 starter Linux image；
- 把 image 写入 microSD；
- 使用课程指定 UART console path；
- 启动 KV260；
- 观察 boot log 并完成首次 login / shell check；
- 明确 development host 与 KV260 PS/Linux runtime host 是两台不同执行环境。

本 Lab 不要求 host↔PL register readback，也不教授完整 AXI。

**通过证据：** 保存 image/version/checksum、UART boot log、kernel/OS identification 与一次简单 shell command 输出。能够回答“JTAG program PL”和“PS/Linux boot”为什么是两条不同路径。

### LAB-HW-06 — Real host↔PL loopback / 真正的软件到硬件往返

**前置：** LSN-015、LAB-HW-05。

**主要新操作：** 在已经会启动 PS/Linux 的前提下，让 KV260 runtime host 控制 PL。

最小语义保持与 L15 一致：

```text
write value → PL stores/processes → read back result
```

本 Lab 先冻结 semantic contract，再在 RMD-012B 选择 KV260 的最小稳定 runtime transport；不为了“先跑起来”提前要求学生理解完整 AXI。

**通过证据：** 写入、PL 状态变化、读回顺序均与预期一致，self-checking script 能检测错误值/错误顺序，并能区分 Linux/transport failure 与 core behavior failure。

### LAB-HW-07 — BRAM neuron state / 第一次使用真实片上 RAM resource

**主要新操作：** 把 L9 的抽象 `state[address]` 映射为真实 FPGA on-chip memory。

只要求：

- register array 与 block RAM 的角色差异；
- address；
- read/write；
- 本实现实际采用的 synchronous read behavior；
- synthesis/resource report 中确认 memory resource。

不展开 primitive 全参数、ECC 或复杂多端口仲裁。

**通过证据：** 多地址 state 的读写结果正确，resource report 与设计预期一致。

### LAB-HW-08 — Small FlyBrain replay / 小网络第一次跑在真实 FPGA

**主要新操作：** 把已经通过 Python/RTL simulation 的小网络迁移到 KV260，不重新发明算法。

同一 fixed input / seed：

```text
Python fixed reference
        ↕ compare
KV260 FlyBrain small network
```

**通过证据：** spike/state replay 与 reference 在冻结 contract 下匹配；记录 bitstream、network fixture、input fixture 与输出 hash/trace。

### LAB-HW-09 — DDR integrity / 第一次真实读写外部内存

**前置：** LSN-016、LSN-017。

**主要新操作：** 使用 KV260 平台现成 DDR/PS/PL 基础设施完成稳定读写，不手写 DDR PHY/controller。

实验顺序：

```text
known payload
→ write
→ read
→ byte-for-byte/checksum compare
→ only then measure
```

**通过证据：** integrity PASS + transfer size + elapsed time + effective bandwidth，并记录 access pattern。任何 integrity failure 都阻断性能结论。

### LAB-HW-10 — AXI/burst measurement / 协议概念变成真实数据移动

**前置：** LSN-018 与 LAB-HW-09。

**主要新操作：** 在真实平台上比较小/零散访问与连续/burst-oriented 路径的有效带宽和延迟。

必须完成的是“使用与测量”；自己从零写完整 AXI master 属于可选挑战。

默认 measurement protocol（Lab prose 可以在有证据时更严格，但不能更模糊）：

- 同一 bitstream、同一 data volume、同一 payload 与 measurement boundary；
- 先做 **5 次 warm-up**，warm-up 不进入统计；
- 每种 access pattern 至少 **20 次 measured repetitions**；
- 以 **median** 作为主结果，同时保存 min/max 与原始样本；
- 在同一实验 session 再重复一批 measurement；两批 median 的相对差异应 **≤10%**。超过 10% 时先报告“measurement unstable”，不得据此下性能结论；
- workload contract、计时起止点与是否包含 host/software overhead 必须写清楚。

**通过证据：** 至少两种 access pattern 满足上述可重复 benchmark；结果不得脱离 workload contract 宣称“AXI/FPGA 更快”。

## 6. 哪些内容故意不教

第一轮 Physical Lab 不系统教授：

- JTAG protocol 内部状态机；
- boot firmware 内部实现；
- Linux kernel/driver 开发；
- DDR PHY training；
- 完整 AXI channel/ordering/outstanding/coherency；
- Vivado 所有 IP Integrator 功能；
- floorplanning / advanced timing closure；
- clock-domain crossing 全体系。

只有 FlyBrain 实际需要并且现有抽象不足时，再增加独立 bridge lab。

## 7. 作业与验收形式

Physical Lab 不强行套用 Python grader。允许的正式作业证据包括：

- toolchain/version preflight log；
- Vivado report 解析结果；
- programming/target log；
- UART boot log；
- terminal readback；
- self-checking host script；
- hardware output trace；
- photo（只作补充证据）；
- resource/timing summary；
- bitstream/build manifest；
- differential replay report；
- bandwidth raw samples + summary。

每个 Lab 的自动化部分仍进入 CI；真正需要 KV260 的步骤放入 physical checkpoint / hardware runner，不伪造普通 CI 的“板上通过”。

## 8. 文档优先实现顺序

本轮先完成：

1. URD / ADD / LEARNING_PATH / ROADMAP；
2. RMD / MDD / TDD / TRACE；
3. KV260 reference platform 与本 Lab 规范。

之后才允许：

4. 编写 `labs/zh/`、`labs/en/`；
5. 在 LAB-HW-00/02/03/05/06 prose 中冻结具体 Vivado version、board files、pin/constraint、starter Linux image 与 host transport；
6. 写 `boards/kv260/`、RTL/platform scripts；
7. 在真实 KV260 上逐 Lab dry run；
8. 将可自动化部分加入 CI。

没有完成对应文档与 oracle 的 Lab，不进入 board-specific implementation。
