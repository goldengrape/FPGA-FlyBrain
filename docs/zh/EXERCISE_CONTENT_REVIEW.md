# Exercise Notebook 内容审稿

## 1. 范围与结论

最初一轮审稿覆盖 LSN-001~005、LSN-009~012 共 9 份 Python 作业 Notebook；后续章节继续覆盖 Platform 4、Platform 5，并在第 11 节补审新加入的 LSN-006~008 作业。当前 1~23 课均已有正式作业入口。

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

LSN-012：updated = list(target_accum) 建议保留。Python list copy 不是本课主要学习目标；本课真正要考的是 source range、weighted event 与 target update。原 grader 仅在零出度时检查返回对象不同，不能证明“不修改输入对象”的 API 契约；第 12 节记录补充检查。

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

## 8. 第二轮纵向审稿：难度曲线与重复度

### 8.1 难度曲线

作业难度不需要单调增加。当前更合理的曲线是：

| Lesson | 主要负担 | 相对难度 | 角色 |
|---|---|---:|---|
| 01 | 一步 LIF 算术 + threshold/reset | 低 | 起步 |
| 02 | 数值编码、rounding、saturation | 中 | 第一次数值工程 |
| 03 | 设计 distinguishing probe | 中高 | 从实现转向验证思维 |
| 04 | state / next-state / clock 分层 | 中高 | 第一次硬件时序思维 |
| 05 | truth table 与组合逻辑 | 低~中 | **有意的巩固谷**，为 RTL 腾出认知空间 |
| 06~08 | RTL / SystemVerilog / simulation + semantic workbook | 持续上升 | Python 作业检查语义翻译；真实 RTL lab 承担语法与验证负担 |
| 09 | time multiplexing / addressed state | 中 | 从 RTL 切回架构抽象的缓冲课 |
| 10 | bounded FIFO + ownership/backpressure | 中 | 事件运输语义 |
| 11 | sparse packing + lookup | 中高~高 | 当前最大算法跳级点 |
| 12 | 多数据结构端到端整合 | 高（概念） | 集成课，代码量不必比 11 更大 |

因此 LSN-005 和 LSN-009 比前一课“代码更容易”并不是问题。它们是有意降低语法/算法负担，让注意力转向新的硬件或架构概念。

### 8.2 Human Check 重复度

第二轮发现，部分 Human Check 虽然已经指向学生实现，但仍与 lesson 的 Human Check / Exit Ticket 高度重复。

修订原则：

- lesson Human Check：回答“概念是什么、为什么重要”；
- exercise Human Check：回答“我的实现中哪一段体现这个概念、如果写错会出现什么症状、怎样定位”。

重点调整 LSN-002、003、005、009、011。

### 8.3 LSN-011 的脚手架边界

LSN-011 可以提供“实现规划”，例如提醒学生最终需要完成：

1. 为每个 source 确定自己的记录组；
2. 按 source 顺序形成 contiguous records；
3. 在每组开始时记录 start，并记录 count；
4. runtime lookup 只依赖 start/count。

这属于数据布局的设计分解，不直接给出 Python 语句，也不泄露 grader 向量。它能降低不必要的算法跳级，同时保留核心思考。

### 8.4 第二轮修订目标

- 不提高所有作业的代码难度；
- 保留 05、09 的巩固作用；
- 把 Human Check 从知识复述改成实现诊断；
- 为 11 增加有限脚手架；
- 不修改 grader 语义和测试向量。


## 9. Platform 4 作业内容审稿：LSN-013~018

### 9.1 总体结论

第三轮内容审稿覆盖 LSN-013~018 六份 Python Exercise Notebook。与早期作业相比，这一组已经稳定采用：

> 先不用代码 → 函数语义契约 → 有效输入域 → 小范围 TODO → 外部 grader → Human Check

六份作业均经真实学生路径复测并通过，grader 参考实现与典型错误实现也有维护者测试保护。本轮不修改 grader 语义或隐藏测试向量。

### 9.2 逐课判断

| Lesson | 作业定位 | 审稿结论 |
|---|---|---|
| 13 | timing budget consolidation | 合适；把 critical path、slack、pass/fail 从工具输出还原成可手算语义 |
| 14 | board-clock planning | 合适；counter width 的 2 的幂边界由 grader 独立检查 |
| 15 | host/PL state ordering | 合适；重点是 persistent state/readback，不提前学习总线协议 |
| 16 | data-movement cost comparison | 合适；已明确只是分项成本模型，不把较大项当系统总时间 |
| 17 | burst/access-pattern planning | 合适；只训练连续地址分组与启动成本，不模拟 DDR controller |
| 18 | VALID/READY acceptance | 合适；只抽取协议合规 trace 中真正 accepted beat，不让学生实现完整 AXI |

