#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "evals/manifest.json"
EXPECTED_PATH = ROOT / "evals/expected-results.json"
REQUIRED_CASES = {
    "validation-positive",
    "validation-negative",
    "tagging-positive",
    "tagging-negative",
    "comparison-positive",
    "comparison-negative",
    "combined",
}
REQUIRED_MODE_POLARITY = {
    "validation": {"validation-positive", "validation-negative"},
    "tagging": {"tagging-positive", "tagging-negative"},
    "comparison": {"comparison-positive", "comparison-negative"},
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected JSON object in {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(manifest: dict[str, Any]) -> set[str]:
    if manifest.get("schema_version") != 1:
        raise SystemExit("manifest schema_version must be 1")

    policy = manifest.get("fixture_policy")
    expected_policy = {
        "synthetic_only": True,
        "contains_personal_data": False,
        "contains_confidential_data": False,
        "runtime_contract_modified": False,
    }
    if policy != expected_policy:
        raise SystemExit(f"Unexpected fixture_policy: {policy!r}")

    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("manifest files must be a non-empty list")

    listed_paths: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit("manifest entry must be an object")
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        if not isinstance(relative, str) or not relative.startswith("evals/"):
            raise SystemExit(f"Invalid manifest path: {relative!r}")
        if relative in listed_paths:
            raise SystemExit(f"Duplicate manifest path: {relative}")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise SystemExit(f"Invalid SHA-256 for {relative}")

        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"Missing manifest file: {relative}")
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise SystemExit(
                f"Checksum mismatch for {relative}: expected {expected_hash}, got {actual_hash}"
            )
        listed_paths.add(relative)

    return listed_paths


def validate_cases(expected: dict[str, Any], manifest_paths: set[str]) -> None:
    if expected.get("schema_version") != 1:
        raise SystemExit("expected-results schema_version must be 1")

    cases = expected.get("cases")
    if not isinstance(cases, list):
        raise SystemExit("expected-results cases must be a list")

    ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise SystemExit("case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise SystemExit("case id must be a non-empty string")
        if case_id in ids:
            raise SystemExit(f"Duplicate case id: {case_id}")
        ids.add(case_id)
        by_id[case_id] = case

        modes = case.get("mode")
        if not isinstance(modes, list) or not modes:
            raise SystemExit(f"Case {case_id}: mode must be a non-empty list")
        if any(mode not in {"validation", "tagging", "comparison"} for mode in modes):
            raise SystemExit(f"Case {case_id}: unknown mode {modes!r}")

        inputs = case.get("inputs")
        if not isinstance(inputs, list) or not inputs:
            raise SystemExit(f"Case {case_id}: inputs must be a non-empty list")
        for relative in inputs:
            if relative not in manifest_paths:
                raise SystemExit(f"Case {case_id}: input is absent from manifest: {relative}")

        if not isinstance(case.get("expected"), dict):
            raise SystemExit(f"Case {case_id}: expected must be an object")

    if ids != REQUIRED_CASES:
        missing = sorted(REQUIRED_CASES - ids)
        extra = sorted(ids - REQUIRED_CASES)
        raise SystemExit(f"Unexpected case set; missing={missing}, extra={extra}")

    for mode, required_ids in REQUIRED_MODE_POLARITY.items():
        if not required_ids.issubset(ids):
            raise SystemExit(f"Missing positive/negative coverage for {mode}")
        for case_id in required_ids:
            if mode not in by_id[case_id]["mode"]:
                raise SystemExit(f"Case {case_id} does not declare mode {mode}")

    combined = by_id["combined"]
    expected_order = ["comparison", "validation", "tagging"]
    if combined.get("execution_order") != expected_order:
        raise SystemExit(
            f"Combined execution_order must be {expected_order}, got {combined.get('execution_order')!r}"
        )
    if combined.get("mode") != expected_order:
        raise SystemExit("Combined mode list must match execution_order")


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    expected = load_json(EXPECTED_PATH)
    manifest_paths = validate_manifest(manifest)
    validate_cases(expected, manifest_paths)
    print(
        "PASS: 7 cases, positive/negative coverage for 3 modes, combined order, "
        f"and {len(manifest_paths)} SHA-256 checks validated"
    )


if __name__ == "__main__":
    main()
