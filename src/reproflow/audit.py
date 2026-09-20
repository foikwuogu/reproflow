"""Audit: score a repository against the reproflow reproducibility
checklist. Each criterion is a structural / file-presence / light-content
check — this does not execute the target repository's own pipeline.

The eight criteria are drawn directly from docs/CODEBOOK.md and mirror the
build-standards this framework itself follows, so the framework is
auditing itself against the same bar it names for others.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CRITERIA = [
    "packaging",
    "tests",
    "ci",
    "provenance",
    "stats_file",
    "docs_set",
    "citation_metadata",
    "license",
]

# Per-criterion importance weights used by AuditResult.score. These reflect
# this framework's own thesis (see paper/paper.md "Statement of need" and
# docs/CODEBOOK.md): the reproducibility *mechanics* that let an independent
# third party actually re-run the work (tests, CI, provenance) matter more
# than packaging polish or administrative metadata. Rationale, criterion by
# criterion:
#   provenance          2.0  the specific claim this project makes ("every
#                             input is traceable"); the criterion most
#                             directly tied to the project's stated purpose
#   tests               1.5  a repository nobody can verify by re-running
#                             its checks is not independently reproducible
#   ci                  1.5  automated, third-party re-execution (not just
#                             "it worked on my machine") is what makes the
#                             tests criterion trustworthy over time
#   packaging           1.0  installability is necessary for anyone else to
#                             run the code at all, but is a lower bar than
#                             actually testing or tracing it
#   stats_file          1.0  ties prose claims to a re-derivable artifact,
#                             this project's own "stats-file rule"
#   docs_set            1.0  documents the process but does not itself
#                             verify anything
#   citation_metadata   0.5  administrative: helps attribution/discovery,
#                             does not affect whether results reproduce
#   license             0.5  administrative: legal clarity, not a
#                             reproducibility mechanic
# These weights are the author's own editorial judgment, not a derived or
# externally validated metric — see docs/LIMITATIONS.md and docs/CODEBOOK.md.
CRITERION_WEIGHTS = {
    "packaging": 1.0,
    "tests": 1.5,
    "ci": 1.5,
    "provenance": 2.0,
    "stats_file": 1.0,
    "docs_set": 1.0,
    "citation_metadata": 0.5,
    "license": 0.5,
}

DOCS_SET_FILES = {
    "codebook": ["docs/CODEBOOK.md", "CODEBOOK.md"],
    "limitations": ["docs/LIMITATIONS.md", "LIMITATIONS.md"],
    "verify_checklist": ["docs/VERIFY_CHECKLIST.md", "VERIFY_CHECKLIST.md"],
    "next_steps": ["docs/NEXT_STEPS.md", "NEXT_STEPS.md"],
}


@dataclass
class CriterionResult:
    name: str
    status: str  # "pass" | "partial" | "fail"
    detail: str
    evidence: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "status": self.status, "detail": self.detail, "evidence": self.evidence}


@dataclass
class AuditResult:
    repo_name: str
    repo_path: str
    commit: Optional[str]
    criteria: list

    @property
    def unweighted_score(self) -> float:
        """Plain mean across the eight criteria, each counted equally.
        Kept alongside `score` for transparency: it's the number this
        project reported before criteria were weighted, and it's what
        docs/LIMITATIONS.md compares the weighted score against."""
        status_value = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
        total = sum(status_value[c.status] for c in self.criteria)
        return round(total / len(self.criteria), 3) if self.criteria else 0.0

    @property
    def score(self) -> float:
        """Weighted mean using CRITERION_WEIGHTS. This is the headline
        score reported in README.md, paper.md, and TECHNICAL_REPORT.md."""
        status_value = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
        if not self.criteria:
            return 0.0
        total_weight = sum(CRITERION_WEIGHTS[c.name] for c in self.criteria)
        weighted_total = sum(CRITERION_WEIGHTS[c.name] * status_value[c.status] for c in self.criteria)
        return round(weighted_total / total_weight, 3) if total_weight else 0.0

    def to_dict(self) -> dict:
        return {
            "repo_name": self.repo_name,
            "repo_path": self.repo_path,
            "commit": self.commit,
            "score": self.score,
            "unweighted_score": self.unweighted_score,
            "criteria": [c.to_dict() for c in self.criteria],
        }


def _exists_any(root: Path, candidates: list[str]) -> Optional[Path]:
    for rel in candidates:
        p = root / rel
        if p.exists():
            return p
    return None


def _find_files(root: Path, pattern: str, exclude_dirs=(".git", "node_modules", "__pycache__")) -> list[Path]:
    out = []
    for p in root.rglob(pattern):
        if any(part in exclude_dirs for part in p.parts):
            continue
        out.append(p)
    return out


def check_packaging(root: Path) -> CriterionResult:
    pyproject = root / "pyproject.toml"
    setup_py = root / "setup.py"
    requirements = root / "requirements.txt"
    if pyproject.exists() or setup_py.exists():
        which = "pyproject.toml" if pyproject.exists() else "setup.py"
        return CriterionResult("packaging", "pass", f"installable package: {which} present", [which])
    if requirements.exists():
        return CriterionResult(
            "packaging", "partial",
            "requirements.txt present but no pyproject.toml/setup.py: dependencies are pinned "
            "but the project is not installable as a package (no console entry point, no version).",
            ["requirements.txt"],
        )
    return CriterionResult("packaging", "fail", "no pyproject.toml, setup.py, or requirements.txt found", [])


def check_tests(root: Path) -> CriterionResult:
    test_files = [p for p in _find_files(root, "test_*.py")] + [p for p in _find_files(root, "*_test.py")]
    test_files = sorted(set(test_files))
    if len(test_files) >= 3:
        rel = [str(p.relative_to(root)) for p in test_files[:5]]
        return CriterionResult("tests", "pass", f"{len(test_files)} test file(s) found", rel)
    if test_files:
        rel = [str(p.relative_to(root)) for p in test_files]
        return CriterionResult("tests", "partial", f"only {len(test_files)} test file(s) found", rel)
    return CriterionResult("tests", "fail", "no test_*.py or *_test.py files found", [])


def check_ci(root: Path) -> CriterionResult:
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return CriterionResult("ci", "fail", "no .github/workflows directory", [])
    yml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not yml_files:
        return CriterionResult("ci", "fail", ".github/workflows exists but has no workflow files", [])

    runs_tests = False
    for f in yml_files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if re.search(r"\bpytest\b", text) or re.search(r"\bunittest\b", text):
            runs_tests = True
            break

    rel = [str(f.relative_to(root)) for f in yml_files]
    if runs_tests:
        return CriterionResult("ci", "pass", f"{len(yml_files)} workflow(s), at least one runs the test suite", rel)
    return CriterionResult(
        "ci", "partial",
        f"{len(yml_files)} workflow(s) present but none appear to invoke pytest/unittest "
        "(may automate publishing/metadata rather than testing)",
        rel,
    )


def check_provenance(root: Path) -> CriterionResult:
    from . import provenance as prov

    ledger = _exists_any(root, ["data/raw/PROVENANCE.txt", "PROVENANCE.txt"])
    if ledger is None:
        return CriterionResult("provenance", "fail", "no PROVENANCE.txt found under data/raw/ or repo root", [])
    ok, problems = prov.ledger_is_well_formed(ledger)
    rel = str(ledger.relative_to(root))
    if ok:
        n = len(prov.parse_ledger(ledger))
        return CriterionResult("provenance", "pass", f"{rel} present and well-formed ({n} record(s))", [rel])
    return CriterionResult(
        "provenance", "partial", f"{rel} present but not fully conformant: {'; '.join(problems)}", [rel]
    )


def check_stats_file(root: Path) -> CriterionResult:
    candidates = _find_files(root, "stats.json")
    if not candidates:
        return CriterionResult("stats_file", "fail", "no stats.json found", [])
    rel = [str(p.relative_to(root)) for p in candidates]
    # A stats file only earns "pass" if it actually parses as JSON with content.
    for p in candidates:
        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
            if data:
                return CriterionResult("stats_file", "pass", f"parseable, non-empty stats file at {rel[0]}", rel)
        except (json.JSONDecodeError, OSError):
            continue
    return CriterionResult("stats_file", "partial", "stats.json present but empty or unparseable", rel)


def check_docs_set(root: Path) -> CriterionResult:
    found = {}
    for key, candidates in DOCS_SET_FILES.items():
        p = _exists_any(root, candidates)
        if p is not None:
            found[key] = str(p.relative_to(root))
    n = len(found)
    total = len(DOCS_SET_FILES)
    if n == total:
        return CriterionResult("docs_set", "pass", f"all {total} standard docs present", list(found.values()))
    if n > 0:
        missing = sorted(set(DOCS_SET_FILES) - set(found))
        return CriterionResult("docs_set", "partial", f"{n}/{total} present; missing: {missing}", list(found.values()))
    return CriterionResult("docs_set", "fail", "none of CODEBOOK/LIMITATIONS/VERIFY_CHECKLIST/NEXT_STEPS found", [])


def check_citation_metadata(root: Path) -> CriterionResult:
    cff = _exists_any(root, ["CITATION.cff"])
    authors = _exists_any(root, ["AUTHORS.json"])
    if cff and authors:
        return CriterionResult("citation_metadata", "pass", "CITATION.cff and AUTHORS.json both present",
                                ["CITATION.cff", "AUTHORS.json"])
    if cff or authors:
        present = "CITATION.cff" if cff else "AUTHORS.json"
        return CriterionResult("citation_metadata", "partial", f"only {present} present", [present])
    return CriterionResult("citation_metadata", "fail", "neither CITATION.cff nor AUTHORS.json present", [])


def check_license(root: Path) -> CriterionResult:
    license_files = [p for p in root.glob("LICENSE*") if p.is_file()]
    if not license_files:
        return CriterionResult("license", "fail", "no LICENSE file at repository root", [])
    rel = [p.name for p in license_files]
    if len(license_files) > 1:
        return CriterionResult("license", "pass", f"{len(license_files)} license files (dual code/data licensing)", rel)
    return CriterionResult("license", "pass", "LICENSE file present", rel)


CHECKS = {
    "packaging": check_packaging,
    "tests": check_tests,
    "ci": check_ci,
    "provenance": check_provenance,
    "stats_file": check_stats_file,
    "docs_set": check_docs_set,
    "citation_metadata": check_citation_metadata,
    "license": check_license,
}


def _read_commit(root: Path) -> Optional[str]:
    import subprocess

    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return None


def audit_repo(root: Path | str, repo_name: Optional[str] = None) -> AuditResult:
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"repo path does not exist: {root}")
    results = [check(root) for check in CHECKS.values()]
    return AuditResult(
        repo_name=repo_name or root.name,
        repo_path=str(root),
        commit=_read_commit(root),
        criteria=results,
    )


def audit_many(repo_paths: dict[str, Path | str]) -> list[AuditResult]:
    """repo_paths: {display_name: path}. Order preserved."""
    return [audit_repo(path, repo_name=name) for name, path in repo_paths.items()]


def to_markdown_table(results: list[AuditResult]) -> str:
    """Weighted-score table (see CRITERION_WEIGHTS). A row of the raw
    per-criterion weights is included so the table is self-documenting
    without a reader having to cross-reference audit.py."""
    header = "| Repository | " + " | ".join(CRITERIA) + " | Score |"
    sep = "|---" * (len(CRITERIA) + 2) + "|"
    weight_row = "| *weight* | " + " | ".join(f"*{CRITERION_WEIGHTS[c]:g}*" for c in CRITERIA) + " | |"
    symbol = {"pass": "PASS", "partial": "PARTIAL", "fail": "FAIL"}
    lines = [header, sep, weight_row]
    for r in results:
        crit_by_name = {c.name: c for c in r.criteria}
        row = [r.repo_name]
        for crit in CRITERIA:
            row.append(symbol[crit_by_name[crit].status])
        row.append(f"{r.score:.2f}")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)
