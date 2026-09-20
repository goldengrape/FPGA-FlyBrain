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

**主要新操作：** 从一个极小、没有 clock/reset/AXI/Linux 依赖的 RTL，完整经历 synthesis → implementation → bitstream → JTAG program。

第一版教学实现现在冻结为 **Bank 45 GPIO marker**：

- top module：`kv260_marker_top`；
- logical output：`bank45_gpio[4:0]`；
- 固定逻辑 pattern：`5'b10101`；
- target part：`xck26-sfvc784-2LV-c`；
- physical mapping 使用课程提供的 `boards/kv260/constraints/bank45_gpio.xdc`；
- XDC 来源于 AMD/Xilinx Board Store 中 KV260 carrier `bank45_gpio` 的 5-bit LED-class interface，以及 K26 SOM `part0_pins.xml` 对应的 package pin mapping。

冻结的 package pins 为：

| logical bit | K26 SOM signal | package pin | I/O standard |
|---|---|---|---|
| `bank45_gpio[0]` | SOM240 D18 | J11 | LVCMOS33 |
| `bank45_gpio[1]` | SOM240 B17 | J10 | LVCMOS33 |
| `bank45_gpio[2]` | SOM240 B18 | K13 | LVCMOS33 |
| `bank45_gpio[3]` | SOM240 A15 | F11 | LVCMOS33 |
| `bank45_gpio[4]` | SOM240 C24 | A12 | LVCMOS33 |

本 Lab **不要求学生理解这些 constraint**；把 XDC 当成课程提供的 board adapter。为什么 RTL port 还需要 XDC、为什么是这些 pin，在 LAB-HW-04 再拆开讲。

build helper 输出固定目录下的 bitstream、utilization report、timing summary；program helper 只接受已经生成的 bitstream，并在 JTAG chain 中明确找到 `xck26*` device 后才 program。

**通过证据至少包括：**

- synthesis/implementation/DRC 完成；因为这个 marker 故意是 clockless，build 必须明确报告 `TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS` 并保存 timing summary，而不是宣称 timing closure；
- bitstream SHA-256；
- Vivado/JTAG programming success；
- `xck26*` target identification；
- Bank 45 LED-class output 上出现稳定、可重复的 marker 状态，并记录照片/观察结果；
- 当前 Git commit 与 carrier revision。

**物理显示极性边界：** Board Store 能证明这 5 个信号属于 `bank45_gpio` LED-class output，并给出 pin mapping；在真实 KV260 dry run 之前，课程不伪造某个具体丝印 LED 的亮灭极性。学生必须记录实际可见状态；完成真实 dry run 后再把物理 designator/polarity 升级为 tested fact。

**DS34 不是通用 JTAG programming oracle。** AMD 对 DS34 的定义是 PS 成功加载 PL design 时点亮。LAB-HW-03 采用 Vivado/JTAG direct programming，因此主要证据是 Vivado/device programming status + 本设计自己的 Bank 45 observable output。

### LAB-HW-04 — Constraints + clock/reset/I/O / 逻辑 port 连接到真实世界

**主要新操作：** 在已经会生成/program bitstream 的前提下，理解 logical RTL port 怎样通过 clock/reset/platform glue 与 physical board resource 连接。

第一版教学实现冻结为 **PS clock/reset 驱动的 PL blink proof**：

- PS 只承担 platform infrastructure，不引入 Linux/AXI；
- Zynq UltraScale+ MPSoC `pl_clk0` 作为 PL clock，教学口径为 nominal 100 MHz；
- PS `pl_resetn0` 进入 `proc_sys_reset`；
- `proc_sys_reset/peripheral_aresetn` 是本设计冻结的 **design-local active-low reset**；
- `kv260_blink_core` 用 counter 分频，在 `bank45_gpio[0]` 产生肉眼可见的周期变化，其余 bits 保持 marker；
- physical output 继续复用 LAB-HW-03 的 `bank45_gpio.xdc`，这样本 Lab 只新增 clock/reset/constraint interpretation，而不是再换一套外围设备。

这里必须明确三层 reset：

