# KV260_REFERENCE_PLATFORM — KV260 参考硬件平台

## 0. 文档角色

本文件冻结 FPGA-FlyBrain **实体上板教学的参考开发板**。它不是对 AMD 官方手册的替代，而是说明本项目怎样使用这块板、哪些细节必须在实验中记录、哪些板卡专有知识不得泄漏进 FlyBrain core RTL。

**参考板卡：AMD Kria KV260 Vision AI Starter Kit。**

项目允许未来增加其他板卡，但学生第一次完整上板路径只保证 KV260。概念 Lesson 保持尽量板卡无关；`LAB-HW-*` Physical Lab 可以明确使用 KV260 的接口、工具和板卡文件。

## 1. 为什么冻结参考板卡

“理解 FPGA”可以板卡无关，但“第一次真的用 FPGA”不能只写抽象步骤。零经验学习者需要知道：

- 电源接哪里；
- 哪个 USB 接口承担 JTAG/UART；
- 电脑如何确认目标器件存在；
- Vivado 里选择哪个 board；
- bitstream 怎样进入 PL；
- reset、I/O、DDR 和 host/PS 在这块板上分别在哪里；
- 失败时怎样区分电源、连接、toolchain、constraint、program 与 runtime 问题。

因此课程采用：

```text
board-neutral core concepts
        +
KV260 reference physical path
        +
platform shell isolation
```

而不是用“支持任意 FPGA 板”换取无法照做的上板教程。

## 2. 已由 AMD 官方资料确认的 KV260 基线

课程编写实体实验时，以 AMD **Kria KV260 Vision AI Starter Kit User Guide (UG1089)**、KV260 Data Sheet (DS986)、Vivado Board Flow 文档和对应板卡文件为一手依据。

当前官方资料确认：

- KV260 Starter Kit 由 **K26 SOM + carrier card + thermal solution** 组成；
- 板卡需要 **12 V / 3 A** 电源，DC 输入为 **J12**；官方说明 starter kit 包装本身不含电源适配器；
- carrier card 的 **J4** 是集成 FTDI 的 USB 2.0 UART + JTAG 接口；
- **J3** 是绕过 FTDI 的 direct JTAG 接口；
- **J11** 是 microSD card interface；
- **J10** 是 1 Gb/s Ethernet；
- **SW2** 是 SOM-level reset；它用于复位整个 SOM，**不能自动等同于 FlyBrain 某个 RTL module 的 local `rst_n`**；
- SOM 上的 **DS34** 是 PS done LED，点亮表示 **PS 已成功加载 PL design**；它不是所有 programming path 的通用“FPGA 已配置”指示灯；
- KV260 carrier card 至少存在 Rev. 1.0 与 Rev. 2.0 两个版本，部分接口/功能有版本差异；
- Vivado 提供 **KV260 Starter Kit** board flow；该 board flow 能利用 SOM/companion-card 元数据处理固定平台资源与相关约束；
- AMD 的软件入门路径使用 microSD 上的 starter Linux image；本课程后续 host↔PL lab 会把“开发电脑”和“KV260 上的 PS/Linux runtime host”明确区分。

官方入口：

- UG1089: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit
- Interfaces: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Interfaces
- Powering: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Powering-the-Starter-Kit-and-Power-Budgets
- Vivado Board Flow: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Vivado-Board-Flow
- Software Getting Started: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Software-Getting-Started

## 3. 学生需要准备什么

实体 Lab 的最低硬件清单在对应 Lab 编写时再次核对。进入实体板前，先完成 **LAB-HW-00 vendor toolchain preflight**，把开发电脑上的 Vivado、JTAG cable driver 和 KV260 board files 与真实板卡问题分开。当前文档阶段冻结下面这些类别：

- KV260 Vision AI Starter Kit；
- 符合官方要求的 12 V / 3 A 电源；
- microSD card（用于官方 Linux/后续 PS runtime 路径）；
- 可连接 J4 的 USB data cable；
- 一台运行课程支持的 AMD Vivado 工具链的开发电脑；
- 后续 I/O lab 如使用 Pmod，则只使用课程明确列出的 3.3 V 兼容器件/模块。

**禁止把“USB 插上了”当作板卡已供电。** KV260 的主板电源路径与 JTAG/UART data connection 是不同问题。

## 4. 两个“host”必须分清

KV260 是 SoC FPGA 平台。实体教学中有两个容易混淆的角色：

### Development host

外部电脑，负责：

- 编辑 RTL；
- 运行 Vivado；
- synthesis / implementation / bitstream；
- 通过 JTAG 发现并配置目标；
- 收集 build report。

### Runtime host / PS

K26 上的 Arm processing system（PS），后续通常运行 Linux，负责：

- runtime control；
- host↔PL register/message exchange；
- 文件/网络/实验控制；
- 后续数据装载与 telemetry。

因此 Physical Lab 不把“电脑通过 JTAG program FPGA”和“runtime software 通过 PS↔PL 接口控制 PL”混成同一个动作。

