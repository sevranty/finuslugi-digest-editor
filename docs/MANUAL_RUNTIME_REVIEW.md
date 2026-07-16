# Manual runtime review

Use this template only when runtime files change or when the installed personal skill is synchronized.

## Metadata

```text
repository_commit:
runtime_digest:
installed_skill_version:
reviewer:
date:
```

## Validation mode

```text
input:
active_redpolicy:
expected_invariants:
observed_result:
verdict:
```

## Tag formation

```text
input:
expected_card_count:
expected_semantic_roles:
observed_result:
verdict:
```

## Tag audit

```text
input:
existing_tags:
expected_findings:
observed_result:
verdict:
```

## Comparison mode

```text
source:
checked_version:
expected_discrepancies:
observed_result:
verdict:
```

## Combined order

Required order:

```text
comparison -> validation -> tagging
```

Record separate results and confirm that no mode is triggered only because multiple files are attached.
