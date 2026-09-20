# LEARNING_PATH — 教学路径 / Learning Architecture

## 0. 这份文档解决什么问题

`RMD.md` 回答“系统按什么顺序实现”；本文件回答“学生按什么概念顺序学习”。两条路径互相追踪，但不能互相替代。

本项目面向的典型读者是学过大学基础生理学、知道膜电位、动作电位和突触，但几乎没有数字硬件背景的生命科学学生。因此课程不能把 `FPGA`、`LIF`、`RTL`、`FIFO`、`AXI` 等缩写当作默认常识。

教学界面采用三层结构：

```text
LEARNING_PATH.md
    ↓ 定义概念顺序、术语引入顺序与学习目标
Jupyter Notebook lessons
    ↓ 像教材一样解释 + 像实验室一样运行 + AI 协作 + 人类检查
正式工程文件（python/ rtl/ tb/ tests/）
    ↓ 可测试、可复用、可进入 CI 的实现
```

**核心边界：Notebook 是“可执行教材 + 实验台”，不是正式实现的唯一事实来源。** 成熟算法、RTL、测试和接口最终必须进入普通源码文件；Notebook 再 import/调用它们完成教学实验。

---

## 1. 读者承诺

课程默认读者：

- 知道膜电位、动作电位、阈值、突触、兴奋/抑制和不应期的大致含义；
- 会基本代数、简单微积分、向量和矩阵；
- 可能听过 AND / OR / NOT，但不要求会数字电路设计；
- **不要求**事先知道 FPGA、HDL、RTL、SystemVerilog、RAM、FIFO、DDR、AXI、计算机体系结构；
- Python 可以边做边学。

因此，如果一个概念不在上述“已知”中，教材第一次使用它时必须负责解释。

---

## 2. 术语与缩写规则

### LP-T1 首次出现必须展开

任何缩写第一次出现时，必须写成：

> **中文名称（English Full Name, ABBR）**：一句白话定义；再说明“为什么现在需要它”。

例如：

> **现场可编程门阵列（Field-Programmable Gate Array, FPGA）**：一种上电后可以按照我们的设计配置成不同数字电路的芯片。这个项目最终会把神经元计算真正变成 FPGA 内部的数字电路。

> **漏电积分发放模型（Leaky Integrate-and-Fire, LIF）**：一种把神经元简化为“膜电位逐渐衰减、输入不断累积、超过阈值就产生一次 spike 并复位”的计算模型。

之后才可以只写 `FPGA`、`LIF`。

### LP-T2 不允许“缩写瀑布”

一段话中如果连续出现多个新缩写，必须拆开。一个 lesson 只能有一个主要新概念；支持它的术语可以出现，但必须逐个解释。

### LP-T3 Notebook 应能独立阅读

即使某个缩写上一课讲过，本课第一次出现时也至少做简短回顾；读者不应因为漏上一页就完全失去上下文。

### LP-T4 工程 ID 不抢占学生注意力

`FR1`、`DP2`、`RMD-003A`、`T-006` 等是项目追踪 ID，不是教学概念。它们不再放在 Notebook 第一屏，而统一放到课末的 **Project Trace / 项目追踪** 区。

### LP-T5 全局术语表只做备查

`docs/zh/GLOSSARY.md` 保存项目术语表，但**不能用“去查 glossary”代替首次解释**。

---

## 3. 教学设计原则

### LP-1 一个 lesson 只引入一个主要陌生概念
遵守 ADD 中的 `Learning Independence Axiom`。如果完成一个 lesson 必须同时理解两个以上尚未掌握的新概念，就拆课或增加 bridge lesson。

### LP-2 从学生已有知识出发
优先采用：

```text
已知神经生理
    ↓
一个明确问题
    ↓
数学/计算抽象
    ↓
可执行实验
    ↓
一个新的硬件概念
    ↓
正式工程实现
```

而不是先系统讲完数字电路、HDL 或计算机体系结构。

### LP-3 先建立直觉，再给定义，再给代码
一个陌生词不应通过代码“顺便出现”。推荐顺序：

1. 为什么会遇到这个问题；
2. 生活/生理学类比；
3. 准确定义；
4. 最小例子；
5. 代码或电路；
6. 观察结果；
7. 回到定义解释结果。