1. **SW2**：SOM-level hard reset，作用于整块 SOM；
2. **PS `pl_resetn0`**：platform reset source；
3. **`peripheral_aresetn`**：经过 reset controller 同步后送入 `kv260_blink_core.resetn` 的 design-local reset。

因此可以说“SW2 会在更上游触发系统级 reset sequence”，但**不能说 SW2 就是 RTL 的 `resetn`**。

本 Lab 只教当前需要的 constraint 概念：

- logical port 没有天然 package pin；
- `PACKAGE_PIN` 把 port 连接到 K26 package；
- `IOSTANDARD LVCMOS33` 对应 Board Store 对这些 Bank 45 carrier signals 的 3.3 V 约束；
- clock 来自 PS→PL 内部 clock path，所以不为 `bank45_gpio` 伪造外部 clock constraint。

**通过证据：**

- synthesis/implementation 完成，implemented design 中真实存在 clock 与 setup/hold timing path，且 worst setup/hold slack 都非负；
- blink bitstream hash 与 program log；
- `bank45_gpio[0]` 出现周期变化、其他 marker bits 保持稳定；
- 学生能指出 XDC 中至少一个 logical bit → package pin 的 mapping；
- 学生能解释 `pl_resetn0`、`peripheral_aresetn` 与 SW2 的层级差异；
- resource/timing report、Git commit、board/carrier revision 被写入 T-HW-011 evidence manifest。



### LAB-HW-05 — PS/Linux first boot + UART console / 第一次启动 runtime host

**前置：** LAB-HW-00~04。

**主要新操作：** 让 KV260 的 PS/runtime host 独立启动起来，不同时第一次学习 PS↔PL transport。

第二阶段 authoring image 冻结为当前 AMD/Canonical 面向 Kria K26 的 Ubuntu Server image：

- distribution：**Ubuntu Server 24.04 LTS**；
- image archive：`iot-limerick-kria-classic-server-2404-classic-24.04-x07-20250423.img.xz`；
- 来源：Canonical **Install Ubuntu on AMD** / Kria K26；
- target：KV260/KR260/KD240 unified Kria image；
- microSD：16 GB UHS-1 或更大；
- 初学者写卡工具：**Raspberry Pi Imager**，与当前 AMD Kria guide 一致。

下载身份写入 `boards/kv260/runtime/ubuntu24_image.json`。仓库现在冻结 image filename/source，但**不会伪造** Canonical 可见下载目录没有发布的 upstream SHA-256。学生使用课程 helper 对实际下载的 archive 计算 SHA-256 并记录。在课程完成一次受控下载、把 expected SHA-256 升级写入 manifest 之前，可以执行 T-HW-005，但不能把 image-hash gate 宣称为 fully frozen PASS。

实体 boot path：

- microSD 插 J11；
- J4 FTDI USB 作为 UART console；
- J12 12 V / 3 A power；
- UART：**115200 baud、8 data bits、no parity、1 stop bit、no flow control**；
- Ubuntu 初始登录：`ubuntu` / `ubuntu`，首次登录按系统要求修改密码。

从上电开始保存完整 UART transcript，进入 shell 后记录：

```bash
uname -a
cat /etc/os-release
cat /proc/device-tree/model; echo
sudo xmutil boardid
sudo xmutil bootfw_status
```

Linux 成功启动不等于 custom PL 已加载；反过来，Vivado/JTAG 成功 program PL 也不等于 Linux 已启动。两条路径必须分开理解。

boot firmware 在主流程中**先观察，不把“更新固件”混成第一次 Linux boot 的必做动作**。如果当前 firmware 阻止受支持 Ubuntu image 启动，再按 AMD boot-firmware update/recovery guide 走 troubleshooting branch，并保留证据。

断电前执行：

```bash
sudo shutdown -h now
```

**通过证据：** exact image filename、实际下载 archive 的 SHA-256、写卡方法、UART settings/port、UART boot log、kernel/OS/model 输出、boot-firmware status、当前 Git commit、board/carrier revision 与 clean shutdown record。只要 course expected SHA-256 仍为 null，就不能宣称 formal image-hash PASS。

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
