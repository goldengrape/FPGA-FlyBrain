# Exercise Notebook Student-Perspective Dry Run

## 1. Method

This pass deliberately used a student perspective:

- read only the lesson and matching Exercise Notebook first;
- complete the hand calculation / trace;
- implement TODOs independently;
- do not inspect grader vectors before solving;
- validate against the current grader only after producing the solutions;
- record friction in environment setup, task interpretation, lesson lookup, hint density, and debugging.

All nine Python exercises (LSN-001~005 and LSN-009~012) were solvable from the lesson and assignment text. The independently derived implementations passed all current grader groups.

## 2. Most important finding: grader imports are fragile in a real Jupyter cwd

Exercise Notebooks live under `exercises/en/*.ipynb`.

Jupyter Server's FileContentsManager normally starts the kernel in the directory containing the notebook. A learner opening an exercise therefore commonly gets a cwd such as `<repo>/exercises/en`.

The check cells currently use imports such as:

```python
from exercises.grader.lesson01 import check
```

The current project is not installed as an importable package by `pyproject.toml`, and the pytest `pythonpath = ["."]` setting affects pytest only. A plain `uv sync` does not make the repository root importable from a Python process started in `exercises/en`.

A real learner can therefore reach the final check cell and see:

```text
ModuleNotFoundError: No module named 'exercises'
```

This was the only blocker found in the dry run, and it was fixed in the same revision cycle. Each grader check cell now locates the repository root by walking upward from the current working directory and inserts that root into sys.path before importing the grader. A maintainer regression test now launches a separate Python process from both exercises/zh and exercises/en to verify the same path.

## 3. Lesson-by-lesson dry run

| Lesson | Pre-code work | Independently solvable? | Likely lesson lookup | Student friction |
|---|---|---|---|---|
| 01 | Strong | Yes | Usually unnecessary | Low |
| 02 | Effective 5-bit example | Yes | Signed-range / bit-shift formula | Low-medium; lesson already contains near-complete quantize code |
| 03 | Strong verification exercise | Yes | Easy to find ready-made probes in lesson | Medium |
| 04 | Strong cycle table | Yes | Usually unnecessary | Medium; state parameter in clock_edge is intentionally unused |
| 05 | Clear truth-table work | Yes | No | Low; appropriate consolidation before RTL |
| 09 | Clear address trace | Yes | No | Low-medium |
| 10 | Excellent ownership/backpressure trace | Yes | Rarely | Low; one of the strongest independent exercises |
| 11 | Planning greatly reduces the algorithmic cliff | Yes | Nested-loop example | Medium-high; lesson also exposes most of the construction algorithm |
| 12 | Natural range/event/accumulator trace | Yes | Bridge code is very close to TODO | Medium |

## 4. Hand-work verification

The dry-run hand calculations were internally consistent and use values distinct from the grader vectors.

## 5. Grader experience

After independently producing solutions, all groups for Lessons 01, 02, 03, 04, 05, 09, 10, 11, and 12 passed.

The conceptual-group feedback level is appropriate for self-study. The main grader-experience issue is the import-path blocker, not the feedback text.

## 6. Lesson code as an answer source

This is an open-book self-study course, so lesson examples should remain executable. However, the dry run suggests distinguishing:

- reproduction / consolidation exercises, such as Lesson 5;
- transfer / design exercises, where learners should adapt or construct something new.

Direct answer paths are strongest in Lessons 2, 3, 11, and 12. Do not remove the lesson examples; instead consider small transfer requirements in those exercises.

## 7. Lesson 4 API friction

`clock_edge(state, value_to_store)` correctly needs only `value_to_store` to produce the new state. The unused `state` parameter is pedagogically defensible because it makes before/after state explicit, but beginners may think they forgot to use an argument.

Keep the signature for grader compatibility and explicitly explain why state is present but not recomputed from.

## 8. Environment result

The grader import blocker has been fixed. Maintainer tests now start an independent Python subprocess from `exercises/zh` and `exercises/en`, run the same repository-root bootstrap used by the notebooks, and verify that the grader can be imported. This check is part of the Python exercise infrastructure CI and currently passes.

## 9. Conclusion

