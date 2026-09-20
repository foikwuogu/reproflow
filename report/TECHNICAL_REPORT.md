# reproflow: a reproducible-engineering framework for security-relevant data pipelines

STATUS: DRAFT (unverified — see docs/VERIFY_CHECKLIST.md)

**Authors:** Friday Ogochukwu Ikwuogu (ORCID [0009-0009-2222-1318](https://orcid.org/0009-0009-2222-1318)), Abidemi Orimogunje, Eria Othieno Pinyi, David Mike-Ewewie
**Date:** 2026-09-20
**License:** CC BY 4.0 (this report); MIT (code) — see `LICENSE`
**DOI:** pending first Zenodo release

## 1. Motivation

Five prior repositories from this research program — `icsprio` (an ICS
vulnerability-prioritization package), `ong-ot-dataset` (an oil & gas OT
vulnerability dataset pipeline), `pipeline-control-validation` (a
PHMSA/DOE control-failure validation study), `pqc-ot-crosswalk` (a
post-quantum-cryptography applicability study for OT protocols), and
`crosswalk-lookup` (a TSA Pipeline-2021-02 compliance-mapping tool) —
were each built to be individually reproducible, but not against a shared,
checked standard. This project extracts that standard from the strongest
of the five, packages it as `reproflow`, and uses it to audit all five
plus itself.

## 2. The framework

`reproflow` defines reproducibility for a data-pipeline repository as
eight structural criteria, each scored `pass` (1.0), `partial` (0.5), or
`fail` (0.0):

1. **Packaging** — an installable `pyproject.toml` or `setup.py`, not just
   a pinned `requirements.txt`.
2. **Tests** — three or more `test_*.py` / `*_test.py` files.
3. **Continuous integration** — a GitHub Actions workflow that actually
   invokes the test suite, not only a publishing or metadata-update
   workflow.
4. **Provenance** — a `PROVENANCE.txt` ledger recording, per fetch,
   filename, byte count, SHA-256, source URL, and access date.
5. **A machine-readable stats file** — a non-empty, parseable
   `stats.json` that any document's numbers can be interpolated from.
6. **A standard documentation set** — `CODEBOOK.md`, `LIMITATIONS.md`,
   `VERIFY_CHECKLIST.md`, `NEXT_STEPS.md`.
7. **Citation metadata** — both `CITATION.cff` and `AUTHORS.json`.
8. **A license file.**

Full pass/partial/fail rules for each criterion are in
`docs/CODEBOOK.md`; the implementation is `src/reproflow/audit.py`.

The headline score is a **weighted** mean across the eight criteria:
provenance (weight 2.0), tests and CI (1.5 each), packaging, the stats
file, and the documentation set (1.0 each), and citation metadata and
licensing (0.5 each) — see `docs/CODEBOOK.md` for the full table and the
rationale (the weights favor the mechanics that make a result
independently re-runnable — provenance, tests, CI — over administrative
or presentational criteria). The flat, unweighted mean across the same
eight criteria is also reported throughout (as `unweighted_score` in
`stats.json`) for comparison, since the weighting is an editorial
judgment call, not a derived or externally validated metric
(`docs/LIMITATIONS.md` §4 discusses what either figure does and does not
imply). The check itself is structural either way: it confirms the right
files exist and have the right shape, not that a repository's own
pipeline currently runs end-to-end (`docs/LIMITATIONS.md` §1).

## 3. Method

`code/01_fetch_repos.py` clones each evidence repository at its current
default-branch HEAD and logs the clone's commit hash, byte size, source
URL, and access date to `data/raw/PROVENANCE.txt`, using
`reproflow.provenance.record_repo_clone()`. `code/02_run_audit.py` then
runs `reproflow.audit.audit_repo()` against each clone and against this
project's own repository, and writes the full structured result to
`data/processed/audit_results.json`, a human-readable version to
`data/processed/qa_report.txt`, and every number this report quotes to
`data/processed/stats.json`. `code/03_figures.py` renders the compliance
heatmap (\autoref{fig:heatmap} in the paper; `paper/figures/compliance_heatmap.png`
here) from the same JSON.

No evidence repository was modified by this project; all five are
read-only inputs, audited as found (see `BUILD_SPEC.md`).

## 4. Results

| Repository | Packaging (1.0) | Tests (1.5) | CI (1.5) | Provenance (2.0) | Stats file (1.0) | Docs set (1.0) | Citation (0.5) | License (0.5) | Weighted score | Unweighted score |
|---|---|---|---|---|---|---|---|---|---|---|
| icsprio | PASS | PASS | PASS | PARTIAL | PASS | PASS | PASS | PASS | **0.89** | 0.94 |
| ong-ot-dataset | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PASS | PASS | PASS | PASS | **0.67** | 0.75 |
| pipeline-control-validation | PARTIAL | FAIL | FAIL | PARTIAL | PASS | PASS | PASS | PASS | **0.50** | 0.62 |
| pqc-ot-crosswalk | FAIL | FAIL | FAIL | PARTIAL | PASS | PASS | PASS | PASS | **0.44** | 0.56 |
| crosswalk-lookup | FAIL | FAIL | FAIL | PARTIAL | FAIL | PASS | PASS | PASS | **0.33** | 0.44 |
| **reproflow (this project)** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **1.00** | 1.00 |

(Reproduced exactly from `data/processed/stats.json` and
`audit_results.json`; commit hashes for each clone are in
`data/raw/PROVENANCE.txt`. Parenthesized numbers in the header row are
each criterion's weight, from `docs/CODEBOOK.md`.)

- Weighted mean score across the five evidence repositories: **0.57**
  (min 0.33 for crosswalk-lookup, max 0.89 for icsprio). The unweighted
  (flat eight-way) mean is **0.66** (min 0.44, max 0.94) — the weighted
  figure is lower because the repositories that fail most often
  (`pipeline-control-validation`, `pqc-ot-crosswalk`, `crosswalk-lookup`)
  fail disproportionately on the higher-weighted tests/CI/provenance
  criteria rather than the lower-weighted administrative ones.
- Every evidence repository logs provenance for its fetches; none yet use
  `reproflow`'s own ledger schema, which is why all five score `partial`
  rather than `pass` on that criterion (`docs/LIMITATIONS.md` §2).
- `icsprio`, the earliest and most actively maintained of the five, is
  the only evidence repository with a full, installable package, an
  offline test suite of meaningful size (12 files), and CI that runs it —
  it is also the only one of the five with its own Zenodo DOI already
  minted at the time of audit.
- `crosswalk-lookup`, the newest and smallest of the five (a static HTML
  lookup tool plus its data pipeline), has no packaging, no tests, no CI,
  and no `stats.json`, despite otherwise carrying full documentation,
  citation metadata, and licensing — consistent with it being built as a
  static site rather than a Python package, a case the checklist was not
  originally tuned for (see `docs/NEXT_STEPS.md`).
- `reproflow` scores 1.00 (both weighted and unweighted) on its own audit
  as of this draft.

\autoref{fig:heatmap}: `paper/figures/compliance_heatmap.png` — repository
x criterion compliance, viridis sequential ramp, PASS/PARTIAL/FAIL
direct-labeled per cell, per-repository score in the right margin.

## 5. Discussion

The spread in Table 1 is the practical case for `reproflow`: the same
author, working on the same class of problem across the same few months,
produced repositories that range from fully compliant with a standard
that did not yet exist to missing most of its mechanical components —
not because any one repository was carelessly built, but because there
was no checked standard to build against until this project extracted
one from the best of them. `reproflow audit` turns "is this reproducible"
from a judgment call into a checklist a CI job can run on every push, and
`reproflow init` means a new project starts at `icsprio`'s level rather
than working up to it.

The self-audit result (1.00) is not evidence the framework is complete —
see `docs/LIMITATIONS.md` for what the checklist does not check (whether
tests are good tests, whether CI is currently green, whether an
unfamiliar provenance schema is nonetheless sound) — only that it
currently meets its own bar, which is the minimum a tool making this kind
of claim should be able to say about itself.

## 6. Limitations

See `docs/LIMITATIONS.md` for the full list; in summary: the audit checks
structure, not execution; the provenance criterion is schema-specific to
this framework's own ledger format; the evidence set is five repositories
from one author, not a representative sample; the per-criterion weights
behind the headline score are the author's own editorial judgment, not a
derived or externally validated metric (the unweighted mean is reported
alongside it for exactly this reason); and the publish gate's secret
detection is a conservative pattern list, not a general-purpose scanner.

## 7. Availability

Code: `https://github.com/foikwuogu/reproflow` (MIT). This report is the
primary write-up filed with the archival release: **Zenodo DOI pending
first release** (`docs/PUBLISH_GUIDE.md`). `paper/paper.md` is a
short-form supplementary summary in the same document, not a separate
JOSS submission — see that file's status line for why.

## Citation

See `CITATION.cff`.
