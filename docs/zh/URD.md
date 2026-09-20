# URD — Idea Brief / 用户需求文档

## 0. 文档信息
- 项目：FPGA果蝇 / From Membrane Potential to Silicon
- 版本：v0.3-r1
- 状态：Reference board frozen; physical-lab documentation pass
- 本文档角色：定义“为什么做、给谁做、做到什么算成功”。

## 1. 项目愿景
为具有生命科学或医学背景、但缺乏计算机硬件训练的大学生，提供一条以真实果蝇连接组为主线、AI 辅助工程为方法、FPGA 为目标硬件的学习与实践路径。

读者从已知的神经生理学概念出发，把“神经元如何放电”逐步翻译成数学模型、数字逻辑、硬件模块、稀疏事件驱动体系结构，最终在 FPGA 上运行一个由真实果蝇 MaleCNS 连接结构约束的脉冲神经网络，并由电脑提供感觉输入、读取输出和进行可视化。

## 2. 目标读者
典型读者：医学、生物学、神经科学、生物医学工程等专业大二至大三学生。

### 已知知识
- 理解膜电位、动作电位、阈值、不应期、突触、兴奋/抑制。
- 会基本代数、微积分、向量与矩阵运算。
- 对 AND / OR / NOT 等最基本数字逻辑有概念，但不要求熟练。
- 可以没有 FPGA、HDL、计算机组成、嵌入式开发经验；课程必须支持“第一次拿到 FPGA 开发板”的零经验路径。
- 可以不会系统编程；Python 只要求愿意边做边学。

### 不假设具备
- Verilog/SystemVerilog
- FPGA 工具链
- 计算机体系结构
- AXI / DDR / DMA
- 神经形态计算
- SNN 硬件设计

## 3. 核心用户任务
- **U1** 从熟悉的神经生理概念出发理解一个最小 LIF 神经元模型。
- **U2** 用 AI 辅助完成 Python 参考模型、SystemVerilog RTL、testbench 和文档，但始终能解释代码对应的物理/数学/硬件意义。
- **U3** 将一个神经元逐步扩展为多神经元、稀疏突触、事件队列和事件驱动网络。
- **U4** 在 FPGA 上运行该网络，并能观察、验证和测量结果。
- **U5** 导入真实 MaleCNS 连接组的子图，最终扩展到完整目标规模。
- **U6** 建立 Python float → Python fixed-point → RTL/FPGA 的验证链。
- **U7** 学会把需求拆成 FR/DP，分析耦合，建立模块契约、测试 oracle、实现顺序与追踪关系。
- **U8** 最终能读懂并开始参与 FPGA accelerator、SNN accelerator、sparse accelerator、neuromorphic hardware 等方向。

## 4. 成功标准
### 学习成功
- 能解释 register、RAM、FIFO、pipeline、fixed point、DDR bandwidth、event-driven computation 为什么在本项目中出现。
- 能独立解释一个 LIF neuron RTL 的状态、输入、输出与时序。
- 能从一块未配置的参考开发板开始，完成正确供电、目标发现、bitstream build/program、最小物理 I/O 验证和 host↔PL readback，并能按层区分 connection/build/program/runtime failure。
- 能根据一个功能需求草拟 FR/DP 和简单设计矩阵。

### 工程成功
- 有可运行的 Python LIF 参考模型。
- 有可仿真的 SystemVerilog 单神经元实现。
- 有多神经元时分复用实现。
- 有稀疏突触表、spike FIFO、事件路由和 synapse engine。
- 有在参考板卡 AMD Kria KV260 Vision AI Starter Kit 上可重复构建、program、验证的 FPGA 版本，并保留 board/tool/artifact evidence。
- 有外部内存支持。
- 有真实 MaleCNS 子图版本。
- 最终可运行完整目标 MaleCNS 模型，电脑负责感觉输入/输出与可视化。

### 验证成功
- 关键计算可与 Python fixed-point reference 比较。
- 单模块有 testbench 和明确 test oracle。
- 关键 build slice 有可重复命令和 Git checkpoint。
- 所有主要需求可追踪到设计、模块、测试和实现任务。

## 5. 当前范围
### In scope
LIF/简化脉冲神经元、Python reference、SystemVerilog RTL、FPGA 仿真与上板、KV260 零基础 Physical Lab 路径、稀疏连接、event-driven spike processing、BRAM/URAM/DDR、MaleCNS 数据转换、AI-assisted engineering/vibe coding、公理设计、测试/追踪/Git checkpoint，以及教材/公开项目双用途文档。

### Out of scope
完整生物学果蝇脑或意识复制、Hodgkin–Huxley 级全面生物物理模拟、模拟电路、晶体管工艺、自研 ASIC 流片、医疗器械/临床系统，以及第一阶段就加入 STDP、复杂神经调质和完整身体模型。

## 6. 关键约束
- **C1** 所有新硬件概念应由当前工程问题自然引出。
- **C2** AI 可生成代码，但人必须理解模型、需求、接口、架构和验证标准。
- **C3** 不允许“代码能跑”替代可验证性。
- **C4** 不为了公理设计矩阵漂亮而制造无意义模块。
- **C5** 文档保持小而可用；未来想法进入 PARKING_LOT。
- **C6** 硬件购买延后到仿真阶段通过之后。
- **C7** 第一套完整实体教学路径冻结 **AMD Kria KV260 Vision AI Starter Kit** 为 reference board；FlyBrain core 与稳定接口仍保持板卡可替换，板卡专有内容隔离在 platform shell / Physical Lab。

## 7. 关键假设
- **A1** MaleCNS 数据在项目执行期间保持可公开获取。
- **A2** 基础版本先采用简化 LIF 模型。
- **A3** 定点数是 FPGA 主实现方向；浮点用于软件参考。
- **A4** 第一阶段允许 AI 生成大量样板代码和 testbench，但关键模块必须有解释与验证。

## 8. 开放问题与已解决决策

**已解决：**
- **Q1** 第一套完整上板教学锁定 **AMD Kria KV260 Vision AI Starter Kit**。其他板卡以后可增加 porting guide，但不要求第一版课程同时维护多套零基础上板步骤。

**仍开放：**
- **Q2** 完整 MaleCNS 最终采用固定时间步 + 稀疏传播，还是 lazy/event-driven neuron update？
- **Q3** 公开教材中文优先，还是同步中英文？——当前决定：GitHub 工程文档同步中英文。
- **Q4** 最终闭环 demo 选虚拟身体、简单游戏，还是自建二维环境？

## 9. 北极星
> 让一个生命科学学生亲手把神经生理学翻译成可验证、可运行、可测量的数字硬件系统，并借此进入 AI hardware 的基本世界。
