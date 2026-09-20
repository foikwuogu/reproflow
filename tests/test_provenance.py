import hashlib
import json

from reproflow import provenance


def test_sha256_of_file_matches_hashlib(tmp_path):
    f = tmp_path / "data.csv"
    f.write_bytes(b"a,b,c\n1,2,3\n")
    expected = hashlib.sha256(f.read_bytes()).hexdigest()
    assert provenance.sha256_of_file(f) == expected


def test_record_appends_well_formed_line(tmp_path):
    f = tmp_path / "source.csv"
    f.write_bytes(b"hello world")
    ledger = tmp_path / "PROVENANCE.txt"

    rec = provenance.record(f, source_url="https://example.org/source.csv", ledger=ledger)

    assert rec.filename == "source.csv"
    assert rec.bytes == len(b"hello world")
    assert rec.sha256 == hashlib.sha256(b"hello world").hexdigest()
    assert ledger.exists()

    lines = ledger.read_text().splitlines()
    assert len(lines) == 1
    assert "source_url=https://example.org/source.csv" in lines[0]


def test_record_missing_file_raises(tmp_path):
    ledger = tmp_path / "PROVENANCE.txt"
    try:
        provenance.record(tmp_path / "nope.csv", source_url="https://x", ledger=ledger)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_multiple_records_accumulate(tmp_path):
    ledger = tmp_path / "PROVENANCE.txt"
    for i in range(3):
        f = tmp_path / f"file{i}.csv"
        f.write_bytes(f"row{i}".encode())
        provenance.record(f, source_url=f"https://example.org/{i}", ledger=ledger)

    records = provenance.parse_ledger(ledger)
    assert len(records) == 3
    assert {r["filename"] for r in records} == {"file0.csv", "file1.csv", "file2.csv"}


def test_ledger_is_well_formed_true_for_clean_ledger(tmp_path):
    f = tmp_path / "a.csv"
    f.write_bytes(b"x")
    ledger = tmp_path / "PROVENANCE.txt"
    provenance.record(f, source_url="https://x", ledger=ledger)

    ok, problems = provenance.ledger_is_well_formed(ledger)
    assert ok
    assert problems == []


def test_ledger_is_well_formed_false_for_missing_ledger(tmp_path):
    ok, problems = provenance.ledger_is_well_formed(tmp_path / "does_not_exist.txt")
    assert not ok
    assert problems


def test_ledger_is_well_formed_false_for_incomplete_record(tmp_path):
    ledger = tmp_path / "PROVENANCE.txt"
    ledger.write_text("filename=only.csv | bytes=10\n")
    ok, problems = provenance.ledger_is_well_formed(ledger)
    assert not ok
    assert "missing fields" in problems[0]


def test_write_json_summary_round_trips(tmp_path):
    f = tmp_path / "a.csv"
    f.write_bytes(b"x")
    ledger = tmp_path / "PROVENANCE.txt"
    provenance.record(f, source_url="https://x", ledger=ledger)

    out = tmp_path / "summary.json"
    provenance.write_json_summary(ledger, out)
    data = json.loads(out.read_text())
    assert len(data) == 1
    assert data[0]["filename"] == "a.csv"


def test_ledger_is_well_formed_bounds_report_for_wholly_mismatched_schema(tmp_path):
    # Regression test: a ledger written in a different (still internally
    # consistent) format, where every line "misses" all five required
    # fields, once produced a problems report sized to the ledger (one
    # entry per line) rather than to the number of distinct problems.
    ledger = tmp_path / "PROVENANCE.txt"
    lines = [
        f"2026-09-{i:02d} | file{i}.json | {i * 100} bytes | sha256:{'a' * 64} | https://example.org/{i}"
        for i in range(1, 101)
    ]
    ledger.write_text("\n".join(lines) + "\n")

    ok, problems = provenance.ledger_is_well_formed(ledger)
    assert not ok
    assert len(problems) == 1
    assert "100 record(s)" in problems[0]
    assert "different provenance convention" in problems[0]


def test_record_repo_clone_uses_commit_hash_when_no_git(tmp_path):
    repo = tmp_path / "not_a_git_repo"
    repo.mkdir()
    (repo / "file.txt").write_text("content")
    ledger = tmp_path / "PROVENANCE.txt"

    rec = provenance.record_repo_clone(repo, source_url="https://github.com/x/y", ledger=ledger)

    assert rec.sha256 == "unknown"
    assert rec.filename == "not_a_git_repo"
    assert "commit hash" in rec.note
