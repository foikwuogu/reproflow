# Limitations

STATUS: DRAFT (unverified — see VERIFY_CHECKLIST.md)

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

4. **The compliance score is an unweighted mean.** All eight criteria
   count equally toward a repository's score. A repository missing tests
   entirely and a repository missing only `NEXT_STEPS.md` both lose the
   same 0.125 from a perfect score, even though the two gaps are not
   equally consequential for reproducibility. The score is a summary for
   comparison across repositories, not a certification.

5. **Secret detection in the publish gate is deliberately conservative.**
   `reproflow.gate` matches a small set of high-confidence secret shapes
   (GitHub/AWS/OpenAI-style key prefixes, PEM headers, a Zenodo token
   assignment pattern) rather than running a general entropy scanner. It
   will miss secret formats outside this list and should not be treated as
   a complete secret scan; a dedicated secret-scanning tool remains
   necessary for anything security-sensitive.

6. **JOSS suitability is the author's read of the JOSS criteria, not a
   pre-submission decision by JOSS editors.** Whether reproflow clears the
   "substantial scholarly effort" bar is for JOSS reviewers to judge; this
   project's paper makes the case but does not assume the outcome.
