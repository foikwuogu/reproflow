import json

from reproflow import audit


def _touch(path, content=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_fully_compliant_repo_scores_high(tmp_path):
    _touch(tmp_path / "pyproject.toml", "[project]\nname='x'\n")
    _touch(tmp_path / "tests" / "test_a.py", "def test_a(): pass\n")
    _touch(tmp_path / "tests" / "test_b.py", "def test_b(): pass\n")
    _touch(tmp_path / "tests" / "test_c.py", "def test_c(): pass\n")
    _touch(
        tmp_path / ".github" / "workflows" / "ci.yml",
        "jobs:\n  test:\n    steps:\n      - run: pytest -q\n",
    )
    _touch(
        tmp_path / "data" / "raw" / "PROVENANCE.txt",
        "filename=a.csv | bytes=10 | sha256=abc | source_url=https://x | access_date=2026-01-01\n",
    )
    _touch(tmp_path / "data" / "processed" / "stats.json", json.dumps({"n": 1}))
    for name in ["CODEBOOK.md", "LIMITATIONS.md", "VERIFY_CHECKLIST.md", "NEXT_STEPS.md"]:
        _touch(tmp_path / "docs" / name, "content\n")
    _touch(tmp_path / "CITATION.cff", "cff-version: 1.2.0\n")
    _touch(tmp_path / "AUTHORS.json", "{}\n")
    _touch(tmp_path / "LICENSE", "MIT\n")

    result = audit.audit_repo(tmp_path, repo_name="fully-compliant")
    assert result.score == 1.0
    for crit in result.criteria:
        assert crit.status == "pass", f"{crit.name} was {crit.status}: {crit.detail}"


def test_empty_repo_scores_zero(tmp_path):
    result = audit.audit_repo(tmp_path, repo_name="empty")
    assert result.score == 0.0
    for crit in result.criteria:
        assert crit.status == "fail"


def test_requirements_txt_only_is_partial_packaging(tmp_path):
    _touch(tmp_path / "requirements.txt", "pandas\n")
    result = audit.check_packaging(tmp_path)
    assert result.status == "partial"


def test_ci_without_pytest_is_partial(tmp_path):
    _touch(
        tmp_path / ".github" / "workflows" / "publish.yml",
        "jobs:\n  publish:\n    steps:\n      - run: echo hi\n",
    )
    result = audit.check_ci(tmp_path)
    assert result.status == "partial"


def test_ci_missing_entirely_fails(tmp_path):
    result = audit.check_ci(tmp_path)
    assert result.status == "fail"


def test_two_test_files_is_partial_not_pass(tmp_path):
    _touch(tmp_path / "tests" / "test_a.py", "")
    _touch(tmp_path / "tests" / "test_b.py", "")
    result = audit.check_tests(tmp_path)
    assert result.status == "partial"


def test_malformed_provenance_ledger_is_partial(tmp_path):
    _touch(tmp_path / "data" / "raw" / "PROVENANCE.txt", "filename=a.csv | bytes=10\n")
    result = audit.check_provenance(tmp_path)
    assert result.status == "partial"


def test_docs_set_partial_when_some_missing(tmp_path):
    _touch(tmp_path / "docs" / "CODEBOOK.md", "x")
    _touch(tmp_path / "docs" / "LIMITATIONS.md", "x")
    result = audit.check_docs_set(tmp_path)
    assert result.status == "partial"
    assert "verify_checklist" in result.detail


def test_citation_metadata_partial_when_only_one_present(tmp_path):
    _touch(tmp_path / "CITATION.cff", "x")
    result = audit.check_citation_metadata(tmp_path)
    assert result.status == "partial"


def test_audit_many_preserves_order_and_names(tmp_path):
    repo_a = tmp_path / "a"
    repo_b = tmp_path / "b"
    repo_a.mkdir()
    repo_b.mkdir()
    results = audit.audit_many({"Alpha": repo_a, "Beta": repo_b})
    assert [r.repo_name for r in results] == ["Alpha", "Beta"]


def test_to_markdown_table_has_header_and_rows(tmp_path):
    result = audit.audit_repo(tmp_path, repo_name="empty")
    table = audit.to_markdown_table([result])
    assert "| Repository |" in table
    assert "empty" in table


def test_stats_file_empty_json_is_partial(tmp_path):
    _touch(tmp_path / "stats.json", "{}")
    result = audit.check_stats_file(tmp_path)
    assert result.status == "partial"


def test_stats_file_invalid_json_is_partial(tmp_path):
    _touch(tmp_path / "stats.json", "{not valid json")
    result = audit.check_stats_file(tmp_path)
    assert result.status == "partial"
