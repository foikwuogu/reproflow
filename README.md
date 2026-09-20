# reproflow

**Status:** DRAFT v0.1.0 (unverified — see `docs/VERIFY_CHECKLIST.md`) | **Maintainer:** Friday Ogochukwu Ikwuogu, [0009-0009-2222-1318](https://orcid.org/0009-0009-2222-1318) | **License:** code MIT, docs/report/paper CC BY 4.0

A reproducible-engineering framework for security-relevant data pipelines:
Python packaging, an offline test suite, continuous integration, provenance
logging, and a publish gate — plus an auditor that scores a repository
against the standard, and a scaffolder that generates a new project already
meeting it.

The framework is demonstrated on five of the author's own critical-
infrastructure-security repositories: [icsprio](https://github.com/foikwuogu/icsprio),
[ong-ot-dataset](https://github.com/foikwuogu/ong-ot-dataset),
[pipeline-control-validation](https://github.com/foikwuogu/pipeline-control-validation),
[pqc-ot-crosswalk](https://github.com/foikwuogu/pqc-ot-crosswalk), and
[crosswalk-lookup](https://github.com/foikwuogu/crosswalk-lookup). The audit
in `data/processed/` is the evidence that motivated building this framework
in the first place: practice was inconsistent across five real projects, and
this is the standard extracted from the best of them plus a tool that checks
any repository — including this one — against it.

## What is here

```
src/reproflow/     the installable package: provenance, gate, audit, scaffold, cli
tests/             offline pytest suite (fixtures, no network)
code/               numbered scripts that produce THIS project's own evidence:
                    01_fetch_repos.py  -- clone the five evidence repos, log provenance
                    02_run_audit.py    -- audit each one + reproflow itself
data/raw/           evidence_repos/ (cloned repos) + PROVENANCE.txt
data/processed/     audit_results.json, stats.json, qa_report.txt
docs/               CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, NEXT_STEPS
paper/              paper.md (short-form summary, supplementary) + figures/
report/             TECHNICAL_REPORT.md (primary write-up, for Zenodo)
```

## Install

```
pip install -e ".[dev]"
```

Pure standard library at runtime — no third-party dependencies. `[dev]`
adds `pytest` for the test suite; `[figures]` adds `matplotlib` for the
compliance chart.

## Use the framework on your own project

```bash
# Scaffold a new, already-compliant project
reproflow init my-project --name "My Project" \
    --author-name "Your Name" --author-orcid 0000-0000-0000-0000 \
    --author-email you@example.org

# Log a fetch
reproflow provenance record data/raw/source.csv \
    --source-url https://example.org/source.csv

# Score any repository against the checklist
reproflow audit run /path/to/repo --json result.json

# Check a project is release-ready
reproflow gate check .
```

## Reproduce this project's own evidence

```
pip install -e ".[dev]"
pytest -q                          # unit tests
python code/01_fetch_repos.py      # clone the 5 evidence repos, log provenance
python code/02_run_audit.py        # audit them + reproflow itself
```

A stranger should be able to run these from this README alone and
reproduce `data/processed/` exactly (see `docs/VERIFY_CHECKLIST.md` for
what "exactly" was actually confirmed to mean).

## Headline numbers (from `data/processed/stats.json`; unverified — see status line)

Across the five evidence repositories, mean compliance with the eight-
criterion checklist — weighted toward provenance, tests, and CI, the
mechanics that make a result independently reproducible (see
`docs/CODEBOOK.md` for the weights and rationale) — is 0.57 (min 0.33 for
crosswalk-lookup, max 0.89 for icsprio); reproflow's own self-audit scores
1.00 as of this draft. The unweighted (flat eight-way) mean is 0.66, min
0.44, max 0.94 — both figures are in `stats.json` for comparison. See
`data/processed/qa_report.txt` for the full per-repository, per-criterion
breakdown and `docs/LIMITATIONS.md` before citing any of it — every
`partial` provenance score reflects a schema mismatch with this
framework's own ledger format, not an absence of provenance tracking (all
five evidence repos log provenance; none use this exact schema yet).

## Sources

| Source | Vintage | License | Accessed |
|---|---|---|---|
| github.com/foikwuogu/icsprio | HEAD at clone | MIT (code) / CC BY 4.0 (data) | 2026-09-20 |
| github.com/foikwuogu/ong-ot-dataset | HEAD at clone | MIT (code) / CC BY 4.0 (data) | 2026-09-20 |
| github.com/foikwuogu/pipeline-control-validation | HEAD at clone | MIT (code) / CC BY 4.0 (data) | 2026-09-20 |
| github.com/foikwuogu/pqc-ot-crosswalk | HEAD at clone | MIT (code) / CC BY 4.0 (data) | 2026-09-20 |
| github.com/foikwuogu/crosswalk-lookup | HEAD at clone | MIT (code) / CC BY 4.0 (data, partial\*) | 2026-09-20 |

\* crosswalk-lookup's dataset excludes CIS Controls v8 and IEC 62443 cells
from CC BY 4.0, per their own source licenses (CC BY-NC-ND 4.0 and
proprietary ISA/IEC respectively) — see that repository's own LICENSE.

Commit hashes for each clone are in `data/raw/PROVENANCE.txt`.

## Limitations

See `docs/LIMITATIONS.md` before using or citing anything here.

## Citation

See `CITATION.cff`. DOI: pending first Zenodo release (see
`docs/PUBLISH_GUIDE.md`).
