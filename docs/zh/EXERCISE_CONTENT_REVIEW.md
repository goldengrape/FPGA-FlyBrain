# Exercise Notebook 内容审稿

## 1. 范围与结论

本轮审稿覆盖 LSN-001~005、LSN-009~012 共 9 份 Python 作业 Notebook。当前架构已经稳定，grader 语义与测试向量不在本轮重设计范围内。

总体判断：多数 Notebook 仍偏向“带说明的 starter code”，还没有完全达到正式电子作业集的教学密度。当前常见结构是“课程摘要 → 任务规则 → 一个代码单元 → grader → Human Check”。最需要补的是写代码前的手算、预测、表格推演或状态追踪。

目标结构应进一步变成：为什么做 → 本题目标 → 先不用代码 → 分步实现 → 自动检查 → Human Check → 可选延伸。

## 2. 全局修订原则

1. 每课增加至少一个“先不用代码”环节：手算一个数值更新、补 cycle/state 表、填 FIFO 操作轨迹、手工构造 source index，或追踪一次 event range 与 accumulator 变化。
2. 这些例子不能直接复用 grader 的隐藏测试向量，也不应把实现翻译成可直接抄写的伪代码答案。
3. 当一课包含两个以上独立概念时，题面应明确分成 Part A / Part B；可以仍然只在最后统一调用 grader。
4. threshold 比较方式、overflow policy、FIFO full 语义、source index 格式、是否允许修改输入对象等属于 specification，应明确写出，不算剧透。
5. Human Check 应尽量针对刚完成的实现，而不是简单重复课程 Exit Ticket。
6. 外部 grader 的目标是避免测试在作业页面无意中成为提示，并保持 Notebook 清爽；它不是防作弊安全边界。

## 3. 逐课审稿

| Lesson | 当前判断 | 主要问题 | 修订方向 |
|---|---|---|---|
| 01 | 需要明显加强 | 直接从公式跳到两个函数；没有手算桥梁；数学公式块目前渲染有问题 | 修复公式；增加一次 leak 手算与一次 threshold/reset 预测；拆成 Part A / B |
| 02 | 需要明显加强 | signed range、scale、round、saturation 一次进入代码，容易变成照课文写 Python | 增加一个不同于 grader 的 4-bit 小例子，先算整数码、表示值、最小刻度和溢出结果 |
| 03 | 基础很好 | frozen contract 与 distinguishing probes 是两类能力，但目前同层呈现 | 分成 Part A 实现 v0、Part B boundary probe、Part C update-order counterexample；要求解释为什么例子能区分规则 |
| 04 | 需要明显加强 | state / candidate / value_to_store / clock edge 概念密集；三个函数一起调试；starter 中 del candidate_state 没有教学价值 | 先给 cycle table；按 combinational → clock edge → sequence 分步；移除 del 写法 |
| 05 | 需要明显加强 | Python 中实现 NOT/AND/OR 容易退化成语法题 | 先从 truth table 预测，再实现 gates，最后组合 comparator + enable，强调逻辑关系而非 Python 语法 |
| 09 | 中等加强 | 缺少 address/state/write-back 的逐步 trace | 增加 address / before / input / after 表；拆 Part A addressed update、Part B round robin |
| 10 | 基础很好 | backpressure 语义清楚，但缺 ownership 操作轨迹 | 用符号事件 A/B/C 做 capacity=2 的 push/push/push/pop/retry 表，先填 queue 与 accepted |
| 11 | 基础很好但难度较高 | build_source_index 对初学者算法负担明显高于前几课 | 给一个不同于 grader 的小图，先手工填 start/count 与 records；特别解释 zero-fanout |
| 12 | 基础很好 | 从题面直接进入 process_one_spike；copy scaffold 的教学定位未说明 | 先手工追踪 range → weighted events → accum before/after；说明 list copy 是有意提供的 scaffold |

## 4. 特别问题

LSN-001：Exercise Notebook 中公式当前使用普通方括号包围，不能按预期渲染为数学块，应改成标准 LaTeX 数学定界符。

LSN-004：starter 中的 del candidate_state 虽不影响判题，但会引出与硬件状态无关的 Python 问题。应改为更自然的变量使用或下划线解包。

LSN-012：updated = list(target_accum) 建议保留。Python list copy 不是本课主要学习目标；本课真正要考的是 source range、weighted event 与 target update。grader 继续保护“不修改输入对象”的 API 契约即可。

## 5. 外部审核意见的取舍

保留《M》对测试完整性、迁移一致性与路径清理的判断。

《Q》提出的 Rich Display 与 cocotb 属于未来体验/RTL 基础设施建议，不进入本轮 Python 作业内容修订。也不采用“外部 grader = 防作弊”这一表述。

对 LSN-012 的 accum is not initial，也不扩展成“硬件必须使用 Python copy semantics”的普遍原则。它只是当前教学 Python API 的明确契约；正式 RTL 的 state-update 语义应由后续接口与时序规范定义。

## 6. 修订优先级

第一批：LSN-001、002、004、005。它们最容易让初学者感觉自己只是在把课文翻译成 Python。

第二批：LSN-009~012。重点补 trace/table，不改变现有契约。

LSN-003 只需结构化整理，不需要重写核心任务。

## 7. 完成标准

修订后的每份 Exercise Notebook 应满足：单独打开即可理解为什么做；至少有一个写代码前的手算、预测或 trace；例子不复用 grader 隐藏向量；TODO 只考本课核心概念；不直接展示 assert 或测试向量；Human Check 紧贴学生刚写的实现；不新增 grader 语义；中英文结构与要求同步。