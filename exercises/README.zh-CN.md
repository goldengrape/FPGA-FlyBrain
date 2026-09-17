# FPGA FlyBrain 作业与检查

前四课采用同一种作业格式：**固定函数签名 + 小段 TODO + 公开的 pytest 检查 + Human Check**。

作业的目标不是考 Python 花活，而是确认你能把课程中的模型规则写成一个可测试的函数。除 TODO 区域外，尽量不要修改函数名、参数和返回值；这些接口本身就是本课规范的一部分。

## 怎么做

先同步环境：

```bash
uv sync --group dev
```

完成某一课的 TODO 后，只运行那一课的检查。例如第一课：

```bash
uv run pytest exercises/checks/check_lesson01.py -q
```

检查文件故意命名为 `check_lessonXX.py`，而不是普通的 `test_*.py`。这样未完成的学生作业不会被项目常规测试自动收集；只有你显式运行某课检查时，它才参与判定。

所有检查都是公开的。可以打开检查文件看每个测试在验证什么。课程希望你逐渐学会把测试当成 specification 的可执行版本，而不是把测试当成“老师藏起来的答案”。

## 什么叫“通过”

自动检查只判断**可执行行为**。如果所有测试通过，说明你的函数满足当前公开测试覆盖到的接口与规则；它不等于已经理解了概念。

每课还有 Human Check。这里不自动评分：你应该能在不让 AI 代答的情况下，用自己的话解释为什么代码和测试应该这样工作。如果自动测试通过，但无法解释某个测试为什么成立，这一课还没有完成。

AI 可以用于解释报错、比较两种实现、生成额外测试或审查代码。若 AI 直接写了 TODO，也要继续完成 Human Check，并至少能手算一个测试用例。

## 前四课

| Lesson | Starter code | 自动检查 | 主要检查内容 | Human Check |
|---|---|---|---|---|
| 01 | `lesson01_lif.py` | `check_lesson01.py` | leak、integration、`>=` threshold、reset | 手算一步 LIF；解释为什么 `V_rest` 是无输入固定点 |
| 02 | `lesson02_fixed_point.py` | `check_lesson02.py` | signed range、rounding、quantization、saturation | 解释 range/precision 权衡；说明 saturation 与 wraparound 为什么不同 |
| 03 | `lesson03_semantics.py` | `check_lesson03.py` | 冻结 v0 语义；构造 boundary/counterexample | 解释为什么随机测试可能漏掉 `>` 与 `>=` 的差异 |
| 04 | `lesson04_state_clock.py` | `check_lesson04.py` | combinational next-state、register update、clocked sequence | 指出一个 cycle 中哪些值属于旧 state、candidate、真正保存的 state |

也可以一次运行前四课：

```bash
uv run pytest \
  exercises/checks/check_lesson01.py \
  exercises/checks/check_lesson02.py \
  exercises/checks/check_lesson03.py \
  exercises/checks/check_lesson04.py -q
```

Starter code 初始状态包含 `NotImplementedError`，所以在没有完成 TODO 前检查失败是预期行为。

## 作业 1：从 Leak 到完整 LIF

文件：`exercises/lesson01_lif.py`

完成 `leak_step(...)` 与 `lif_step(...)`。第一课作业固定规则为：

- `V_next_candidate = V_rest + alpha * (V - V_rest) + input`；
- `candidate >= threshold` 就 spike；
- spike 后立即把保存状态设为 `reset`。

Human Check：给定 `V=-60, V_rest=-70, alpha=0.9, input=11, threshold=-50`，先不用代码手算 candidate voltage，并解释为什么这是一个 threshold boundary case。

## 作业 2：把小数放进有限位宽

文件：`exercises/lesson02_fixed_point.py`

完成 `signed_limits(total_bits)` 与 `quantize(x, total_bits, frac_bits)`。本课固定使用 Python `round()`，并采用 saturation overflow policy。测试覆盖正数、负数、格点值以及正负溢出。

Human Check：在 `total_bits=8, frac_bits=4` 时说明最小刻度；如果只增加 `frac_bits` 而总位宽不变，为什么精度增加的同时范围会缩小？

## 作业 3：让 specification 变成可区分的测试

文件：`exercises/lesson03_semantics.py`

按明确给出的 v0 contract 实现 `lif_step_v0(...)`，然后自己构造两个**区分测试（distinguishing probes）**：一个恰好落在 threshold 上，用来区分 `>=` 与 `>`；另一个让 `alpha * v + current` 与 `alpha * (v + current)` 得到不同结果。

检查程序不会要求某一组固定数字，而是检查你返回的例子是否真的能区分两种规则。

Human Check：解释为什么一万个普通随机样本也可能没有一个精心构造的 boundary case 更能说明 `>` 和 `>=` 的语义差异。

## 作业 4：把 next state 和 register state 分开

文件：`exercises/lesson04_state_clock.py`

完成 `combinational_step(...)`、`clock_edge(...)` 与 `run_clocked_accumulator(...)` 中的状态更新。检查会验证课程示例 `[1, 1, 1, 1, 2, 2]` 在 threshold 为 4 时的 state 与 spike 历史。

Human Check：解释为什么 `candidate_state=4` 和 `state_after=0` 可以在同一个 cycle 都是正确的，它们分别表示什么。
