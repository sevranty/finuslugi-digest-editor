# Maintenance contract

## Change classes

| Change | Required action |
|---|---|
| runtime file | validate all modes, update runtime digest, rebuild package, sync personal skill in a separate authorised task |
| fixture or expected result | run fixture and repository validators, update checksums |
| repository documentation | run repository validator and link check |
| package tooling or contract | run all package tests and two-build byte comparison |
| asset or provenance | validate dimensions, checksum, rights and package exclusion |

## Runtime digest

The runtime digest is the ordered SHA-256 list of the seven paths in `release/package.json`.

A runtime change requires:

1. explicit Issue scope
2. regression review for validation, tag formation/audit, comparison and combined order
3. package version decision
4. deterministic rebuild
5. separate personal-skill synchronization and smoke evidence

Repository-only changes do not require personal-skill synchronization.

## Evidence

- use the current PR HEAD, not a stale SHA in an old comment
- record local commands and outcomes
- do not claim hosted CI passed when GitHub Checks did not run
- preserve concise errors with exact paths
