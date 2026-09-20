# Exercise Notebook 学生视角 Dry Run

## 1. 方法

本轮把自己限制在“普通学生”视角：

- 只阅读中文 lesson 与对应 Exercise Notebook；
- 先完成手算 / trace；
- 再独立填写 TODO；
- 不先查看 grader 源码或具体测试向量；
- 完成解答后，才用现有 grader 契约验证是否通过；
- 同时记录环境、题意、回翻教材、提示密度与调试反馈中的摩擦。

最初一轮 Dry Run 覆盖 9 份 Python 作业（LSN-001~005、009~012），均能依据教材和题面独立完成。随后补齐的 LSN-006~008 独立作业册见第 12 节；当前 LSN-001~023 已都有正式作业入口。

## 2. 最重要的发现：grader import 在真实 Jupyter 路径下不稳

Exercise Notebook 位于：

`exercises/zh/*.ipynb`

Jupyter Server 的 FileContentsManager 默认让 kernel 从 Notebook 所在目录启动。因此学生正常打开 `exercises/zh/01_membrane_to_lif.ipynb` 时，kernel cwd 通常是：

`<repo>/exercises/zh`

当前 check cell 使用：

```python
from exercises.grader.lesson01 import check
```

但 `pyproject.toml` 当前没有把仓库安装成可 import 的 package；`[tool.pytest.ini_options] pythonpath = ["."]` 只影响 pytest。单纯 `uv sync` 也不会让仓库根目录自动出现在从 `exercises/zh` 启动的 Python `sys.path` 中。

因此真实学生路径可能在最后一步遇到：

```text
ModuleNotFoundError: No module named 'exercises'
```

这是本轮唯一的 blocker。本轮 dry run 已在同一变更周期内修复：每个 grader check cell 会先从当前工作目录向上定位仓库根目录，再把根目录加入 `sys.path`，因此从 `exercises/zh`、`exercises/en` 或仓库根目录执行都能稳定 import grader，不要求学生手工修改路径。维护者测试也新增了从 Notebook 工作目录启动子进程的回归检查。

## 3. 逐课 Dry Run

| Lesson | 手算 / trace | TODO 可独立完成？ | 需要回翻教材？ | 学生视角摩擦 |
|---|---|---|---|---|
| 01 | 很合适；负数 threshold 能迫使学生认真比较大小 | 是 | 通常不需要 | 低。candidate 与 stored state 区分清楚 |
| 02 | 5-bit 例子有效，避开 grader 向量 | 是 | 容易回看 bit-shift / signed range 公式 | 中低。教材中已有几乎完整的 quantize()，容易直接复制 |
| 03 | probe 设计是很好的验证思维练习 | 是 | 很容易回到教材找到现成 boundary/counterexample | 中。题面说“自己构造”，但教材已经给了可直接复用的数值 |
| 04 | cycle table 很有效 | 是 | 不需要 | 中。clock_edge(state, value_to_store) 中 state 对正确实现不参与计算，初学者会怀疑是不是漏用了参数 |
| 05 | truth table 很清楚 | 是 | 不需要 | 低。代码极易；这是进入 RTL 前合理的 consolidation valley |
| 09 | address trace 清楚 | 是 | 不需要 | 低~中。教材 loop 与作业实现非常接近，但架构重点仍然成立 |
| 10 | A/B/C ownership trace 很强 | 是 | 基本不需要 | 低。当前是最像“独立作业”的一课之一 |
| 11 | 手工 packing + planning 显著降低算法跳级 | 是 | 可能需要回看教材 nested loop | 中高。教材已经展示几乎完整构建算法，因此既能救急，也容易变成照抄 |
| 12 | range → events → accum trace 很自然 | 是 | 很容易回看 Lesson 12 bridge code | 中。概念整合很好，但核心 TODO 与教材 bridge code 非常接近 |

## 4. 手算结果检查

