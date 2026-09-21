#!/usr/bin/env python3
"""Record/verify the LAB-HW-05 Ubuntu image identity without inventing a hash."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "ubuntu24_image.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    if not args.image.is_file():
        print("STATUS=FAIL")
        print("ERROR=IMAGE_NOT_FOUND")
        print(f"IMAGE={args.image}")
        return 2

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        expected_name = manifest["image_filename"]
        expected_hash = manifest.get("expected_sha256")
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print("STATUS=FAIL")
        print("ERROR=MANIFEST_INVALID")
        print(f"DETAIL={exc}")
        return 2

    actual_hash = sha256_file(args.image)
    size = args.image.stat().st_size

    print("FPGA_FLYBRAIN_LAB=LAB-HW-05")
    print(f"IMAGE_FILENAME={args.image.name}")
    print(f"IMAGE_SIZE_BYTES={size}")
    print(f"IMAGE_SHA256={actual_hash}")
    print(f"COURSE_IMAGE_FILENAME={expected_name}")

    if args.image.name != expected_name:
        print("STATUS=FAIL")
        print("ERROR=IMAGE_FILENAME_MISMATCH")
        return 3

    if expected_hash is None:
        print("EXPECTED_SHA256=UNSET")
        print("STATUS=RECORDED_UNVERIFIED")
        print("DETAIL=Formal image-hash PASS is blocked until the course manifest freezes expected_sha256.")
        return 0

    print(f"EXPECTED_SHA256={expected_hash}")
    if actual_hash.lower() != expected_hash.lower():
        print("STATUS=FAIL")
        print("ERROR=IMAGE_SHA256_MISMATCH")
        return 4

    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
