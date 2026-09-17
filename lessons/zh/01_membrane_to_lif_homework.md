# 第一课作业｜代码怎样判定“写对了”？

这份页面是 **LSN-001《从膜电位到一个最小计算神经元》** 的作业与检查部分。

从这一课开始，课程会把一部分练习写成类似经典在线编程作业的形式：函数签名、参数、返回值和大部分脚手架已经给出，只留下很小的 TODO 区域。你的任务是把这一课刚学到的规则填进去。

```python
def leak_step(v, input_value, alpha, v_rest):
    # YOUR CODE STARTS HERE
    ...
    # YOUR CODE ENDS HERE
```

这样做有两个目的：把注意力放在本课概念，而不是 Python 文件组织或 API 设计；函数接口固定以后，可以用单元测试自动检查行为是否符合规范。

## 本课作业在哪里

Starter code：`exercises/lesson01_lif.py`

公开检查：`exercises/checks/check_lesson01.py`

先完成 `leak_step(...)`，再完成 `lif_step(...)`。尽量只修改 `YOUR CODE` 区域，不要改变函数签名。

## 怎么检查

在仓库根目录运行：

```bash
uv sync --group dev
uv run pytest exercises/checks/check_lesson01.py -q
```

刚开始看到失败是正常的，因为 TODO 里故意放着 `NotImplementedError`。随着函数完成，失败的测试应该逐渐变成通过。

测试检查的是几种**行为性质**：

- `V == V_rest` 且没有输入时，状态保持在静息电位；
- 高于或低于 `V_rest` 的状态都向静息电位衰减；
- 输入在 leak 后加入 candidate voltage；
- candidate voltage **恰好等于** threshold 时也产生 spike；
- spike 后保存状态等于 reset；
- 未达到 threshold 时不产生 spike。

所有检查都是公开的，你可以直接阅读 `check_lesson01.py`。以后课程会逐渐要求你自己写这样的测试。

## pytest 通过意味着什么

如果看到 `6 passed`，说明你的实现满足了这六个公开测试覆盖到的规则。它不能证明所有可能输入都绝对正确，也不能代替理解。

因此课程用两种检查互补：

- **Automated Check**：pytest 判断函数的可执行行为；
- **Human Check**：你能否不用 AI 代答，解释为什么这个行为应该成立。

第一课的 Human Check：

> 给定 `V=-60, V_rest=-70, alpha=0.9, input=11, threshold=-50`，手算一个时间步的 candidate voltage。它为什么正好是 threshold boundary case？如果规则从 `>=` 偷偷变成 `>`，结果会发生什么？

如果 pytest 全绿，但这个问题说不清楚，建议先不要进入下一课。

## 为什么检查文件叫 `check_...`

这些是学生作业检查，初始状态本来就应该失败。为了不让未完成作业污染以后正式工程代码的常规测试，我们不让 pytest 默认自动收集它们；需要显式给出文件路径才运行。

以后正式的 reference model、fixed-point model、RTL 验证会使用项目自己的 tests/testbench。两类测试使用相同的思维，但承担不同角色。

前四课完整作业说明见 `exercises/README.zh-CN.md`。
