#!/usr/bin/env python3
"""03_figures.py — build the compliance heatmap from data/processed/stats.json
and data/processed/audit_results.json. Carries a DRAFT tag until run with
--final; the tag is drawn in-figure so it survives even if a document
embeds the image without reading the filename.
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "paper" / "figures"

STATUS_VALUE = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
CRITERIA_LABELS = {
    "packaging": "Packaging",
    "tests": "Tests",
    "ci": "CI",
    "provenance": "Provenance",
    "stats_file": "Stats file",
    "docs_set": "Docs set",
    "citation_metadata": "Citation",
    "license": "License",
}


def build_heatmap(results: list[dict], draft: bool) -> plt.Figure:
    criteria = list(CRITERIA_LABELS.keys())
    repo_names = [r["repo_name"] for r in results]
    matrix = np.array(
        [[STATUS_VALUE[next(c for c in r["criteria"] if c["name"] == crit)["status"]] for crit in criteria]
         for r in results]
    )

    n_rows = len(repo_names)
    fig = plt.figure(figsize=(12.5, 0.65 * n_rows + 2.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[len(criteria), 0.9, 0.35], wspace=0.08)
    ax = fig.add_subplot(gs[0, 0])
    ax_score = fig.add_subplot(gs[0, 1], sharey=ax)
    ax_cbar = fig.add_subplot(gs[0, 2])

    # Sequential, single-hue ramp for a magnitude encoding (viridis family),
    # per the framework's own figure standard.
    im = ax.imshow(matrix, cmap="viridis", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(criteria)))
    ax.set_xticklabels([CRITERIA_LABELS[c] for c in criteria], rotation=35, ha="right")
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(repo_names)

    # Direct annotation of the one value that matters in each cell.
    symbol = {1.0: "PASS", 0.5: "PART", 0.0: "FAIL"}
    for i in range(n_rows):
        for j in range(len(criteria)):
            val = matrix[i, j]
            color = "black" if val >= 0.5 else "white"
            ax.text(j, i, symbol[val], ha="center", va="center", color=color, fontsize=8)

    # Score column: its own small axis, not overlapping the colorbar.
    scores = [r["score"] for r in results]
    ax_score.set_xlim(0, 1)
    ax_score.set_ylim(n_rows - 0.5, -0.5)
    ax_score.axis("off")
    ax_score.set_title("Score", fontsize=10)
    for i, s in enumerate(scores):
        ax_score.text(0.05, i, f"{s:.2f}", ha="left", va="center", fontsize=10, fontweight="bold")

    cbar = fig.colorbar(im, cax=ax_cbar)
    cbar.set_ticks([0, 0.5, 1.0])
    cbar.set_ticklabels(["Fail", "Partial", "Pass"])

    title = "reproflow reproducibility-checklist audit"
    if draft:
        title += "  [DRAFT — unverified]"
    fig.suptitle(title, fontsize=12, y=0.98)
    fig.text(
        0.5, 0.01,
        "Evidence repositories cloned 2026-09-20 (commit hashes in data/raw/PROVENANCE.txt). "
        "Structural/file-presence audit; does not execute each repo's own pipeline.",
        fontsize=7, color="gray", va="bottom", ha="center",
    )
    fig.subplots_adjust(left=0.22, right=0.86, top=0.88, bottom=0.28)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true", help="remove DRAFT tag from figures")
    args = parser.parse_args()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    results = json.loads((PROCESSED_DIR / "audit_results.json").read_text(encoding="utf-8"))

    fig = build_heatmap(results, draft=not args.final)
    out_path = FIGURES_DIR / "compliance_heatmap.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
