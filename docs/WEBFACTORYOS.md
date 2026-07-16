# WebFactoryOS handoff

## Identity

```text
PROJECT_ID: FINUSLUGI_DIGEST_EDITOR
SHORT_ID: FDE
REPOSITORY_NAME: finuslugi-digest-editor
PROJECT_DISPLAY_NAME: Редактор дайджеста Финуслуг
PRIMARY_CHAT: 🔗 FDE • 🧩 finuslugi-digest-editor • 📝 Редактор дайджеста Финуслуг
```

## Ownership

FDE owns:

- runtime files and behaviour
- editorial, tagging and comparison protocols
- fixtures, package contract, assets and execution evidence
- FDE Issues, branches and PRs

WebFactoryOS owns:

- project routing and registry
- uniqueness of project identifiers
- generated project maps
- shared naming and relation contracts

## Boundary

- no WFO code, schema, workflow or package is imported into FDE
- no network or CI dependency on WFO
- no cross-repository write permission
- WFO status never replaces FDE execution evidence
- FDE stores only project-specific deltas and links to shared WFO rules

## Relations

- local completion task: https://github.com/sevranty/finuslugi-digest-editor/issues/15
- naming contract: https://github.com/sevranty/web-factory-os/issues/62
- WFO registry task: https://github.com/sevranty/web-factory-os/issues/63
