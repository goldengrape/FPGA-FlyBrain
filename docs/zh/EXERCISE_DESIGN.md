# 作业 Notebook 设计规范

## 1. 目的

FPGA FlyBrain 的作业不是裸代码填空，而是一组可独立阅读、可立即运行、可自我检查的电子作业册。

课程 Notebook 负责讲授概念；作业 Notebook 负责让学习者用代码、手算、预测和解释把概念转化为可执行能力。学习者不应为了弄清“题目是什么、为什么要做、做到什么算完成”而在 README、starter Python、测试文件之间来回跳转。

本规范主要适用于 Python 作业。RTL 课程沿用相同的教学结构，但检查方式改为编译、仿真、lint 和波形观察。

## 2. 核心原则

每份作业 Notebook 必须做到：

1. **可以独立阅读。** 单独打开 Notebook 时，学习者知道这份作业对应哪一课、练什么、为什么练、需要完成什么。
2. **题目先于代码。** 先用 Markdown 写清背景、任务和约束，再出现 TODO。
3. **不把测试写成提示。** 学生可见 Notebook 中不直接展示 assert、具体测试向量或完整判题逻辑。
4. **即时反馈。** 学习者完成一个小任务后，可以在当前 Jupyter kernel 中立即运行检查。
5. **检查与解释分开。** 自动检查只判断可执行行为；Human Check 判断学习者能否解释概念、边界和结果。
6. **保持接口稳定。** 函数名、参数、返回值是课程规范的一部分；除非作业明确要求，不应由学习者任意修改。
7. **测试公开与否不是安全边界。** 本项目是开源自学课程。grader 放在仓库中，是为了避免测试实现直接出现在作业页面并无意中提示答案，而不是为了防作弊。

## 3. 学生看到的 Notebook 结构

Python 作业统一采用以下顺序：

1. 标题与对应课程
2. 为什么做这道题
3. 你将完成什么
4. 规则与约束
5. 手算 / 预测 / 小例子
6. 学生代码单元
7. 检查你的实现
8. Human Check
9. 可选延伸实验

不是每一题都必须机械出现全部九个标题，但信息必须完整，并保持“解释 → 实现 → 检查 → 再解释”的顺序。

### 3.1 代码前必须先写“语义契约”

**函数签名不能替代题目说明。** 在学生看到代码之前，题面必须先用自然语言说明这个函数在当前模型中的作用。

每个需要学生实现的函数，至少应明确：

- **作用**：这个函数在模型或数据流中完成哪一步；
- **输入**：每个参数在当前课程语境中代表什么，而不只是 Python 类型；
- **输出**：函数会产生几个结果，每个结果代表什么；
- **返回顺序**：如果返回 tuple / 多个值，逐项说明第 1、2、3 项的含义；
- **时间/状态含义**：如果涉及 state、next state、candidate、event，要说明这些值属于哪个时间点或哪个处理阶段；
- **副作用**：是否允许修改传入的 list / state，必要时明确说明。

例如，不应只写：

~~~python
def lif_step(...) -> tuple[float, bool]:
    ...
~~~

而应先说明：

> 返回 `(next_v, spike)`。  
> `next_v` 是本次更新结束后、将保存到下一时间步的膜电位；  
> `spike` 是布尔值，表示本次更新是否产生 spike。

目标是：即使学习者还不熟悉 Python 的 `tuple[float, bool]` 类型标注，也能仅凭文字知道要完成什么。

### 3.2 学生代码单元

TODO 区域应尽量短，只包含本课真正要学生完成的部分。不要把大量样板代码、I/O、测试框架或课程基础设施混入 TODO。

示例：

~~~python
def threshold_reached(value: int, threshold: int) -> bool:
    # YOUR CODE STARTS HERE
    raise NotImplementedError("TODO")
    # YOUR CODE ENDS HERE
~~~

### 3.3 检查单元

Notebook 不直接包含 pytest 测试函数。它只导入外部 grader，并把当前 kernel 中的学生函数传入。

示意：

~~~python
from exercises.grader.lesson05 import check

check(
    gate_not=gate_not,
    gate_and=gate_and,
    gate_or=gate_or,
    threshold_reached=threshold_reached,
    spike_enabled=spike_enabled,
)
~~~

这样 grader 检查的就是学习者刚刚运行过的当前实现，不要求把 Notebook 另存为 Python 模块，也不需要重新启动 kernel。

## 4. grader 设计

grader 位于：

~~~text
exercises/
├── grader/
│   ├── __init__.py
│   ├── lesson01.py
│   ├── ...
│   └── lesson12.py
└── zh/
    └── ...
~~~

每课 grader 对外暴露一个简单的 check(...) 接口。

### 4.1 grader 的职责

grader 应：

- 接收当前 Notebook 中定义的 callable 或必要对象；
- 运行一组足以判定课程要求的检查；
- 捕获内部断言和异常；
- 返回或打印适合学生阅读的简洁结果；
- 不在失败信息中泄露具体测试向量、期望值或内部 assert 表达式。

推荐输出：

~~~text
Lesson 05 checks

✓ Boolean logic
✓ Threshold behavior
✗ Enable behavior

