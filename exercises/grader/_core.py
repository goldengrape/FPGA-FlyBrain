"""Shared helpers for student-facing graders."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import os
import traceback


_DEBUG_ENV = "FPGA_FLYBRAIN_GRADER_DEBUG"


@dataclass(frozen=True)
class CheckGroup:
    name: str
    passed: bool
    hint: str | None = None
    error: str | None = None


def _debug_enabled() -> bool:
    value = os.environ.get(_DEBUG_ENV, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def evaluate_group(
    name: str,
    predicate: Callable[[], bool],
    hint: str | None = None,
) -> CheckGroup:
    try:
        passed = bool(predicate())
    except Exception:
        return CheckGroup(
            name=name,
            passed=False,
            hint=hint,
            error=traceback.format_exc() if _debug_enabled() else None,
        )
    return CheckGroup(name=name, passed=passed, hint=hint)


def report(title: str, groups: list[CheckGroup]) -> bool:
    print(title)
    print()
    for group in groups:
        mark = "✓" if group.passed else "✗"
        print(f"{mark} {group.name}")
        if not group.passed and group.hint:
            print(f"  {group.hint}")
        if not group.passed and group.error:
            print("  Debug exception:")
            for line in group.error.rstrip().splitlines():
                print(f"    {line}")
    passed = sum(group.passed for group in groups)
    print()
    print(f"{passed} / {len(groups)} groups passed")
    return passed == len(groups)
