# Exercise Notebook Content Review

## 1. Scope and conclusion

The initial review covered the nine Python Exercise Notebooks for LSN-001~005 and LSN-009~012. Later sections cover Platforms 4 and 5, and Section 11 reviews the newly added LSN-006~008 workbooks. The current Lesson 01–23 sequence now has a formal exercise entry for every lesson.

Overall, most notebooks still read more like documented starter code than a formal electronic workbook. The missing teaching layer is pre-code reasoning: a hand calculation, prediction, table trace, state trace, or small manual data-layout exercise.

The target flow is: why → objective → work without code first → staged implementation → automatic check → Human Check → optional extension.

## 2. Global revision rules

1. Add at least one pre-code reasoning activity to every exercise.
2. Do not reuse hidden grader vectors and do not convert the implementation into near-copyable pseudocode.
3. Split tasks into Part A / Part B when they cover distinct concepts, even if one final grader remains.
4. Threshold rules, overflow policy, FIFO-full behavior, data format, and mutation rules are specifications and should remain explicit.
5. Human Checks should refer to the implementation just completed rather than simply repeat the lesson Exit Ticket.
6. External graders are used to avoid accidental solution hints and keep the workbook clean; they are not an anti-cheating security boundary.

## 3. Lesson-by-lesson review

| Lesson | Assessment | Main issue | Revision direction |
|---|---|---|---|
| 01 | Significant revision | Jumps from formula directly to two functions; no hand calculation; math block rendering is broken | Fix math rendering; add leak calculation and threshold/reset prediction; split Part A/B |
| 02 | Significant revision | Signed range, scaling, rounding, and saturation enter code at once | Add a small 4-bit hand example distinct from grader vectors before implementation |
| 03 | Strong foundation | Frozen contract and distinguishing probes are different skills but presented at one level | Split v0 implementation, boundary probe, and update-order counterexample; require explanation |
| 04 | Significant revision | Too many state concepts and three functions at once; del candidate_state is distracting | Add a cycle table; stage combinational → clock edge → sequence; remove the del pattern |
| 05 | Significant revision | Python NOT/AND/OR risks becoming a syntax exercise | Start from truth-table prediction, then gates, then comparator + enable composition |
| 09 | Moderate revision | Missing explicit address/state/write-back trace | Add address/before/input/after table; split addressed update and round robin |
| 10 | Strong foundation | Needs an ownership/backpressure trace | Use symbolic A/B/C events with push/push/push/pop/retry and predict queue + accepted |
| 11 | Strong but demanding | build_source_index is a larger algorithmic jump | Add a small hand-packed graph with start/count and records, including zero fanout |
| 12 | Strong foundation | Goes directly from specification to process_one_spike | Add a manual range → weighted events → accumulator trace; state that list-copy scaffold is intentional |

## 4. Specific issues

LSN-001 uses plain square brackets around the formula instead of proper math delimiters.

LSN-004 contains del candidate_state in the starter sequence. It is behaviorally harmless but pedagogically irrelevant.

LSN-012 should keep updated = list(target_accum). Python list-copy mechanics are not the lesson objective; the lesson should focus on routing and target updates.

## 5. Treatment of external review comments

The maintainer review's findings on test completeness and migration fidelity are retained. Rich display and cocotb are future experience/RTL-infrastructure ideas and are outside this Python-content pass.

The grader is not framed as an anti-cheating system. Likewise, the LSN-012 copy check is a teaching-Python API contract, not a universal claim about hardware state semantics.

## 6. Priority

First revise LSN-001, 002, 004, and 005. Then revise LSN-009~012 mainly by adding traces and tables. LSN-003 needs structural refinement rather than a rewrite.

## 7. Definition of done

Each revised Exercise Notebook should stand on its own, include a pre-code calculation/prediction/trace, avoid hidden grader vectors, keep TODOs focused, keep asserts out of the notebook, tie Human Checks to the implementation, preserve grader semantics, and keep Chinese/English structure synchronized.

## 8. Second longitudinal review: difficulty curve and repetition

### 8.1 Difficulty curve

Exercise difficulty does not need to increase monotonically.

| Lesson | Main load | Relative difficulty | Role |
|---|---|---:|---|
| 01 | One-step LIF arithmetic + threshold/reset | Low | Entry |
| 02 | Numeric encoding, rounding, saturation | Medium | First numerical-engineering task |
| 03 | Designing distinguishing probes | Medium-high | Shift from implementation to verification thinking |
| 04 | State / next-state / clock separation | Medium-high | First hardware-timing mindset |
| 05 | Truth tables and combinational logic | Low-medium | **Intentional consolidation valley** before RTL |
| 06~08 | RTL / SystemVerilog / simulation + semantic workbook | Rising | Python workbooks check semantic translation; real RTL labs carry syntax and verification load |
| 09 | Time multiplexing / addressed state | Medium | Architecture reset after the RTL block |
| 10 | Bounded FIFO + ownership/backpressure | Medium | Event-transport semantics |
| 11 | Sparse packing + lookup | Medium-high to high | Largest current algorithmic jump |
| 12 | End-to-end integration of data structures | High conceptually | Integration lesson; code need not exceed Lesson 11 |

The lower code difficulty of Lessons 5 and 9 is therefore intentional rather than a defect.

### 8.2 Human Check repetition

Some Exercise Human Checks still overlap too heavily with lesson Human Checks and Exit Tickets.

