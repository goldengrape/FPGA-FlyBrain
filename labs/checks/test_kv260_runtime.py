"""Host-side contract tests for KV260 Stage-2 runtime helpers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "boards" / "kv260" / "runtime"
HASH_IMAGE = RUNTIME / "hash_image.py"
LOOPBACK = RUNTIME / "loopback_mmio.py"
IMAGE_MANIFEST = RUNTIME / "ubuntu24_image.json"


def test_loopback_dry_run_is_self_checking(tmp_path):
    trace = tmp_path / "trace.json"
    result = subprocess.run(
        [
            sys.executable,
            str(LOOPBACK),
            "--dry-run",
            "--json-out",
            str(trace),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "TRANSPORT=DRY_RUN_MODEL" in result.stdout
    assert "SAMPLE_COUNT=12" in result.stdout
    assert "STATUS=PASS" in result.stdout

    payload = json.loads(trace.read_text(encoding="utf-8"))
    assert payload["lab_id"] == "LAB-HW-06"
    assert payload["base"] == 0xA0010000
    assert len(payload["trace"]) == 12
    assert payload["trace"][-1]["write"] == 0xFFFFFFFF
    assert payload["trace"][-1]["read"] == 0


def test_hash_image_records_but_does_not_fake_expected_hash(tmp_path):
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    image = tmp_path / manifest["image_filename"]
    image.write_bytes(b"fpga-flybrain-test-image")

    result = subprocess.run(
        [sys.executable, str(HASH_IMAGE), str(image)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "IMAGE_SHA256=" in result.stdout
    assert "EXPECTED_SHA256=UNSET" in result.stdout
    assert "STATUS=RECORDED_UNVERIFIED" in result.stdout
    assert "STATUS=PASS" not in result.stdout


def test_hash_image_can_enforce_frozen_hash(tmp_path):
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    image = tmp_path / manifest["image_filename"]
    image.write_bytes(b"known")
    import hashlib

    expected = hashlib.sha256(b"known").hexdigest()
    manifest["expected_sha256"] = expected
    local_manifest = tmp_path / "manifest.json"
    local_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(HASH_IMAGE),
            str(image),
            "--manifest",
            str(local_manifest),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert f"EXPECTED_SHA256={expected}" in result.stdout
    assert "STATUS=PASS" in result.stdout


def test_hash_image_rejects_wrong_filename(tmp_path):
    image = tmp_path / "wrong.img.xz"
    image.write_bytes(b"wrong")
    result = subprocess.run(
        [sys.executable, str(HASH_IMAGE), str(image)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 3
    assert "ERROR=IMAGE_FILENAME_MISMATCH" in result.stdout


def test_collect_boot_info_shell_syntax():
    result = subprocess.run(
        ["bash", "-n", str(RUNTIME / "collect_boot_info.sh")],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
