# Exercise Notebook Content Review

## 1. Scope and conclusion

This review covers the nine Python Exercise Notebooks for LSN-001~005 and LSN-009~012. The architecture is stable; existing grader semantics and vectors are not being redesigned in this pass.

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