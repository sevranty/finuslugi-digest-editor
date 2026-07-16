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

## Final post-merge reconciliation record

This record closes the documentation gap found by FDE#19 after PR#16, PR#17 and PR#18.

### Fixed baseline and scope

- baseline: `main@57dd91c59e4b187887521897d4ceac46269a4254`
- branch: `docs/fde-019-post-merge-reconciliation`
- allowed diff: `docs/PROJECT_DEBT.md`, `docs/VALIDATION.md`
- runtime files, fixtures, assets, design, package contract, scripts, tests and LICENSE: unchanged
- exact reviewed PR HEAD and final squash commit are recorded in FDE#19 and its linked PR; embedding the current commit SHA in this file would invalidate that SHA by creating another commit

### Validation evidence

| Check | Result | Evidence |
|---|---|---|
| Runtime blob identity | PASS | all seven runtime files match the Git blob SHAs from baseline `57dd91c59e4b187887521897d4ceac46269a4254` |
| Fixture and repository validators | PASS by unchanged-input proof | validator code, fixtures, expected results, manifests, assets and package contract are outside the FDE#19 diff; the final-main validation chain remains PR#17 and PR#18 |
| Unit validation | PASS, 19/19 | recorded for the unchanged scripts and tests in FDE#15 and PR#17 |
| Documentation hygiene | PASS | no private key marker, absolute local path, temporary filename or broken local evidence reference introduced |
| Changed paths | PASS | exactly `docs/PROJECT_DEBT.md` and `docs/VALIDATION.md` |
| Package build A/B | PASS | deterministic builds are byte-identical |
| Archive root and allowlist | PASS | one root `finuslugi-digest-editor/`; exactly seven runtime files |
| Archive SHA-256 | PASS | `dee73ce96b52b5f189f307be6deb4f9a19945fd9d6254198bfb2af64e21cd2bc` |
| Runtime diff against baseline | PASS | empty |
| Protected-resource diff | PASS | empty |
| GitHub Checks | absent | not reported as passed |

### Lifecycle evidence location

The linked FDE#19 Issue and PR are the mutable lifecycle record. They must contain:

- exact base and reviewed HEAD
- full two-file diff
- fixed-HEAD review verdict and unresolved-thread count
- guarded squash merge result
- final `main` SHA

This separation keeps the repository document durable without a self-invalidating embedded HEAD SHA.
