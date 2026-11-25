import csv
import hashlib
import re
from pathlib import Path

import build_modules
import pytest
import refs
import render_status
import yaml

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_TOP = [
    "README.md", "CONTRIBUTING.md", "LICENSE", "CITATION.cff", "CHANGELOG.md",
    "SECURITY.md", "pyproject.toml", "Makefile",
]
REQUIRED_DOCS = [
    "getting_started.md", "learning_roadmap.md", "methodology_standards.md",
    "mathematical_reference.md", "banking_glossary.md", "regulatory_glossary.md",
    "dataset_guide.md", "limitations_and_disclaimers.md", "architecture_assessment.md",
    "project_status.md",
]
REQUIRED_RESEARCH = [
    "README.md", "paper_catalog.csv", "regulatory_sources.md", "standards_mapping.md",
    "research_gaps.md",
]
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".ipynb_checkpoints"}


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not SKIP_DIRS.intersection(path.parts):
            yield path


@pytest.mark.parametrize("name", REQUIRED_TOP)
def test_top_level_file_exists(name):
    assert (ROOT / name).exists()


@pytest.mark.parametrize("name", REQUIRED_DOCS)
def test_doc_exists(name):
    assert (ROOT / "docs" / name).stat().st_size > 200


@pytest.mark.parametrize("name", REQUIRED_RESEARCH)
def test_research_file_exists(name):
    assert (ROOT / "research" / name).stat().st_size > 100


def test_no_empty_directories():
    empty = []
    for path in ROOT.rglob("*"):
        if path.is_dir() and not SKIP_DIRS.intersection(path.parts):
            if not any(path.iterdir()):
                empty.append(str(path.relative_to(ROOT)))
    assert empty == []


def test_every_dataset_has_card_and_matching_checksum():
    csv_files = sorted((ROOT / "datasets" / "synthetic").glob("*.csv"))
    assert csv_files
    for csv_path in csv_files:
        card = yaml.safe_load(csv_path.with_suffix(".yaml").read_text())
        assert card["sha256"] == hashlib.sha256(csv_path.read_bytes()).hexdigest()
        for field in ["title", "kind", "license", "leakage_risks", "representativeness"]:
            assert field in card


def test_dataset_catalog_lists_every_dataset():
    names = {p.stem for p in (ROOT / "datasets" / "synthetic").glob("*.csv")}
    with (ROOT / "datasets" / "catalog.csv").open() as handle:
        listed = {row["name"] for row in csv.DictReader(handle)}
    assert listed == names


def test_paper_catalog_matches_registry():
    with (ROOT / "research" / "paper_catalog.csv").open() as handle:
        rows = {row["key"]: row for row in csv.DictReader(handle)}
    assert set(rows) == set(refs.REFS)
    for key, record in refs.REFS.items():
        assert rows[key]["verified"] == ("yes" if record["verified"] else "no")


def test_every_spec_reference_is_in_registry():
    for spec in build_modules.all_specs():
        for key in spec["refs"]:
            assert key in refs.REFS


def test_declared_status_is_supported_by_evidence():
    for spec in build_modules.all_specs():
        assert render_status.status_problems(spec) == [], spec["module"]


def test_module_with_unverified_reference_is_not_complete():
    for spec in build_modules.all_specs():
        if render_status.unverified_refs(spec):
            assert spec["status"] != "Complete"


def test_status_page_is_current(tmp_path):
    before = (ROOT / "docs" / "project_status.md").read_text()
    render_status.write_status(build_modules.all_specs())
    after = (ROOT / "docs" / "project_status.md").read_text()
    assert before == after


def test_relative_markdown_links_resolve():
    pattern = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
    broken = []
    for path in markdown_files():
        for target in pattern.findall(path.read_text()):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).exists():
                broken.append(f"{path.relative_to(ROOT)} -> {target}")
    assert broken == []


def test_no_placeholder_text_in_docs():
    banned = ["TODO", "lorem ipsum", "TBD"]
    for path in markdown_files():
        text = path.read_text()
        for word in banned:
            assert word not in text, f"{word} in {path.relative_to(ROOT)}"
