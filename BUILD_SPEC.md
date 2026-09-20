# Build spec

```
PROJECT:        reproflow — Reproducible Data-Pipeline Engineering Framework
                 (archetype: Pipeline/tool, with a technical-report/JOSS write-up)

QUESTION:       What does it take to make a critical-infrastructure-security data
                 pipeline verifiably reproducible — and how do five real research
                 repositories from the same author measure up against that standard?

SOURCES:        - github.com/foikwuogu/icsprio (cloned, evidence repo 1)
                 - github.com/foikwuogu/ong-ot-dataset (cloned, evidence repo 2)
                 - github.com/foikwuogu/pipeline-control-validation (cloned, evidence repo 3)
                 - github.com/foikwuogu/pqc-ot-crosswalk (cloned, evidence repo 4)
                 - github.com/foikwuogu/crosswalk-lookup (cloned, evidence repo 5)
                 All cloned 2026-09-20; commit hash of each clone logged to
                 data/raw/PROVENANCE.txt by code/01_fetch_repos.py.

UNIT:           A repository, audited against a fixed checklist; a framework
                 component (packaging / tests / CI / provenance / docs).

MEASURES:       Per repo: packaging present (pyproject.toml vs. requirements.txt
                 vs. none), test suite present + test-file count, CI workflow
                 present + whether it runs the test suite, provenance log present
                 + well-formed, machine-readable stats file present, documentation
                 set completeness (CODEBOOK/LIMITATIONS/VERIFY_CHECKLIST/NEXT_STEPS),
                 CITATION.cff + AUTHORS.json present, LICENSE present. Combined into
                 a compliance score (criteria met / criteria total) per repo.
                 Checklist criteria are drawn directly from this framework's own
                 documentation standard (docs/CODEBOOK.md defines each).

OUTPUTS:        - reproflow: pip-installable Python package + CLI
                   (`reproflow init|provenance|gate|audit`), stdlib-only.
                 - tests/: offline pytest suite (fixtures, no network).
                 - .github/workflows/ci.yml: runs the test suite on push/PR.
                 - data/processed/audit_results.json, stats.json, qa_report.txt:
                   the five-repo audit, produced by code/02_run_audit.py.
                 - paper/figures/compliance_heatmap.png: audit results, DRAFT until verified.
                 - paper/paper.md: JOSS submission paper.
                 - report/TECHNICAL_REPORT.md: fuller write-up for Zenodo, DRAFT until verified.
                 - docs/: CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, NEXT_STEPS, PUBLISH_GUIDE.

VENUES:         GitHub (public repo) + Zenodo (versioned DOI) + JOSS submission
                 (paper.md + review checklist); author submits to JOSS personally.

VERIFY POINTS:  - The audit checklist and pass/fail thresholds for each criterion
                   (docs/VERIFY_CHECKLIST.md) — the author should confirm these
                   are the right bar and not tuned to favor icsprio.
                 - Whether a repo's older draft state (e.g. pqc-ot-crosswalk is
                   marked DRAFT v0.1.0 in its own README) should be scored as of
                   the cloned commit, not assumed current — confirm against the
                   live repos before publication.
                 - The claim that this is the author's own prior work (not a
                   third party's) — confirm before naming these repos in a
                   public paper.

LICENSE:        Code: MIT. Docs/report/paper: CC BY 4.0.

ASSUMPTIONS:    - Audit checks file presence, structural conventions, and light
                   content parsing (e.g. "does the CI file invoke pytest"), not
                   full execution of each evidence repo's own pipeline — running
                   five independent, network-dependent pipelines end-to-end is
                   out of scope for what the framework itself needs to prove.
                 - Evidence repos are read-only inputs; per the author's choice,
                   this build does NOT modify icsprio, ong-ot-dataset,
                   pipeline-control-validation, pqc-ot-crosswalk, or
                   crosswalk-lookup. Any gaps the audit finds are reported, not
                   patched, in this build.
                 - Author block and co-author list use the standard block on
                   file; JOSS listed venue per the author's selection.
```
