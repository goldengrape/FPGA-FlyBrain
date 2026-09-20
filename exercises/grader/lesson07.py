"""Checks for Lesson 07: combinational next-state and sequential register update."""

from ._core import evaluate_group, report


def evaluate(if_neuron_comb, if_neuron_register_edge, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Combinational path", "检查 candidate、非 spike next_v 与 spike_next。"),
        ("Threshold boundary", "检查 candidate 恰好等于 threshold 时是否 spike 并准备 reset_value。"),
        ("Register edge", "检查正常写回与同步低有效 reset 的优先级。"),
    ) if zh else (
        ("Combinational path", "Check candidate, non-spike next_v, and spike_next."),
        ("Threshold boundary", "Check that candidate equal to threshold spikes and prepares reset_value."),
        ("Register edge", "Check normal writeback and synchronous active-low reset precedence."),
    )

    def comb_path():
        return (
            if_neuron_comb(5, -2, 9, 0) == (3, 3, False)
            and if_neuron_comb(-3, 4, 7, -1) == (1, 1, False)
        )

    def threshold_boundary():
        return (
            if_neuron_comb(6, 2, 8, -4) == (8, -4, True)
            and if_neuron_comb(7, 3, 8, 2) == (10, 2, True)
        )

    def register_edge():
        return (
            if_neuron_register_edge(11, True, True, -3) == (11, True)
            and if_neuron_register_edge(11, True, False, -3) == (-3, False)
        )

    return [
        evaluate_group(labels[0][0], comb_path, labels[0][1]),
        evaluate_group(labels[1][0], threshold_boundary, labels[1][1]),
        evaluate_group(labels[2][0], register_edge, labels[2][1]),
    ]


def check(if_neuron_comb, if_neuron_register_edge, language: str = "zh") -> bool:
    title = "第 07 课检查" if language.lower().startswith("zh") else "Lesson 07 checks"
    return report(title, evaluate(if_neuron_comb, if_neuron_register_edge, language))
