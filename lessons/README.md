# Executable Lessons / 可执行课程

These Jupyter Notebooks are the **student-facing textbook and laboratory layer** of FPGA FlyBrain. They combine full teaching narrative, runnable experiments, AI-assisted tasks, human checks, and engineering handoffs.

这些 Jupyter Notebook 是 FPGA FlyBrain 的**学生教材与实验界面**。Notebook 里的 Markdown 不是代码之间的说明碎片，而是正式教材正文；代码、图表和实验是教材的一部分。

> Notebooks are not the engineering source of truth. Mature implementations move into `python/`, `rtl/`, `tb/`, or `tests/`, and the Notebook later imports/calls those formal modules.
>
> Notebook 不是正式工程实现的唯一事实来源。成熟实现应进入 `python/`、`rtl/`、`tb/` 或 `tests/`，Notebook 后续调用这些正式模块。

## Teaching standard / 教学写作标准

Every lesson should obey these rules / 每课遵守以下规则：

1. **First-use expansion / 首次出现展开**  
   Never assume abbreviations are known. Write the full name before using `FPGA`, `LIF`, `RTL`, `FIFO`, `DDR`, `AXI`, etc.  
   不默认学生认识缩写。第一次出现 `FPGA`、`LIF`、`RTL`、`FIFO`、`DDR`、`AXI` 等时，必须先写中英文全称并用白话解释。

2. **One primary new concept / 一课一个主要新概念**  
   Supporting vocabulary may appear, but it must be explained and must not silently become another major learning objective.

3. **Why → intuition → definition → experiment / 为什么 → 直觉 → 定义 → 实验**  
   A new term should not first appear inside code.

4. **Project IDs go last / 工程 ID 后置**  
   `FR/DP/RMD/T/PFR/PDP` are traceability metadata, not beginner vocabulary. Put them in a `Project Trace` section near the end of the Notebook.

5. **Predict before running / 先预测再运行**  
   Experiments should ask the learner to make a prediction before changing parameters or executing a test.

6. **AI helps implementation, not ownership / AI 帮实现，不替代理解**  
   Each `AI Task` should be followed by a `Human Check` that the learner must be able to answer independently.

7. **Standalone readability / 单课可独立阅读**  
   Briefly remind the reader what a previously introduced abbreviation means when it first appears in a new Notebook.

8. **Do not teach by technical inaccuracy / 不用技术错误换取“好懂”**  
   Simplification is encouraged, but a simplified explanation must remain technically defensible.

9. **Declarative diagrams over ASCII / 用字符描述流程图而非 ASCII 字符画**  
   All conceptual diagrams, state machines, timing flows, and hardware block diagrams must be written using declarative diagram code (primarily Mermaid fenced code blocks: ```` ```mermaid ````). Do not draw diagrams with spaces, hyphens, and ASCII art. Mermaid renders natively as clean vector graphics in JupyterLab and GitHub, is accessible, and keeps structural revisions clear in Git diffs.  
   所有概念流程、状态机流转、时序因果与硬件模块图，一律使用字符声明式语法（以 Mermaid 代码块 ```` ```mermaid ```` 为主）进行结构化描述，禁止使用空格、连字符和文本折线拼凑 ASCII 字符画。字符描述图在 JupyterLab 与 GitHub 中可原生渲染为矢量图，支持精准的版本差异追踪，且便于长期维护。

10. **Executable homework contracts / 可执行作业契约**  
    For suitable programming exercises, provide a fixed function signature, a small TODO region, public pytest checks, and a Human Check. Automated checks verify executable behavior; Human Checks verify that the learner can explain why the behavior is correct. Homework checks use explicit `check_lessonXX.py` files so unfinished student work does not pollute normal project tests.  
    对适合编程判定的作业，提供固定函数签名、小范围 TODO、公开 pytest 检查与 Human Check。自动检查负责验证可执行行为，Human Check 负责确认学生能解释规则为什么成立。学生作业检查使用显式 `check_lessonXX.py`，避免未完成作业污染项目常规测试。

Reference / 备查：
- [中文 Learning Path](../docs/zh/LEARNING_PATH.md)
- [English Learning Path](../docs/en/LEARNING_PATH.md)
- [中文术语表](../docs/zh/GLOSSARY.md)
- [English Glossary](../docs/en/GLOSSARY.md)
- [中文作业与检查说明](../exercises/README.zh-CN.md)
- [English exercise and checking guide](../exercises/README.md)

## First learning block / 第一组课程

| ID | 中文 | English | Homework / 作业 | Primary concept / 主要概念 | Engineering slice |
|---|---|---|---|---|---|
| LSN-001 | [从膜电位到一个最小计算神经元](zh/01_membrane_to_lif.ipynb) | [From membrane potential to a minimal computational neuron](en/01_membrane_to_lif.ipynb) | [中文检查说明](zh/01_membrane_to_lif_homework.md) / [English](en/01_membrane_to_lif_homework.md) | 模型是有目的的简化 / purposeful modeling; LIF | RMD-001 |
| LSN-002 | [数字硬件怎样保存 0.22？](zh/02_float_to_fixed.ipynb) | [How does digital hardware store 0.22?](en/02_float_to_fixed.ipynb) | `exercises/lesson02_fixed_point.py` | finite-width numbers | RMD-002 |
| LSN-003 | [“都叫 LIF”为什么还不够？](zh/03_freeze_neuron_semantics.ipynb) | [Why is “we both use LIF” not enough?](en/03_freeze_neuron_semantics.ipynb) | `exercises/lesson03_semantics.py` | specification & semantics | RMD-003 |
| LSN-004 | [电路怎样记住上一时刻的膜电位？](zh/04_state_and_clock.ipynb) | [How can a circuit remember the previous membrane potential?](en/04_state_and_clock.ipynb) | `exercises/lesson04_state_clock.py` | digital state & clock | RMD-003A |

## Planned next learning block / 下一组课程规划

The next lessons are intentionally smaller than a traditional “intro to HDL” jump / 下一组继续小步前进：

- `LSN-005` — digital logic building blocks / 数字逻辑积木：bit、Boolean logic、AND/OR/NOT、comparator
- `LSN-006` — what is Register-Transfer Level (RTL)? / 什么是寄存器传输级：HDL、SystemVerilog、module/port
- `LSN-007` — first RTL neuron / 第一个 RTL 神经元
- `LSN-008` — testbench, waveform, and simulation / 测试平台、波形与仿真

This sequencing follows the project's **Learning Independence Axiom**: do not require a beginner to learn clocks, SystemVerilog syntax, RTL semantics, and neuron hardware all at once.
