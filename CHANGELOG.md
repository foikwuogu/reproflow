# Changelog

## v0.1.0 (2026-09-20, DRAFT — unverified)

Initial release.

- `reproflow.provenance`: record fetched files and cloned repos to a
  `key=value` ledger; parse and validate it.
- `reproflow.gate`: publish-gate scan for draft stamps, unresolved
  verify-tags, bracketed placeholders, and secret-shaped strings.
- `reproflow.audit`: score a repository against an eight-criterion
  reproducibility checklist (packaging, tests, CI, provenance, stats file,
  docs set, citation metadata, license).
- `reproflow.scaffold` / `reproflow init`: generate a new project from the
  standard layout.
- `reproflow` CLI wiring all four.
- Evidence audit of five prior repositories (icsprio, ong-ot-dataset,
  pipeline-control-validation, pqc-ot-crosswalk, crosswalk-lookup) plus
  reproflow's own self-audit, in `data/processed/`.
- `paper/paper.md` (JOSS submission draft) and
  `report/TECHNICAL_REPORT.md` (fuller write-up for Zenodo).
