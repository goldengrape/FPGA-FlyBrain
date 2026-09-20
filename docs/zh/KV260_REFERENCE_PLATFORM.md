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

## 7. 这份文档现在不冻结什么

本次是 **documentation-first** 修订，还不写板卡代码，因此暂不冻结：

- 具体 PL user-output pin；
- 具体 XDC pin assignment；
- host↔PL 最终使用 AXI-Lite、UIO、XRT 或其他 runtime transport 的实现细节；
- DDR access software stack；
- Vivado 的精确支持版本；
- starter Linux image 的精确版本/checksum；
- design-local reset 最终采用哪个 platform/local source。

这些将在对应 `LAB-HW-*` prose 与 TDD oracle 先审完、并在真实 KV260 上完成对应 dry run 后，再进入 board-specific implementation。LAB-HW-00 冻结 vendor toolchain version/board files；LAB-HW-05 冻结 starter Linux image/UART first-boot path；LAB-HW-04 冻结 design-local reset source；LAB-HW-06 冻结 runtime transport。选择时优先采用 AMD 官方支持路径，且不得因为某个 demo 方便而改变 FlyBrain core contract。

**证据语义也必须与路径一致：** 如果使用 Vivado/JTAG 直接 program PL，以 Vivado/device status 和设计自身 observable output 为主要证据；只有 PS 实际负责加载 PL 时，DS34 的 PS-done 语义才能用于该路径的证据。

## 8. 参考板卡决策

本文件解决原 URD Q1：

> **FPGA-FlyBrain 的第一块、也是完整教学保证的参考开发板冻结为 AMD Kria KV260 Vision AI Starter Kit。**

其他板卡以后可以增加 porting guide，但不要求第一版课程同时维护多套零基础上板步骤。
