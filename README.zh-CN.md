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

### 2. 建立个人作业副本

不要直接在 Git 跟踪的 `exercises/zh/` 官方作业模板上写答案。先为当前课程建立一个不会被 Git 跟踪的个人副本：

```bash
uv run python scripts/start_exercise.py 01
```

它会创建：

```text
exercises/work/zh/01_membrane_to_lif.ipynb
```

`exercises/work/` 已加入 `.gitignore`，所以学生答案不会出现在普通 `git status` / commit 中，也不会和以后课程模板更新冲突。已有工作副本不会被脚本覆盖。

英文作业使用：

```bash
uv run python scripts/start_exercise.py 01 --lang en
```

一次建立全部当前 Python 作业：

```bash
uv run python scripts/start_exercise.py all
```

更完整的作业流程见 [作业册 README](exercises/README.zh-CN.md)。

### 3. 启动课程界面

```bash
uv run jupyter lab
```

做作业时打开 `exercises/work/zh/` 下的个人副本；`exercises/zh/` 是课程发布的官方 starter。

### 4. 注册课程专属内核（必须）

课程与作业 Notebook 的元数据指定了 `fpga-flybrain` 内核，因此第一次使用前需要先注册它。JupyterLab 在交互界面里有时可以通过手动选择其他内核恢复，但 `nbconvert --execute` 这类无交互执行会在缺少该内核时直接报 `NoSuchKernel`。

执行：

```bash
uv run ipython kernel install --user --name fpga-flybrain --display-name "FPGA FlyBrain"
```

注册后，在 JupyterLab 打开 Notebook 时，内核选择 **FPGA FlyBrain** 即可。

### 5. 依赖管理原则

- **禁止在 Notebook 中临时安装**：不要在 Notebook 单元格中使用 `%pip install` 或 `!pip install`，以免破坏环境的可复现性。
- **声明式增补依赖**：如果后续需要新增科学计算库，请在命令行执行 `uv add <package>`；若需要开发或测试工具，执行 `uv add --dev <package>`。版本变动会记录在 `pyproject.toml` 与 `uv.lock` 中。

### 6. 第六到八课与第十三课的 HDL 工具链

第一次配置请先看：[HDL 工具链安装与 Jupyter 启动](docs/zh/HDL_TOOLCHAIN_SETUP.md)。特别注意：激活 OSS CAD Suite 后，要从**同一个终端**启动 JupyterLab。

第 6–8 课使用 **SystemVerilog-2012** 做 RTL/仿真，第 13 课会直接调用 Yosys 做一次真实 synthesis dry run。Python 依赖继续由 `uv` 管理；HDL simulator 与 synthesis tool 是独立的系统工具，不属于 Python 包。

GitHub Actions 会从 Ubuntu runner 安装 Icarus Verilog、Verilator 与 Yosys，并在每次 CI 中打印实际版本。目前已经完整验证通过的一组基线是：

- Icarus Verilog 12.0
- Verilator 5.020
- Yosys 0.33

开发 VM 也已使用 OSS CAD Suite 2026-09-18 验证过（Icarus 14.0、Verilator 5.053、Yosys 0.69）。

较老的 Icarus 10.x **不作为本课程支持基线**。不要仅仅为了适配旧 simulator，把课程中的 `always_ff` / `always_comb` 降级成旧式 Verilog；更合适的做法是使用支持当前 SystemVerilog 的工具链。

本地完整检查：

```bash
./scripts/check_rtl_learning.sh
```

它会运行 Icarus self-checking simulation、Verilator lint、Yosys synthesis sanity check，并确认 Lesson 8 的 VCD 波形确实生成。第 13 课 Notebook 还会单独调用 Yosys 综合 `rtl/learning/clocked_accumulator.sv`，让学生直接阅读一次真实 synthesis 输出。

### 7. 实体 FPGA 参考板：AMD Kria KV260

实体上板教学已冻结 **AMD Kria KV260 Vision AI Starter Kit** 为第一套完整 reference board。概念课仍尽量板卡无关，但零基础 Physical Lab 会给出 KV260 的 vendor toolchain preflight、供电、JTAG/UART、target discovery、first bitstream、constraints/I/O、PS/Linux first boot、host↔PL、BRAM、DDR 与 AXI/burst 实操路径。

documentation-first 规范已经进入实现阶段。**LAB-HW-00~07** 已有中英文学生 Notebook 与 `boards/kv260/` support/runtime artifact；LAB-HW-07 已加入第一套真实 BRAM neuron-state 教学 store 与 multi-address runtime check。真实 KV260 T-HW evidence 与真实 Vivado LAB-HW-07 full-build dry run 仍待执行。

先看：

- [KV260 参考硬件平台](docs/zh/KV260_REFERENCE_PLATFORM.md)
- [实体 FPGA 实验教学规范](docs/zh/PHYSICAL_FPGA_LABS.md)
- [实体 FPGA Lab Notebook](labs/README.zh-CN.md)

