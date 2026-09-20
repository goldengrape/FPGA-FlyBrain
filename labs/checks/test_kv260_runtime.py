"""Host-side contract tests for KV260 LAB-HW-05 runtime helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "boards" / "kv260" / "runtime"
HASH_IMAGE = RUNTIME / "hash_image.py"
IMAGE_MANIFEST = RUNTIME / "ubuntu24_image.json"
COLLECT_BOOT_INFO = RUNTIME / "collect_boot_info.sh"


def test_image_manifest_freezes_identity_without_inventing_checksum():
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "AUTHORING_CANDIDATE"
    assert manifest["distribution"] == "Ubuntu Server 24.04 LTS"
    assert "KV260" in manifest["target"]
    assert manifest["image_filename"].endswith("20250423.img.xz")
    assert manifest["source_page"] == "https://ubuntu.com/download/amd"
    assert manifest["expected_sha256"] is None
    assert manifest["formal_hash_pass_blocked"] is True


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
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-05" in result.stdout
    assert "IMAGE_SHA256=" in result.stdout
    assert "EXPECTED_SHA256=UNSET" in result.stdout
    assert "STATUS=RECORDED_UNVERIFIED" in result.stdout
    assert "STATUS=PASS" not in result.stdout


def test_hash_image_can_enforce_frozen_hash(tmp_path):
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    image = tmp_path / manifest["image_filename"]
    image.write_bytes(b"known")

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


def test_collect_boot_info_shell_syntax_and_contract():
    result = subprocess.run(
        ["bash", "-n", str(COLLECT_BOOT_INFO)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    text = COLLECT_BOOT_INFO.read_text(encoding="utf-8")
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-05" in text
    assert "uname -a" in text
    assert "/etc/os-release" in text
    assert "/proc/device-tree/model" in text
    assert "xmutil boardid" in text
    assert "xmutil bootfw_status" in text
