# DOCUMENT_AUTHORITY — 文档优先与规范治理

## 0. 核心原则

FPGA-FlyBrain 采用 **documentation-first** 工程原则：文档不是代码的事后说明，而是需求、设计、接口、验证和实施决策的正式载体。

> **先决定并写清楚，再让测试固化，最后让代码实现。**

如果文档与实现冲突，不能因为“代码已经这样运行”就默认代码定义了正确行为。先确定当前 scope 下已经批准的规范；在没有明确修改规范之前，实现应追随文档。

## 1. 文档定义 intended behavior

正式文档负责定义：需求与非目标、FR/DP 分解、模块边界与接口、数值/状态/时序语义、test oracle、实施 checkpoint 与 TRACE。

代码、RTL、testbench、脚本和 Notebook 是这些决定的实现或教学投影，不能偷偷创造新的正式系统语义。

以下行为不能仅因为现有代码这样写就自动升级为 specification：临时 bit width、wraparound/saturation、reset polarity/timing、FIFO full 行为、接口字段、调度顺序、性能优化、教学简化。

## 2. 工程文档按 scope 分工

- **URD**：用户需求、目标、约束、非目标和成功条件。
- **ADD**：FR/DP 分解、Independence Axiom、耦合分析。
- **MDD**：正式模块、接口、数据结构以及数值/状态/时序 contract。
- **TDD**：把已批准 contract 转成 test oracle、verification level 和 acceptance criteria。
- **RMD**：实现 slice、学习顺序、交付物和 specification checkpoint；不得为方便实现而覆盖 URD/ADD/MDD。
- **TRACE**：连接需求、FR、DP、模块、测试、RMD 与教学内容；负责映射和发现缺口，不重新定义语义。

文档之间不是简单的线性覆盖关系；冲突时先判断问题属于哪个 scope。

## 3. 教学文档同样具有高优先级

PROJECT_BIBLE、ROADMAP、LEARNING_PATH、课程 Notebook、Exercise Notebook 和 Glossary 共同决定学习曲线、概念出现顺序与解释方式。

教学内容必须忠实翻译正式工程事实，但可以使用明确标注的 teaching simplification。教学简化必须显式写清，例如：teaching artifact、not formal MOD-xxx、overflow outside this lesson contract。

教学文档不能静默修改正式 engineering contract；正式工程文档也不应为了实现方便破坏 Learning Independence Axiom。

## 4. 测试不是规范的替代品

测试和 grader 是规范的可执行证据，但不是天然正确。

当 test 与 specification 冲突时，依次检查：

1. specification 是否已经冻结；
2. test oracle 是否正确翻译 specification；
3. implementation 是否正确实现 oracle。

不得为了让 CI 变绿而反向修改规范，也不得因为历史测试通过就宣布某个行为已经被正式批准。

## 5. 默认变更顺序

~~~text
需求 / 设计问题
      ↓
更新中英文正式文档
      ↓
更新或新增 test oracle
      ↓
更新 TRACE
      ↓
实现 code / RTL
      ↓
CI / simulation / replay
~~~

如果只是实现违反了已经冻结的规范，可以直接修 bug；但 commit / issue 应明确指出恢复的是哪条既有 contract。

## 6. 规范冲突处理

先按 scope 找权威来源：

- 用户需求 → URD
- FR/DP 分解 → ADD
- module/interface/semantic → MDD
- expected result / acceptance → MDD + TDD
- 当前是否应该实现 → RMD
- 是否存在需求到测试/实现的闭环 → TRACE
- 概念是否过早、课程是否过载 → PROJECT_BIBLE / LEARNING_PATH / RMD

已经在 specification checkpoint 冻结的决定优先于临时代码。尚未冻结的问题应记录为 open decision，而不是假装现有实现已经给出正式答案。

## 7. 双语要求

中文和英文是同一套规范的两个表达版本，不是两个独立 specification。涉及 FR/DP/MOD/T/RMD ID、接口 contract、数值/时序语义、acceptance criteria、当前状态和本治理规则的修改必须同步。

若双语版本冲突，应视为文档缺陷并修复，不应偷偷选择其中一种语言作为真正规范。

## 8. AI-assisted engineering

AI 可以起草代码、testbench、文档和实现方案，但不能因为生成了一个能运行的实现，就把它升级为项目规范。

涉及需求、语义、接口、数值 policy、test oracle 或架构边界的变化，必须先进入文档并由人确认。

~~~text
human intent
→ documented contract
→ AI-assisted implementation
→ executable verification
→ human review
~~~

## 9. 许可证

除非某个文件或第三方依赖另有明确许可声明，本仓库的原创文档、Notebook、Python、SystemVerilog、testbench、脚本和其他内容统一采用根目录 MIT License。

许可证决定别人可以怎样使用材料；本文档决定项目内部什么算正式事实。