Dry Run 中的手算结果均可由题面直接得到：

- L01：candidate = -63；threshold=-60 时不 spike；threshold=-63 时 spike 并 reset；
- L02：5-bit signed range = [-16, 15]，frac_bits=3 时 scale=8、step=0.125；0.70 → code 6 → 0.75；3.0 saturation → code 15 → 1.875；
- L04：手工 cycle trace 能明确看到 candidate=5 与 edge 后 reset=0 的分离；
- L09：最终 state memory = [7, 3, 5]；
- L10：C 在 full 时被拒绝但仍由 caller 保存；pop A 后 retry C 成功；
- L11：index = [(0,1),(1,0),(1,2)]，records = [(2,5),(0,-1),(1,4)]；
- L12：source 1 只读取 records[1:3]，产生 [(0,-2),(2,3)]，新 accum = [3,0,4]。

这些例子都没有复用对应 grader 的具体测试向量。

## 5. Grader 体验

先按题面独立完成所有实现，再进行验证：LSN-001、002、003、004、005、009、010、011、012 的所有 grader group 均通过。

反馈粒度总体合适：失败时只暴露概念组，不暴露具体向量。对于自学课程，这比原始 pytest assertion 更适合。

当前最大的 grader 体验问题不是反馈内容，而是前述 import path blocker。

## 6. “回教材就能看到答案”的问题

这不是所有课程都必须避免的问题。当前课程是 open-book 自学，不是闭卷考试；lesson 本来就应该给出可运行的最小例子。

但 Dry Run 显示需要区分两种练习目标：

- **reproduction / consolidation**：看懂后重新实现。LSN-005 适合这样做；
- **transfer / design**：把已学概念迁移到新结构或自己设计例子。LSN-003、011、012 更应该偏向这一类。

目前答案暴露最明显的是：

- LSN-002：lesson 直接包含与作业几乎同形的 quantize() / signed_limits()；
- LSN-003：lesson 已经给出有效 threshold boundary 与 update-order counterexample；
- LSN-011：lesson 的 nested loop 基本就是 build_source_index() 的算法；
- LSN-012：lesson 的 Bridge code 基本就是 process_one_spike() 的主体。

建议不删除教材中的可执行示例，而是在作业中增加“迁移要求”或限制直接复用示例数值。例如 LSN-003 可以明确要求 probe 不复用教材中的数字；LSN-011/012 可以让输入格式或输出 trace 多一个很小的变化，但这类改动需要同步 grader，宜单独设计。

## 7. LSN-004 的 API 摩擦

```python
def clock_edge(state: int, value_to_store: int) -> int:
```

正确实现只需要返回 `value_to_store`，因此 `state` 参数在函数体里天然不使用。

从教学角度它有一个合理目的：显式展示 edge 前旧 state 与 edge 后新 state。但如果不解释，Python 初学者很容易认为“不使用参数一定是我漏写了逻辑”。

建议保留当前签名以避免改 grader，但在 Part B 明确写一句：

> `state` 参数用于让函数调用显式保留“edge 前 state”这个角色；本函数不再根据旧 state 重新计算新值，因为组合逻辑已经产生 `value_to_store`。

## 8. 环境层结果

grader import blocker 已修复，并新增维护者级“真实 kernel cwd”测试：从 `exercises/zh` 与 `exercises/en` 目录启动独立 Python 子进程，执行与 Notebook 相同的 repo-root bootstrap，再 import grader。

该测试已经进入 Python exercise infrastructure CI，当前通过。

## 9. Dry Run 结论

这一轮早期 9 份作业在**概念清晰度、手算桥梁、TODO 范围、grader 反馈**四方面已经可以使用；后续新增的 LSN-006~008 另在第 12 节复测。

下一步优先级应是：

