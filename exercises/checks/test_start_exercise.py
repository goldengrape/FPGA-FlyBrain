"""Tests for scripts/start_exercise.py."""

from pathlib import Path

import pytest

from scripts.start_exercise import (
    EXERCISE_FILES,
    create_work_copy,
    normalize_lesson,
)


def test_normalize_lesson_accepts_common_forms():
    assert normalize_lesson("1") == "01"
    assert normalize_lesson("01") == "01"
    assert normalize_lesson("06") == "06"
    assert normalize_lesson("8") == "08"
    assert normalize_lesson("lesson11") == "11"
    assert normalize_lesson("18") == "18"
    assert normalize_lesson("all") == "all"


def test_normalize_lesson_rejects_missing_python_exercise():
    with pytest.raises(ValueError):
        normalize_lesson("24")


def test_create_work_copy_creates_ignored_style_workspace_and_never_overwrites(tmp_path: Path):
    filename = EXERCISE_FILES["01"]
    source = tmp_path / "exercises" / "zh" / filename
    source.parent.mkdir(parents=True)
    source.write_text("official starter", encoding="utf-8")

    destination, created = create_work_copy(tmp_path, "01", "zh")
    assert created is True
    assert destination == tmp_path / "exercises" / "work" / "zh" / filename
    assert destination.read_text(encoding="utf-8") == "official starter"

    destination.write_text("student answer", encoding="utf-8")

    same_destination, created_again = create_work_copy(tmp_path, "01", "zh")
    assert created_again is False
    assert same_destination == destination
    assert destination.read_text(encoding="utf-8") == "student answer"


def test_create_work_copy_requires_official_template(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        create_work_copy(tmp_path, "01", "en")



def test_all_declared_exercises_can_be_copied_without_overwriting(tmp_path: Path):
    for lesson, filename in EXERCISE_FILES.items():
        source = tmp_path / "exercises" / "zh" / filename
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"official starter {lesson}", encoding="utf-8")

    destinations = []
    for lesson in EXERCISE_FILES:
        destination, created = create_work_copy(tmp_path, lesson, "zh")
        assert created is True
        destinations.append(destination)

    assert len(destinations) == len(EXERCISE_FILES)
    assert len(set(destinations)) == len(EXERCISE_FILES)

    for lesson in EXERCISE_FILES:
        destination, created = create_work_copy(tmp_path, lesson, "zh")
        assert created is False
        assert destination.read_text(encoding="utf-8") == f"official starter {lesson}"
