# Limitations

STATUS: VERIFIED v0.1.0

Written before any paper discussion section, so the discussion cannot
outrun what is honestly known here.

1. **The audit checks structure, not execution.** `reproflow audit`
   confirms a test directory, a CI workflow, a provenance ledger, etc.
   exist and look right; it does not run each evidence repository's own
   pipeline end to end, so a repository could pass a criterion (e.g. "CI
   runs pytest") while that CI is currently red, or fail (e.g. "no
   `stats.json`") while an equivalent file exists under an unanticipated
   path. Spot-check each score before citing it (see VERIFY_CHECKLIST.md).

2. **The provenance criterion is schema-specific.** `check_provenance`
   only recognizes this framework's own `key=value | key=value` ledger
   line format. icsprio, for example, logs provenance in a different,
   internally consistent pipe-delimited format with the same substantive
   fields (date, filename, bytes, hash, URL); it scores `partial` here not
   because its provenance logging is weak, but because it predates this
   framework and uses a different schema. The audit report says so
   explicitly per repository; readers should not take a `partial`
   provenance score as evidence the underlying repository lacks
   provenance tracking.

3. **The evidence set is the author's own five repositories, not a
   sample.** All five (icsprio, ong-ot-dataset,
   pipeline-control-validation, pqc-ot-crosswalk, crosswalk-lookup) were
   built by the same author, over roughly the same months, and several
   reuse code from one another. The audit demonstrates the framework
   against real, motivating cases and gives a before/after picture as the
   author's own practice matured — it is not evidence of how repositories
   in general fare against this checklist, and no claim of that kind
   should be drawn from it.

4. **The compliance score is weighted, and the weights are the author's
   own editorial judgment, not a derived or externally validated
   metric.** The headline score (`docs/CODEBOOK.md` has the full table)
   counts `provenance` (2.0), `tests` and `ci` (1.5 each) more heavily
   than `packaging`/`stats_file`/`docs_set` (1.0 each) and
   `citation_metadata`/`license` (0.5 each), on the reasoning that the
   first group are the mechanics that let an independent third party
   actually re-run and verify the work, while the second group is closer
   to administrative or presentational. A reader who weighs these
   criteria differently would get a different number from the same
   underlying pass/partial/fail data — that data (and the flat unweighted
   mean, reported alongside the weighted one everywhere it is quoted, as
   `unweighted_score`) is in `data/processed/stats.json` for anyone who
   wants to recompute with their own weights. Neither figure is a
   certification.

5. **Secret detection in the publish gate is deliberately conservative.**
   `reproflow.gate` matches a small set of high-confidence secret shapes
   (GitHub/AWS/OpenAI-style key prefixes, PEM headers, a Zenodo token
   assignment pattern) rather than running a general entropy scanner. It
   will miss secret formats outside this list and should not be treated as
   a complete secret scan; a dedicated secret-scanning tool remains
   necessary for anything security-sensitive.

6. **This release targets Zenodo only, not JOSS.** The author considered
   JOSS and decided the "substantial scholarly effort" bar felt like a
   stretch on reflection (`docs/VERIFY_CHECKLIST.md` "Judgment calls to
   own"); `paper/paper.md` is kept as a short-form supplementary summary
   in the same JOSS-style structure, not as an active submission draft. A
   JOSS submission remains a possible future step (`docs/NEXT_STEPS.md`)
   if that assessment changes.