1. 已修复真实 Jupyter 下的 grader import blocker；
2. 已解释 LSN-004 的 unused state 参数；
3. 已要求 LSN-003 自选 probe 数字，减少直接复用教材示例；
4. 后续再明确哪些作业是 consolidation、哪些承担 transfer/design，并决定是否进一步减少 LSN-002/011/012 从 lesson 直接复制答案的路径。

不建议现在为了“更难”而普遍增加代码量。


## 10. Platform 4（LSN-013~018）学生路径复测

### 10.1 范围与方法

在 LSN-013~018 建立后，再按普通学生路径做一轮独立复测：

1. 用 `scripts/start_exercise.py 13~18` 创建 `exercises/work/zh/` 作业副本；
2. 只依据 lesson 与题面完成 TODO，不读取 grader 隐藏向量；
3. 从头执行 Notebook，并确认 grader 输出；
4. 额外执行 Lesson 13 的 Yosys synthesis dry run；
5. 对课程代码单元格同时做中文与英文自动执行，防止本地化版本漂移。

结果：六份作业均得到 **3 / 3 groups passed**，即 **6 / 6 作业端到端通过**。

### 10.2 逐课结果

| Lesson | 学生路径结果 | 重点观察 |
|---|---|---|
| 13 | 通过 | 能区分 simulation / synthesis / timing；Yosys 摘要可读；无 Yosys 时给出可操作安装提示 |
| 14 | 通过 | 50,000,000 cycles/tick 与 26-bit counter 可由题面独立推出；grader 反馈已按概念正交化 |
| 15 | 通过 | host/PL state persistence 与 readback 顺序清楚；作业不提前使用 AXI/transaction 术语 |
| 16 | 通过 | compute 与 transfer 是分项成本比较，不冒充完整 elapsed-time 模型 |
| 17 | 通过 | burst grouping、断档与空请求边界清楚；不要求学生先懂 DDR PHY |
| 18 | 通过 | VALID/READY、stall、accepted beat 与 payload 稳定性规则一致 |

### 10.3 自动化 Student Dry Run

`lessons/checks/test_platform4_student_dryrun.py` 现在会同时执行中英文 LSN-013~018 的教学代码单元格：

- 中文与英文 Lesson 13：无 Yosys 时的提示；
- 中文与英文 Lesson 13：timing 输出格式；
- 中文与英文 Lesson 13：在安装 Yosys 的 RTL CI 中执行真实 synthesis；
- 中文与英文 Lesson 14~18：示例代码按学生看到的顺序执行并核对输出。

因此 Platform 4 的 student dry run 已从一次性人工检查变成持续 CI 保护。

### 10.4 Yosys 版本结果

Lesson 13 的 synthesis 摘要已分别在项目支持的两类环境中验证：

- Ubuntu CI：Yosys 0.33；
- OSS CAD Suite：Yosys 0.69。

两代 `stat` cell 输出格式不同，Notebook 解析器已兼容两者。学生默认只看到教学摘要，完整输出保存在 `yosys_log` 中。

### 10.5 Platform 4 Dry Run 结论

LSN-013~018 已满足当前作业册的核心要求：题意可独立理解、有效输入域明确、TODO 范围小、grader 不泄漏向量、Human Check 紧贴实现，并且真实学生路径 6/6 通过。

后续 Platform 5 新增作业时，应继续复用这一流程：**先人工 student dry run，再把可自动化的学生路径转成 CI。**


## 11. Platform 5（LSN-019~023）学生模拟阅读与 Dry Run

### 11.1 方法

本轮按“学生真正会走的路径”复测 LSN-019~023，而不是只调用 grader 函数：

