# Verification checklist (author completes before any release)

STATUS: DRAFT (unverified)

Initial and date each line in your own copy before publishing. `reproflow
gate check .` enforces the mechanical items; the rest are yours to confirm
by hand. `scripts/publish_gate.py` (thin wrapper around the same check)
refuses to proceed while any remain.

## Reproduce
- [x] `pytest -q` passes from a fresh clone (this needs network access to install
      `pytest`; confirm on your own machine or let GitHub Actions CI confirm on push)
      — *2026-09-20: confirmed via GitHub Actions CI #1 (commit 55c6a42),
      all 4 Python versions (3.9-3.12) green, "Run test suite" step passed
      on each (48 passed on 3.11, no pytest warnings).*
- [x] `python code/01_fetch_repos.py` re-clones all five evidence repos
      — *2026-09-20, Claude (agent-run): re-cloned all five into a fresh,
      independent scratch directory; all five succeeded and all five
      commit hashes matched `data/raw/PROVENANCE.txt` exactly.*
- [x] `python code/02_run_audit.py` reproduces `data/processed/stats.json`
      and `audit_results.json` exactly (scores match this draft)
      — *2026-09-20, Claude: re-ran the auditor against that fresh clone.
      All 5 scores and all 40 individual criterion cells (5 repos x 8
      criteria) matched the committed `audit_results.json` exactly — zero
      mismatches.*
- [x] Every number in `paper/paper.md` and `report/TECHNICAL_REPORT.md`
      re-derived from `stats.json` after the re-run
      — *2026-09-20, Claude: every score cited in both documents (0.94,
      0.75, 0.62, 0.56, 0.44, 1.00, mean 0.66) checked against
      `stats.json` — all match exactly.*

## Source-level checks
- [x] Confirm icsprio, ong-ot-dataset, pipeline-control-validation,
      pqc-ot-crosswalk, and crosswalk-lookup are still public at the URLs
      in `data/raw/PROVENANCE.txt`, and that naming them in a public paper
      as your own prior work is something you want on the record
      — *"still public" confirmed 2026-09-20 by Claude (fresh reclone
      succeeded for all five). "Naming them as my own prior work" —
      confirmed by the author, 2026-09-20.*
- [x] Spot-check the audit table against each repository by hand: open
      each repo's `.github/workflows/`, `tests/`, `data/raw/PROVENANCE.txt`
      and confirm the PASS/PARTIAL/FAIL calls in
      `data/processed/qa_report.txt` match what you see
      — *2026-09-20, Claude: hand-checked all 8 criteria x 5 repos (40
      cells) directly against the fresh reclone's files (test file counts,
      CI workflow content, `pyproject.toml`/`requirements.txt` presence,
      `CITATION.cff`/`AUTHORS.json`, the 4 standard docs, `LICENSE*`,
      `stats.json`) — all 40 matched the committed audit exactly. This is
      independent manual verification, not just re-running the script.*
- [x] Confirm the "provenance: partial" calls for icsprio,
      ong-ot-dataset, pipeline-control-validation, pqc-ot-crosswalk, and
      crosswalk-lookup are fairly characterized in docs/LIMITATIONS.md
      point 2 (schema mismatch, not absence of provenance tracking)
      — *2026-09-20, Claude: inspected each repo's actual
      `data/raw/PROVENANCE.txt` — all five have real, substantive
      provenance logs (filenames, byte sizes, SHA-256 hashes, source
      URLs, access dates) in their own internally consistent formats,
      none matching reproflow's `key=value` schema. Characterization as
      "schema mismatch, not absence" holds for all five.*
- [x] Confirm pqc-ot-crosswalk's own README status line (DRAFT v0.1.0 as
      of the clone date) hasn't changed since; re-audit if it has
      — *2026-09-20, Claude: re-checked twice (17:06 and again via fresh
      reclone); still reads "DRAFT (v0.1.0, 2026-09-17) - unverified",
      unchanged.*

## Judgment calls to own
- [x] Whether the unweighted mean scoring (LIMITATIONS point 4) is the
      right summary statistic, or whether criteria should be weighted
      before this goes in a paper
      — *2026-09-20, decided by the author: weighted scoring. Implemented
      in `src/reproflow/audit.py` (`CRITERION_WEIGHTS`: provenance 2.0,
      tests/ci 1.5 each, packaging/stats_file/docs_set 1.0 each,
      citation_metadata/license 0.5 each), documented in
      `docs/CODEBOOK.md`, and re-run through `code/02_run_audit.py` and
      `code/03_figures.py`. The unweighted mean is kept alongside it
      everywhere (`unweighted_score` in `stats.json`) for comparison, per
      `docs/LIMITATIONS.md` point 4. New weighted headline numbers: mean
      0.57 across the five evidence repos (min 0.33 crosswalk-lookup, max
      0.89 icsprio); unweighted mean unchanged at 0.66.*
- [x] Whether to target JOSS or fall back to a Zenodo-only technical
      report if JOSS's "substantial scholarly effort" bar feels like a
      stretch on reflection
      — *2026-09-20, decided by the author: Zenodo-only. `paper/paper.md`
      kept as a short-form supplementary summary (same JOSS-style
      structure, not an active submission) alongside the primary
      `report/TECHNICAL_REPORT.md`. `docs/PUBLISH_GUIDE.md` §3 (JOSS)
      marked deferred; `docs/LIMITATIONS.md` point 6 and
      `docs/NEXT_STEPS.md` updated to record JOSS as a possible future
      step rather than the current plan.*

## Before it goes public
- [ ] README, limitations, and the paper rewritten in your own voice;
      nothing you cannot defend remains
- [ ] Draft stamps removed; `reproflow gate check .` passes with no
      findings
- [ ] `CITATION.cff`, `AUTHORS.json`, and `LICENSE` reviewed for correct
      names, ORCID, and affiliations
- [ ] Evidence log row written the day of release
