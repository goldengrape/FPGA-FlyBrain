"""Checks for Lesson 11: sparse source index."""

from ._core import evaluate_group, report


_EDGES = [(0, 1, 2), (0, 3, -1), (2, 1, 3), (3, 2, 1)]


def evaluate(build_source_index, lookup_source, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        ("Source index packing", "检查每个 source 的 start/count，包括 zero-fanout source。"),
        ("Sparse lookup", "检查 lookup 是否只返回该 source 的连续记录区间。"),
        ("Record order", "检查同一 source 内输入 edge 的顺序是否保留。"),
    ) if zh else (
        ("Source index packing", "Check each source start/count, including zero-fanout sources."),
        ("Sparse lookup", "Check that lookup returns exactly the contiguous range for one source."),
        ("Record order", "Check that input edge order is preserved within a source."),
    )

    def packing_ok():
        index, records = build_source_index(4, _EDGES)
        return index == [(0, 2), (2, 0), (2, 1), (3, 1)] and records == [(1, 2), (3, -1), (1, 3), (2, 1)]

    def lookup_ok():
        index, records = build_source_index(4, _EDGES)
        expected = [[(1, 2), (3, -1)], [], [(1, 3)], [(2, 1)]]
        return all(lookup_source(i, index, records) == expected[i] for i in range(4))

    def order_ok():
        index, records = build_source_index(2, [(0, 1, 4), (0, 0, 5)])
        return lookup_source(0, index, records) == [(1, 4), (0, 5)]

    return [
        evaluate_group(labels[0][0], packing_ok, labels[0][1]),
        evaluate_group(labels[1][0], lookup_ok, labels[1][1]),
        evaluate_group(labels[2][0], order_ok, labels[2][1]),
    ]


def check(build_source_index, lookup_source, language: str = "zh") -> bool:
    title = "Lesson 11 checks" if not language.lower().startswith("zh") else "第 11 课检查"
    return report(title, evaluate(build_source_index, lookup_source, language))