1. 先按学生视角阅读 lesson 与 exercise prose，确认函数目标、输入、输出、有效域与 return order 可以从题面独立推出；
2. 检查 Before coding 示例与 grader 隐藏向量是否过度重合；发现 L19/L21/L23 有重合后已更换为独立数值；
3. 使用与 `scripts/start_exercise.py` 相同的 `create_work_copy()` 路径，在临时 repo 中创建 `exercises/work/<lang>/` personal copy；
4. 从 personal-work 目录执行 Notebook bootstrap，验证它能向上定位 `exercises/grader`；
5. 原始学生可见 code cell 全部先做 `compile()`，避免“grader cell 能跑但 TODO cell 本身语法已坏”的假通过；
6. 将只根据题面独立推导出的 reference implementation 放入 TODO 位置，然后按 Notebook code-cell 顺序执行，要求最终输出 `3 / 3 groups passed`；
7. 同时执行中英文 Lesson 19~23 的教学代码单元格，核对公开输出；
8. PDF 另做真实 render 视觉检查，不能只依赖自动像素判断。

维护者能看到 grader，因此这不是“盲测”。为避免这种权限污染学生视角，本轮额外把 pre-code 数值与 grader vectors 做了独立性检查，并修掉了发现的重合。

### 11.2 模拟阅读：只看题面能否解题

| Lesson | 从题面独立推导的核心步骤 | 学生摩擦判断 |
|---|---|---|
| 19 | 为所有 neuron 初始化 in/out degree；每条 `source→target` 分别递增 outgoing/incoming；保留 zero-degree entry | 低；主要风险是把 source/target 写反 |
| 20 | 原样复制 schema/source/converter version；`byte_count=len(payload)`；对 exact bytes 计算 SHA-256；返回 exact 5-key dict | 中低；需要理解 integrity 与 provenance 是不同维度 |
| 21 | 对每个 stage 算 `demand/capacity`；从 utilization dict 中找唯一最大值；不修改输入 dict | 中；Python 的 `max(..., key=...)` 可能需要语言层帮助，但工程语义清楚 |
| 22 | trace 先放 initial；每一步重新观察当前位置；小于 target 则 +1，大于则 -1，相等则 0；不能 overshoot | 低；reverse direction 已由 grader 单独保护 |
| 23 | `throughput=events/seconds`；`energy=watts*seconds`；`energy/event=energy/events` | 低；重点不是公式难度，而是不要把 metric calculation 误当成 benchmark comparability 结论 |

手算样例也能独立得到：

- L19：`[11,22,44,55]` 与 `11→22, 22→22, 44→11, 44→55` 得到 in-degree `{11:1,22:2,44:0,55:1}`、out-degree `{11:1,22:1,44:2,55:0}`；
- L21：A=`6/12=0.5`，B=`6/8=0.75`；两者 raw demand 相同，但 B utilization 更高；
- L22：initial=0、target=2、steps=4 得到 `[0,1,2,2,2]`；
- L23：1200 events / 0.4 s = 3000 events/s；15 W × 0.4 s = 6 J；6/1200 = 0.005 J/event。

### 11.3 Dry Run 结果

自动化学生路径覆盖：

- 5 课 × 2 语言的学生可见 code cell 全部可编译；
- 5 课 × 2 语言的 personal-work copy 路径全部从 `exercises/work/<lang>/` 目录执行；
- 10 / 10 workbooks 使用独立 reference implementation 后均得到 **3 / 3 groups passed**；
- 5 课 × 2 语言的 lesson example code 均按学生看到的顺序执行并匹配预期输出；
- Python exercise infrastructure 当前总结果：**129 passed, 2 skipped**。两个 skip 仍是没有 Yosys 的 Python job 中 Lesson 13 中英文真实 synthesis；RTL workflow 已实际覆盖该路径。

### 11.4 本轮 Dry Run 实际发现并修掉的问题

