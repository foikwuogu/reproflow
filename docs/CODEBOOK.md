# Codebook

STATUS: VERIFIED v0.1.0

This defines every criterion `reproflow audit` checks, what counts as
pass/partial/fail for each, and every field in the ledger and result
formats the package produces. Anything the audit report or paper quotes
traces back to a definition here.

## Audit criteria (`reproflow.audit`)

Each criterion is scored `pass` (1.0), `partial` (0.5), or `fail` (0.0) for
a given repository. Checks are structural and light-content (file
presence, directory conventions, a regex match inside a workflow file) —
they do not execute the audited repository's own pipeline.

### Scoring: weighted (headline) and unweighted (comparison)

The repository's headline score (`AuditResult.score`, `"score"` in
`audit_results.json` / `stats.json`) is a **weighted** mean: each
criterion's pass/partial/fail value is multiplied by an importance weight
before averaging. The weights reflect this framework's own thesis —
reproducibility *mechanics* that let an independent third party actually
re-run and verify the work count for more than packaging polish or
administrative metadata:

| Criterion | Weight | Rationale |
|---|---|---|
| `provenance` | 2.0 | The specific claim this project makes ("every input is traceable"); most directly tied to the project's stated purpose. |
| `tests` | 1.5 | A repository nobody can verify by re-running its checks is not independently reproducible. |
| `ci` | 1.5 | Automated, third-party re-execution (not just "it worked on my machine") is what makes the tests criterion trustworthy over time. |
| `packaging` | 1.0 | Necessary for anyone else to run the code at all, but a lower bar than actually testing or tracing it. |
| `stats_file` | 1.0 | Ties prose claims to a re-derivable artifact — this project's own "stats-file rule." |
| `docs_set` | 1.0 | Documents the process but does not itself verify anything. |
| `citation_metadata` | 0.5 | Administrative: aids attribution/discovery, does not affect whether results reproduce. |
| `license` | 0.5 | Administrative: legal clarity, not a reproducibility mechanic. |

The weighted score is `sum(weight[c] * value[status]) / sum(weight[c])`
across the eight criteria. These weights are the author's own editorial
judgment, not a derived or externally validated metric — see
`LIMITATIONS.md` §4.

For transparency and comparison, `AuditResult.unweighted_score`
(`"unweighted_score"` in the same JSON files) is also always computed: the
plain flat mean across the eight criteria, each counted equally, exactly
as this project reported before weighting was introduced. Both figures
are reported side by side in `stats.json`, `paper/paper.md`, and
`report/TECHNICAL_REPORT.md`.

| Criterion | pass | partial | fail |
|---|---|---|---|
| `packaging` | `pyproject.toml` or `setup.py` present | only `requirements.txt` present (deps pinned, not installable as a package) | none of the three present |
| `tests` | 3+ files matching `test_*.py` / `*_test.py` | 1–2 such files | none found |
| `ci` | `.github/workflows/*.yml` exists and at least one file references `pytest` or `unittest` | workflow file(s) exist but none appear to run the test suite (e.g. publish-only automation) | no `.github/workflows` directory or no workflow files |
| `provenance` | `data/raw/PROVENANCE.txt` (or repo-root `PROVENANCE.txt`) exists and every record has `filename`, `bytes`, `sha256`, `source_url`, `access_date` in this module's `key=value \| key=value` line format | ledger exists but is empty, has some malformed records, or uses a different (possibly still valid) provenance convention | no ledger file found |
| `stats_file` | a `stats.json` exists anywhere in the tree, parses as JSON, and is non-empty | `stats.json` exists but is empty or fails to parse | no `stats.json` found |
| `docs_set` | all four of `CODEBOOK.md`, `LIMITATIONS.md`, `VERIFY_CHECKLIST.md`, `NEXT_STEPS.md` present (at repo root or under `docs/`) | 1–3 present | none present |
| `citation_metadata` | both `CITATION.cff` and `AUTHORS.json` present at repo root | only one of the two present | neither present |
| `license` | a `LICENSE*` file present at repo root (2+ such files, e.g. code + data licensing, still scores `pass`) | — (no partial state defined) | no `LICENSE*` file |

## Provenance ledger fields (`reproflow.provenance`)

Each line of `PROVENANCE.txt` is one fetch, written as
`key=value | key=value | ...`:

| Field | Definition |
|---|---|
| `filename` | Name of the fetched file, or the cloned repository's directory name for `record_repo_clone()` |
| `bytes` | Size in bytes of the fetched file, or total size of the cloned repository's working tree (excluding `.git`) |
| `sha256` | SHA-256 of the file's bytes, or the git commit hash for a cloned repository (noted in `note` when this substitution applies) |
| `source_url` | The exact URL fetched from |
| `access_date` | UTC timestamp of the fetch, ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`) |
| `note` | Optional free-text annotation |

## Publish gate finding kinds (`reproflow.gate`)

| Kind | Trigger |
|---|---|
| `draft_stamp` | A line matching `STATUS:\s*DRAFT` (case-insensitive) |
| `verify_tag` | A line containing the literal marker this framework uses to flag an unresolved number or claim |
| `placeholder` | A bracketed placeholder using any of these lead words (case-insensitive), such as insert, todo, tbd, pending, or fill-in, e.g. an unfilled to-do item in square brackets |
| `secret` | A line matching a high-confidence secret shape: GitHub token prefix, AWS access key ID, an OpenAI-style key prefix, a PEM private-key header, or a `ZENODO_*TOKEN=` assignment |

By default the gate excludes `.git`, virtual-env and build directories,
`templates/` (scaffold templates ship with intentional placeholders), and
`tests/` (fixture data intentionally contains marker strings for testing).

## Evidence-repository audit (`data/processed/audit_results.json`, `stats.json`)

`code/02_run_audit.py` runs `reproflow.audit.audit_repo()` against each
cloned evidence repository and against this project itself, and writes:

- `audit_results.json` — one object per repository: `repo_name`,
  `repo_path`, `commit` (git commit hash at clone time), `score`
  (weighted), `unweighted_score`, and the eight `criteria` objects
  (`name`, `status`, `detail`, `evidence`).
- `stats.json` — every summary number the paper and report quote:
  `criterion_weights`, per-repo weighted and unweighted scores, the
  weighted and unweighted mean/min/max across the five evidence repos,
  reproflow's own self-audit score (both forms), and a pass-count per
  criterion across the evidence repos.
- `qa_report.txt` — the same information formatted for a human reader.
