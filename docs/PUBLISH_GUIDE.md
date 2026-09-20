# Publish guide

The GitHub repository is published and the Zenodo archive is available at
[10.5281/zenodo.22865360](https://doi.org/10.5281/zenodo.22865360). This
guide records the release workflow for future versions.

**Publication decision (2026-09-20): Zenodo-only.** The author considered
JOSS and decided against it on reflection (see
`docs/VERIFY_CHECKLIST.md` "Judgment calls to own" and
`docs/LIMITATIONS.md` §6) — the active plan is §1 GitHub (already done as
of this writing: the repository is pushed and CI is green) and §2 Zenodo.
§3 JOSS below is kept only as a deferred reference in case that decision
is revisited later (`docs/NEXT_STEPS.md`); do not act on it as part of
this release.

**Before any future release:** finish `docs/VERIFY_CHECKLIST.md` and
confirm `reproflow gate check .` reports no findings.

## 1. GitHub

1. Create the repository at [github.com/new](https://github.com/new).
   Name it `reproflow` (matches `pyproject.toml`, `CITATION.cff`, and every
   URL already written into the docs). Leave it empty — this project
   already has a README.
2. From inside `/home/claude/reproflow` (or wherever you've copied this
   project to your own machine):
   ```bash
   git init -b main
   git add -A
   git commit -m "Initial release: reproflow v0.1.0"
   git remote add origin https://github.com/foikwuogu/reproflow.git
   git push -u origin main
   ```
3. Releases tab -> "Draft a new release" -> tag `v0.1.0`, title
   `v0.1.0`. Release notes: paste the "v0.1.0" section of `CHANGELOG.md`.
   Publish.
4. Settings -> General -> confirm the description and topics (suggested
   topics: `reproducibility`, `research-software`, `provenance`,
   `continuous-integration`, `critical-infrastructure-security`).

## 2. Zenodo

Simplest path, since this is already a GitHub project:

1. Log in at [zenodo.org](https://zenodo.org) with ORCID login (your
   ORCID, `0009-0009-2222-1318`, then attaches automatically).
2. Account -> GitHub -> flip the switch for `foikwuogu/reproflow`.
3. Back on GitHub, create the `v0.1.0` release (step 1.3 above) if you
   haven't yet — Zenodo archives it and mints a DOI within minutes.
4. Copy the minted DOI into:
   - `CITATION.cff` (`doi:` field, replacing the previous pending DOI)
   - The README status line and the "Citation" section
   - `docs/PUBLISH_GUIDE.md` itself (this file), for your own record
5. Add the DOI badge Zenodo gives you to the top of `README.md`.

If you'd rather not enable the GitHub integration, the manual path is:
New upload -> drag in a `v0.1.0` source archive -> set upload type
"Software", title `reproflow: A Reproducible Engineering Framework for
Security-Relevant Data Pipelines`, authors and ORCIDs from
`AUTHORS.json`, description from the paper's Summary section, license
MIT, keywords from `pyproject.toml`, version `0.1.0`, related identifier
the GitHub URL -> Publish.

## 3. JOSS (deferred — not part of the current plan)

Kept for reference only. The author's current decision is Zenodo-only
(see the note at the top of this file and `docs/LIMITATIONS.md` §6); skip
this section unless that decision is revisited. JOSS's own checklist,
already satisfied by this repository:

- [x] OSI-approved license (MIT) — `LICENSE`
- [x] Installation instructions — `README.md`
- [x] Usage examples / API documented — `README.md`, `docs/CODEBOOK.md`
- [x] Automated tests — `tests/` (offline, no network required)
- [x] Contributing guidelines — `CONTRIBUTING.md`
- [x] `paper.md` and `paper.bib` — `paper/`
- [ ] "Substantial scholarly effort" — reviewers decide this; the paper's
      Statement of Need makes the case (§ Statement of need in
      `paper/paper.md`), but confirm you still believe it on re-reading

Steps:

1. Tag and push the GitHub release, and get the Zenodo DOI first (§ 1–2
   above) — JOSS wants a specific archived version, not "main".
2. Submit at [joss.theoj.org/papers/new](https://joss.theoj.org/papers/new)
   with the repository URL (`https://github.com/foikwuogu/reproflow`) and
   the `v0.1.0` / Zenodo DOI as the version to review.
3. Review happens as a public GitHub issue on the JOSS `joss-reviews`
   repository. Respond to each reviewer checklist item with a commit to
   `reproflow` and a reply on the issue. Acceptance mints a second,
   paper-specific DOI — add that one to `CITATION.cff` as well once it
   exists (keep the software DOI too; JOSS papers carry both).

If, on reflection, "substantial scholarly effort" feels like a stretch for
a first release, the fallback is: skip JOSS for now, keep the Zenodo
software release, and resubmit to JOSS once `NEXT_STEPS.md`'s PyPI
release and provenance-format auto-detector land — both strengthen the
case.

## 4. PyPI (optional, listed in NEXT_STEPS.md as a v0.2 target)

1. Create an account and a project-scoped API token at
   [pypi.org](https://pypi.org).
2. `python -m pip install build twine`
3. `python -m build`
4. `python -m twine upload dist/*` — username `__token__`, password the
   API token.
5. Tag the same version on GitHub and Zenodo if not already done.

## After every step

Write the evidence-log row the same day: date, artifact, venue, URL or
DOI, status, files saved. Then update this file, the README status line,
and `CITATION.cff` so they never say something out of date about where
this project actually is.
