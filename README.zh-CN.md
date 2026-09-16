# FPGA 果蝇 / FPGA FlyBrain

[English](README.md)

**从膜电位到硅：** 一个面向生命科学学生的学习与工程项目，目标是逐步构建一套运行在 FPGA 上、由真实果蝇 MaleCNS 连接组约束的事件驱动脉冲神经系统。

本仓库采用中英文双语维护。`FR1`、`DP4`、`MOD-007`、`T-010`、`RMD-013A`、`LSN-004` 等工程与教学 ID 在两种语言中保持一致，使需求、设计、实现、测试和课程可以长期追踪。

## 北极星目标

从一个可以理解和验证的 LIF 神经元开始，逐步构建一套可验证的 FPGA 系统，最终能够加载并运行来自 MaleCNS 连接组的脉冲神经网络；电脑负责感觉输入、输出解码、可视化和实验控制。

本项目**不**声称复制完整的生物学果蝇脑，也不涉及意识上传。它是一个由连接组约束的计算模型，同时也是生命科学学生进入 AI hardware / neuromorphic computing 的学习载体。

## 方法

项目结合：

- 神经生理学 → 数学模型 → 数字硬件的三层翻译；
- AI-assisted / vibe coding，但需求、模型、架构和 test oracle 由人负责；
- MIT 公理设计思想：`FR`/`DP`、耦合分析、下三角可解耦设计；
- Learning Independence Axiom：每个学习 slice 只引入一个主要陌生概念；
- 分层验证：Python float → Python fixed-point → RTL simulation → FPGA replay；
- Git checkpoint 和端到端 TRACE。

## 文档

### 面向读者的指南
| 中文 | English |
|---|---|
| [项目创作圣经](docs/zh/PROJECT_BIBLE.md) | [Project Bible](docs/en/PROJECT_BIBLE.md) |
| [高层学习路线](docs/zh/ROADMAP.md) | [High-level Roadmap](docs/en/ROADMAP.md) |
| [教学路径 / Learning Architecture](docs/zh/LEARNING_PATH.md) | [Learning Architecture](docs/en/LEARNING_PATH.md) |

### 工程事实文档
| 中文 | English |
|---|---|
| [项目需求 / URD](docs/zh/URD.md) | [Idea Brief / URD](docs/en/URD.md) |
| [公理设计 / ADD](docs/zh/ADD.md) | [Axiomatic Design / ADD](docs/en/ADD.md) |
| [模块设计 / MDD](docs/zh/MDD.md) | [Building Blocks / MDD](docs/en/MDD.md) |
| [测试验证 / TDD](docs/zh/TDD.md) | [Check Plan / TDD](docs/en/TDD.md) |
| [实施路线 / RMD](docs/zh/RMD.md) | [Build Path / RMD](docs/en/RMD.md) |
| [追踪矩阵 / TRACE](docs/zh/TRACE.md) | [Project Map / TRACE](docs/en/TRACE.md) |

`URD/ADD/MDD/TDD/RMD/TRACE` 是工程事实来源；创作圣经、高层路线、教学路径与 Notebook 负责帮助人学习和理解项目，但不替代这些规范。

## 可执行课程

Notebook 层把叙事、可运行实验、AI 协作任务、人类理解检查和正式工程交接放在一起。

1. [LSN-001 — 从膜电位到 LIF](lessons/zh/01_membrane_to_lif.ipynb)
2. [LSN-002 — 从浮点数到有限位宽](lessons/zh/02_float_to_fixed.ipynb)
3. [LSN-003 — 冻结神经元语义](lessons/zh/03_freeze_neuron_semantics.ipynb)
4. [LSN-004 — 状态与时钟](lessons/zh/04_state_and_clock.ipynb)

参见[双语课程索引](lessons/README.md)。

## 当前状态

规划、体系结构和第一组教学内容已经初始化。前四个中英文可执行课程已经分别映射到：

1. `RMD-001` — Python LIF 浮点参考模型
2. `RMD-002` — fixed-point 探索
3. `RMD-003` — 冻结 v0 神经元语义
4. `RMD-003A` — Digital Hardware Bridge

**正式工程实现**的 RMD-001 仍未宣告完成。在早期仿真与概念验证通过之前，暂不购买 FPGA 硬件。
