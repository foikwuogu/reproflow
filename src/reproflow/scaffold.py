"""Scaffold: generate a new project from the reproflow standard layout
(docs/BUILD_SPEC template convention: numbered scripts, data/raw + processed,
docs set, CI workflow, provenance-ready code, tests directory).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

TEMPLATES_DIR = Path(__file__).parent / "templates"

# (template filename, destination relative path)
LAYOUT = [
    ("pyproject.toml.tmpl", "pyproject.toml"),
    ("gitignore.tmpl", ".gitignore"),
    ("ci.yml.tmpl", ".github/workflows/ci.yml"),
    ("fetch.py.tmpl", "code/01_fetch.py"),
    ("build.py.tmpl", "code/02_build.py"),
    ("qa.py.tmpl", "code/03_qa.py"),
    ("figures.py.tmpl", "code/04_figures.py"),
    ("README.md.tmpl", "README.md"),
    ("CODEBOOK.md.tmpl", "docs/CODEBOOK.md"),
    ("LIMITATIONS.md.tmpl", "docs/LIMITATIONS.md"),
    ("VERIFY_CHECKLIST.md.tmpl", "docs/VERIFY_CHECKLIST.md"),
    ("NEXT_STEPS.md.tmpl", "docs/NEXT_STEPS.md"),
    ("CITATION.cff.tmpl", "CITATION.cff"),
    ("AUTHORS.json.tmpl", "AUTHORS.json"),
]

EMPTY_DIRS = [
    "data/raw",
    "data/processed",
    "tests",
    "paper/figures",
]


def _slugify(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")


def render(template_text: str, context: dict) -> str:
    out = template_text
    for key, value in context.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out


def init_project(
    dest: Path | str,
    project_name: str,
    description: str = "[One paragraph: what this is, the question it answers, who it is for.]",
    author_name: str = "[Given Surname]",
    author_email: str = "[email]",
    author_orcid: str = "0000-0000-0000-0000",
    author_affiliation: str = "[Affiliation]",
    github_user: str = "[github-user]",
    force: bool = False,
) -> list[Path]:
    """Create the standard project skeleton at `dest`. Returns the list of
    files written. Refuses to overwrite existing files unless force=True.
    """
    dest = Path(dest)
    project_slug = _slugify(project_name)
    context = {
        "project_name": project_name,
        "project_slug": project_slug,
        "description": description,
        "author_name": author_name,
        "author_email": author_email,
        "author_orcid": author_orcid,
        "author_affiliation": author_affiliation,
        "github_user": github_user,
        "today": date.today().isoformat(),
    }

    written: list[Path] = []
    for empty_dir in EMPTY_DIRS:
        (dest / empty_dir).mkdir(parents=True, exist_ok=True)

    for template_name, rel_dest in LAYOUT:
        src = TEMPLATES_DIR / template_name
        out_path = dest / rel_dest
        if out_path.exists() and not force:
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = render(src.read_text(encoding="utf-8"), context)
        out_path.write_text(rendered, encoding="utf-8")
        written.append(out_path)

    return written
