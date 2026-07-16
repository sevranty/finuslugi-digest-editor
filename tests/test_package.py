from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts import build_package
from scripts import validate_package


class PackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.files = [
            "SKILL.md",
            "agents/openai.yaml",
            "references/comparison-protocol.md",
            "references/file-handling.md",
            "references/redpolicy.md",
            "references/tagging-protocol.md",
            "references/validation-protocol.md",
        ]
        for relative in self.files:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative == "SKILL.md":
                content = "---\nname: finuslugi-digest-editor\ndescription: test\n---\n"
            elif relative == "agents/openai.yaml":
                content = 'display_name: "Редактор дайджеста Финуслуг"\n'
            else:
                content = "# test\n"
            path.write_text(content, encoding="utf-8")
        release = self.root / "release"
        release.mkdir()
        (release / "package.json").write_text(
            json.dumps({
                "schema_version": 1,
                "project": "finuslugi-digest-editor",
                "package_version": "1.0.0",
                "archive_root": "finuslugi-digest-editor",
                "files": self.files,
            }),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_deterministic_build(self):
        a = self.root / "a.zip"
        b = self.root / "b.zip"
        build_package.build(a, self.root)
        build_package.build(b, self.root)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        validate_package.validate_archive(a, self.root)

    def _bad_zip(self, entries: dict[str, bytes]) -> Path:
        path = self.root / "bad.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
        return path

    def _valid_entries(self) -> dict[str, bytes]:
        return {
            f"finuslugi-digest-editor/{relative}": (self.root / relative).read_bytes()
            for relative in self.files
        }

    def test_extra_file_rejected(self):
        entries = self._valid_entries()
        entries["finuslugi-digest-editor/README.md"] = b"x"
        with self.assertRaisesRegex(ValueError, "unexpected entries"):
            validate_package.validate_archive(self._bad_zip(entries), self.root)

    def test_wrong_root_rejected(self):
        entries = {
            name.replace("finuslugi-digest-editor/", "wrong/", 1): data
            for name, data in self._valid_entries().items()
        }
        with self.assertRaisesRegex(ValueError, "unexpected entries"):
            validate_package.validate_archive(self._bad_zip(entries), self.root)

    def test_traversal_rejected(self):
        entries = self._valid_entries()
        entries["finuslugi-digest-editor/../escape"] = b"x"
        with self.assertRaisesRegex(ValueError, "unsafe path"):
            validate_package.validate_archive(self._bad_zip(entries), self.root)

    def test_missing_manifest_rejected(self):
        archive = self.root / "nometa.zip"
        build_package.build(archive, self.root)
        Path(str(archive) + ".manifest.json").unlink()
        with self.assertRaisesRegex(ValueError, "manifest sidecar is missing"):
            validate_package.validate_archive(archive, self.root)

    def test_checksum_sidecar_rejected(self):
        archive = self.root / "checksum.zip"
        build_package.build(archive, self.root)
        Path(str(archive) + ".sha256").write_text("wrong\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum sidecar mismatch"):
            validate_package.validate_archive(archive, self.root)

    def test_manifest_hash_rejected(self):
        archive = self.root / "good.zip"
        _, manifest, _ = build_package.build(archive, self.root)
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["archive_sha256"] = "0" * 64
        manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "manifest SHA-256 mismatch"):
            validate_package.validate_archive(archive, self.root)


if __name__ == "__main__":
    unittest.main()
