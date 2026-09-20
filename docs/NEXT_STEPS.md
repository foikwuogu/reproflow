# Next steps

STATUS: DRAFT

What v0.2 adds, so v0.1 is understood as a first release.

- [ ] Publish to PyPI so `pip install reproflow` works without cloning
- [ ] Add a provenance-ledger format auto-detector so `check_provenance`
      recognizes common alternative schemas (e.g. icsprio's pipe-delimited
      format) as first-class rather than reporting them as non-conformant
      to this framework's own convention
- [ ] Weighted or configurable scoring, so a project can declare which of
      the eight criteria matter most for its context
- [ ] `reproflow audit --execute` mode that actually runs a target
      repository's test suite and CI-equivalent steps locally, rather than
      checking only for their presence
- [ ] A hosted, updating dashboard of the evidence-repository audit, so
      the comparison in the paper does not go stale as those repos change
- [ ] Extend the secret-scanning patterns in `reproflow.gate` and consider
      delegating to an established scanner (e.g. gitleaks) rather than a
      fixed pattern list
