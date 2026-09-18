"""Shared helpers for student-facing graders."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class CheckGroup:
    name: str
    passed: bool
    hint: str | None = None


def evaluate_group(
    name: str,
    predicate: Callable[[], bool],
    hint: str | None = None,
) -> CheckGroup:
    try:
        passed = bool(predicate())
    except Exception:
        passed = False
    return CheckGroup(name=name, passed=passed, hint=hint)


def report(title: str, groups: list[CheckGroup]) -> bool:
    print(title)
    print()
    for group in groups:
        mark = "✓" if group.passed else "✗"
        print(f"{mark} {group.name}")
        if not group.passed and group.hint:
            print(f"  {group.hint}")
    passed = sum(group.passed for group in groups)
    print()
    print(f"{passed} / {len(groups)} groups passed")
    return passed == len(groups)
