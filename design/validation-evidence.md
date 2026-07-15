# FDE#8 validation evidence

## Fixed state

- Base: `main@59bf1df196de15c95c222573a6707254b22dca28`
- Branch: `feat/fde-008-project-image`
- Initial task HEAD: `13f34279d107378ad74697e067a54c6828e7b397`
- Selected direction: `Evidence grid`

## Concept selection

Three low-fidelity compositions were prepared:

```text
design/concepts/
|-- evidence-grid.svg
|-- editorial-lens.svg
`-- controlled-diff.svg
```

Weighted evaluation:

| Direction | Score |
|---|---:|
| Evidence grid | 4.80 / 5.00 |
| Controlled diff | 4.35 / 5.00 |
| Editorial lens | 3.90 / 5.00 |

Evidence grid was selected because it gives equal weight to review, tagging and comparison and remains understandable at small preview sizes.

## Final assets

```text
assets/
|-- source/
|   `-- social-preview.svg
|-- social-preview.png
|-- project-image.png
`-- provenance.json
```

Validation results:

- SVG master: `1280 x 640`, PASS;
- social preview PNG: `1280 x 640`, `2137 bytes`, PASS;
- project image PNG: `1080 x 1080`, `1992 bytes`, PASS;
- social preview below `1 MB`: PASS;
- 80 px safe area: PASS;
- readability at `320 x 160`: PASS;
- solid background: PASS;
- light context: PASS;
- dark context: PASS;
- third-party logos: none;
- copied interfaces: none;
- real or confidential data: none;
- personal skill package changes: none.

## Checksum evidence

The exact SHA-256 and Git blob SHA-1 values are recorded in `assets/provenance.json`.

## Lifecycle boundary

- Assets are repository-only.
- `SKILL.md`, `agents/openai.yaml` and `references/*` must remain unchanged.
- The repository social-preview setting must not be changed before the Draft PR review and explicit lifecycle decision.
