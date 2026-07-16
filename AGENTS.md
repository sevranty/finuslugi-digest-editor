# Agent routing

## Project

- PROJECT_ID: `FINUSLUGI_DIGEST_EDITOR`
- SHORT_ID: `FDE`
- Repository: `https://github.com/sevranty/finuslugi-digest-editor`
- Tasks: `https://github.com/sevranty/finuslugi-digest-editor/issues`

## Rules

- Route FDE implementation work to an FDE Issue
- Use one branch and one PR per active completion task
- Treat WebFactoryOS as routing metadata, not a runtime dependency
- Change `SKILL.md`, `agents/openai.yaml` or `references/**` only when the Issue explicitly authorizes runtime behaviour changes
- Preserve exact paths, URLs, commits and error text
- Do not write to another repository from an FDE task
- Do not change repository settings, secrets, tags, Releases or the installed personal skill without explicit scope

## Validation

Run from the repository root:

```bash
git diff --check
python3 scripts/validate_fixtures.py
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -p 'test_*.py'
```
