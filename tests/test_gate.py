from reproflow import gate


def test_clean_tree_passes(tmp_path):
    (tmp_path / "README.md").write_text("# Project\n\nA finished, released project.\n")
    findings = gate.scan_tree(tmp_path)
    assert findings == []
    assert gate.gate_passes(findings)


def test_detects_draft_stamp(tmp_path):
    (tmp_path / "README.md").write_text("STATUS: DRAFT v0.1 (unverified)\n")
    findings = gate.scan_tree(tmp_path)
    kinds = {f.kind for f in findings}
    assert "draft_stamp" in kinds
    assert not gate.gate_passes(findings)


def test_detects_draft_stamp_with_markdown_bold(tmp_path):
    (tmp_path / "README.md").write_text("**Status:** DRAFT v0.1.0 (unverified)\n")
    findings = gate.scan_tree(tmp_path)
    assert any(f.kind == "draft_stamp" for f in findings)


def test_detects_verify_tag(tmp_path):
    (tmp_path / "LIMITATIONS.md").write_text("The match rate is [VERIFY] percent.\n")
    findings = gate.scan_tree(tmp_path)
    assert any(f.kind == "verify_tag" for f in findings)


def test_detects_placeholder_bracket(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "NEXT_STEPS.md").write_text("- [ ] [insert next milestone]\n")
    findings = gate.scan_tree(tmp_path)
    assert any(f.kind == "placeholder" for f in findings)


def test_detects_github_token(tmp_path):
    (tmp_path / "notes.txt").write_text("token: ghp_" + "b" * 36 + "\n")
    findings = gate.scan_tree(tmp_path)
    assert any(f.kind == "secret" for f in findings)


def test_detects_aws_key(tmp_path):
    (tmp_path / "config.txt").write_text("AKIAABCDEFGHIJKLMNOP\n")
    findings = gate.scan_tree(tmp_path)
    assert any(f.kind == "secret" for f in findings)


def test_excludes_git_directory(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config.md").write_text("STATUS: DRAFT\n")
    findings = gate.scan_tree(tmp_path)
    assert findings == []


def test_ignores_binary_and_non_text_extensions(tmp_path):
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n STATUS: DRAFT")
    findings = gate.scan_tree(tmp_path)
    assert findings == []


def test_format_report_pass(tmp_path):
    report = gate.format_report([], tmp_path)
    assert "PASS" in report


def test_format_report_fail_groups_by_kind(tmp_path):
    (tmp_path / "a.md").write_text("STATUS: DRAFT\n[VERIFY]\n")
    findings = gate.scan_tree(tmp_path)
    report = gate.format_report(findings, tmp_path)
    assert "FAIL" in report
    assert "[draft_stamp]" in report
    assert "[verify_tag]" in report


def test_excludes_evidence_repos_directory_by_default(tmp_path):
    # Read-only third-party clones under data/raw/evidence_repos are not
    # this project's own authored content; their draft/verify markers are
    # theirs to resolve, not something a downstream audit should flag.
    nested = tmp_path / "data" / "raw" / "evidence_repos" / "some-repo"
    nested.mkdir(parents=True)
    (nested / "README.md").write_text("STATUS: DRAFT\n[VERIFY]\n")
    findings = gate.scan_tree(tmp_path)
    assert findings == []


def test_gate_module_source_does_not_trip_its_own_patterns():
    # Regression test: gate.py's own docstrings/strings once described its
    # patterns using the literal marker text, which made the module trip
    # its own scan when run against this project's source tree.
    import reproflow.gate as gate_module
    findings = gate.scan_file(__import__("pathlib").Path(gate_module.__file__))
    assert findings == []