### 9.3 本轮修订原则

- 作业首次出现的术语不能抢跑后续 lesson；因此 LSN-015 作业使用“读写往返 / read-write roundtrip”，不再提前使用 `transaction` 或 AXI。
- grader feedback group 应尽量对应一个概念；LSN-014 已把 cycles-per-tick、counter width、minimum width 解耦。
- lesson 与 exercise 可以使用简化性能模型，但必须明确模型边界；LSN-016 已把 compute/transfer 定义为 component-cost comparison。
- 学生可见 grader 继续只报告概念组，不显示隐藏输入和期望答案。

### 9.4 完成状态

LSN-013~018 六份作业均完成内容审稿与学生 dry run。对应执行记录见 `EXERCISE_STUDENT_DRY_RUN.md` 第 10 节。


## 10. Platform 5 作业内容审稿：LSN-019~023

本轮按客观审稿结果修订，不以 CI 绿灯替代题意与 oracle 审查。

- **L19**：directed degree 任务保留；grader 新增“不修改输入 list”检查；pre-code 数值与隐藏向量解耦。
- **L20**：标题改为“装入真实 MaleCNS 子图之前”；manifest 从仅 integrity 修正为 integrity + provenance，统一要求 `schema_version/source_release/converter_version/byte_count/sha256`，grader 要求 exact key set。
- **L21**：pre-code 数值与 grader 解耦；grader 新增输入 dict 不可修改检查；hotspot 明确为 supporting term。
- **L22**：grader 新增 reverse-direction oracle，拒绝只会向右移动的实现。
- **L23**：pre-code benchmark 数值与 grader 解耦；energy/event 明确为 supporting metric。

Platform 5 五张课程结构图全部迁移为 Markdown inline SVG，不再使用 Mermaid。PDF CI 使用 SVG 专用填充色验证最终渲染，且已对生成 artifact 做真实视觉检查。

对应学生路径执行记录见 `EXERCISE_STUDENT_DRY_RUN.md` 第 11 节。

## 11. LSN-006~008 补齐作业内容审稿

三份新增作业刻意不让学生在 Notebook 里“用字符串写 SystemVerilog”，也不把 HDL simulator 变成 Python 作业的隐藏系统依赖。它们选择与课程主概念一一对应、且可用纯函数判定的语义层任务。

| Lesson | 作业定位 | 内容审稿结论 |
|---|---|---|
| 06 | one-edge RTL semantics | 合适；用一个 rising edge 把 module/register/reset 语义落到可手算更新，不提前考 overflow policy |
| 07 | combinational vs sequential split | 合适；Part A / B 明确区分 candidate/next-state 与 register writeback，threshold equality 单独成为边界 |
| 08 | self-checking oracle | 合适；比较 sampled trace、first mismatch 与 length mismatch，明确不替代 clock generation / RTL simulation |

共同约束：

- 每题都先手算，且例子与 hidden grader vector 解耦；
- TODO 前明确输入、输出和 tuple 返回顺序；
- grader 按 3 个概念组反馈，不显示隐藏向量；
- 维护者负向测试覆盖忽略 reset、严格 `>` threshold、只比较共同前缀/错误 mismatch 定位；
- 中英文代码单元保持一致；
- 真实 `rtl/learning/`、`tb/learning/` 和 `check_rtl_learning.sh` 仍是 HDL 行为验证的正式教学路径。

这组三课因此不再是作业体系中的空档，同时也没有把 Python 层扩大成“假的 RTL 仿真器”。

## 12. LSN-010~012 判题契约复查（2026-09-20）

本次复查发现，原测试会接受三类违反现有题目契约的实现：原地修改 FIFO 输入、未经 source 分组直接复制 records、用赋值代替 accumulator 累加。修订只补充已有契约的测试，不改变题目接口或正式 RTL 语义。

- **LSN-010**：新增输入保持不变检查，覆盖空队列、未满/已满 push 与空/非空 pop；独立拒绝原地 push 和原地 pop。
- **LSN-011**：用 source 交错的连接检查重新分组、精确 start/count、零出度和组内原始顺序；拒绝直接复制 records 或额外按 target 排序。
- **LSN-012**：新增非零初值、重复 target 和负权重检查；比较调用前后的输入快照，并检查返回新的 accumulator 列表。零出度检查也使用调用前的快照，避免输入和输出同时被修改却误判通过。

维护者测试包含正确实现和上述典型错误实现。新增回归断言在修订前使三项课程测试失败；修订后 `uv run pytest exercises/checks/test_graders.py -q` 的 27 项测试通过。这证明这些具体错误会被拒绝，不代表穷尽所有输入。

