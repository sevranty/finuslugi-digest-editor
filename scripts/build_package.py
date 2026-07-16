#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "release/package.json"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644 << 16


def load_contract(root: Path = ROOT) -> dict:
    path = root / "release/package.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise SystemExit("release/package.json: schema_version must be 1")
    if data.get("project") != "finuslugi-digest-editor":
        raise SystemExit("release/package.json: unexpected project")
    if data.get("archive_root") != "finuslugi-digest-editor":
        raise SystemExit("release/package.json: unexpected archive_root")
    if not isinstance(data.get("package_version"), str) or not data["package_version"]:
        raise SystemExit("release/package.json: package_version is required")
    files = data.get("files")
    if not isinstance(files, list) or len(files) != 7 or len(set(files)) != 7:
        raise SystemExit("release/package.json: files must contain 7 unique paths")
    for relative in files:
        path_value = Path(relative)
        if path_value.is_absolute() or ".." in path_value.parts:
            raise SystemExit(f"release/package.json: unsafe path: {relative}")
    return data


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path, root: Path = ROOT) -> tuple[Path, Path, Path]:
    contract = load_contract(root)
    archive_root = contract["archive_root"]
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    manifest_files = []
    for relative in contract["files"]:
        source = root / relative
        if not source.is_file():
            raise SystemExit(f"Missing package source: {relative}")
        manifest_files.append({
            "path": relative,
            "sha256": file_sha256(source),
            "bytes": source.stat().st_size,
        })

    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for item in sorted(manifest_files, key=lambda value: value["path"]):
            relative = item["path"]
            info = zipfile.ZipInfo(f"{archive_root}/{relative}", date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = FILE_MODE
            info.create_system = 3
            archive.writestr(info, (root / relative).read_bytes(), compresslevel=9)

    digest = file_sha256(output)
    manifest = {
        "schema_version": 1,
        "project": contract["project"],
        "package_version": contract["package_version"],
        "archive_root": archive_root,
        "archive": output.name,
        "archive_sha256": digest,
        "files": manifest_files,
    }
    manifest_path = Path(str(output) + ".manifest.json")
    checksum_path = Path(str(output) + ".sha256")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    checksum_path.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return output, manifest_path, checksum_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(ROOT / "dist/finuslugi-digest-editor.zip"),
    )
    args = parser.parse_args()
    output, manifest, checksum = build(Path(args.output))
    print(f"PASS: {output}")
    print(f"MANIFEST: {manifest}")
    print(f"SHA256: {checksum}")


if __name__ == "__main__":
    main()