### LP-4 AI 降低实现摩擦，但不能替代模型所有权
Notebook 可以给出 `AI Task`，让 AI 协助生成样板代码、测试或解释；随后必须有 `Human Check`，要求学习者解释状态、输入、输出、时序和 test oracle。

### LP-5 每课必须产生可观察结果
至少有一种：数值轨迹、图、波形、事件序列、资源报告、带宽测量、板上输出或可视化。

### LP-6 每课必须有工程交接点
Notebook 中成熟的实现必须迁移到正式源码。Notebook 随后调用正式模块，不长期维护第二份“影子实现”。

### LP-7 每课都维护“概念账本”
Notebook 应明确写出：

- **本课以前已经知道**；
- **本课第一次学习**；
- **只预告、暂时不要求掌握**。

这样避免预告词被误认为考试范围。

### LP-8 课程图统一使用 inline SVG；禁用 Mermaid 与 ASCII 字符画

从 Platform 5 开始，概念流程、数据流图、状态转移图、时序因果及硬件模块架构统一使用 **Markdown 中的 inline SVG**。不再为新课或本轮修订内容引入 Mermaid。也禁止用空格、连字符拼 ASCII 字符画，或用不可审查截图替代结构图。

**工程理由：**

1. **PDF 可验证**：本项目已经实际观察到 Jupyter/webpdf 对 Mermaid 的空图与假阳性问题；inline SVG 直接进入浏览器 DOM，打印链路更可控；
2. **可版本控制**：SVG 仍是文本，节点、标签、连线与颜色都可进入 Git diff；
3. **可以做视觉 CI**：课程 SVG 使用专用填充色，PDF CI 可检查这些像素是否真正出现在最终页面；
4. **语义显式**：图仍然是可审查的声明式结构，不退化成截图或手工 ASCII。

Platform 5 的 LSN-019~023 已全部改为 inline SVG。较早 lesson 中尚存的 legacy Mermaid 不在本 PR 中批量重写；后续只要这些 lesson 被修改，就应同步迁移为 inline SVG。
---

## 4. 每个 Notebook 的推荐结构

1. **欢迎与本课位置** — 我们在整条路线的哪里。
2. **你已经知道什么** — 从生理学/数学直觉出发。
3. **今天只解决一个问题**。
4. **术语卡片** — 第一次出现的术语逐个展开。
5. **直觉模型**。
6. **准确模型/定义**。
7. **逐行阅读最小代码或电路**。
8. **Run** — 运行。
9. **Observe** — 明确告诉学生看什么。
10. **Try It** — 改一个参数，先预测再运行。
11. **AI Task** — 允许委托给 AI 的工作。
12. **Human Check** — 必须自己能回答。
13. **Engineering Handoff** — 正式源码/测试落在哪里。
14. **Project Trace** — LSN/RMD/FR/DP/T ID，放在最后。
15. **Exit Ticket** — 通过标准。

Notebook 的 Markdown 不是代码之间的装饰文字，而是教材正文。

---

## 5. 第一组课程：从膜电位到数字状态

| Lesson | Notebook | 主要新概念 | 工程映射 |
|---|---|---|---|
| LSN-001 | `lessons/zh/01_membrane_to_lif.ipynb` | 科学模型是有目的的简化；认识 LIF | RMD-001 |
| LSN-002 | `lessons/zh/02_float_to_fixed.ipynb` | 有限位宽数值表示 | RMD-002 |
| LSN-003 | `lessons/zh/03_freeze_neuron_semantics.ipynb` | 先冻结可测试语义，再实现 | RMD-003 |
| LSN-004 | `lessons/zh/04_state_and_clock.ipynb` | 数字状态与时钟 | RMD-003A |

### LSN-001 — 从膜电位到 LIF
先解释 Jupyter Notebook 是什么、整个项目最终为什么会用 FPGA，再完整解释 **Leaky Integrate-and-Fire (LIF)** 三个词分别是什么意思。第一课不要求理解 FPGA 内部结构。

### LSN-002 — 从浮点数到有限位宽
先解释 bit、二进制、floating-point、fixed-point、quantization、rounding、overflow、saturation，再做位宽实验。明确 Python `float` 也不是无限精度实数。