两者之间还必须有独立的 **PS/Linux first-boot bridge**：starter Linux image → microSD → UART console → boot/login。学生先证明 PS/Linux runtime host 本身能启动，再进入 PS↔PL loopback；不能把 Linux boot、serial console 和 host transport 第一次同时引入。

## 5. 平台抽象边界

FlyBrain core RTL 不得知道 KV260 connector 名称、pin、Linux device path 或 Vivado project layout。

规划结构：

```text
FlyBrain core RTL
      │ stable logical interfaces
      ▼
KV260 platform shell
  ├─ clock/reset adaptation
  ├─ board-visible I/O
  ├─ PS↔PL control path
  ├─ on-chip memory mapping
  └─ DDR/platform integration
      │
      ▼
KV260 board files / constraints / build scripts
```

板卡专有实现进入规划中的：

```text
boards/kv260/
```

不得把 KV260 pin 或 platform IP 直接写进 `rtl/neuron/`、`rtl/event/` 等 core 模块。

## 6. Carrier revision 与证据记录

每一次实体 Lab 都必须记录：

- board model：KV260；
- carrier revision（Rev. 1.0 / 2.0 或实际标识）；
- Vivado/tool version；
- board file / platform version（能确定时）；
- bitstream 或 build artifact hash；
- Git commit；
- 实验日期；
- 通过标准所需的照片、terminal/readback、report 或 waveform 证据。

如果某个步骤只在特定 carrier revision 上成立，Lab 必须明确写出，不能让学生从失败现象反推板卡版本差异。

## 7. 当前已实现实体 Lab 冻结了什么——什么仍然只是 provisional

documentation-first 决策已经推进到 **LAB-HW-00~08** 的实际实现阶段。

仓库现在冻结：

- reference target part：`xck26-sfvc784-2LV-c`；
- LAB-HW-03 board-visible logical output 与 Bank 45 XDC mapping；
- LAB-HW-04 的 PS `pl_clk0` / `pl_resetn0` clock-reset 教学路径；
- LAB-HW-03/04/06/07/08 使用 direct Vivado/JTAG programming；
- LAB-HW-05 Ubuntu Server 24.04 LTS first-boot/UART path；
- LAB-HW-06 PS `M_AXI_HPM0_FPD` → SmartConnect → AXI GPIO `0xA0010000` 教学 loopback；
- LAB-HW-07 教学 state geometry：**1024 × 32-bit word = 4 KiB**；
- LAB-HW-07 PS-visible BRAM base：**`0xA0000000`**，以及 block-RAM resource oracle；
- LAB-HW-08 replay 事实源：`lab08_four_neuron_replay_v1.json`，严格来自 Lesson-12 四神经元 teaching event machine；
- LAB-HW-08 expected spike order `[0,1,2,3]`、final teaching accumulator state `[0,0,0,0]` 与 4 条 encoded weighted-event record；
- LAB-HW-08 memory/control layout：`0xA0000000` 的 4 KiB state/trace BRAM + `0xA0010000` AXI GPIO control/status；
- LAB-HW-08 host-access rule：只有 engine `busy=0` 时 host 才访问共享 BRAM；本 Lab 不教 concurrent host/engine arbitration；
- LAB-HW-08 verification boundary：deterministic Python fixture oracle → open-source RTL replay → physical differential readback。teaching event machine 与正式 LIF model 保持分离。

以下内容**还不能升级成已验证的实体事实**：

- 早期 Bank 45 marker 在真实板上的具体可见 polarity 等细节；
- Vivado 2026.1 是否可从 authoring candidate 升级为 tested/supported course baseline；
- LAB-HW-05 Ubuntu archive 的可信 expected SHA-256；
- 选定 Ubuntu 24.04 image/kernel 在真实 KV260 上是否允许 fixed `/dev/mem` 教学 mapping；如果 OS policy 阻止，对应 T-HW checkpoint 继续 blocked，并通过仓库修订 transport，不能降低系统安全设置；
- 真实 Vivado LAB-HW-08 build 是否能在目标 device 上完成 shared-BRAM/control block design、timing、DRC，并给出非零 RAMB resource；
- 真实 KV260 T-HW-008 differential replay PASS；
- 最终正式 MOD-004~009、最终 LIF numeric contract、通用 programmable network image/loader、concurrent memory arbitration，以及后续 MOD-010/DDR software stack。

这些事实只有在真实 KV260 dry run 针对具体 Git commit 与 artifact 留下 T-HW evidence 后，才能升级为 tested fact。

已实现的 board-support code 位于 `boards/kv260/`。FlyBrain core RTL 仍然不得依赖 KV260 connector 名、package pin、Vivado project layout 或 Linux device path。

## 8. 参考板卡决策

本文件解决原 URD Q1：

> **FPGA-FlyBrain 的第一块、也是完整教学保证的参考开发板冻结为 AMD Kria KV260 Vision AI Starter Kit。**

其他板卡以后可以增加 porting guide，但不要求第一版课程同时维护多套零基础上板步骤。
