import json

from reproflow.cli import main


def test_cli_init_creates_project(tmp_path, capsys):
    dest = str(tmp_path / "proj")
    rc = main(["init", dest, "--name", "CLI Project", "--author-name", "Jane Doe"])
    assert rc == 0
    assert (tmp_path / "proj" / "README.md").exists()
    out = capsys.readouterr().out
    assert "Scaffolded" in out


def test_cli_provenance_record(tmp_path, capsys):
    f = tmp_path / "source.csv"
    f.write_text("a,b\n1,2\n")
    ledger = tmp_path / "PROVENANCE.txt"
    rc = main(["provenance", "record", str(f), "--source-url", "https://x", "--ledger", str(ledger)])
    assert rc == 0
    assert ledger.exists()
    out = capsys.readouterr().out
    assert "source_url=https://x" in out


def test_cli_gate_check_pass(tmp_path, capsys):
    (tmp_path / "README.md").write_text("# Clean project\n")
    rc = main(["gate", "check", str(tmp_path)])
    assert rc == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_gate_check_fail_and_json(tmp_path, capsys):
    (tmp_path / "README.md").write_text("STATUS: DRAFT\n")
    json_out = tmp_path / "findings.json"
    rc = main(["gate", "check", str(tmp_path), "--json", str(json_out)])
    assert rc == 1
    assert "FAIL" in capsys.readouterr().out
    findings = json.loads(json_out.read_text())
    assert len(findings) == 1
    assert findings[0]["kind"] == "draft_stamp"


def test_cli_audit_run_writes_json(tmp_path, capsys):
    out_json = tmp_path / "result.json"
    rc = main(["audit", "run", str(tmp_path), "--name", "demo-repo", "--json", str(out_json)])
    assert rc == 0
    data = json.loads(out_json.read_text())
    assert data["repo_name"] == "demo-repo"
    assert "score" in data
    out = capsys.readouterr().out
    assert "demo-repo" in out


def test_cli_audit_report_combines_results(tmp_path, capsys):
    repo_a = tmp_path / "a"
    repo_a.mkdir()
    result_a = tmp_path / "a_result.json"
    main(["audit", "run", str(repo_a), "--name", "repo-a", "--json", str(result_a)])

    repo_b = tmp_path / "b"
    repo_b.mkdir()
    result_b = tmp_path / "b_result.json"
    main(["audit", "run", str(repo_b), "--name", "repo-b", "--json", str(result_b)])

    out_table = tmp_path / "table.md"
    rc = main(["audit", "report", str(result_a), str(result_b), "--out", str(out_table)])
    assert rc == 0
    table = out_table.read_text()
    assert "repo-a" in table
    assert "repo-b" in table
