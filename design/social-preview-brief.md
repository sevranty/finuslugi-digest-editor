# Social preview design brief

## Status

FDE#8 started from `main@59bf1df196de15c95c222573a6707254b22dca28`.

This document defines the visual and technical boundary before any final asset is produced. It is repository-only and must not enter the personal skill package.

## GitHub requirements

Source: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview

- accepted formats: PNG, JPG, GIF;
- maximum file size: under 1 MB;
- minimum recommended dimensions: 640 x 320 px;
- best-display dimensions: 1280 x 640 px;
- transparent PNG is supported, but a solid background is preferred for predictable rendering across platforms and dark mode.

## Product message

Primary name:

```text
finuslugi-digest-editor
```

Secondary descriptor:

```text
Вычитка • теги • сравнение
```

The visual must communicate evidence-based editorial control rather than generic AI generation.

## Hard constraints

- no Finuslugi, MOEX, OpenAI, ChatGPT, or third-party logos;
- no copied interface screenshots;
- no real digest data, metrics, names, or confidential fragments;
- no claims beyond the three supported modes;
- no visual implication that the skill automatically edits source files;
- all graphic elements must be original, generated for this repository, or built from simple geometric primitives;
- final assets stay outside the personal skill package.

## Safe area

Use a 1280 x 640 master canvas.

```text
+----------------------------------------------------------------+
| 80 px outer safe margin                                        |
|                                                                |
|   title and core symbol inside central 1120 x 480 area          |
|                                                                |
| 80 px outer safe margin                                        |
+----------------------------------------------------------------+
```

Keep small text out of the design. The secondary descriptor must remain readable at approximately 320 x 160 px preview size.

## Visual directions

### A. Evidence grid — recommended

A structured field of three editorial cards representing:

1. review findings;
2. semantic tags;
3. version comparison.

The cards are connected by a single evidence line and use restrained check, label, and diff symbols. This direction maps directly to the three-mode contract and remains understandable without product logos.

Strengths:

- highest functional clarity;
- easy to scale and crop;
- visually distinct from generic chat or sparkle imagery;
- can be built entirely from original geometric primitives.

Risk:

- requires careful simplification to avoid looking like a dashboard screenshot.

### B. Editorial lens

A large abstract lens passes over text lines and reveals verified fragments, tags, and a corrected status marker.

Strengths:

- strong metaphor for evidence and review;
- compact central composition;
- good project-image potential.

Risk:

- comparison mode is less explicit;
- may resemble generic search or inspection branding.

### C. Controlled diff

Two abstract document columns are compared through a central vertical control layer. Removed, preserved, and changed fragments are represented by geometric line segments rather than readable content.

Strengths:

- comparison and factual integrity are immediately visible;
- strong horizontal composition for 2:1 format.

Risk:

- tags and editorial review become secondary;
- can look like a developer diff tool unless typography is balanced.

## Direction decision

Direction A, Evidence grid, is the default recommendation because it gives equal visual weight to all three supported modes and avoids over-indexing on comparison alone.

Before final export, prepare three low-fidelity compositions using the same title and descriptor. Select the final composition by:

| Criterion | Weight |
|---|---:|
| Three-mode clarity | 30% |
| Readability at small size | 25% |
| Brand neutrality | 20% |
| Visual distinctiveness | 15% |
| Ease of reproducible export | 10% |

## Planned assets

```text
assets/
|-- source/
|   `-- social-preview.svg
|-- project-image.png
|-- social-preview.png
`-- provenance.json
```

Expected exports:

- `assets/social-preview.png`: 1280 x 640 px, solid background, under 1 MB;
- `assets/project-image.png`: square derivative for project listings where needed;
- `assets/source/social-preview.svg`: editable vector source;
- `assets/provenance.json`: authorship, generation method, dimensions, file sizes, SHA-256 and license status.

## Validation before PR

- dimensions verified from file metadata;
- social preview file under 1 MB;
- title readable at 25% scale;
- descriptor readable at 25% scale;
- no third-party marks or copied visual assets;
- solid-background and dark-interface mock checks completed;
- SHA-256 recorded for source and exports;
- assets excluded from personal skill package;
- Draft PR created before any repository social-preview setting is changed.
