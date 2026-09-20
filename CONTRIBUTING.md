# Contributing

Issues and pull requests are welcome.

1. Fork and clone; `pip install -e ".[dev]"`.
2. Add or update tests under `tests/` for any behavior change — `pytest -q`
   must pass.
3. `python -m reproflow.cli gate check .` should report no new findings
   (the repository still carries DRAFT stamps until the v0.1.0 verification
   gate passes; don't add new ones).
4. Keep the standard library the runtime default. A new hard dependency
   needs a reason in the pull request description.
5. If you change what a criterion in `reproflow.audit` checks, update
   `docs/CODEBOOK.md`'s table in the same pull request — that table is the
   only place the pass/partial/fail rule for each criterion is defined.

## Code of conduct

Be respectful and constructive. Disagreement about design is welcome;
personal attacks are not.
