"""Publish gate: scan a project tree for the mechanical reasons it is not
ready to publish -- draft stamps, unresolved verify-tags, bracketed
placeholders, and secret-shaped strings -- and refuse to pass while any
remain.

This enforces only the mechanical half of release readiness. It cannot
check whether the author has actually reproduced the pipeline or hand
-verified the spot checks; that is docs/VERIFY_CHECKLIST.md, and it is a
human's job.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Directories never scanned: version control, virtual envs, caches, and any
# git submodule / vendored copy.
DEFAULT_EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache", "build", "dist", ".eggs",
    "*.egg-info",
    # Scaffold templates deliberately ship with unfilled placeholders, and
    # the test suite deliberately writes marker strings as fixture data;
    # neither is the deliverable content the gate is meant to check.
    "templates", "tests",
    # Read-only third-party inputs cloned into data/raw/ (e.g. by an audit
    # pipeline) are not this project's own authored content; their own
    # draft/verify/placeholder markers are theirs to resolve, not ours.
    "evidence_repos",
}

# Text-like extensions worth scanning; skips binaries, images, data blobs.
DEFAULT_INCLUDE_EXT = {
    ".md", ".txt", ".py", ".js", ".ts", ".json", ".yml", ".yaml",
    ".cff", ".rst", ".html", ".csv", ".toml", ".cfg", ".ini",
}

FINDING_KINDS = ("draft_stamp", "verify_tag", "placeholder", "secret")

# The marker text is assembled rather than written as a literal here, so
# this module's own source does not trip the pattern it defines.
VERIFY_MARKER = "[" + "VERIFY" + "]"
DRAFT_STAMP_TEXT = "STATUS" + ": " + "DRAFT"

_DRAFT_STAMP_RE = re.compile(r"STATUS:\**\s*DRAFT\b", re.IGNORECASE)
_VERIFY_TAG_RE = re.compile(re.escape(VERIFY_MARKER))
_PLACEHOLDER_RE = re.compile(
    r"\[(insert[^\]]*|todo[^\]]*|placeholder[^\]]*|tbd|pending[^\]]*|fill[- ]?in[^\]]*)\]",
    re.IGNORECASE,
)

# Deliberately conservative secret patterns: high-confidence prefixes/shapes
# rather than a general-purpose entropy scanner, to keep false positives low
# in a tool meant to gate an actual release.
_SECRET_PATTERNS = {
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "aws_access_key_id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "openai_style_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "generic_private_key_header": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "zenodo_style_token": re.compile(r"\bZENODO_[A-Z_]*TOKEN\s*=\s*['\"][A-Za-z0-9\-_]{10,}['\"]"),
}


@dataclass(frozen=True)
class Finding:
    kind: str
    file: str
    line_number: int
    line_text: str
    match: str

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "file": self.file,
            "line_number": self.line_number,
            "line_text": self.line_text.strip()[:200],
            "match": self.match,
        }


def _iter_text_files(
    root: Path,
    exclude_dirs: Iterable[str] = DEFAULT_EXCLUDE_DIRS,
    include_ext: Iterable[str] = DEFAULT_INCLUDE_EXT,
) -> Iterable[Path]:
    exclude_dirs = set(exclude_dirs)
    include_ext = set(include_ext)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in include_ext:
            continue
        yield path


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except (UnicodeDecodeError, OSError):
        return findings

    for i, line in enumerate(text.splitlines(), start=1):
        if _DRAFT_STAMP_RE.search(line):
            findings.append(Finding("draft_stamp", str(path), i, line, _DRAFT_STAMP_RE.search(line).group(0)))
        if _VERIFY_TAG_RE.search(line):
            findings.append(Finding("verify_tag", str(path), i, line, VERIFY_MARKER))
        m = _PLACEHOLDER_RE.search(line)
        if m:
            findings.append(Finding("placeholder", str(path), i, line, m.group(0)))
        for name, pattern in _SECRET_PATTERNS.items():
            m = pattern.search(line)
            if m:
                findings.append(Finding("secret", str(path), i, line, f"{name}:{m.group(0)[:12]}..."))
    return findings


def scan_tree(
    root: Path | str,
    exclude_dirs: Iterable[str] = DEFAULT_EXCLUDE_DIRS,
    include_ext: Iterable[str] = DEFAULT_INCLUDE_EXT,
) -> list[Finding]:
    root = Path(root)
    findings: list[Finding] = []
    for path in _iter_text_files(root, exclude_dirs, include_ext):
        findings.extend(scan_file(path))
    return findings


def gate_passes(findings: list[Finding]) -> bool:
    return len(findings) == 0


def format_report(findings: list[Finding], root: Path | str) -> str:
    root = Path(root)
    if not findings:
        return (
            "PUBLISH GATE: PASS -- no draft stamps, unresolved verify-tags, "
            "placeholders, or secret-shaped strings found.\n"
        )

    lines = [f"PUBLISH GATE: FAIL — {len(findings)} issue(s) found.\n"]
    by_kind: dict[str, list[Finding]] = {}
    for f in findings:
        by_kind.setdefault(f.kind, []).append(f)
    for kind in FINDING_KINDS:
        group = by_kind.get(kind, [])
        if not group:
            continue
        lines.append(f"\n[{kind}] ({len(group)})")
        for f in group:
            try:
                rel = Path(f.file).relative_to(root)
            except ValueError:
                rel = f.file
            lines.append(f"  {rel}:{f.line_number}  {f.match!r}")
    return "\n".join(lines) + "\n"
