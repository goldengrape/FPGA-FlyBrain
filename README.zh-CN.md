# FPGA 果蝇 / FPGA FlyBrain

[English](README.md)

**从膜电位到硅：** 一个面向生命科学学生的学习与工程项目，目标是逐步构建一套运行在 FPGA 上、由真实果蝇 MaleCNS 连接组约束的事件驱动脉冲神经系统。

本仓库采用中英文双语维护。`FR1`、`DP4`、`MOD-007`、`T-010`、`RMD-013A` 等工程 ID 在两种语言中完全一致，使需求、设计、实现、教学和测试可以长期追踪。

## 北极星目标

从一个可以理解和验证的神经元模型开始，逐步构建一套可验证的 FPGA 系统，最终能够加载并运行来自 MaleCNS 连接组的脉冲神经网络；电脑负责感觉输入、输出解码、可视化和实验控制。

本项目**不**声称复制完整的生物学果蝇脑，也不涉及意识上传。它是一个由连接组约束的计算模型，同时也是生命科学学生进入 AI hardware / neuromorphic computing 的学习载体。

## 教学原则

课程面向这样一类学习者：可能学过基础神经生理，但**不默认知道 FPGA、LIF、RTL、FIFO、DDR、AXI 是什么**。

统一教学顺序是：

> 为什么会遇到这个问题 → 建立直觉 → 准确定义术语 → 运行实验 → 观察 → 回到定义解释结果

Jupyter Notebook 被当作真正的教材章节，而不是代码外面包几句说明。缩写第一次出现必须展开；工程追踪 ID 放在课末；每一课只承担一个主要陌生概念。

## 方法

项目结合：

- 神经生理学 → 数学模型 → 数字硬件的三层翻译；
- AI-assisted / vibe coding，但需求、模型、架构和 test oracle 由人负责；
- MIT 公理设计思想：`FR`/`DP`、耦合分析、下三角可解耦设计；
- 用 **Learning Independence Axiom** 约束课程设计；
- 分层验证：Python float → Python fixed-point → RTL simulation → FPGA replay；
- Git checkpoint 和端到端 TRACE。

## 快速开始：本地运行环境

本项目使用 [uv](https://github.com/astral-sh/uv) 统一管理 Python 依赖、虚拟环境与 Jupyter 运行流程。克隆仓库后，无需手动建立 Conda 环境或逐个执行 `pip install`。

### 1. 同步依赖

```bash
git clone https://github.com/goldengrape/FPGA-FlyBrain
cd FPGA-FlyBrain
uv sync
```

该命令会依据 `uv.lock` 自动在 `.venv` 中安装运行所需的全部依赖库（包括课程代码所需的 `numpy`、`matplotlib` 以及实验界面所需的 `jupyterlab`、`ipykernel`、`pytest`）。

### 2. 启动课程界面

```bash
uv run jupyter lab
```

### 3. 注册课程专属内核（推荐）

为了避免在 Jupyter 中混淆不同环境的 Python 内核，建议注册一个显式内核：

```bash
uv run ipython kernel install --user --name fpga-flybrain --display-name "FPGA FlyBrain"
```

注册后，在 JupyterLab 打开 Notebook 时，内核选择 **FPGA FlyBrain** 即可。

### 4. 依赖管理原则

- **禁止在 Notebook 中临时安装**：不要在 Notebook 单元格中使用 `%pip install` 或 `!pip install`，以免破坏环境的可复现性。
- **声明式增补依赖**：如果后续需要新增科学计算库，请在命令行执行 `uv add <package>`；若需要开发或测试工具，执行 `uv add --dev <package>`。版本变动会记录在 `pyproject.toml` 与 `uv.lock` 中。

## 从这里开始学

第一组可执行课程位于 [`lessons/`](lessons/README.md)：

1. [从膜电位到一个最小计算神经元](lessons/zh/01_membrane_to_lif.ipynb)
2. [数字硬件怎样保存 0.22？](lessons/zh/02_float_to_fixed.ipynb)
3. [“都叫 LIF”为什么还不够？](lessons/zh/03_freeze_neuron_semantics.ipynb)
4. [电路怎样记住上一时刻的膜电位？](lessons/zh/04_state_and_clock.ipynb)

### NotebookLM 公开课程笔记本

如果更适合通过听讲、问答和快速复习来学习，也可以使用项目的公开 NotebookLM：

[打开 FPGA FlyBrain NotebookLM](https://notebook.google.com/notebook/ad55b316-1d40-40e6-b2fa-2beef29a5b56)

其中会基于课程资料生成各课的音频讲解等学习内容，也可以围绕课程内容直接提问。GitHub 仓库仍然是 Notebook、代码、作业、测试与工程文档的主要来源；NotebookLM 作为讲解与交互式学习入口与之配合使用。

## 文档

### 面向读者的指南
| 中文 | English |
|---|---|
| [项目创作圣经](docs/zh/PROJECT_BIBLE.md) | [Project Bible](docs/en/PROJECT_BIBLE.md) |
| [高层学习路线](docs/zh/ROADMAP.md) | [High-level Roadmap](docs/en/ROADMAP.md) |
| [教学路径](docs/zh/LEARNING_PATH.md) | [Learning Architecture](docs/en/LEARNING_PATH.md) |
| [初学者术语表](docs/zh/GLOSSARY.md) | [Beginner Glossary](docs/en/GLOSSARY.md) |

### 工程事实文档
| 中文 | English |
|---|---|
| [项目需求 / URD](docs/zh/URD.md) | [Idea Brief / URD](docs/en/URD.md) |
| [公理设计 / ADD](docs/zh/ADD.md) | [Axiomatic Design / ADD](docs/en/ADD.md) |
| [模块设计 / MDD](docs/zh/MDD.md) | [Building Blocks / MDD](docs/en/MDD.md) |
| [测试验证 / TDD](docs/zh/TDD.md) | [Check Plan / TDD](docs/en/TDD.md) |
| [实施路线 / RMD](docs/zh/RMD.md) | [Build Path / RMD](docs/en/RMD.md) |
| [追踪矩阵 / TRACE](docs/zh/TRACE.md) | [Project Map / TRACE](docs/en/TRACE.md) |

`URD/ADD/MDD/TDD/RMD/TRACE` 是工程事实来源；创作圣经、高层路线、教学路径、术语表和 Notebook 负责帮助人理解和学习项目，但不替代这些规范。

## 当前状态

项目规划、系统架构和第一次课程审计已经完成；第一段正式工程实现尚未声明完成。

当前工程顺序：

1. `RMD-001` — Python LIF 浮点参考模型
2. `RMD-002` — fixed-point 探索
3. `RMD-003` — 冻结 v0 神经元语义
4. `RMD-003A` — Digital Hardware Bridge

在早期仿真与概念验证通过之前，暂不购买 FPGA 硬件。
