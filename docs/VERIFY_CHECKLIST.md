# Verification checklist (author completes before any release)

STATUS: DRAFT (unverified)

Initial and date each line in your own copy before publishing. `reproflow
gate check .` enforces the mechanical items; the rest are yours to confirm
by hand. `scripts/publish_gate.py` (thin wrapper around the same check)
refuses to proceed while any remain.

## Reproduce
      install `pytest`; it was not available in the sandbox that built
 [x] `pytest -q` passes from a fresh clone (this needs network access to
      this draft — confirm on your own machine or let GitHub Actions CI
- [ ] `python code/01_fetch_repos.py` re-clones all five evidence repos
- [ ] `python code/02_run_audit.py` reproduces `data/processed/stats.json`
      and `audit_results.json` exactly (scores match this draft)
- [ ] Every number in `paper/paper.md` and `report/TECHNICAL_REPORT.md`
      re-derived from `stats.json` after the re-run

## Source-level checks
- [ ] Confirm icsprio, ong-ot-dataset, pipeline-control-validation,
      pqc-ot-crosswalk, and crosswalk-lookup are still public at the URLs
      in `data/raw/PROVENANCE.txt`, and that naming them in a public paper
      as your own prior work is something you want on the record
- [ ] Spot-check the audit table against each repository by hand: open
      each repo's `.github/workflows/`, `tests/`, `data/raw/PROVENANCE.txt`
      and confirm the PASS/PARTIAL/FAIL calls in
      `data/processed/qa_report.txt` match what you see
- [ ] Confirm the "provenance: partial" calls for icsprio,
      ong-ot-dataset, pipeline-control-validation, pqc-ot-crosswalk, and
      crosswalk-lookup are fairly characterized in docs/LIMITATIONS.md
      point 2 (schema mismatch, not absence of provenance tracking)
- [ ] Confirm pqc-ot-crosswalk's own README status line (DRAFT v0.1.0 as
      of the clone date) hasn't changed since; re-audit if it has

## Judgment calls to own
- [ ] Whether the unweighted mean scoring (LIMITATIONS point 4) is the
      right summary statistic, or whether criteria should be weighted
      before this goes in a paper
- [ ] Whether to target JOSS or fall back to a Zenodo-only technical
      report if JOSS's "substantial scholarly effort" bar feels like a
      stretch on reflection

## Before it goes public
- [ ] README, limitations, and the paper rewritten in your own voice;
      nothing you cannot defend remains
- [ ] Draft stamps removed; `reproflow gate check .` passes with no
      findings
- [ ] `CITATION.cff`, `AUTHORS.json`, and `LICENSE` reviewed for correct
      names, ORCID, and affiliations
- [ ] Evidence log row written the day of release
