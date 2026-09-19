# FPGA FlyBrain 作业册

[English](README.md)

Python 作业使用 Jupyter Notebook。每份作业都应当能独立阅读：先说明为什么做、要完成什么和有哪些约束，再提供小范围 TODO、自动检查入口和 Human Check。

完整设计规范见：[作业 Notebook 设计规范](../docs/zh/EXERCISE_DESIGN.md)。

## 学生怎么做

### 1. 不要直接修改官方 starter

`exercises/zh/` 和 `exercises/en/` 保存 Git 跟踪的**官方作业模板**。这些文件会随着课程更新，因此不建议直接在里面长期保存个人答案。

学生自己的作业统一放在：

```text
exercises/work/
├── zh/
└── en/
```

整个 `exercises/work/` 已加入 `.gitignore`，普通 `git status`、commit 和 `git pull` 不会把你的答案当成课程源码。

### 2. 用一个命令开始作业

从仓库根目录运行：

```bash
uv sync --group dev
uv run python scripts/start_exercise.py 01
```

第一个命令会创建：

```text
exercises/work/zh/01_membrane_to_lif.ipynb
```

然后启动：

```bash
uv run jupyter lab
```

在 JupyterLab 中打开 **`exercises/work/zh/` 下的副本**，而不是 `exercises/zh/` 下的官方 starter。

其他用法：

```bash
# 第 11 课中文作业
uv run python scripts/start_exercise.py 11

# 第 1 课英文作业
uv run python scripts/start_exercise.py 01 --lang en

# 一次建立全部当前中文 Python 作业
uv run python scripts/start_exercise.py all

# 一次建立全部当前英文 Python 作业
uv run python scripts/start_exercise.py all --lang en
```

脚本**绝不会覆盖已经存在的学生副本**。再次运行同一命令时会提示：

```text
Already exists, kept unchanged: exercises/work/zh/01_membrane_to_lif.ipynb
```

因此可以安全地重复执行。

### 3. 做题流程

典型流程是：

```text
官方 starter
  ↓ start_exercise.py 复制一次
个人 work Notebook
  ↓
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
```

学生可见 Notebook **不直接展示自动测试的 assert、具体测试向量或完整判题逻辑**。检查单元会把当前 Jupyter kernel 中刚定义的函数传给 `exercises/grader/` 下的外部 grader。

grader 只报告概念分组是否通过，例如：

```text
第 05 课检查

✓ Boolean gates
✓ Threshold behavior
✗ Enable behavior

2 / 3 groups passed
```

失败信息可以提示应检查哪个概念，但不会打印具体失败输入和期望答案。

### 4. 更新课程不会覆盖你的答案

以后更新仓库时：

```bash
git pull
```

Git 更新的是官方课程模板和代码。你的 `exercises/work/` 不被跟踪，因此不会因为课程更新而产生 Notebook merge conflict。

如果官方 starter 更新了，你可以继续保留现有 work 副本；如果想从新 starter 重新开始，可以先自行备份或重命名旧 work 文件，再运行 `start_exercise.py`。脚本不会主动删除或覆盖任何已有答案。

### 5. 如果你已经直接修改过官方 Notebook

如果你是在引入 `exercises/work/` 之前开始做题，并且答案还写在例如：

```text
exercises/zh/01_membrane_to_lif.ipynb
```

先运行：

```bash
uv run python scripts/start_exercise.py 01
```

脚本会把你**当前本地版本**复制到 `exercises/work/zh/`。确认个人副本中答案完整后，再把官方模板恢复为 Git 版本：

```bash
git restore exercises/zh/01_membrane_to_lif.ipynb
```

这样以后你的答案和课程源码就分开了。

## Python 作业目录

下表链接指向官方 starter，方便阅读和版本追踪。真正做题时请通过 `start_exercise.py` 建立 `work/` 副本。

| Lesson | 官方作业 Notebook | 主要练习 |
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
| 13 | [读懂一个 timing budget](zh/13_simulation_is_not_chip.ipynb) | critical path、slack、timing pass/fail |
| 14 | [把板上时钟变成可观察 tick](zh/14_what_is_fpga_board.ipynb) | board clock、counter width、observable tick |
| 15 | [模拟 host ↔ programmable logic 往返](zh/15_host_talks_to_fpga.ipynb) | persistent PL state、readback ordering |
| 16 | [判断 compute / data movement bottleneck](zh/16_data_movement_cost.ipynb) | latency、bandwidth、simple cost model |
| 17 | [估算 sequential/random burst 成本](zh/17_external_memory_ddr.ipynb) | burst grouping、setup cost、access pattern |
| 18 | [识别 VALID/READY 接受的 data beat](zh/18_axi_subset.ipynb) | handshake、stall、accepted beat |
| 19 | [计算 connectome 的 in/out degree](zh/19_what_is_connectome.ipynb) | directed graph structure、zero-degree neuron |
| 20 | [建立最小 image manifest](zh/20_load_malecns_subset.ipynb) | schema version、byte count、SHA-256 integrity |
| 21 | [找出 utilization 最高的 stage](zh/21_scaling_bottlenecks.ipynb) | utilization、scale-dependent bottleneck |
| 22 | [生成 closed-loop position trace](zh/22_closed_loop_world.ipynb) | feedback、target-reaching trace |
| 23 | [计算 throughput 与 energy per event](zh/23_cpu_gpu_fpga_benchmark.ipynb) | benchmark metric、duration-aware energy |

第 13–18 课进入 FPGA 板、host、DDR 与 AXI 主题，但正式作业仍提供**无板可完成**的 Python/推理版本；实体板实验作为对应 RMD slice 的工程延伸，不把购买硬件变成继续学习的门槛。

第 19–23 课进入 connectome integrity、scaling、closed loop 与 benchmark。正式作业使用 teaching fixture 与 synthetic measurement，因此完整 MaleCNS 下载、正式 converter、GPU 或实体 FPGA 都不是继续学习这些 contract 的前置条件。

第 6–8 课主要练习 SystemVerilog、testbench 和 waveform，继续使用 RTL 教学检查：

```bash
./scripts/check_rtl_learning.sh
```

后续如果为 6–8 课增加独立作业册，也遵守同一套“题目先于代码、检查不泄露答案、Human Check 补充理解”的原则。

## 对课程维护者

学生即时检查实现位于 `exercises/grader/`。

维护者测试位于 `exercises/checks/`，当前主要入口：

```bash
uv run pytest \
  exercises/checks/test_graders.py \
  exercises/checks/test_notebook_structure.py \
  exercises/checks/test_start_exercise.py \
  lessons/checks/test_platform4_notebook_structure.py \
  lessons/checks/test_platform4_student_dryrun.py \
  lessons/checks/test_platform5_notebook_structure.py \
  lessons/checks/test_platform5_student_dryrun.py -q
```

`test_start_exercise.py` 会验证 lesson 选择、工作副本路径以及“已有学生答案绝不覆盖”的行为。

GitHub Actions 的 Python exercise infrastructure workflow 会自动运行作业基础设施测试。

当前不使用 nbgrader，也不使用 testbook。只有出现明确的新需求时再评估。
