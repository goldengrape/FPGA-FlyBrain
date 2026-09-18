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

10. **Exercise Notebooks + external graders / 作业 Notebook + 外部 grader**  
    Suitable programming exercises live in a separate Exercise Notebook with a fixed function signature, a small TODO region, an external grader call, and a Human Check. Student-facing notebooks do not directly display grading asserts or concrete grader vectors.  
    适合编程判定的作业使用独立 Exercise Notebook：固定函数签名、小范围 TODO、外部 grader 检查和 Human Check。学生可见 Notebook 不直接展示判题 assert 或具体测试向量。

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
| LSN-001 | [从膜电位到一个最小计算神经元](zh/01_membrane_to_lif.ipynb) | [From membrane potential to a minimal computational neuron](en/01_membrane_to_lif.ipynb) | [中文](../exercises/zh/01_membrane_to_lif.ipynb) / [English](../exercises/en/01_membrane_to_lif.ipynb) | 模型是有目的的简化 / purposeful modeling; LIF | RMD-001 |
| LSN-002 | [数字硬件怎样保存 0.22？](zh/02_float_to_fixed.ipynb) | [How does digital hardware store 0.22?](en/02_float_to_fixed.ipynb) | [中文](../exercises/zh/02_float_to_fixed.ipynb) / [English](../exercises/en/02_float_to_fixed.ipynb) | finite-width numbers | RMD-002 |
| LSN-003 | [“都叫 LIF”为什么还不够？](zh/03_freeze_neuron_semantics.ipynb) | [Why is “we both use LIF” not enough?](en/03_freeze_neuron_semantics.ipynb) | [中文](../exercises/zh/03_freeze_neuron_semantics.ipynb) / [English](../exercises/en/03_freeze_neuron_semantics.ipynb) | specification & semantics | RMD-003 |
| LSN-004 | [电路怎样记住上一时刻的膜电位？](zh/04_state_and_clock.ipynb) | [How can a circuit remember the previous membrane potential?](en/04_state_and_clock.ipynb) | [中文](../exercises/zh/04_state_and_clock.ipynb) / [English](../exercises/en/04_state_and_clock.ipynb) | digital state & clock | RMD-003A |

## Second learning block / 第二组课程

| ID | 中文 | English | Practice / 检查 | Primary concept / 主要概念 | Engineering mapping |
|---|---|---|---|---|---|
| LSN-005 | [数字逻辑积木](zh/05_logic_building_blocks.ipynb) | [Digital logic building blocks](en/05_logic_building_blocks.ipynb) | [中文](../exercises/zh/05_logic_building_blocks.ipynb) / [English](../exercises/en/05_logic_building_blocks.ipynb) | Boolean logic | RMD-003A |
| LSN-006 | [什么是 RTL？](zh/06_what_is_rtl.ipynb) | [What is RTL?](en/06_what_is_rtl.ipynb) | compile-only RTL check + state walkthrough | RTL / HDL / module / port | prepares RMD-004 |
| LSN-007 | [第一个 RTL 神经元](zh/07_first_rtl_neuron.ipynb) | [The first RTL neuron](en/07_first_rtl_neuron.ipynb) | Python oracle + RTL review | combinational + sequential | RMD-004 teaching precursor |
| LSN-008 | [我们怎么知道硬件是对的？](zh/08_testbench_waveform_simulation.ipynb) | [How do we know hardware is correct?](en/08_testbench_waveform_simulation.ipynb) | self-checking testbench + persistent VCD waveform | simulation/testbench | RMD-005/005A |

`rtl/learning/` and `tb/learning/` are teaching artifacts. They do **not** declare formal `MOD-003 lif_neuron_engine` complete.

This sequencing follows the **Learning Independence Axiom**: clocks, Boolean logic, HDL syntax, RTL structure, and verification are introduced separately.



## Third learning block / 第三组课程

| ID | 中文 | English | Practice / 检查 | Primary concept / 主要概念 | Engineering mapping |
|---|---|---|---|---|---|
| LSN-009 | [一个计算单元服务很多神经元](zh/09_time_multiplex_many_neurons.ipynb) | [One compute unit serves many neurons](en/09_time_multiplex_many_neurons.ipynb) | [中文](../exercises/zh/09_time_multiplex_many_neurons.ipynb) / [English](../exercises/en/09_time_multiplex_many_neurons.ipynb) | time multiplexing | RMD-006/007 precursor |
| LSN-010 | [spike 为什么需要排队](zh/10_spike_fifo_backpressure.ipynb) | [Why spikes need a queue](en/10_spike_fifo_backpressure.ipynb) | [中文](../exercises/zh/10_spike_fifo_backpressure.ipynb) / [English](../exercises/en/10_spike_fifo_backpressure.ipynb) | bounded FIFO + backpressure | RMD-007A/009 precursor |
| LSN-011 | [不要扫描所有突触](zh/11_sparse_synapse_lookup.ipynb) | [Do not scan every synapse](en/11_sparse_synapse_lookup.ipynb) | [中文](../exercises/zh/11_sparse_synapse_lookup.ipynb) / [English](../exercises/en/11_sparse_synapse_lookup.ipynb) | sparse adjacency / CSR-like indexing | RMD-008 |
| LSN-012 | [一个 spike 的完整旅程](zh/12_one_spike_journey.ipynb) | [The complete journey of one spike](en/12_one_spike_journey.ipynb) | [中文](../exercises/zh/12_one_spike_journey.ipynb) / [English](../exercises/en/12_one_spike_journey.ipynb) | event-driven causal chain | RMD-007A/010/011 |

These lessons use small Python models to teach architecture semantics before formalizing `MOD-004~009` in RTL. They align dataflow and test intent with MDD/TDD without declaring those formal modules complete.

这四课先用小规模 Python 模型讲清架构语义，再进入 `MOD-004~009` 的正式 RTL。课程会对齐 MDD/TDD 中的数据流与测试意图，但不宣称这些正式模块已经完成。

## RTL learning checks / RTL 教学检查

After installing an HDL toolchain that provides Icarus Verilog, Verilator, and Yosys, run the complete teaching-RTL check with:

```bash
./scripts/check_rtl_learning.sh
```

安装包含 Icarus Verilog、Verilator 与 Yosys 的 HDL 工具链后，可以用一条命令检查当前教学 RTL：

```bash
./scripts/check_rtl_learning.sh
```

The script checks / 脚本会执行：

1. Lesson 6 Icarus compile + self-checking simulation；
2. Lesson 6 Verilator lint；
3. Lesson 6 Yosys synthesis sanity check；
4. Lesson 8 Icarus compile + self-checking simulation；
5. Lesson 8 VCD waveform existence/non-empty check；
6. Lesson 8 Verilator lint；
7. Lesson 8 Yosys synthesis sanity check。

Build artifacts are written under `build/rtl-learning/` and are ignored by Git.
