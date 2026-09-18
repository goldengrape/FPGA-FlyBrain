"""Checks for Lesson 04: state and clock."""

from ._core import evaluate_group, report


def evaluate(combinational_step, clock_edge, run_clocked_accumulator, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Combinational next-state", "检查 candidate、spike 和待写入寄存器的值。"),
        ("Clock edge", "检查寄存器只保存已经计算好的 value_to_store。"),
        ("Clocked sequence", "检查多个 cycle 的 state 与 spike 历史。"),
    ) if zh else (
        ("Combinational next-state", "Check candidate, spike, and the value prepared for the register."),
        ("Clock edge", "Check that the register stores the precomputed value_to_store."),
        ("Clocked sequence", "Check state and spike history across multiple cycles."),
    )

    def comb_ok():
        return combinational_step(3, 1, 4, 0) == (4, True, 0)

    def edge_ok():
        return clock_edge(3, 7) == 7

    def seq_ok():
        states, spikes = run_clocked_accumulator([1, 1, 1, 1, 2, 2], 4, 0, 0)
        if states != [0, 1, 2, 3, 0, 2, 0] or spikes != [False, False, False, True, False, True]:
            return False
        states, spikes = run_clocked_accumulator([2], 10, 0, 5)
        return states == [5, 7] and spikes == [False]

    return [
        evaluate_group(labels[0][0], comb_ok, labels[0][1]),
        evaluate_group(labels[1][0], edge_ok, labels[1][1]),
        evaluate_group(labels[2][0], seq_ok, labels[2][1]),
    ]


def check(combinational_step, clock_edge, run_clocked_accumulator, language: str = "zh") -> bool:
    title = "Lesson 04 checks" if not language.lower().startswith("zh") else "第 04 课检查"
    return report(title, evaluate(combinational_step, clock_edge, run_clocked_accumulator, language))