### LSN-003 — 冻结神经元语义
解释 specification、semantics、test oracle。通过 `>=` 与 `>`、更新顺序等最小反例说明：“都叫 LIF”并不足以让两个实现相同。

### LSN-004 — 状态与时钟
从“软件变量为什么能记住值”进入数字状态；只要求理解 combinational logic、state/register、clock/clock edge 和 next state。SystemVerilog/RTL 只做预告，不在本课要求掌握。

---

## 6. 课程的概念路径

下面是当前正式教学顺序。表中的 Notebook 是否已经建立，以第 9 节“当前教学状态”和仓库实际文件为准。

### 平台 2：从数字状态到第一个 RTL 神经元

| Lesson | 第一次重点解释 | 工程映射 |
|---|---|---|
| LSN-005 数字逻辑积木 | bit、Boolean logic、AND/OR/NOT、comparator | RMD-003A |
| LSN-006 什么是 RTL | Register-Transfer Level、HDL、SystemVerilog、module/port | 准备 RMD-004 |
| LSN-007 第一个 RTL 神经元 | combinational path、sequential update、`always_comb`/`always_ff` | RMD-004 教学前置 |
| LSN-008 我们怎么知道硬件是对的 | testbench、waveform、simulation | RMD-005/005A |

### 平台 3：很多神经元如何成为事件计算机

| 计划 Lesson | 第一次重点解释 | 工程映射 |
|---|---|---|
| LSN-009 一个计算单元服务很多神经元 | time multiplexing；memory/address/RAM 为支持术语 | RMD-006/007 |
| LSN-010 spike 为什么需要排队 | bounded FIFO 与 backpressure | RMD-007A/009 |
| LSN-011 不要扫描所有突触 | sparse graph、adjacency list、CSR-like source index | RMD-008 |
| LSN-012 一个 spike 的完整旅程 | event-driven computation；整合 queue/lookup/weighted event | RMD-007A/010/011 |

> **教学顺序与 RMD 工程实现顺序不要求逐项相同。** LSN-010/011 先用 Python 隔离理解 queue/backpressure 与 sparse lookup，LSN-012 再做 RMD-007A 式端到端整合；RMD-007A 仍位于正式 MOD-006/007/005 RTL 实现之前。

### 平台 4：从仿真到真实 FPGA 与外部内存

| Lesson | 第一次重点解释 | 工程映射 |
|---|---|---|
| LSN-013 仿真不是芯片 | synthesis、implementation、timing、bitstream | RMD-011A |
| LSN-014 什么是 FPGA 板 | FPGA、I/O、clock/reset、开发板 | RMD-012/012A |
| LSN-015 电脑怎样和 FPGA 说话 | host、CPU、SoC、programmable logic | RMD-012B/013 |
| LSN-016 为什么搬数据比加法更难 | memory hierarchy、latency、throughput、bandwidth | RMD-013A |
| LSN-017 外部内存是什么 | DDR、burst、random vs sequential access | RMD-014 |
| LSN-018 AXI 只学我们需要的部分 | Advanced eXtensible Interface (AXI)、transaction、valid/ready | RMD-014A/015/016 |

### 平台 4A：KV260 Physical Lab Track

概念课不再把“实体上板”只留在 Engineering Handoff。参考板卡冻结为 **AMD Kria KV260 Vision AI Starter Kit**，实体能力通过独立 `LAB-HW-*` 逐步建立。

详细规范：

- [KV260 参考硬件平台](KV260_REFERENCE_PLATFORM.md)
- [实体 FPGA 实验教学规范](PHYSICAL_FPGA_LABS.md)

| Physical Lab | 主要新操作 | 概念前置 | RMD |
|---|---|---|---|
| LAB-HW-00 | 识别 KV260 的电源、JTAG/UART、microSD、reset、I/O 与 carrier revision | LSN-014 | RMD-012 |
| LAB-HW-01 | 正确供电并让开发工具发现真实 target | LSN-014 | RMD-012 |
| LAB-HW-02 | synthesis → implementation → bitstream → program | LSN-013/014 | RMD-012A |
| LAB-HW-03 | clock/reset/I/O constraint 与实体输入输出 | LSN-014 | RMD-012A |
| LAB-HW-04 | KV260 PS/runtime host ↔ PL 的真实 loopback | LSN-015 | RMD-012B |
| LAB-HW-05 | 把抽象 neuron state RAM 映射到真实片上 BRAM resource | LSN-009/016 | RMD-013 |
| LAB-HW-06 | 小型 FlyBrain 网络上板并与 Python fixed reference replay 比较 | LSN-012~016 | RMD-013 |
| LAB-HW-07 | 真实 DDR write/read integrity + bandwidth measurement | LSN-016/017 | RMD-014 |
| LAB-HW-08 | 在真实平台比较 small/scattered 与 burst-oriented transfer | LSN-018 | RMD-014A |