注意：第 6–13 课的 OSS CAD Suite 与后续 KV260 的 AMD Vivado/platform toolchain 是两层不同工具链。

## 从这里开始学

当前可执行课程位于 [`lessons/`](lessons/README.md)：

1. [从膜电位到一个最小计算神经元](lessons/zh/01_membrane_to_lif.ipynb)
2. [数字硬件怎样保存 0.22？](lessons/zh/02_float_to_fixed.ipynb)
3. [“都叫 LIF”为什么还不够？](lessons/zh/03_freeze_neuron_semantics.ipynb)
4. [电路怎样记住上一时刻的膜电位？](lessons/zh/04_state_and_clock.ipynb)
5. [数字电路有哪些最基本的逻辑积木？](lessons/zh/05_logic_building_blocks.ipynb)
6. [什么是 RTL？](lessons/zh/06_what_is_rtl.ipynb)
7. [第一个 RTL 神经元](lessons/zh/07_first_rtl_neuron.ipynb)
8. [我们怎么知道硬件是对的？](lessons/zh/08_testbench_waveform_simulation.ipynb)
9. [一个计算单元怎样服务很多神经元？](lessons/zh/09_time_multiplex_many_neurons.ipynb)
10. [spike 为什么需要排队？](lessons/zh/10_spike_fifo_backpressure.ipynb)
11. [为什么不能每次 spike 都扫描所有突触？](lessons/zh/11_sparse_synapse_lookup.ipynb)
12. [一个 spike 的完整旅程](lessons/zh/12_one_spike_journey.ipynb)
13. [仿真不是芯片](lessons/zh/13_simulation_is_not_chip.ipynb)
14. [什么是 FPGA 板？](lessons/zh/14_what_is_fpga_board.ipynb)
15. [电脑怎样和 FPGA 说话？](lessons/zh/15_host_talks_to_fpga.ipynb)
16. [为什么搬数据比加法更难？](lessons/zh/16_data_movement_cost.ipynb)
17. [外部内存是什么？](lessons/zh/17_external_memory_ddr.ipynb)
18. [AXI 只学我们需要的部分](lessons/zh/18_axi_subset.ipynb)
19. [什么是 connectome？](lessons/zh/19_what_is_connectome.ipynb)
20. [装入真实 MaleCNS 子图之前：先验证 network image](lessons/zh/20_load_malecns_subset.ipynb)
21. [规模变大以后，瓶颈会跑到哪里？](lessons/zh/21_scaling_bottlenecks.ipynb)
22. [给果蝇一个世界：把 loop 闭合起来](lessons/zh/22_closed_loop_world.ipynb)
23. [三种机器做同一个实验](lessons/zh/23_cpu_gpu_fpga_benchmark.ipynb)

对应的独立作业册位于 [`exercises/`](exercises/README.zh-CN.md)。Python 作业使用 Jupyter Notebook，自动检查由外部 grader 执行；作业页面不直接展示判题 `assert` 或具体测试向量。

### NotebookLM 公开课程笔记本

如果更适合通过听讲、问答和快速复习来学习，也可以使用项目的公开 NotebookLM：

