#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/comparison-protocol.md",
    "references/file-handling.md",
    "references/redpolicy.md",
    "references/tagging-protocol.md",
    "references/validation-protocol.md",
]
REQUIRED_REFERENCES = RUNTIME_FILES[2:]
FORBIDDEN_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "macOS absolute path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "Linux absolute home": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "Windows absolute home": re.compile(r"[A-Za-z]:\\Users\\"),
}
TEMP_SUFFIXES = (".tmp", ".bak", ".orig", ".rej", ".swp", "~")


class ValidationError(ValueError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_file(root: Path, relative: str) -> Path:
    path = root / relative
    if not path.is_file():
        raise ValidationError(f"missing file: {relative}")
    return path


def validate_runtime(root: Path) -> None:
    for relative in RUNTIME_FILES:
        require_file(root, relative)
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n"):
        raise ValidationError("SKILL.md: frontmatter missing")
    closing = skill.find("\n---\n", 4)
    if closing < 0:
        raise ValidationError("SKILL.md: frontmatter closing delimiter missing")
    fields = []
    for line in skill[4:closing].splitlines():
        if ":" in line:
            fields.append(line.split(":", 1)[0].strip())
    if fields != ["name", "description"]:
        raise ValidationError(f"SKILL.md: unexpected frontmatter fields: {fields!r}")
    if "\nname: finuslugi-digest-editor\n" not in skill:
        raise ValidationError("SKILL.md: unexpected skill name")
    for reference in REQUIRED_REFERENCES:
        if f"`{reference}`" not in skill:
            raise ValidationError(f"SKILL.md: missing reference: {reference}")

    agent = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    required_agent_text = [
        'display_name: "Редактор дайджеста Финуслуг"',
        'short_description: "Вычитка, теги и сравнение дайджестов"',
        "default_prompt:",
        "allow_implicit_invocation: true",
    ]
    for value in required_agent_text:
        if value not in agent:
            raise ValidationError(f"agents/openai.yaml: missing field: {value}")


def validate_fixtures(root: Path) -> None:
    manifest_path = require_file(root, "evals/manifest.json")
    expected_path = require_file(root, "evals/expected-results.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValidationError("evals/manifest.json: schema_version must be 1")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) != 11:
        raise ValidationError("evals/manifest.json: expected 11 file entries")
    listed = set()
    for entry in entries:
        relative = entry.get("path")
        digest = entry.get("sha256")
        if not isinstance(relative, str) or not relative.startswith("evals/"):
            raise ValidationError(f"evals/manifest.json: invalid path: {relative!r}")
        if relative in listed:
            raise ValidationError(f"evals/manifest.json: duplicate path: {relative}")
        path = require_file(root, relative)
        if sha256(path) != digest:
            raise ValidationError(f"evals/manifest.json: checksum mismatch: {relative}")
        listed.add(relative)
    cases = expected.get("cases")
    if not isinstance(cases, list) or len(cases) != 7:
        raise ValidationError("evals/expected-results.json: expected 7 cases")
    ids = {case.get("id") for case in cases}
    required = {
        "validation-positive", "validation-negative",
        "tagging-positive", "tagging-negative",
        "comparison-positive", "comparison-negative", "combined",
    }
    if ids != required:
        raise ValidationError(f"evals/expected-results.json: unexpected cases: {sorted(ids)!r}")
    combined = next(case for case in cases if case.get("id") == "combined")
    order = ["comparison", "validation", "tagging"]
    if combined.get("execution_order") != order or combined.get("mode") != order:
        raise ValidationError("evals/expected-results.json: combined order mismatch")


def validate_readme_and_license(root: Path) -> None:
    readme = require_file(root, "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
    for link in links:
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        relative = link.split("#", 1)[0]
        if relative and not (root / relative).exists():
            raise ValidationError(f"README.md: broken local link: {relative}")
    license_text = require_file(root, "LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in license_text or "Permission is hereby granted" not in license_text:
        raise ValidationError("LICENSE: incomplete MIT text")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValidationError(f"{path.name}: invalid PNG signature")
    return struct.unpack(">II", data[16:24])


def validate_assets(root: Path) -> None:
    provenance_path = require_file(root, "assets/provenance.json")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("personal_skill_package_included") is not False:
        raise ValidationError("assets/provenance.json: package exclusion must be false")
    items = provenance.get("files")
    if not isinstance(items, list):
        raise ValidationError("assets/provenance.json: files must be a list")
    by_path = {item.get("path"): item for item in items if isinstance(item, dict)}
    required = {
        "assets/source/social-preview.svg",
        "assets/social-preview.png",
        "assets/project-image.png",
    }
    if set(by_path) != required:
        raise ValidationError(
            f"assets/provenance.json: unexpected file set: {sorted(by_path)!r}"
        )
    for relative in sorted(required):
        item = by_path[relative]
        path = require_file(root, relative)
        if item.get("sha256") != sha256(path):
            raise ValidationError(f"assets/provenance.json: checksum mismatch: {relative}")
        if item.get("format") == "png":
            if png_dimensions(path) != (item.get("width"), item.get("height")):
                raise ValidationError(f"assets/provenance.json: dimensions mismatch: {relative}")


def validate_package_contract(root: Path) -> None:
    contract = json.loads(
        require_file(root, "release/package.json").read_text(encoding="utf-8")
    )
    if contract.get("schema_version") != 1:
        raise ValidationError("release/package.json: schema_version must be 1")
    if contract.get("archive_root") != "finuslugi-digest-editor":
        raise ValidationError("release/package.json: unexpected archive_root")
    if contract.get("files") != RUNTIME_FILES:
        raise ValidationError("release/package.json: runtime allowlist mismatch")


def validate_hygiene(root: Path) -> None:
    for path in root.rglob("*"):
        if ".git" in path.parts or "dist" in path.parts:
            continue
        if path.is_file() and path.name.endswith(TEMP_SUFFIXES):
            raise ValidationError(f"temporary file: {path.relative_to(root)}")
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                raise ValidationError(f"{path.relative_to(root)}: forbidden {label}")


def validate(root: Path = ROOT) -> None:
    validate_runtime(root)
    validate_fixtures(root)
    validate_readme_and_license(root)
    validate_assets(root)
    validate_package_contract(root)
    validate_hygiene(root)


def main() -> None:
    try:
        validate(ROOT)
    except (ValidationError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print("PASS: runtime 7/7, fixtures 7 cases and 11 checksums, package boundary, docs, assets and hygiene")


if __name__ == "__main__":
    main()