Physical Lab 必须同时满足：

- 一次只引入一个主要实体操作；
- 明确桌面硬件、线缆和供电；
- 把 Build / Program / Run 分开；
- 给出 Expected Evidence，而不是“没有报错”；
- 提供 power → cable/JTAG → toolchain → constraints → programming → runtime → core 的 troubleshooting 顺序；
- 记录 board revision、tool version、Git commit、artifact hash 与实验结果；
- 实验需要真实 KV260 时，不允许普通 CI 假装完成板上验证。

### 平台 5：真实连接组与完整系统

| 计划 Lesson | 第一次重点解释 | 工程映射 |
|---|---|---|
| LSN-019 什么是 connectome | connectome、neuron ID、edge、metadata | RMD-017 |
| LSN-020 装入真实 MaleCNS 子图之前：先验证 network image | manifest、checksum、provenance、differential test；teaching fixture 不冒充正式 artifact | RMD-017/018 |
| LSN-021 规模变大以后发生什么 | bottleneck、utilization、hotspot | RMD-019~022 |
| LSN-022 给果蝇一个世界 | sensory encoder、decoder、closed loop | RMD-023~025 |
| LSN-023 三种机器做同一个实验 | CPU、GPU、FPGA、latency/throughput/power | RMD-028 |

---

## 7. Notebook 与正式代码的关系

允许 Notebook：
- 完整教学叙事；
- 小规模演示代码；
- 参数扫描；
- 图表、波形和可视化；
- AI prompt / critique；
- 实验控制和 benchmark 分析。

不允许 Notebook 长期成为：
- `lif_float` 的唯一实现；
- RTL 模块唯一存放位置；
- test oracle 唯一来源；
- 接口/数值规范唯一说明。

成熟后：

```text
Notebook prototype
      ↓
formal source module
      ↓
unit test / oracle
      ↓
Notebook imports formal module for teaching and experiments
```

---

## 8. 双语维护规则

- 中英文 lesson 使用相同 `LSN-*`、`RMD-*`、`FR/DP`、`T-*` ID。
- 代码 cell 尽量完全相同；翻译叙事和问题，不改变工程语义。
- 缩写的 full name 在两种语言中必须一致。
- 修改课程结构时，中英文 `LEARNING_PATH.md` 和对应 Notebook 在同一变更中同步。

## 9. 当前教学状态

- Learning Architecture：已定义并完成首次教学审计。
- LSN-001~004：进入“教材化”修订，要求术语首次展开、工程 ID 后置、叙事先于代码。
- LSN-005~008：第二组双语 Notebook 已建立；教学 RTL 放在 `rtl/learning/`，不替代正式 `MOD-003`。
- LSN-009~012：第三组双语 Notebook 已建立；先用小规模 Python event-machine 实验讲清 time multiplexing、FIFO/backpressure、sparse lookup 与 event-driven causal chain，不宣称 MOD-004~009 已完成。
- LSN-013~018：第四组双语 Notebook 已建立；正式作业仍可无板完成，但 **KV260 Physical Lab Track 已在文档层冻结为正式学习路径**，不再把实体 FPGA/DDR 实验仅作为可选“工程延伸”。
- LSN-019~023：第五组双语 Notebook 与独立作业已建立；connectome teaching fixture、synthetic scaling/benchmark 数字与 toy closed loop 只教学 contract，不冒充 RMD-017~028 的正式 MaleCNS artifact、全系统结果或真实性能 measurement。
- KV260 reference board 与 `LAB-HW-00~08` 的教学/验收规范已完成 documentation-first 决策；对应 Lab Notebook、board-specific RTL/constraints/scripts 尚未实现。
- 第一项正式工程实现仍为 `RMD-001`，尚未声明完成。