Revised distinction:

- lesson Human Check: what the concept means and why it matters;
- exercise Human Check: where the concept appears in the learner's implementation, what a mistake would look like, and how to diagnose it.

Lessons 2, 3, 5, 9, and 11 receive targeted revisions.

### 8.3 Scaffolding boundary for Lesson 11

Lesson 11 may provide implementation planning without giving Python pseudocode:

1. determine each source's record group;
2. make records contiguous in source order;
3. record start and count for each group;
4. make runtime lookup depend only on start/count.

This reduces an unnecessary algorithmic cliff without exposing grader vectors or a copyable implementation.

### 8.4 Second-pass goals

- do not increase code difficulty everywhere;
- preserve Lessons 5 and 9 as consolidation steps;
- shift Human Checks from recall to implementation diagnosis;
- add bounded scaffolding to Lesson 11;
- preserve grader semantics and test vectors.


## 9. Platform 4 exercise-content review: LSN-013~018

### 9.1 Overall conclusion

The third content-review pass covers the six Python Exercise Notebooks for LSN-013~018. Compared with the early workbook set, this block consistently uses:

> work without code first → semantic contract → valid-input domain → small TODO → external grader → Human Check

All six exercises passed an end-to-end student-path rerun. Maintainer tests also protect the reference implementations and representative conceptual mistakes. This review does not change hidden grader vectors or grader semantics.

### 9.2 Lesson-by-lesson assessment

| Lesson | Exercise role | Review conclusion |
|---|---|---|
| 13 | timing-budget consolidation | Appropriate; turns tool output into hand-checkable critical-path/slack/pass-fail semantics |
| 14 | board-clock planning | Appropriate; the power-of-two counter-width boundary is checked independently |
| 15 | host/PL state ordering | Appropriate; focuses on persistent state/readback without pre-teaching bus protocols |
| 16 | data-movement cost comparison | Appropriate; explicitly a component-cost model rather than total system elapsed time |
| 17 | burst/access-pattern planning | Appropriate; trains contiguous grouping and startup cost without pretending to model a DDR controller |
| 18 | VALID/READY acceptance | Appropriate; extracts accepted beats from protocol-compliant traces without implementing full AXI |

### 9.3 Revision rules from this pass

- Exercise vocabulary must not pull later lessons forward; LSN-015 now uses “read/write roundtrip” rather than early `transaction` or AXI terminology.
- Grader feedback groups should map to one concept where practical; LSN-014 separates cycles-per-tick, counter width, and minimum width.
- Simplified performance models must state their boundary; LSN-016 now frames compute/transfer as component-cost comparison.
- Student-facing graders continue to report conceptual groups without exposing hidden inputs or expected outputs.

### 9.4 Completion status

All six LSN-013~018 exercises now have recorded content review and student dry-run evidence. See Section 10 of `EXERCISE_STUDENT_DRY_RUN.md` for execution details.


## 10. Platform 5 exercise-content review: LSN-019~023

This pass applies the objective review findings rather than treating green CI as a substitute for task/oracle review.

- **L19** keeps the directed-degree task; the grader now enforces input-list immutability and pre-code values are independent of hidden vectors.
- **L20** is explicitly before a real MaleCNS subset load. The manifest is aligned on integrity + provenance with `schema_version/source_release/converter_version/byte_count/sha256`, and the grader requires the exact key set.
- **L21** uses pre-code values distinct from grader vectors, enforces input-dictionary immutability, and labels hotspot as a supporting term.
- **L22** adds a reverse-direction oracle and rejects right-only movement.
- **L23** uses independent pre-code benchmark values and labels energy/event as a supporting metric.

All five Platform 5 structural diagrams were migrated to Markdown inline SVG; Mermaid is no longer used in LSN-019~023. PDF CI verifies the dedicated SVG fill in final output, and the generated artifact has also been visually inspected.

See Section 11 of `EXERCISE_STUDENT_DRY_RUN.md` for the learner-path execution record.

## 11. LSN-006~008 completed-workbook content review

The three new workbooks deliberately avoid asking learners to write SystemVerilog as Python strings, and they do not make an HDL simulator a hidden dependency of the Python exercise path. Instead, each selects one pure semantic task that maps directly to the lesson's primary concept.

| Lesson | Exercise role | Content-review conclusion |
|---|---|---|
| 06 | one-edge RTL semantics | Appropriate; turns module/register/reset meaning into one hand-checkable rising-edge update without prematurely freezing overflow policy |
| 07 | combinational vs sequential split | Appropriate; Part A/B cleanly separates candidate/next-state from register writeback, with threshold equality as an explicit boundary |
| 08 | self-checking oracle | Appropriate; checks sampled trace, first mismatch, and length mismatch while explicitly not replacing clock generation or RTL simulation |

Shared constraints:

- every workbook starts with hand work using values distinct from hidden grader vectors;
- each TODO states inputs, outputs, and tuple return order when applicable;
- graders report three conceptual groups without exposing hidden vectors;
- maintainer negative tests cover ignored reset, strict-`>` threshold behavior, prefix-only checking, and incorrect mismatch selection;
- Chinese and English code cells remain aligned;
- the real `rtl/learning/`, `tb/learning/`, and `check_rtl_learning.sh` path remains the teaching authority for HDL behavior.

This closes the exercise-gap for Lessons 6–8 without turning the Python layer into a fake RTL simulator.

