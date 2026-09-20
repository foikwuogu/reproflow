from reproflow import scaffold


def test_init_project_creates_expected_layout(tmp_path):
    dest = tmp_path / "new-project"
    written = scaffold.init_project(
        dest,
        project_name="My New Project",
        author_name="Jane Doe",
        author_email="jane@example.org",
        author_orcid="0000-0001-2345-6789",
        author_affiliation="Example University",
        github_user="janedoe",
    )
    assert written, "expected files to be written"

    expected = [
        "pyproject.toml",
        ".gitignore",
        ".github/workflows/ci.yml",
        "code/01_fetch.py",
        "code/02_build.py",
        "code/03_qa.py",
        "code/04_figures.py",
        "README.md",
        "docs/CODEBOOK.md",
        "docs/LIMITATIONS.md",
        "docs/VERIFY_CHECKLIST.md",
        "docs/NEXT_STEPS.md",
        "CITATION.cff",
        "AUTHORS.json",
    ]
    for rel in expected:
        assert (dest / rel).exists(), f"missing {rel}"

    for empty_dir in ["data/raw", "data/processed", "tests", "paper/figures"]:
        assert (dest / empty_dir).is_dir()


def test_init_project_substitutes_context(tmp_path):
    dest = tmp_path / "proj"
    scaffold.init_project(
        dest,
        project_name="Acme Widget Study",
        author_name="Jane Doe",
        author_orcid="0000-0001-2345-6789",
    )
    readme = (dest / "README.md").read_text()
    assert "Acme Widget Study" in readme
    assert "Jane Doe" in readme
    assert "{{" not in readme  # no leftover template tokens

    citation = (dest / "CITATION.cff").read_text()
    assert "Jane Doe" in citation
    assert "0000-0001-2345-6789" in citation


def test_init_project_slugifies_name_in_pyproject(tmp_path):
    dest = tmp_path / "proj"
    scaffold.init_project(dest, project_name="My Cool Project!!")
    pyproject = (dest / "pyproject.toml").read_text()
    assert "my-cool-project" in pyproject


def test_init_project_does_not_overwrite_without_force(tmp_path):
    dest = tmp_path / "proj"
    scaffold.init_project(dest, project_name="First")
    (dest / "README.md").write_text("hand-edited content\n")

    written = scaffold.init_project(dest, project_name="Second")
    assert (dest / "README.md").read_text() == "hand-edited content\n"
    assert all("README.md" not in str(p) for p in written)


def test_init_project_overwrites_with_force(tmp_path):
    dest = tmp_path / "proj"
    scaffold.init_project(dest, project_name="First")
    (dest / "README.md").write_text("hand-edited content\n")

    scaffold.init_project(dest, project_name="Second", force=True)
    assert "Second" in (dest / "README.md").read_text()


def test_render_replaces_tokens():
    out = scaffold.render("Hello {{name}}, welcome to {{place}}.", {"name": "Ada", "place": "here"})
    assert out == "Hello Ada, welcome to here."
