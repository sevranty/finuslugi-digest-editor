#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_contract(root: Path = ROOT) -> dict:
    data = json.loads((root / "release/package.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("release/package.json: schema_version must be 1")
    if data.get("project") != "finuslugi-digest-editor":
        raise ValueError("release/package.json: unexpected project")
    if data.get("archive_root") != "finuslugi-digest-editor":
        raise ValueError("release/package.json: unexpected archive_root")
    if not isinstance(data.get("package_version"), str) or not data["package_version"]:
        raise ValueError("release/package.json: package_version is required")
    files = data.get("files")
    if not isinstance(files, list) or len(files) != 7 or len(set(files)) != 7:
        raise ValueError("release/package.json: files must contain 7 unique paths")
    for relative in files:
        path_value = PurePosixPath(relative)
        if path_value.is_absolute() or ".." in path_value.parts:
            raise ValueError(f"release/package.json: unsafe path: {relative}")
    return data


def validate_archive(archive_path: Path, root: Path = ROOT) -> None:
    contract = load_contract(root)
    archive_root = contract["archive_root"]
    expected = [f"{archive_root}/{path}" for path in sorted(contract["files"])]

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("archive: duplicate entries")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"archive: unsafe path: {name}")
        if sorted(names) != expected:
            raise ValueError(f"archive: unexpected entries: {sorted(names)!r}")

        with tempfile.TemporaryDirectory() as temp_dir:
            archive.extractall(temp_dir)
            extracted_root = Path(temp_dir) / archive_root
            extracted = sorted(
                str(path.relative_to(extracted_root)).replace("\\", "/")
                for path in extracted_root.rglob("*")
                if path.is_file()
            )
            if extracted != sorted(contract["files"]):
                raise ValueError(f"archive: extracted file set mismatch: {extracted!r}")
            skill = (extracted_root / "SKILL.md").read_text(encoding="utf-8")
            if "\nname: finuslugi-digest-editor\n" not in skill:
                raise ValueError("archive: SKILL.md has unexpected name")
            agent = (extracted_root / "agents/openai.yaml").read_text(encoding="utf-8")
            if 'display_name: "Редактор дайджеста Финуслуг"' not in agent:
                raise ValueError("archive: agents/openai.yaml has unexpected display_name")

    manifest_path = Path(str(archive_path) + ".manifest.json")
    checksum_path = Path(str(archive_path) + ".sha256")
    if not manifest_path.is_file():
        raise ValueError("archive: manifest sidecar is missing")
    if not checksum_path.is_file():
        raise ValueError("archive: checksum sidecar is missing")

    digest = sha256(archive_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("archive") != archive_path.name:
        raise ValueError("archive: manifest archive name mismatch")
    if manifest.get("archive_sha256") != digest:
        raise ValueError("archive: manifest SHA-256 mismatch")
    if manifest.get("archive_root") != archive_root:
        raise ValueError("archive: manifest root mismatch")

    manifest_files = manifest.get("files")
    if not isinstance(manifest_files, list) or len(manifest_files) != 7:
        raise ValueError("archive: manifest must contain 7 file entries")
    expected_hashes = {
        item.get("path"): item.get("sha256")
        for item in manifest_files
        if isinstance(item, dict)
    }
    if set(expected_hashes) != set(contract["files"]):
        raise ValueError("archive: manifest file set mismatch")
    for relative in contract["files"]:
        source_hash = sha256(root / relative)
        if expected_hashes.get(relative) != source_hash:
            raise ValueError(f"archive: source hash mismatch: {relative}")

    checksum_line = checksum_path.read_text(encoding="utf-8").strip()
    if checksum_line != f"{digest}  {archive_path.name}":
        raise ValueError("archive: checksum sidecar mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    try:
        validate_archive(Path(args.archive))
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print("PASS: deterministic package contract validated")


if __name__ == "__main__":
    main()
