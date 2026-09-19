"""Checks for Lesson 20: minimal image manifest."""

import hashlib

from ._core import evaluate_group, report


def evaluate(image_manifest, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Schema and byte count", "检查 version 与精确 byte count。"),
            ("SHA-256 integrity", "检查 exact payload 的 SHA-256 digest。"),
            ("Payload sensitivity", "检查 payload 改变时 digest 也改变。"),
        )
        if zh
        else (
            ("Schema and byte count", "Check version and exact byte count."),
            ("SHA-256 integrity", "Check the SHA-256 digest of the exact payload."),
            ("Payload sensitivity", "Check digest changes when payload changes."),
        )
    )

    def schema_and_count():
        result = image_manifest(b"abc", "v2")
        return result.get("schema_version") == "v2" and result.get("byte_count") == 3

    def sha256_integrity():
        payload = bytes([0, 1, 2, 255])
        result = image_manifest(payload, "v1")
        return result.get("sha256") == hashlib.sha256(payload).hexdigest()

    def payload_sensitivity():
        first = image_manifest(b"payload-A", "v1")
        second = image_manifest(b"payload-B", "v1")
        return first.get("sha256") != second.get("sha256")

    return [
        evaluate_group(labels[0][0], schema_and_count, labels[0][1]),
        evaluate_group(labels[1][0], sha256_integrity, labels[1][1]),
        evaluate_group(labels[2][0], payload_sensitivity, labels[2][1]),
    ]


def check(image_manifest, language: str = "zh") -> bool:
    title = "第 20 课检查" if language.lower().startswith("zh") else "Lesson 20 checks"
    return report(title, evaluate(image_manifest, language))
