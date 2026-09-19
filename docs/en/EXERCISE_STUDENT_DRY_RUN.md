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

This is the only blocker found in the dry run and should be fixed before content polish continues.

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

## 8. Environment recommendation

Fix the grader import path first, then add a maintainer test that starts Python/kernel-like execution from `exercises/zh` and `exercises/en`, rather than only testing from the repository root.

## 9. Conclusion

The exercises are usable in terms of conceptual clarity, pre-code reasoning, TODO scope, and grader feedback. All nine can be solved and pass.

Priorities after this dry run:

1. fix the real-Jupyter grader import blocker;
2. explain Lesson 4's intentionally unused state parameter;
3. distinguish consolidation exercises from transfer/design exercises;
4. then decide whether to reduce direct answer-copy paths in Lessons 2, 3, 11, and 12.

Do not increase code volume simply to make the assignments feel harder.
