#!/usr/bin/env python3
"""01_fetch_repos.py — clone (or reuse an already-cloned copy of) each
evidence repository and log provenance for it.

Usage:
    python code/01_fetch_repos.py

Evidence repositories are read-only inputs to this project's audit: this
script never writes to them, only clones them and records what was cloned.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLONE_DIR = ROOT / "data" / "raw" / "evidence_repos"
LEDGER = ROOT / "data" / "raw" / "PROVENANCE.txt"

sys.path.insert(0, str(ROOT / "src"))
from reproflow import provenance  # noqa: E402

EVIDENCE_REPOS = {
    "icsprio": "https://github.com/foikwuogu/icsprio.git",
    "ong-ot-dataset": "https://github.com/foikwuogu/ong-ot-dataset.git",
    "pipeline-control-validation": "https://github.com/foikwuogu/pipeline-control-validation.git",
    "pqc-ot-crosswalk": "https://github.com/foikwuogu/pqc-ot-crosswalk.git",
    "crosswalk-lookup": "https://github.com/foikwuogu/crosswalk-lookup.git",
}


def clone(name: str, url: str) -> Path:
    dest = CLONE_DIR / name
    if dest.exists():
        print(f"  {name}: already present at {dest}, skipping clone")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  {name}: cloning {url}")
    subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)
    return dest


def main() -> None:
    print("Fetching evidence repositories...")
    for name, url in EVIDENCE_REPOS.items():
        dest = clone(name, url)
        rec = provenance.record_repo_clone(dest, source_url=url, ledger=LEDGER)
        print(f"    logged: commit={rec.sha256[:12]} bytes={rec.bytes}")
    print(f"\nProvenance written to {LEDGER}")


if __name__ == "__main__":
    main()
