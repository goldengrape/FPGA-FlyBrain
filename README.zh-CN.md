# FPGA 果蝇 / FPGA FlyBrain

[English](README.md)

**从膜电位到硅：** 一个面向生命科学学生的学习与工程项目，目标是逐步构建一套运行在 FPGA 上、由真实果蝇 MaleCNS 连接组约束的事件驱动脉冲神经系统。

本仓库采用中英文双语维护。`FR1`、`DP4`、`MOD-007`、`T-010`、`RMD-013A` 等工程 ID 在两种语言中完全一致，使需求、设计、实现和测试可以长期追踪。

## 北极星目标

从一个可以理解和验证的 LIF 神经元开始，逐步构建一套可验证的 FPGA 系统，最终能够加载并运行来自 MaleCNS 连接组的脉冲神经网络；电脑负责感觉输入、输出解码、可视化和实验控制。

本项目**不**声称复制完整的生物学果蝇脑，也不涉及意识上传。它是一个由连接组约束的计算模型，同时也是生命科学学生进入 AI hardware / neuromorphic computing 的学习载体。

## 方法

项目结合：

- 神经生理学 → 数学模型 → 数字硬件的三层翻译；
- AI-assisted / vibe coding，但需求、模型、架构和 test oracle 由人负责；
- MIT 公理设计思想：`FR`/`DP`、耦合分析、下三角可解耦设计；
- 分层验证：Python float → Python fixed-point → RTL simulation → FPGA replay；
- Git checkpoint 和端到端 TRACE。

## 文档

| 中文 | English |
|---|---|
| [项目需求 / URD](docs/zh/URD.md) | [Idea Brief / URD](docs/en/URD.md) |
| [公理设计 / ADD](docs/zh/ADD.md) | [Axiomatic Design / ADD](docs/en/ADD.md) |
| [模块设计 / MDD](docs/zh/MDD.md) | [Building Blocks / MDD](docs/en/MDD.md) |
| [测试验证 / TDD](docs/zh/TDD.md) | [Check Plan / TDD](docs/en/TDD.md) |
| [实施路线 / RMD](docs/zh/RMD.md) | [Build Path / RMD](docs/en/RMD.md) |
| [追踪矩阵 / TRACE](docs/zh/TRACE.md) | [Project Map / TRACE](docs/en/TRACE.md) |

## 当前状态

规划和体系结构已初始化，第一段实际实现尚未开始。

当前第一批任务：

1. `RMD-001` — Python LIF 浮点参考模型
2. `RMD-002` — fixed-point 探索
3. `RMD-003` — 冻结 v0 神经元语义
4. `RMD-003A` — Digital Hardware Bridge

在早期仿真与概念验证通过之前，暂不购买 FPGA 硬件。