[打开 FPGA FlyBrain NotebookLM](https://notebook.google.com/notebook/ad55b316-1d40-40e6-b2fa-2beef29a5b56)

其中会基于课程资料生成各课的音频讲解等学习内容，也可以围绕课程内容直接提问。GitHub 仓库仍然是 Notebook、代码、作业、测试与工程文档的主要来源；NotebookLM 作为讲解与交互式学习入口与之配合使用。

## 参考资料

下面列出本项目目前直接依赖或会反复引用的基础资料。这里不是完整的 bibliography；随着课程推进，更具体的论文和资料会放到对应 Notebook 中。

### 果蝇连接组

- [Male CNS Connectome Project](https://male-cns.janelia.org/) — 本项目最终使用的完整雄性果蝇中枢神经系统连接组入口，可浏览细胞类型、查询连接并下载数据。
- [Berg et al., *Cell* (2026): *Sexual dimorphism in the complete Drosophila male central nervous system connectome*](https://doi.org/10.1016/j.cell.2026.08.015) — MaleCNS 数据集和分析的正式论文。
- [Schlegel et al., *Nature* (2024): *Whole-brain annotation and multi-connectome cell typing of Drosophila*](https://www.nature.com/articles/s41586-024-07686-5) — FlyWire 全脑注释、细胞类型和跨连接组比较的重要背景资料。

### 神经元模型与计算神经科学

- [Gerstner, Kistler, Naud & Paninski, *Neuronal Dynamics*](https://neuronaldynamics.epfl.ch/online/) — 从单神经元动力学到网络模型的开放在线教材；其中 [Integrate-and-Fire Models](https://neuronaldynamics.epfl.ch/online/Ch1.S3.html) 与第一课直接相关。

### FPGA 与数字设计

- [AMD FPGA Overview](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga.html) — FPGA 产品、架构与基础概念入口。
- [AMD FPGA Architecture](https://docs.amd.com/r/en-US/ug1291-viv/FPGA-Architecture) — 逻辑单元、可编程互连、I/O、时钟和片上资源等 FPGA 结构背景。

### 设计方法

- [MIT Axiomatic Design Introduction](https://web.mit.edu/axiom/www/introduction.shtml) — `FR`/`DP`、Independence Axiom、耦合分析以及 uncoupled / decoupled design 的基础来源。

### 课程工具链

- [JupyterLab Documentation](https://jupyterlab.readthedocs.io/en/stable/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [pytest Documentation](https://docs.pytest.org/en/stable/)

## 文档

### 面向读者的指南
| 中文 | English |
|---|---|
| [项目创作圣经](docs/zh/PROJECT_BIBLE.md) | [Project Bible](docs/en/PROJECT_BIBLE.md) |
| [高层学习路线](docs/zh/ROADMAP.md) | [High-level Roadmap](docs/en/ROADMAP.md) |
| [教学路径](docs/zh/LEARNING_PATH.md) | [Learning Architecture](docs/en/LEARNING_PATH.md) |
| [初学者术语表](docs/zh/GLOSSARY.md) | [Beginner Glossary](docs/en/GLOSSARY.md) |
| [作业 Notebook 设计](docs/zh/EXERCISE_DESIGN.md) | [Exercise Notebook Design](docs/en/EXERCISE_DESIGN.md) |
| [HDL 工具链安装与 Jupyter 启动](docs/zh/HDL_TOOLCHAIN_SETUP.md) | [HDL Toolchain Setup and Jupyter Launch](docs/en/HDL_TOOLCHAIN_SETUP.md) |
| [KV260 参考硬件平台](docs/zh/KV260_REFERENCE_PLATFORM.md) | [KV260 Reference Hardware Platform](docs/en/KV260_REFERENCE_PLATFORM.md) |
| [实体 FPGA 实验教学规范](docs/zh/PHYSICAL_FPGA_LABS.md) | [Physical FPGA Lab Teaching Standard](docs/en/PHYSICAL_FPGA_LABS.md) |

### 工程事实文档
| 中文 | English |
|---|---|
| [文档优先与规范治理](docs/zh/DOCUMENT_AUTHORITY.md) | [Documentation-First Governance](docs/en/DOCUMENT_AUTHORITY.md) |
| [项目需求 / URD](docs/zh/URD.md) | [Idea Brief / URD](docs/en/URD.md) |
| [公理设计 / ADD](docs/zh/ADD.md) | [Axiomatic Design / ADD](docs/en/ADD.md) |
| [模块设计 / MDD](docs/zh/MDD.md) | [Building Blocks / MDD](docs/en/MDD.md) |
| [测试验证 / TDD](docs/zh/TDD.md) | [Check Plan / TDD](docs/en/TDD.md) |
| [实施路线 / RMD](docs/zh/RMD.md) | [Build Path / RMD](docs/en/RMD.md) |
| [追踪矩阵 / TRACE](docs/zh/TRACE.md) | [Project Map / TRACE](docs/en/TRACE.md) |

`docs/` 是项目事实与设计决策的优先来源。完整规则见 [文档优先与规范治理](docs/zh/DOCUMENT_AUTHORITY.md)：规范变更先更新文档，再更新 test oracle / TRACE，最后修改代码或 RTL；现有实现不能因为“已经这样运行”就自动升级成 specification。

`URD/ADD/MDD/TDD/RMD/TRACE` 是工程事实来源；创作圣经、高层路线、教学路径、术语表和 Notebook 负责帮助人理解和学习项目，但不静默替代正式工程 contract。

## 当前状态

项目规划、系统架构和第一次课程审计已经完成；**KV260 reference board 与 LAB-HW-00~10 的实体教学/验收规范已冻结。** LAB-HW-00~07 已建立双语 Notebook 与 CI contract。LAB-HW-03/04 已加入 board-specific RTL、Bank 45 XDC、Vivado build/program helper 与 open-source simulation；LAB-HW-05 已加入 Ubuntu image/UART/boot-evidence helper；LAB-HW-06 已加入冻结的 PS→PL AXI-GPIO 路径、transform RTL/testbench、Vivado build contract 与 self-checking MMIO helper。LAB-HW-08~10 和所有真实板卡 evidence 尚待实现。第一段正式工程实现尚未声明完成。

当前第一批工程任务：

1. `RMD-001` — Python LIF 浮点参考模型
2. `RMD-002` — fixed-point 探索
3. `RMD-003` — 冻结 v0 神经元语义

`RMD-003A` — Digital Hardware Bridge 是**下一批的第一项**，不是当前第一批的一部分。

在早期仿真与概念验证通过之前，暂不购买 FPGA 硬件。


## 许可证

除非文件或第三方依赖另有明确声明，本仓库的原创文档、Notebook、Python、SystemVerilog、testbench、脚本和其他内容采用 [MIT License](LICENSE)。