1. L19/L21/L23 的 pre-code 示例曾与隐藏 grader 数值重合，已全部换成独立数值；
2. L20 原标题暗示已经装入真实 MaleCNS subset，但实际只是 byte fixture，已改成“装入真实 subset 之前先验证 image”；
3. L20 prose 要求 provenance，但旧 exercise/manifest 没有 provenance，现已统一为 `schema_version/source_release/converter_version/byte_count/sha256`；
4. L20 grader 现在要求 exact key set，不再接受悄悄增加字段；
5. L19/L21 grader 现在执行“不修改输入”的书面 contract；
6. L22 grader 原本没有实际测试向左移动，现加入 `initial > target` reverse-direction oracle；
7. 原 student-flow 测试只注入函数后运行 grader cell，现已升级为 personal-work copy + compile all student code cells + 顺序执行整条 workbook code path。

### 11.5 图表交付验证

Platform 5 五张课程图已全部由 Mermaid 改为 inline SVG。最终 GitHub Actions webpdf 中检测到的专用 SVG-fill pixel 数分别为：

- L19：10,194
- L20：14,163
- L21：10,284
- L22：10,408
- L23：15,444

此外对最终 artifact 做了真实 PDF render 视觉检查：五张 SVG 均有完整节点、箭头与文字，没有空白 Mermaid 容器、破图图标、SVG 源码泄漏或裁切。

### 11.6 Platform 5 Dry Run 结论

修订后的 LSN-019~023 已满足当前学生作业路径标准：**题意可独立理解、pre-code 例子不泄漏 grader 数值、TODO contract 明确、grader 覆盖书面语义、personal work-copy 可运行、中英文路径一致、课程图在最终 PDF 中真实可见。**

## 12. LSN-006~008 独立作业补齐后的学生路径复测

### 12.1 设计边界

第 6~8 课仍然以真实 SystemVerilog、testbench 与 waveform 为课程主实验；新增 Exercise Notebook 不把 Python grader 冒充 HDL 工具链。三份作业分别只抽取一个可独立判定的语义：

- L06：一个 `posedge` 上同步低有效 reset 与 state 累加的结果；
- L07：`always_comb` 的 candidate/next-state 与 `always_ff` 的 register writeback 分层；
- L08：self-checking testbench 在采样之后如何用 oracle 找到第一次 mismatch。

所有手算例都与 grader 隐藏向量不同，并明确把 8-bit overflow 排除在这三份作业的正式判题范围之外；真实有限位宽行为继续由教学 RTL 与 RTL CI 观察。

### 12.2 只看题面的手算结果

- L06：`state=7, input=-2, rst_n=True` 得到 5；`rst_n=False` 的 edge 无论旧 state / input 是什么都写成 0。
- L07：`membrane_v=2, input=1, threshold=4` 得 `(candidate,next_v,spike_next)=(3,3,False)`；把 membrane 改成 3 后得到 `(4,0,True)`。
- L08：expected `[(1,F),(2,F),(0,T)]` 与 actual `[(1,F),(3,F),(0,T)]` 的第一次 mismatch index 是 1；若 actual 只有共同前缀两项，则第一个缺失 sample 的 index 是 2。

这些结果都可以从题面直接推出，不需要读取 grader。

### 12.3 自动化学生流

新增 `exercises/checks/test_rtl_bridge_student_flow.py`，对中英文三份作业分别：

1. 通过 `start_exercise.py` 语义建立个人 work copy；
2. 只注入依据题面写出的 reference implementation；
3. 按 Notebook code-cell 顺序执行；
4. 要求最终输出 `3 / 3 groups passed`。

因此 3 课 × 2 语言共 6 条个人作业路径进入持续 CI。当前 Python exercise infrastructure 结果为 **129 passed, 2 skipped**；两个 skip 仍是 Python job 中没有 Yosys 时的 Lesson 13 真实综合检查，RTL workflow 会实际执行该路径。

### 12.4 结论

LSN-006~008 现在既有独立作业册，也保留真实 RTL 实验。作业册负责检查语义理解，`check_rtl_learning.sh` / RTL workflow 负责检查 SystemVerilog compile、simulation、lint、synthesis 与 Lesson 8 VCD；两条路径互补，不互相替代。

