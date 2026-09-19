# DOCUMENT_AUTHORITY — Documentation-First Specification Governance

## 0. Core principle

FPGA-FlyBrain follows a **documentation-first** engineering principle. Documentation is not commentary written after code; it is the formal carrier of requirements, design decisions, interfaces, verification rules, and implementation checkpoints.

> **Decide and document first, freeze the decision in tests second, implement it in code last.**

When documentation and implementation disagree, current code behavior does not automatically define correctness. First identify the approved specification for the relevant scope; unless that specification is intentionally changed, implementation must conform to documentation.

## 1. Documentation defines intended behavior

Formal documents define requirements and non-goals, FR/DP decomposition, module boundaries and interfaces, numeric/state/timing semantics, test oracles, implementation checkpoints, and TRACE.

Python, RTL, testbenches, scripts, and notebooks implement or teach those decisions. They must not silently create new formal system semantics.

Behaviors such as temporary bit width, wraparound/saturation, reset polarity/timing, FIFO-full behavior, interface fields, scheduling order, optimizations, or teaching simplifications do not become specification merely because existing code behaves that way.

## 2. Engineering documents have authority by scope

- **URD**: user needs, goals, constraints, non-goals, and success conditions.
- **ADD**: FR/DP decomposition, Independence Axiom, and coupling analysis.
- **MDD**: formal modules, interfaces, data structures, and numeric/state/timing contracts.
- **TDD**: approved contracts translated into test oracles, verification levels, and acceptance criteria.
- **RMD**: implementation slices, learning order, deliverables, and specification checkpoints; it must not override URD/ADD/MDD for implementation convenience.
- **TRACE**: mapping among requirements, FRs, DPs, modules, tests, RMD slices, and teaching artifacts; it exposes gaps rather than redefining semantics.

These documents are not one simplistic linear override stack. Resolve conflicts by first identifying the scope of the question.

## 3. Teaching documentation also has high priority

PROJECT_BIBLE, ROADMAP, LEARNING_PATH, lesson notebooks, exercise notebooks, and the glossary control the learning curve, concept order, and learner-facing explanation.

Teaching material must faithfully translate formal engineering facts, but it may use explicitly labeled teaching simplifications. Mark them clearly, for example: teaching artifact, not formal MOD-xxx, or overflow outside this lesson contract.

Teaching material must not silently alter formal engineering contracts; formal engineering work should also avoid breaking the Learning Independence Axiom merely for implementation convenience.

## 4. Tests are not substitutes for specification

Tests and graders are executable evidence of a specification, but they are not inherently authoritative.

When a test and a specification disagree, inspect:

1. whether the specification has been frozen;
2. whether the test oracle correctly translates the specification;
3. whether the implementation correctly implements the oracle.

Do not rewrite a specification merely to make CI green, and do not treat passing historical tests as proof that behavior has been formally approved.

## 5. Default change order

~~~text
requirement / design issue
        ↓
update Chinese + English formal documentation
        ↓
update or add test oracle
        ↓
update TRACE
        ↓
implement code / RTL
        ↓
CI / simulation / replay
~~~

For a pure bug fix where implementation violates an already-frozen contract, the contract need not be redesigned; the issue or commit should still identify which documented rule is being restored.

## 6. Resolving conflicts

Identify the authoritative scope first:

- user need → URD
- FR/DP decomposition → ADD
- module/interface/semantic → MDD
- expected result / acceptance → MDD + TDD
- whether something should be implemented now → RMD
- whether requirement-to-test/implementation coverage exists → TRACE
- whether a concept is introduced too early or overloads the course → PROJECT_BIBLE / LEARNING_PATH / RMD

A decision frozen at a specification checkpoint has authority over temporary code. An unfrozen question should remain an open decision rather than being silently answered by the current implementation.

## 7. Bilingual requirement

Chinese and English are two expressions of one specification, not two independent specifications. Changes to FR/DP/MOD/T/RMD IDs, interface contracts, numeric/timing semantics, acceptance criteria, current status, and this governance rule must remain synchronized.

A bilingual disagreement is a documentation defect and should be fixed rather than choosing one language as the hidden real specification.

## 8. AI-assisted engineering

AI may draft code, testbenches, documentation, and implementation options, but a runnable AI-generated implementation does not become project specification.

Changes to requirements, semantics, interfaces, numeric policy, test oracles, or architectural boundaries must enter documentation first and be confirmed by a human.

~~~text
human intent
→ documented contract
→ AI-assisted implementation
→ executable verification
→ human review
~~~

## 9. License

Unless a file or third-party dependency states otherwise, repository-authored documentation, notebooks, Python, SystemVerilog, testbenches, scripts, and other original content are licensed under the root MIT License.

The license governs how others may use the material. This document governs what counts as authoritative project truth.