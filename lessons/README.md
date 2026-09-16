# Executable Lessons / 可执行课程

These Jupyter Notebooks are the **student-facing laboratory and textbook layer** of FPGA FlyBrain. They combine explanation, runnable experiments, AI-assisted tasks, human checks, and engineering handoffs.

这些 Jupyter Notebook 是 FPGA FlyBrain 的**学生学习与实验界面**：把讲解、可运行实验、AI 协作任务、人类理解检查和工程交接放在同一个地方。

> Notebooks are not the engineering source of truth. Mature implementations move into `python/`, `rtl/`, `tb/`, or `tests/`, and the Notebook should later import/call those formal modules.
>
> Notebook 不是正式工程实现的事实来源。成熟实现应进入 `python/`、`rtl/`、`tb/` 或 `tests/`，Notebook 后续调用这些正式模块。

## First learning block / 第一组课程

| ID | 中文 | English | Engineering slice |
|---|---|---|---|
| LSN-001 | [从膜电位到 LIF](zh/01_membrane_to_lif.ipynb) | [From Membrane Potential to LIF](en/01_membrane_to_lif.ipynb) | RMD-001 |
| LSN-002 | [从浮点数到有限位宽](zh/02_float_to_fixed.ipynb) | [From Floating Point to Finite Width](en/02_float_to_fixed.ipynb) | RMD-002 |
| LSN-003 | [冻结神经元语义](zh/03_freeze_neuron_semantics.ipynb) | [Freeze Neuron Semantics](en/03_freeze_neuron_semantics.ipynb) | RMD-003 |
| LSN-004 | [状态与时钟](zh/04_state_and_clock.ipynb) | [State and Clock](en/04_state_and_clock.ipynb) | RMD-003A |

See / 参见:
- [中文 Learning Path](../docs/zh/LEARNING_PATH.md)
- [English Learning Path](../docs/en/LEARNING_PATH.md)
