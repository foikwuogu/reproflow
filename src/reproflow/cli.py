"""reproflow command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import audit as audit_mod
from . import gate as gate_mod
from . import provenance as provenance_mod
from . import scaffold as scaffold_mod


def _cmd_init(args: argparse.Namespace) -> int:
    written = scaffold_mod.init_project(
        dest=args.dest,
        project_name=args.name,
        description=args.description
        or "[One paragraph: what this is, the question it answers, who it is for.]",
        author_name=args.author_name or "[Given Surname]",
        author_email=args.author_email or "[email]",
        author_orcid=args.author_orcid or "0000-0000-0000-0000",
        author_affiliation=args.author_affiliation or "[Affiliation]",
        github_user=args.github_user or "[github-user]",
        force=args.force,
    )
    if written:
        print(f"Scaffolded {len(written)} file(s) at {args.dest}:")
        for p in written:
            print(f"  {p}")
    else:
        print("Nothing written (all target files already exist; pass --force to overwrite).")
    return 0


def _cmd_provenance_record(args: argparse.Namespace) -> int:
    rec = provenance_mod.record(
        path=args.path,
        source_url=args.source_url,
        ledger=args.ledger,
        note=args.note or "",
    )
    print(rec.to_line())
    return 0


def _cmd_gate_check(args: argparse.Namespace) -> int:
    findings = gate_mod.scan_tree(args.path)
    report = gate_mod.format_report(findings, args.path)
    print(report)
    if args.json:
        Path(args.json).write_text(
            json.dumps([f.to_dict() for f in findings], indent=2), encoding="utf-8"
        )
    return 0 if gate_mod.gate_passes(findings) else 1


def _cmd_audit_run(args: argparse.Namespace) -> int:
    result = audit_mod.audit_repo(args.path, repo_name=args.name)
    if args.json:
        Path(args.json).write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    print(audit_mod.to_markdown_table([result]))
    print(f"\nScore: {result.score:.2f}")
    return 0


def _cmd_audit_report(args: argparse.Namespace) -> int:
    results = []
    for item in args.json_files:
        data = json.loads(Path(item).read_text(encoding="utf-8"))
        criteria = [
            audit_mod.CriterionResult(c["name"], c["status"], c["detail"], c.get("evidence", []))
            for c in data["criteria"]
        ]
        results.append(
            audit_mod.AuditResult(
                repo_name=data["repo_name"],
                repo_path=data["repo_path"],
                commit=data.get("commit"),
                criteria=criteria,
            )
        )
    table = audit_mod.to_markdown_table(results)
    print(table)
    if args.out:
        Path(args.out).write_text(table + "\n", encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reproflow", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="scaffold a new project from the standard layout")
    p_init.add_argument("dest", help="destination directory")
    p_init.add_argument("--name", required=True, help="project name")
    p_init.add_argument("--description", default=None)
    p_init.add_argument("--author-name", default=None)
    p_init.add_argument("--author-email", default=None)
    p_init.add_argument("--author-orcid", default=None)
    p_init.add_argument("--author-affiliation", default=None)
    p_init.add_argument("--github-user", default=None)
    p_init.add_argument("--force", action="store_true", help="overwrite existing files")
    p_init.set_defaults(func=_cmd_init)

    p_prov = sub.add_parser("provenance", help="provenance logging")
    prov_sub = p_prov.add_subparsers(dest="prov_command", required=True)
    p_prov_record = prov_sub.add_parser("record", help="log a fetched file")
    p_prov_record.add_argument("path", help="path to the fetched file")
    p_prov_record.add_argument("--source-url", required=True)
    p_prov_record.add_argument("--ledger", default="data/raw/PROVENANCE.txt")
    p_prov_record.add_argument("--note", default=None)
    p_prov_record.set_defaults(func=_cmd_provenance_record)

    p_gate = sub.add_parser("gate", help="publish gate")
    gate_sub = p_gate.add_subparsers(dest="gate_command", required=True)
    p_gate_check = gate_sub.add_parser("check", help="scan a tree for draft stamps/placeholders/secrets")
    p_gate_check.add_argument("path", nargs="?", default=".")
    p_gate_check.add_argument("--json", default=None, help="write findings as JSON to this path")
    p_gate_check.set_defaults(func=_cmd_gate_check)

    p_audit = sub.add_parser("audit", help="score a repository against the reproducibility checklist")
    audit_sub = p_audit.add_subparsers(dest="audit_command", required=True)
    p_audit_run = audit_sub.add_parser("run", help="audit one repository")
    p_audit_run.add_argument("path")
    p_audit_run.add_argument("--name", default=None)
    p_audit_run.add_argument("--json", default=None, help="write the full result as JSON to this path")
    p_audit_run.set_defaults(func=_cmd_audit_run)

    p_audit_report = audit_sub.add_parser("report", help="combine several audit JSON results into one table")
    p_audit_report.add_argument("json_files", nargs="+")
    p_audit_report.add_argument("--out", default=None, help="write the Markdown table to this path")
    p_audit_report.set_defaults(func=_cmd_audit_report)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
