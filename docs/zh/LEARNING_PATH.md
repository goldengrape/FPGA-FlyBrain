# LEARNING_PATH — 教学路径 / Learning Architecture

## 0. 目的

`RMD.md` 回答“系统按什么顺序实现”；本文件回答“学生按什么概念顺序学习”。两者并行，但不互相取代。

教学界面采用三层结构：

```text
LEARNING_PATH.md
    ↓ 定义概念顺序与学习目标
Jupyter Notebook lessons
    ↓ 解释 + 实验 + AI 协作 + 人类检查
正式工程文件（python/ rtl/ tb/ tests/）
    ↓ 可测试、可复用、可进入 CI 的实现
```

**核心边界：Notebook 是可执行教材和实验台，不是正式实现的事实来源。** 正式算法、RTL、测试与接口最终必须落到普通源码文件中。

## 1. 教学设计原则

### LP-1 一个 lesson 只引入一个主要陌生概念
遵守 ADD 中的 `Learning Independence Axiom`。如果一个 lesson 需要同时理解两个以上尚未掌握的新概念，就拆分或插入 bridge lesson。

### LP-2 从学生已有知识出发
优先采用：

```text
已知神经生理 → 数学抽象 → 可执行实验 → 硬件概念 → 正式工程实现
```

而不是先系统讲完数字电路、HDL 或计算机体系结构。

### LP-3 AI 降低实现摩擦，但不能替代模型所有权
Notebook 可以明确给出 `AI Task`，让 AI 协助生成样板代码、测试或解释；随后必须有 `Human Check`，要求学习者解释状态、输入、输出、时序和测试 oracle。

### LP-4 每课必须产生可观察结果
至少出现一种：数值轨迹、波形、事件序列、资源报告、带宽测量、板上输出或可视化。

### LP-5 每课必须有工程交接点
Notebook 中成熟的实现必须移入正式源码路径。Notebook 应 import/调用正式模块，而不是长期复制一份实现。

## 2. 每个 Notebook 的固定结构

1. **你已经知道什么** — 从生理学/数学直觉出发。
2. **本课问题** — 一个具体问题。
3. **一个新概念** — 本课唯一主要陌生概念。
4. **最小模型** — 用最少数学或硬件抽象表达。
5. **Run** — 可执行实验。
6. **Observe** — 要观察的轨迹、波形或事件。
7. **AI Task** — 可以交给 AI 的实现工作。
8. **Human Check** — 不依赖 AI 必须回答的问题。
9. **Engineering Handoff** — 对应正式源码、测试和 RMD slice。
10. **Exit Ticket** — 通过后才能进入下一课的标准。

## 3. 第一组课程：从膜电位到数字状态

| Lesson | Notebook | 主要新概念 | RMD | 工程输出 |
|---|---|---|---|---|
| LSN-001 | `lessons/zh/01_membrane_to_lif.ipynb` | 模型是有目的的简化 | RMD-001 | `python/reference/lif_float.py` |
| LSN-002 | `lessons/zh/02_float_to_fixed.ipynb` | 有限位宽数值表示 | RMD-002 | `python/reference/lif_fixed.py` + 数值决策 |
| LSN-003 | `lessons/zh/03_freeze_neuron_semantics.ipynb` | 先冻结语义，再实现硬件 | RMD-003 | MDD/TDD/TRACE spec checkpoint |
| LSN-004 | `lessons/zh/04_state_and_clock.ipynb` | 数字状态与时钟 | RMD-003A | 3 个微型硬件实验的准备与解释 |

### LSN-001 — 从膜电位到 LIF
起点：知道膜电位、阈值、动作电位、不应期。  
问题：为了研究网络计算，我们最少保留哪些神经元性质？  
完成标志：能解释 `V`、输入、threshold、spike、reset 的生理与计算含义，并运行确定性的 LIF 轨迹。

### LSN-002 — 从浮点数到有限位宽
起点：已经有可运行的 LIF。  
问题：真实数字硬件为什么不能默认把 `V` 当作无限精度实数？  
完成标志：能解释 scale、quantization、rounding、saturation，并比较至少两种位宽选择对 spike timing 的影响。

### LSN-003 — 冻结神经元语义
起点：float 和 fixed-point 行为都已观察。  
问题：如果 AI、Python 和 RTL 各自“理解”不同的 LIF，谁才是对的？  
完成标志：明确一次 update 的输入、状态、输出、更新顺序、threshold/reset/refractory 规则和数值语义；写入工程规范后再进入 RTL。

### LSN-004 — 状态与时钟
起点：知道软件变量会保存值，但尚未学 RTL。  
问题：电路怎样“记住”上一时刻的膜电位？  
完成标志：能解释 combinational 与 sequential、register 与 clock edge，并把 `variable → register`、`if → comparator/control`、`loop → parallel/time-multiplex` 对应起来。

## 4. 后续课程平台

### 平台 2：数字神经元
目标：从 clock/register 过渡到 SystemVerilog、testbench 和 waveform；对应 RMD-004~005A。

### 平台 3：事件神经网络
目标：RAM、time multiplexing、4-neuron event walk-through、sparse adjacency、FIFO、event routing；对应 RMD-006~011。

### 平台 4：真实 FPGA 与内存
目标：synthesis、bitstream、host↔FPGA、memory hierarchy、DDR、AXI subset、bandwidth；对应 RMD-011A~016。

### 平台 5：真实连接组
目标：MaleCNS converter、真实子图、规模扩展、完整网络、闭环与 benchmark；对应 RMD-017~028。

## 5. Notebook 与正式代码的关系

允许 Notebook：
- 小规模演示代码；
- 参数扫描；
- 图表与波形展示；
- AI prompt / critique；
- 实验控制和 benchmark 分析。

不允许 Notebook 长期成为：
- `lif_float` 的唯一实现；
- RTL 模块的唯一存放位置；
- test oracle 的唯一来源；
- 接口/数值规范的唯一说明。

当一个实验成熟后：

```text
Notebook prototype
      ↓
formal source module
      ↓
unit test / oracle
      ↓
Notebook imports formal module for demonstration
```

## 6. 双语维护规则

- 中英文 lesson 使用相同 `LSN-*`、`RMD-*`、`FR/DP`、`T-*` ID。
- 代码 cell 尽量完全相同；只翻译叙事和问题。
- 修改课程结构时，中英文 `LEARNING_PATH.md` 和对应 Notebook 必须在同一变更中同步。

## 7. 当前教学状态

- Learning Architecture：已定义。
- LSN-001~004：建立第一版可执行 Notebook。
- 第一项正式工程实现：仍为 `RMD-001`，尚未声明完成。
