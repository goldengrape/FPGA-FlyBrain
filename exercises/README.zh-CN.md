# FPGA FlyBrain 作业册

[English](README.md)

Python 作业使用 Jupyter Notebook。每份作业都应当能独立阅读：先说明为什么做、要完成什么和有哪些约束，再提供小范围 TODO、自动检查入口和 Human Check。

完整设计规范见：[作业 Notebook 设计规范](../docs/zh/EXERCISE_DESIGN.md)。

## 学生怎么做

从仓库根目录启动：

~~~bash
uv sync --group dev
uv run jupyter lab
~~~

然后打开 exercises/zh/ 下对应课程的 Notebook。

典型流程是：

~~~text
读题
  ↓
先预测 / 手算
  ↓
完成 TODO
  ↓
运行“检查你的实现”
  ↓
根据结果修订
  ↓
完成 Human Check
~~~

学生可见 Notebook **不直接展示自动测试的 assert、具体测试向量或完整判题逻辑**。检查单元会把当前 Jupyter kernel 中刚定义的函数传给 exercises/grader/ 下的外部 grader。

grader 只报告概念分组是否通过，例如：

~~~text
第 05 课检查

✓ Boolean gates
✓ Threshold behavior
✗ Enable behavior

2 / 3 groups passed
~~~

失败信息可以提示应检查哪个概念，但不会打印具体失败输入和期望答案。

## Python 作业目录

| Lesson | 作业 Notebook | 主要练习 |
|---|---|---|
| 01 | [从膜电位到 LIF 的一步更新](zh/01_membrane_to_lif.ipynb) | leak、integration、threshold、reset |
| 02 | [把小数放进有限位宽](zh/02_float_to_fixed.ipynb) | signed range、rounding、quantization、saturation |
| 03 | [把 LIF 变成明确 specification](zh/03_freeze_neuron_semantics.ipynb) | 固定语义、boundary、counterexample |
| 04 | [next state 与 register state](zh/04_state_and_clock.ipynb) | combinational next-state、clock edge、state history |
| 05 | [逻辑门、比较器与 enable](zh/05_logic_building_blocks.ipynb) | Boolean logic、threshold、enable |
| 09 | [一个 engine 轮流服务多个 state](zh/09_time_multiplex_many_neurons.ipynb) | addressed state、round robin |
| 10 | [有界 FIFO 与 backpressure](zh/10_spike_fifo_backpressure.ipynb) | FIFO ordering、full/empty、retry |
| 11 | [稀疏连接的顺序读取表示](zh/11_sparse_synapse_lookup.ipynb) | source index、contiguous records、zero fanout |
| 12 | [一个 source spike 的完整旅程](zh/12_one_spike_journey.ipynb) | source range、weighted event、target accumulator |

第 6–8 课主要练习 SystemVerilog、testbench 和 waveform，继续使用 RTL 教学检查：

~~~bash
./scripts/check_rtl_learning.sh
~~~

后续如果为 6–8 课增加独立作业册，也遵守同一套“题目先于代码、检查不泄露答案、Human Check 补充理解”的原则。

## 对课程维护者

学生即时检查实现位于 exercises/grader/。

维护者测试位于 exercises/checks/，当前主要入口：

~~~bash
uv run pytest   exercises/checks/test_graders.py   exercises/checks/test_notebook_structure.py -q
~~~

test_graders.py 验证 grader 能接受 reference implementation，并能抓住典型错误实现。test_notebook_structure.py 验证双语 Notebook 可以解析、保留 TODO、使用外部 grader，并且学生代码单元没有内嵌测试函数或 assert。

GitHub Actions 的 Python exercise infrastructure workflow 会自动运行这两组检查。

当前不使用 nbgrader，也不使用 testbook。只有出现明确的新需求时再评估。