The exercises are usable in terms of conceptual clarity, pre-code reasoning, TODO scope, and grader feedback. All nine can be solved and pass.

Priorities after this dry run:

1. the real-Jupyter grader import blocker is fixed;
2. Lesson 4 now explains the intentionally unused state parameter;
3. Lesson 3 now requires learner-chosen probe values rather than direct reuse of lesson examples;
4. the remaining design question is how strongly Lessons 2, 11, and 12 should shift from reproduction toward transfer/design.

Do not increase code volume simply to make the assignments feel harder.


## 10. Platform 4 (LSN-013~018) student-path rerun

### 10.1 Scope and method

After LSN-013~018 were established, a second student-path pass was performed:

1. create personal work copies with `scripts/start_exercise.py 13~18`;
2. solve TODOs from the lesson and exercise text without reading hidden grader vectors;
3. execute each Notebook end to end and inspect grader output;
4. run the real Yosys synthesis dry run in Lesson 13;
5. execute both Chinese and English lesson code cells automatically to protect localized variants.

Result: all six exercises reported **3 / 3 groups passed**, so the end-to-end exercise path passed **6 / 6**.

### 10.2 Lesson-by-lesson result

| Lesson | Student-path result | Main observation |
|---|---|---|
| 13 | Pass | Simulation/synthesis/timing separation is clear; Yosys summary is readable; missing-Yosys path gives actionable setup guidance |
| 14 | Pass | 50,000,000 cycles/tick and a 26-bit counter follow directly from the text; grader feedback is concept-orthogonal |
| 15 | Pass | Host/PL persistent state and readback ordering are clear; the exercise no longer pulls AXI/transaction vocabulary forward |
| 16 | Pass | Compute and transfer are component-cost comparisons, not a fake total elapsed-time model |
| 17 | Pass | Burst grouping, gaps, and empty input are clear without requiring DDR-PHY knowledge |
| 18 | Pass | VALID/READY, stall, accepted-beat, and payload-stability semantics are consistent |

### 10.3 Automated student dry run

`lessons/checks/test_platform4_student_dryrun.py` now executes the teaching code cells for both Chinese and English LSN-013~018:

- Lesson 13 missing-Yosys guidance in both languages;
- Lesson 13 beginner-readable timing output in both languages;
- real Lesson 13 synthesis in the RTL CI when Yosys is installed;
- Lesson 14~18 example code and expected outputs in both languages.

The Platform 4 dry run is therefore continuous CI protection rather than a one-off review.

### 10.4 Yosys version coverage

The Lesson 13 synthesis summary has been exercised against both supported environment families:

- Ubuntu CI: Yosys 0.33;
- OSS CAD Suite: Yosys 0.69.

Their `stat` cell formats differ, and the Notebook parser supports both. Learners see a concise teaching summary while the full log remains available in `yosys_log`.

### 10.5 Platform 4 conclusion

LSN-013~018 meet the current workbook bar: standalone task meaning, explicit valid-input domains, small TODO scope, non-leaking graders, implementation-focused Human Checks, and a 6/6 end-to-end student path.

Future Platform 5 exercises should reuse the same pattern: **manual student dry run first, then move automatable student-path checks into CI.**


## 11. Platform 5 (LSN-019~023) simulated reading and dry run

### 11.1 Method

This pass follows the path a learner actually uses rather than calling grader functions directly:

1. read lesson/exercise prose from the learner perspective and verify that function purpose, inputs, outputs, valid domain, and return order are independently inferable;
2. compare pre-code examples against hidden grader vectors; L19/L21/L23 overlaps found during review were replaced with distinct values;
3. use the same `create_work_copy()` path as `scripts/start_exercise.py` to create personal `exercises/work/<lang>/` copies inside a temporary repository;
4. execute from the personal-work directory so the notebook bootstrap must walk upward and discover `exercises/grader`;
5. compile every learner-visible code cell before inserting a solution, preventing a false pass where the grader cell works but the TODO cell is syntactically broken;
6. insert reference implementations derived from the written task contract, then execute workbook code cells in order and require `3 / 3 groups passed`;
7. execute the teaching code cells for both Chinese and English Lessons 19~23 and check the public outputs;
8. render the produced PDFs and inspect them visually rather than relying only on automated pixel checks.