7 / 8 checks passed
~~~

必要时可以给概念级提示，例如“检查 enable 为关闭状态时的行为”，但不要直接打印触发失败的输入和期望输出。

### 4.2 grader 不负责什么

grader 不负责教授题目、不在 Notebook 中展示完整测试、不证明学习者真正理解了概念，也不试图阻止学习者主动打开 grader 源码。

题目和解释属于 Notebook；理解由 Human Check 补充。

## 5. grader 自身如何测试

grader 是课程基础设施，因此它本身必须被普通 pytest 测试。

维护者测试继续放在 exercises/checks/。这些测试至少验证两类情况：

1. 正确的 reference implementation 应通过；
2. 典型错误实现应被 grader 捕获，例如 > 代替 >=、FIFO 满时覆盖旧事件、错误的 sparse range 等。

这层 pytest 面向课程维护，不直接出现在学生作业页面。

当前阶段不引入 nbgrader，也不引入 testbook。只有当项目出现明确的教师发布、学生提交或完整 Notebook 外部执行需求时再评估。

## 6. Human Check

每份作业至少包含一个不能只靠“测试通过”回答的问题，例如：

- 手算一个状态更新；
- 解释一个边界条件为什么重要；
- 说明某个数据结构保存的是什么，而不是什么；
- 预测修改参数后的行为，再运行验证；
- 指出一个 cycle 中旧状态、candidate 和保存后状态的区别。

AI 可以用于解释报错、比较实现或生成额外练习，但 Human Check 应尽量由学习者先独立作答。

## 7. 文件布局

Python 作业迁移为：

~~~text
exercises/
├── README.md
├── README.zh-CN.md
├── grader/
│   ├── __init__.py
│   ├── lesson01.py
│   ├── lesson02.py
│   ├── lesson03.py
│   ├── lesson04.py
│   ├── lesson05.py
│   ├── lesson06.py
│   ├── lesson07.py
│   ├── lesson08.py
│   ├── lesson09.py
│   ├── lesson10.py
│   ├── lesson11.py
│   ├── lesson12.py
│   ├── lesson13.py
│   ├── lesson14.py
│   ├── lesson15.py
│   ├── lesson16.py
│   ├── lesson17.py
│   └── lesson18.py
├── checks/
│   └── ...
├── en/
│   └── ...
└── zh/
    ├── 01_membrane_to_lif.ipynb
    ├── 02_float_to_fixed.ipynb
    ├── 03_freeze_neuron_semantics.ipynb
    ├── 04_state_and_clock.ipynb
    ├── 05_logic_building_blocks.ipynb
    ├── 06_what_is_rtl.ipynb
    ├── 07_first_rtl_neuron.ipynb
    ├── 08_testbench_waveform_simulation.ipynb
    ├── 09_time_multiplex_many_neurons.ipynb
    ├── 10_spike_fifo_backpressure.ipynb
    ├── 11_sparse_synapse_lookup.ipynb
    ├── 12_one_spike_journey.ipynb
    ├── 13_simulation_is_not_chip.ipynb
    ├── 14_what_is_fpga_board.ipynb
    ├── 15_host_talks_to_fpga.ipynb
    ├── 16_data_movement_cost.ipynb
    ├── 17_external_memory_ddr.ipynb
    └── 18_axi_subset.ipynb
~~~

作业文件名尽量与课程 Notebook 对应，使学习者可以自然地在 lessons/zh/ 与 exercises/zh/ 之间切换。

第 6–8 课现在同时提供小型 Python/推理作业册与真实 SystemVerilog/testbench 实验。作业册检查 RTL 语义翻译和 oracle 推理，但不把 Python grader 冒充 RTL compile、simulation 或 waveform 检查。

第 13–18 课进入真实硬件与外部内存主题，但正式作业刻意保留无板可完成的语义/性能模型；实体板、DDR controller 与平台专用步骤属于对应 RMD 的工程实验，不把硬件购买设成作业前置条件。

## 8. 完成标准

一次 Python 作业重构只有在以下条件同时满足时才完成：

- Notebook 单独打开可理解；
- 每个需要学生实现的函数，在代码前都有自然语言 semantic contract，明确作用、输入、输出、返回顺序以及必要的时间/状态含义；
- TODO 保留且没有答案泄露；
- Notebook 中没有直接显示 assert 或完整测试向量；
- grader 可以检查当前 kernel 中的实现；
- grader 失败信息不会直接给出答案；
- grader 有维护者 pytest 覆盖；
- Human Check 与课程主要概念一致；
- README 中的运行说明和路径已经更新；
- 中英文版本保持相同结构和要求。

## 9. 当前决策

截至 2026-09-18，项目采用：

~~~text
Lesson Notebook
    → 教材

Exercise Notebook
    → 正式作业册

external grader
    → 学生即时自动检查，不在 Notebook 展示 assert

pytest
    → 维护者验证 grader 与课程规则

Human Check
    → 理解与解释
~~~

当前不引入 nbgrader、testbook，也不采用以 Notebook 输出快照为核心的判题方案。这些工具只有在出现具体需求时再引入，而不是作为当前作业系统的前置复杂度。
