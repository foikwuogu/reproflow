"""Provenance logging: record what was fetched, when, from where, and its
exact content hash, so a later run can verify it fetched the same bytes.

Design goal: one function call at each fetch site, one line appended to a
plain-text ledger that both humans and scripts can read. Nothing here
requires a network connection or any third-party dependency.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_LEDGER_NAME = "PROVENANCE.txt"


@dataclass(frozen=True)
class ProvenanceRecord:
    """One logged fetch."""

    filename: str
    bytes: int
    sha256: str
    source_url: str
    access_date: str  # ISO 8601, UTC
    note: str = ""

    def to_line(self) -> str:
        parts = [
            f"filename={self.filename}",
            f"bytes={self.bytes}",
            f"sha256={self.sha256}",
            f"source_url={self.source_url}",
            f"access_date={self.access_date}",
        ]
        if self.note:
            parts.append(f"note={self.note}")
        return " | ".join(parts)

    def to_dict(self) -> dict:
        return asdict(self)


def sha256_of_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Stream-hash a file so this works on large downloads without loading
    them fully into memory."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record(
    path: Path | str,
    source_url: str,
    ledger: Path | str,
    access_date: Optional[str] = None,
    note: str = "",
) -> ProvenanceRecord:
    """Hash an already-downloaded file and append one line to the ledger.

    Returns the ProvenanceRecord so callers can also fold it into a QA
    report or a stats file without re-reading the ledger.
    """
    path = Path(path)
    ledger = Path(ledger)
    if not path.exists():
        raise FileNotFoundError(f"cannot record provenance for missing file: {path}")

    rec = ProvenanceRecord(
        filename=path.name,
        bytes=path.stat().st_size,
        sha256=sha256_of_file(path),
        source_url=source_url,
        access_date=access_date or _utc_now_iso(),
        note=note,
    )
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(rec.to_line() + "\n")
    return rec


def record_repo_clone(
    repo_dir: Path | str,
    source_url: str,
    ledger: Path | str,
    access_date: Optional[str] = None,
    note: str = "",
) -> ProvenanceRecord:
    """Log provenance for a cloned git repository, where the identity of
    "what was fetched" is the commit hash rather than a single file's
    content hash. Falls back gracefully if `.git` metadata is missing.
    """
    import subprocess

    repo_dir = Path(repo_dir)
    ledger = Path(ledger)
    commit = "unknown"
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        commit = out.stdout.strip()
    except Exception:
        pass

    size = sum(f.stat().st_size for f in repo_dir.rglob("*") if f.is_file() and ".git" not in f.parts)

    rec = ProvenanceRecord(
        filename=repo_dir.name,
        bytes=size,
        sha256=commit,  # commit hash stands in for a content hash for a repo
        source_url=source_url,
        access_date=access_date or _utc_now_iso(),
        note=note or "sha256 field holds the git commit hash for cloned repositories",
    )
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(rec.to_line() + "\n")
    return rec


def parse_ledger(ledger: Path | str) -> list[dict]:
    """Parse an existing PROVENANCE.txt back into a list of dicts. Used by
    the auditor to check a repository's provenance log is well-formed, and
    by tests to round-trip what `record()` wrote.
    """
    ledger = Path(ledger)
    if not ledger.exists():
        return []
    records = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        fields = {}
        for part in line.split(" | "):
            if "=" not in part:
                continue
            key, _, value = part.partition("=")
            fields[key.strip()] = value.strip()
        records.append(fields)
    return records


REQUIRED_FIELDS = {"filename", "bytes", "sha256", "source_url", "access_date"}


def ledger_is_well_formed(ledger: Path | str, max_reported_problems: int = 5) -> tuple[bool, list[str]]:
    """Return (ok, problems). A well-formed ledger has at least one record
    and every record carries all REQUIRED_FIELDS in this module's
    ``key=value | key=value`` convention.

    ``problems`` is capped at ``max_reported_problems`` entries (plus a
    summary count) so a ledger written in an entirely different, unrelated
    format -- every one of its lines "missing" every required field --
    cannot blow this up into a report sized to the ledger rather than to
    the number of distinct problems.
    """
    records = parse_ledger(ledger)
    problems: list[str] = []
    if not records:
        problems.append("ledger is empty or missing")
        return False, problems

    bad_records = 0
    for i, rec in enumerate(records):
        missing = REQUIRED_FIELDS - set(rec.keys())
        if missing:
            bad_records += 1
            if len(problems) < max_reported_problems:
                problems.append(f"record {i}: missing fields {sorted(missing)}")

    if bad_records == len(records) and bad_records > max_reported_problems:
        # Every record failed the same way at ledger scale: this usually
        # means the file uses a different (possibly still valid) provenance
        # convention rather than being individually corrupt. Say that once.
        problems = [
            f"none of {len(records)} record(s) match this module's key=value schema "
            "(filename=... | bytes=... | sha256=... | source_url=... | access_date=...); "
            "the ledger may use a different provenance convention"
        ]
    elif bad_records > max_reported_problems:
        problems.append(f"... and {bad_records - max_reported_problems} more record(s) with missing fields")

    return (bad_records == 0), problems


def write_json_summary(ledger: Path | str, out_path: Path | str) -> None:
    """Convenience: dump the parsed ledger as JSON, e.g. for a stats file."""
    records = parse_ledger(ledger)
    Path(out_path).write_text(json.dumps(records, indent=2), encoding="utf-8")