The reviewer can see grader code, so this is not a blind test. To protect the learner perspective despite that access, the pass separately checks that pre-code values do not reuse hidden grader vectors.

### 11.2 Simulated reading: can the task be solved from prose alone?

| Lesson | Core algorithm inferable from the task text | Learner friction |
|---|---|---|
| 19 | Initialize in/out degree for every neuron; for each `source→target`, increment outgoing/incoming respectively; keep zero-degree entries | Low; main conceptual failure is reversing source and target |
| 20 | Copy schema/source/converter versions; compute `byte_count=len(payload)`; SHA-256 the exact bytes; return the exact 5-key dict | Low-medium; integrity and provenance must be kept conceptually separate |
| 21 | Compute `demand/capacity` per stage and select the unique maximum utilization without mutating inputs | Medium; Python `max(..., key=...)` may need language help, but the engineering contract is clear |
| 22 | Trace starts with initial position; re-observe every step; +1 below target, -1 above target, 0 at target; never overshoot | Low; reverse direction is now independently protected by the grader |
| 23 | `throughput=events/seconds`; `energy=watts*seconds`; `energy/event=energy/events` | Low; the important distinction is metric calculation versus benchmark comparability |

Hand calculations from the revised pre-code prompts are internally consistent:

- L19: `[11,22,44,55]` with `11→22, 22→22, 44→11, 44→55` gives in-degree `{11:1,22:2,44:0,55:1}` and out-degree `{11:1,22:1,44:2,55:0}`;
- L21: A=`6/12=0.5`, B=`6/8=0.75`; the raw demands are equal, while B has higher utilization;
- L22: initial=0, target=2, steps=4 gives `[0,1,2,2,2]`;
- L23: 1200 events / 0.4 s = 3000 events/s; 15 W × 0.4 s = 6 J; 6/1200 = 0.005 J/event.

### 11.3 Dry-run result

Automated learner-path coverage now includes:

- all learner-visible code cells for 5 lessons × 2 languages compile successfully;
- all 5 × 2 personal-work copies execute from `exercises/work/<lang>/`;
- all 10 workbooks report **3 / 3 groups passed** with independently derived reference implementations;
- teaching code for all 5 lessons × 2 languages runs in learner-visible order and matches expected output;
- Python exercise infrastructure result: **107 passed, 2 skipped**. The two skips remain the real Lesson 13 synthesis checks in the Python job where Yosys is absent; the RTL workflow executes that path for real.

### 11.4 Problems found and fixed during this dry run

1. L19/L21/L23 pre-code values overlapped hidden grader vectors; all were replaced with independent values.
2. L20's old title implied that a real MaleCNS subset had already been loaded even though the lesson used only a byte fixture; the lesson is now explicitly before the real subset load.
3. L20 prose required provenance while the old exercise/manifest omitted it; the contract is now aligned on `schema_version/source_release/converter_version/byte_count/sha256`.
4. L20 grader now requires the exact key set.
5. L19/L21 graders now enforce the written non-mutation contracts.
6. L22 grader now includes an `initial > target` reverse-direction oracle and rejects right-only logic.
7. The old student-flow test only injected a function and ran the grader cell. It now creates personal work copies, compiles all student code cells, and executes the workbook code path in order.

### 11.5 Diagram-delivery verification

All five Platform 5 course diagrams were migrated from Mermaid to inline SVG. Final GitHub Actions webpdf output contains these dedicated SVG-fill pixel counts:

- L19: 10,194
- L20: 14,163
- L21: 10,284
- L22: 10,408
- L23: 15,444

The final artifact was also rendered and inspected visually. All five diagrams show complete boxes, arrows, and labels with no blank Mermaid container, broken-image icon, leaked SVG source, or clipping.

### 11.6 Platform 5 conclusion

The revised LSN-019~023 workbooks now meet the current learner-path bar: **standalone task meaning, non-leaking pre-code examples, explicit TODO contracts, graders that enforce written semantics, runnable personal work copies, aligned bilingual paths, and diagrams that are visibly present in final PDFs.**
