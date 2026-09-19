# Exercise Notebook 学生视角 Dry Run

## 1. 方法

本轮把自己限制在“普通学生”视角：

- 只阅读中文 lesson 与对应 Exercise Notebook；
- 先完成手算 / trace；
- 再独立填写 TODO；
- 不先查看 grader 源码或具体测试向量；
- 完成解答后，才用现有 grader 契约验证是否通过；
- 同时记录环境、题意、回翻教材、提示密度与调试反馈中的摩擦。

9 份 Python 作业（LSN-001~005、009~012）都能依据教材和题面独立完成。按题面得到的实现全部通过当前 grader。

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

这是本轮唯一的 blocker，应优先修复。修复目标是：学生按 README 正常 `uv sync` + `uv run jupyter lab` 后，从任意 lesson/exercise 子目录打开 Notebook 都能稳定 import grader，不要求学生理解或手工修改 `sys.path`。

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

## 8. 环境层建议

优先修复 grader import，然后增加一个维护者级“真实 kernel cwd”测试：从 `exercises/zh` 或 `exercises/en` 目录启动 Python/kernel，确认 grader import 可用。

这比目前只从 pytest 项目根目录测试更接近学生真实路径。

## 9. Dry Run 结论

当前作业在**概念清晰度、手算桥梁、TODO 范围、grader 反馈**四方面已经可以使用；9 份题目都能独立解出并通过 grader。

下一步优先级应是：

1. 修复真实 Jupyter 下的 grader import blocker；
2. 解释 LSN-004 的 unused state 参数；
3. 明确哪些作业是 consolidation，哪些要承担 transfer/design；
4. 再决定是否减少 LSN-002/003/011/012 从 lesson 直接复制答案的路径。

不建议现在为了“更难”而普遍增加代码量。
