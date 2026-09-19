"""Checks for Lesson 20: image manifest integrity and provenance."""

import hashlib

from ._core import evaluate_group, report


EXPECTED_KEYS = {
    "schema_version",
    "source_release",
    "converter_version",
    "byte_count",
    "sha256",
}


def evaluate(image_manifest, language: str = "zh"):
    zh = language.lower().startswith("zh")
    labels = (
        (
            ("Schema and provenance", "检查 schema/source/converter 字段与 exact key set。"),
            ("Byte integrity", "检查 exact payload 的 byte count 与 SHA-256 digest。"),
            ("Payload sensitivity", "检查 payload 改变时 digest 也改变。"),
        )
        if zh
        else (
            ("Schema and provenance", "Check schema/source/converter fields and the exact key set."),
            ("Byte integrity", "Check byte count and SHA-256 for the exact payload."),
            ("Payload sensitivity", "Check digest changes when payload changes."),
        )
    )

    def schema_and_provenance():
        result = image_manifest(
            b"abc",
            "schema-v2",
            "source-r7",
            "converter-v3",
        )
        return (
            set(result) == EXPECTED_KEYS
            and result.get("schema_version") == "schema-v2"
            and result.get("source_release") == "source-r7"
            and result.get("converter_version") == "converter-v3"
        )

    def byte_integrity():
        payload = bytes([0, 1, 2, 255])
        result = image_manifest(
            payload,
            "schema-v1",
            "source-r1",
            "converter-v1",
        )
        return (
            result.get("byte_count") == len(payload)
            and result.get("sha256") == hashlib.sha256(payload).hexdigest()
        )

    def payload_sensitivity():
        first = image_manifest(
            b"payload-A",
            "schema-v1",
            "source-r1",
            "converter-v1",
        )
        second = image_manifest(
            b"payload-B",
            "schema-v1",
            "source-r1",
            "converter-v1",
        )
        return first.get("sha256") != second.get("sha256")

    return [
        evaluate_group(labels[0][0], schema_and_provenance, labels[0][1]),
        evaluate_group(labels[1][0], byte_integrity, labels[1][1]),
        evaluate_group(labels[2][0], payload_sensitivity, labels[2][1]),
    ]


def check(image_manifest, language: str = "zh") -> bool:
    title = "第 20 课检查" if language.lower().startswith("zh") else "Lesson 20 checks"
    return report(title, evaluate(image_manifest, language))
