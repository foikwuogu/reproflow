#!/usr/bin/env python3
"""02_run_audit.py — run reproflow's own auditor against each cloned
evidence repository, and against reproflow itself, writing:
    data/processed/audit_results.json  (full structured results)
    data/processed/stats.json          (every number any document quotes)
    data/processed/qa_report.txt       (human-readable audit report)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLONE_DIR = ROOT / "data" / "raw" / "evidence_repos"
PROCESSED_DIR = ROOT / "data" / "processed"

sys.path.insert(0, str(ROOT / "src"))
from reproflow import audit  # noqa: E402

REPO_DISPLAY_ORDER = [
    "icsprio",
    "ong-ot-dataset",
    "pipeline-control-validation",
    "pqc-ot-crosswalk",
    "crosswalk-lookup",
]


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    repo_paths = {name: CLONE_DIR / name for name in REPO_DISPLAY_ORDER}
    for name, path in repo_paths.items():
        if not path.exists():
            raise SystemExit(f"missing clone for {name} at {path}; run 01_fetch_repos.py first")

    results = audit.audit_many(repo_paths)

    # Also audit reproflow itself, for the "does the framework meet its own
    # bar" comparison point in the report.
    reproflow_result = audit.audit_repo(ROOT, repo_name="reproflow (this project)")

    all_results = results + [reproflow_result]

    # --- audit_results.json: full structured detail ---
    (PROCESSED_DIR / "audit_results.json").write_text(
        json.dumps([r.to_dict() for r in all_results], indent=2), encoding="utf-8"
    )

    # --- qa_report.txt: human-readable ---
    lines = ["QA REPORT: reproducibility audit of evidence repositories", "=" * 60, ""]
    lines.append(f"Repositories audited: {len(results)} evidence repos + reproflow itself")
    lines.append("Audit method: structural/file-presence checks against the 8-criterion")
    lines.append("checklist in docs/CODEBOOK.md; does not execute each repo's own pipeline.")
    lines.append("")
    lines.append(audit.to_markdown_table(all_results))
    lines.append("")
    lines.append("Per-repository detail:")
    for r in all_results:
        lines.append(f"\n-- {r.repo_name} (commit {r.commit[:12] if r.commit else 'unknown'}) --")
        for c in r.criteria:
            lines.append(f"  [{c.status.upper():7s}] {c.name}: {c.detail}")
    qa_text = "\n".join(lines) + "\n"
    (PROCESSED_DIR / "qa_report.txt").write_text(qa_text, encoding="utf-8")

    # --- stats.json: every number any document will quote ---
    scores = {r.repo_name: r.score for r in all_results}
    evidence_scores = {r.repo_name: r.score for r in results}
    criterion_pass_counts = {}
    for crit_name in audit.CRITERIA:
        passes = sum(1 for r in results for c in r.criteria if c.name == crit_name and c.status == "pass")
        criterion_pass_counts[crit_name] = passes

    stats = {
        "n_evidence_repos": len(results),
        "evidence_repo_names": REPO_DISPLAY_ORDER,
        "scores_by_repo": scores,
        "evidence_scores_by_repo": evidence_scores,
        "mean_evidence_score": round(sum(evidence_scores.values()) / len(evidence_scores), 3),
        "min_evidence_score": min(evidence_scores.values()),
        "max_evidence_score": max(evidence_scores.values()),
        "reproflow_self_score": reproflow_result.score,
        "criterion_pass_counts_among_evidence_repos": criterion_pass_counts,
        "n_criteria": len(audit.CRITERIA),
        "criteria_list": audit.CRITERIA,
        "fully_compliant_evidence_repos": [name for name, s in evidence_scores.items() if s == 1.0],
        "least_compliant_evidence_repo": min(evidence_scores, key=evidence_scores.get),
        "most_compliant_evidence_repo": max(evidence_scores, key=evidence_scores.get),
    }
    (PROCESSED_DIR / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(qa_text)
    print(f"\nWrote {PROCESSED_DIR / 'audit_results.json'}")
    print(f"Wrote {PROCESSED_DIR / 'stats.json'}")
    print(f"Wrote {PROCESSED_DIR / 'qa_report.txt'}")


if __name__ == "__main__":
    main()
