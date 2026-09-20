# Next steps

STATUS: DRAFT

What v0.2 adds, so v0.1 is understood as a first release.

- [ ] Publish to PyPI so `pip install reproflow` works without cloning
- [ ] Add a provenance-ledger format auto-detector so `check_provenance`
      recognizes common alternative schemas (e.g. icsprio's pipe-delimited
      format) as first-class rather than reporting them as non-conformant
      to this framework's own convention
- [ ] Configurable scoring: let a project supply its own
      `CRITERION_WEIGHTS` (fixed, author-set weights shipped as of v0.1 —
      see `docs/CODEBOOK.md`) rather than only reproflow's own defaults,
      so a different project's context can weight the eight criteria
      differently
- [ ] Revisit JOSS submission (deferred at v0.1 in favor of a Zenodo-only
      release — see `docs/LIMITATIONS.md` §6 and `docs/PUBLISH_GUIDE.md`
      §3) once the PyPI release and provenance-format auto-detector below
      have landed and strengthened the case
- [ ] `reproflow audit --execute` mode that actually runs a target
      repository's test suite and CI-equivalent steps locally, rather than
      checking only for their presence
- [ ] A hosted, updating dashboard of the evidence-repository audit, so
      the comparison in the paper does not go stale as those repos change
- [ ] Extend the secret-scanning patterns in `reproflow.gate` and consider
      delegating to an established scanner (e.g. gitleaks) rather than a
      fixed pattern list
