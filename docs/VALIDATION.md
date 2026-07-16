# Local validation

Run from the repository root:

```bash
git diff --check
python3 scripts/validate_fixtures.py
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/build_package.py --output dist/finuslugi-digest-editor.zip
python3 scripts/validate_package.py dist/finuslugi-digest-editor.zip
```

The repository validator checks:

- 7 runtime files and the exact package allowlist
- `SKILL.md` frontmatter and reference links
- `agents/openai.yaml` fields
- 7 expected cases and 11 fixture checksums
- README local links and MIT License
- asset provenance, checksums and PNG dimensions
- forbidden private keys, absolute local paths and temporary files

GitHub Checks are optional. When no hosted check exists, the PR must record the exact reviewed HEAD and the output of these local commands.
