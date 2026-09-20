---
title: 'reproflow: a reproducible-engineering framework for security-relevant data pipelines'
tags:
  - Python
  - reproducibility
  - research software engineering
  - provenance
  - continuous integration
  - critical infrastructure security
authors:
  - name: Friday Ogochukwu Ikwuogu
    orcid: 0009-0009-2222-1318
    affiliation: 1
  - name: Abidemi Orimogunje
    affiliation: 2
  - name: Eria Othieno Pinyi
    affiliation: 3
  - name: David Mike-Ewewie
    affiliation: 4
affiliations:
  - name: Independent Researcher, Odessa, Texas, USA
    index: 1
  - name: Electrical and Electronic Engineering Department, Redeemer's University, Ede, Osun State, Nigeria
    index: 2
  - name: Computer Science and Engineering Department, University of Fairfax, USA
    index: 3
  - name: Computer Science Department, University of Texas Permian Basin, Odessa, Texas, USA
    index: 4
date: 20 September 2026
bibliography: paper.bib
---

STATUS: DRAFT (unverified — see docs/VERIFY_CHECKLIST.md; not yet submitted to JOSS)

# Summary

`reproflow` is a small, dependency-free Python package and command-line
tool for making a research data pipeline mechanically reproducible. It
packages four things that are usually reinvented by hand on every project:
a provenance ledger for every fetched input (filename, byte count, SHA-256,
source URL, access date), a "publish gate" that scans a project tree for
draft stamps, unresolved verify-tags, bracketed placeholders, and secret-
shaped strings before release, an auditor that scores any repository
against an eight-criterion reproducibility checklist (packaging, tests,
continuous integration, provenance, a machine-readable stats file,
a standard documentation set, citation metadata, and licensing), and a
scaffolder that generates a new project already meeting that checklist.
None of the four requires a third-party dependency at runtime, so
`reproflow` can sit underneath a pipeline without adding to its dependency
surface.

# Statement of need

Data-pipeline projects in applied security research — the kind that join
public vulnerability feeds, incident reports, or compliance mappings into
a table someone else will cite — accumulate ad hoc reproducibility
practices project by project: one repository gets a provenance log because
that day's task needed one, another gets continuous integration because
a reviewer asked for it, and a documentation set that was thorough in
January is missing entirely by June. There is general guidance for what
"good enough" computational reproducibility looks like [@wilson2017good;
@sandve2013ten], and project-scaffolding tools exist for the closely
related problem of laying out a new data-science repository consistently
[@cookiecutter_data_science]. What is missing between the two is something
that can look at a repository that already exists — including one nobody
set out to scaffold consistently — and say, specifically and
reproducibly, which of the standard's components are present, which are
partially present, and which are missing, so the gap is a list rather
than an impression.

The five evidence repositories this project audits
(`icsprio`, `ong-ot-dataset`, `pipeline-control-validation`,
`pqc-ot-crosswalk`, `crosswalk-lookup`) are the motivating case: all five
are the same author's own critical-infrastructure-security data
pipelines, built over the same few months, and `reproflow audit` finds
real, uneven compliance across them — a mean score of 0.66 across the
five (`icsprio` 0.94 down to `crosswalk-lookup` 0.44) against the same
eight-criterion checklist reproflow itself now scores 1.00 on. That
spread, on one author's own work, is the case for a checklist that is
checked by a program rather than remembered by a person.

# Functionality

```bash
# Scaffold a new, already-compliant project
reproflow init my-project --name "My Project" \
    --author-name "Your Name" --author-orcid 0000-0000-0000-0000

# Log a fetch's provenance
reproflow provenance record data/raw/source.csv \
    --source-url https://example.org/source.csv

# Score any repository against the checklist
reproflow audit run /path/to/repo --json result.json

# Check a project is release-ready
reproflow gate check .
```

`reproflow.provenance` hashes a fetched file (or, for a cloned git
repository, records its commit hash) and appends one line to a plain-text
ledger; `reproflow.gate` walks a tree looking for the mechanical reasons a
release is not ready and refuses to pass while any remain; `reproflow.audit`
runs the same eight structural checks used throughout this paper and
returns a machine-readable score plus a per-criterion explanation, so a
`partial` result always says why (for instance, several evidence
repositories log provenance in an internally consistent format that
predates `reproflow`'s own ledger schema, which the audit reports as a
schema mismatch rather than an absence of provenance tracking — see
`docs/LIMITATIONS.md`); `reproflow.scaffold` generates the file layout the
audit checks for. Full usage and the criterion-by-criterion pass/partial/
fail rules are documented in `docs/CODEBOOK.md`, and the offline `pytest`
suite in `tests/` exercises all four modules without network access.

# Comparison with existing tools

Project scaffolders such as `cookiecutter-data-science`
[@cookiecutter_data_science] solve project layout at creation time but do
not audit an existing repository against a checklist, and general
reproducibility checklists [@wilson2017good; @sandve2013ten] are
guidance for a person to apply by hand rather than a program a CI job can
run. `reproflow` combines both: the same checklist a new project is
scaffolded to meet is the checklist `reproflow audit` checks any
repository against, so drift between a project's initial layout and its
current state is visible rather than assumed away.

# Acknowledgements

Development was AI-assisted (code, scaffolding, and drafting mechanics);
the checklist design, the choice of evidence repositories, and every
number reported here were reviewed and verified by the author before
release, per `docs/VERIFY_CHECKLIST.md`.

# References
