# Lesson 1 homework | How do we decide whether the code is correct?

This page is the homework-and-checking companion to **LSN-001, From membrane potential to a minimal computational neuron**.

Starting here, some exercises use a classic online-programming-assignment pattern: the function signature, parameters, return values, and most scaffolding are supplied, while a small TODO region is left for you to implement.

```python
def leak_step(v, input_value, alpha, v_rest):
    # YOUR CODE STARTS HERE
    ...
    # YOUR CODE ENDS HERE
```

This keeps attention on the lesson concept and gives the checker a stable interface to test.

Starter code: `exercises/lesson01_lif.py`

Public checks: `exercises/checks/check_lesson01.py`

Run from the repository root:

```bash
uv sync --group dev
uv run pytest exercises/checks/check_lesson01.py -q
```

Failures are expected initially because the TODO regions deliberately raise `NotImplementedError`.

The public checks test behavioral properties: rest is a fixed point with zero input, displaced voltages leak toward rest, input is integrated, equality with threshold fires, a spike resets state, and a subthreshold candidate does not fire.

A result such as `6 passed` means the implementation satisfies the behaviors covered by those public tests. It does not prove every possible input is correct and does not replace understanding.

The course therefore uses two complementary checks:

- **Automated Check**: pytest checks executable behavior;
- **Human Check**: you explain why the behavior should hold without having AI answer for you.

Lesson 1 Human Check:

> With `V=-60, V_rest=-70, alpha=0.9, input=11, threshold=-50`, manually compute the candidate voltage. Why is this a threshold boundary case? What changes if `>=` is silently replaced by `>`?

The homework files are named `check_lessonXX.py` instead of ordinary `test_*.py` so unfinished student work is not automatically collected by a normal project test run. Run homework checks explicitly by path.

See `exercises/README.md` for the complete Lesson 1–4 assignment plan.
