# 《从膜电位到硅：在 FPGA 上造一只果蝇》项目创作圣经

- 工作版本：v0.3
- 同步基线：ADD/RMD v0.3-r1
- 定位：面向医学、生物学、神经科学与生物医学工程学生的神经形态计算与 AI 硬件入门项目

## 1. 项目使命
这个项目带一个具有大学生命科学基础、但几乎没有计算机硬件背景的人，从“知道神经元怎么放电”，走到能够理解、设计、实现和验证一台运行真实果蝇连接组的 FPGA 神经形态计算机。

整个项目围绕同一个不断成长的系统展开：

```text
一个 LIF 神经元
→ 多神经元
→ 稀疏突触
→ spike event
→ FPGA
→ 外部内存
→ 真实 MaleCNS 子图
→ 完整目标网络
→ 闭环环境
```

最终目标不是声称复制完整生物学果蝇脑，而是在 FPGA 上运行一个**由真实 MaleCNS 连接结构约束、可验证、可测量的脉冲神经网络**。

## 2. 目标读者
假想读者是医学、生物学、神经科学或生物医学工程专业大二/大三学生。

默认已经知道：
- 膜电位、动作电位、阈值、不应期、突触、兴奋/抑制；
- 基本微积分、向量、矩阵；
- 对 AND/OR/NOT 和二进制有一点印象。

不要求预先学过：SystemVerilog、FPGA、计算机组成、AXI/DDR/DMA、神经形态计算或 AI 芯片设计。

## 3. 毕业画像
完成项目后，读者不必成为专业芯片工程师，但应该能够把一个神经计算问题主动拆成：

```text
状态在哪里？
数据从哪里来？
如何存？
如何移动？
哪个单元计算？
怎样并行？
怎样验证？
瓶颈在哪里？
```

他/她应该已经亲手接触 register、RAM、FIFO、pipeline、fixed point、DDR bandwidth、sparse/event-driven computation、FPGA accelerator 和 neuromorphic hardware 的基本概念。

## 4. 三层翻译
重要概念尽量同时用三种语言描述：

| 生物语言 | 数学语言 | 硬件语言 |
|---|---|---|
| 膜电位 | 状态变量 V | register / RAM state |
| 突触强度 | weight | fixed-point value |
| 动作电位 | threshold event | comparator + spike flag |
| 不应期 | state constraint | counter / FSM |
| 神经连接 | sparse graph | adjacency / CSR-like image |
| spike | discrete event | FIFO message |
| 神经网络 | dynamical system | memory + compute + event router |

这三层之间的翻译，是整套课程最重要的方法。

## 5. AI-assisted engineering，而不是 AI 替代思考
项目从第一章开始就充分使用 AI / vibe coding。

AI 可以帮助：
- 写样板代码；
- 生成 testbench；
- 解释工具报错；
- 维护文档；
- 做差分测试脚本；
- 搜索实现方案；
- 生成实验数据处理代码。

但人必须拥有：
- 需求；
- 模型假设；
- FR/DP；
- 模块边界与接口；
- test oracle；
- 性能权衡；
- 是否接受结果的判断。

核心规则：**AI 可以替学习者写代码，但不能替学习者拥有模型。**

AI 的任何“测试通过”“时序满足”“性能更快”等结论，都必须有真实命令、波形、报告或 benchmark 证据。

## 6. 公理设计是项目的工程骨架
项目采用 Axiomatic Design 的基本语言：
- Functional Requirement（FR）：系统必须完成什么；
- Design Parameter（DP）：用什么设计满足它；
- Constraint（C）：不可违反的边界。

设计遵守两条核心原则：
1. 尽量保持 FR 独立；
2. 满足独立性的情况下，优先选择更简单、成功路径更明确的方案。

FlyBrain 产品系统当前被整理为严格下三角的 decoupled design。验证、AI 协作、Git/TRACE 等横跨全项目的机制被放在单独的 process FR/DP 层，不与产品功能混在一张矩阵中。

## 7. Learning Independence Axiom
我们把“独立性公理”进一步用于课程设计：

> 一个学习 slice 最多引入一个主要陌生概念；如果任务成功需要同时掌握多个未知概念，就插入 bridge slice。

因此路线中明确存在：
- Python → RTL 的 Digital Hardware Bridge；
- 多神经元 → event-driven 的 4-neuron bridge；
- simulation → FPGA 的 synthesis/first-bitstream/loopback bridge；
- FPGA → DDR/AXI 的 memory hierarchy/bandwidth bridge。

桥接章节不是“补课附录”，而是正式课程内容。

## 8. 工程文档体系
`docs/` 是设计事实来源。

- URD：为什么做、给谁做、成功是什么；
- ADD：FR/DP、矩阵和耦合；
- MDD：模块、接口和数据契约；
- TDD：正确性、oracle 和测试；
- RMD：最安全的实施/学习顺序；
- TRACE：需求 → 设计 → 模块 → 测试 → 任务的链接。

未来 `okf/` 是 AI 检索层，`.vibe/` 保存机器可读追踪状态。它们不得悄悄发明新需求；设计变更先改 `docs/`。

## 9. 每章的标准结构
每章尽量从一个已经出现的问题开始，然后依次回答：

1. **生物问题**：系统发生了什么？
2. **计算模型**：怎样最小化表达？
3. **硬件问题**：机器需要保存、读取或计算什么？
4. **最少新知识**：当前只需要学习哪个新概念？
5. **Design Split**：FR/DP 是否独立？
6. **Build**：让人和 AI 一起实现。
7. **Test**：oracle 是什么？
8. **Measure**：误差、吞吐、资源或功耗是多少？
9. **Explain-back**：学习者能否不用 AI 解释当前系统？
10. **Git checkpoint**：保存一个可复现状态。

## 10. 生物真实性是一条可实验的轴
基础版本使用 LIF，不把它当作真实神经元的完整描述。

未来可以逐步加入：

```text
LIF
→ refractory/adaptation
→ conductance-based synapse
→ short-term plasticity
→ STDP
→ neuron classes
→ neuromodulation
```

每增加一层生物复杂度，同时问两个问题：行为/预测能力增加多少？硬件成本增加多少？

## 11. 明确不做什么
当前项目不试图：
- 证明或复制意识；
- 宣称连接组等于完整大脑；
- 完整教授神经科学、半导体物理或所有 SystemVerilog；
- 第一阶段追求最高性能；
- 一上来就买昂贵 HBM FPGA；
- 为了让 ADD 矩阵漂亮而制造无意义模块。

## 12. 成功的真正标准
完整 MaleCNS 是北极星，但不是唯一标准。

如果一个生命科学学生走到中途，已经能理解 register、BRAM、FIFO、pipeline、memory bandwidth、sparse accelerator，并能够问“这个神经算法该怎样映射到硬件、如何验证”，项目就已经成功了一大部分。

最终作品是一台机器；真正获得的是一种新的看问题方式：

```text
细胞
→ 动力系统
→ 网络
→ 图计算
→ 数字逻辑
→ 存储系统
→ 并行架构
→ AI hardware
```
