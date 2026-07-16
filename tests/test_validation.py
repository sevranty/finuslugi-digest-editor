from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import validate_repository as vr


class ValidationNegativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self._minimal_repo()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write(self, relative: str, content: str | bytes) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")

    def _minimal_repo(self) -> None:
        skill = "---\nname: finuslugi-digest-editor\ndescription: test\n---\n" + "\n".join(
            f"`{path}`" for path in vr.REQUIRED_REFERENCES
        )
        self._write("SKILL.md", skill)
        self._write(
            "agents/openai.yaml",
            'display_name: "Редактор дайджеста Финуслуг"\n'
            'short_description: "Вычитка, теги и сравнение дайджестов"\n'
            'default_prompt: "test"\nallow_implicit_invocation: true\n',
        )
        for path in vr.REQUIRED_REFERENCES:
            self._write(path, "# test\n")
        self._write("README.md", "# test\n")
        self._write("LICENSE", "MIT License\nPermission is hereby granted\n")
        self._write(
            "release/package.json",
            json.dumps({
                "schema_version": 1,
                "archive_root": "finuslugi-digest-editor",
                "files": vr.RUNTIME_FILES,
            }),
        )

    def _add_complete_repository_data(self) -> None:
        fixture_paths = [
            "evals/fixtures/validation-positive.md",
            "evals/fixtures/validation-negative.md",
            "evals/fixtures/tagging-positive.md",
            "evals/fixtures/tagging-negative.md",
            "evals/fixtures/comparison-positive-source.md",
            "evals/fixtures/comparison-positive-target.md",
            "evals/fixtures/comparison-negative-source.md",
            "evals/fixtures/comparison-negative-target.md",
            "evals/fixtures/combined-source.md",
            "evals/fixtures/combined-final.md",
        ]
        cases = [
            {"id": "validation-positive", "mode": ["validation"], "inputs": [fixture_paths[0]], "expected": {}},
            {"id": "validation-negative", "mode": ["validation"], "inputs": [fixture_paths[1]], "expected": {}},
            {"id": "tagging-positive", "mode": ["tagging"], "inputs": [fixture_paths[2]], "expected": {}},
            {"id": "tagging-negative", "mode": ["tagging"], "inputs": [fixture_paths[3]], "expected": {}},
            {"id": "comparison-positive", "mode": ["comparison"], "inputs": fixture_paths[4:6], "expected": {}},
            {"id": "comparison-negative", "mode": ["comparison"], "inputs": fixture_paths[6:8], "expected": {}},
            {
                "id": "combined",
                "mode": ["comparison", "validation", "tagging"],
                "execution_order": ["comparison", "validation", "tagging"],
                "inputs": fixture_paths[8:10],
                "expected": {},
            },
        ]
        expected_path = "evals/expected-results.json"
        self._write(expected_path, json.dumps({"schema_version": 1, "cases": cases}))
        for index, relative in enumerate(fixture_paths):
            self._write(relative, f"fixture {index}\n")
        manifest_paths = [expected_path, *fixture_paths]
        manifest_files = [
            {
                "path": relative,
                "sha256": vr.sha256(self.root / relative),
            }
            for relative in manifest_paths
        ]
        self._write(
            "evals/manifest.json",
            json.dumps({"schema_version": 1, "files": manifest_files}),
        )

        svg_path = "assets/source/social-preview.svg"
        social_path = "assets/social-preview.png"
        project_path = "assets/project-image.png"
        self._write(svg_path, '<svg width="1280" height="640"/>\n')
        self._write(
            social_path,
            b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (1280).to_bytes(4, "big") + (640).to_bytes(4, "big"),
        )
        self._write(
            project_path,
            b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (1080).to_bytes(4, "big") + (1080).to_bytes(4, "big"),
        )
        asset_items = [
            {"path": svg_path, "format": "svg", "width": 1280, "height": 640, "sha256": vr.sha256(self.root / svg_path)},
            {"path": social_path, "format": "png", "width": 1280, "height": 640, "sha256": vr.sha256(self.root / social_path)},
            {"path": project_path, "format": "png", "width": 1080, "height": 1080, "sha256": vr.sha256(self.root / project_path)},
        ]
        self._write(
            "assets/provenance.json",
            json.dumps({"personal_skill_package_included": False, "files": asset_items}),
        )

    def test_full_repository_positive(self):
        self._add_complete_repository_data()
        vr.validate(self.root)

    def assert_invalid(self, func, text: str) -> None:
        with self.assertRaisesRegex(vr.ValidationError, text):
            func(self.root)

    def test_missing_runtime(self):
        (self.root / "SKILL.md").unlink()
        self.assert_invalid(vr.validate_runtime, "missing file")

    def test_wrong_frontmatter_fields(self):
        self._write("SKILL.md", "---\nname: finuslugi-digest-editor\nextra: x\ndescription: test\n---\n")
        self.assert_invalid(vr.validate_runtime, "frontmatter fields")

    def test_wrong_skill_name(self):
        text = (self.root / "SKILL.md").read_text().replace(
            "name: finuslugi-digest-editor", "name: wrong"
        )
        self._write("SKILL.md", text)
        self.assert_invalid(vr.validate_runtime, "skill name")

    def test_missing_reference_link(self):
        text = (self.root / "SKILL.md").read_text().replace(
            "`references/redpolicy.md`", ""
        )
        self._write("SKILL.md", text)
        self.assert_invalid(vr.validate_runtime, "missing reference")

    def test_agent_metadata(self):
        self._write("agents/openai.yaml", "display_name: wrong\n")
        self.assert_invalid(vr.validate_runtime, "missing field")

    def test_broken_readme_link(self):
        self._write("README.md", "[missing](docs/MISSING.md)\n")
        self.assert_invalid(vr.validate_readme_and_license, "broken local link")

    def test_incomplete_license(self):
        self._write("LICENSE", "MIT\n")
        self.assert_invalid(vr.validate_readme_and_license, "incomplete MIT")

    def test_private_key(self):
        self._write("docs/leak.md", "-----BEGIN " + "PRIVATE KEY-----\n")
        self.assert_invalid(vr.validate_hygiene, "private key")

    def test_absolute_local_path(self):
        self._write("docs/path.md", "/" + "Users/example/project\n")
        self.assert_invalid(vr.validate_hygiene, "macOS absolute path")

    def test_windows_absolute_local_path(self):
        self._write("docs/path.md", "C:" + "\\Users\\example\\project\n")
        self.assert_invalid(vr.validate_hygiene, "Windows absolute home")

    def test_temporary_file(self):
        self._write("notes.tmp", "x")
        self.assert_invalid(vr.validate_hygiene, "temporary file")


if __name__ == "__main__":
    unittest.main()
