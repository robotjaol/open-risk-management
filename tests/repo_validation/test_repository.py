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
    "research_gaps.md", "literature_review.md", "source_register.md",
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


def dataset_files():
    files = []
    for folder in ["synthetic", "raw", "processed"]:
        files += sorted((ROOT / "datasets" / folder).glob("*.csv"))
    return files


def test_every_dataset_has_card_and_matching_checksum():
    csv_files = dataset_files()
    assert len(csv_files) >= 8
    for csv_path in csv_files:
        card = yaml.safe_load(csv_path.with_suffix(".yaml").read_text())
        assert card["sha256"] == hashlib.sha256(csv_path.read_bytes()).hexdigest()
        for field in ["title", "kind", "license", "leakage_risks", "representativeness"]:
            assert field in card, f"{field} missing in {csv_path.name}"


def test_real_dataset_cards_have_source_and_access_date():
    real = [p for p in dataset_files() if p.parent.name in ("raw", "processed")]
    assert len(real) >= 4
    for csv_path in real:
        card = yaml.safe_load(csv_path.with_suffix(".yaml").read_text())
        assert card["kind"] == "empirical"
        assert card["source_url"].startswith("https://")
        assert card["access_date"]
        assert card["changes"]


def test_dataset_catalog_lists_every_dataset():
    names = {p.stem for p in dataset_files()}
    with (ROOT / "datasets" / "catalog.csv").open() as handle:
        listed = {row["name"] for row in csv.DictReader(handle)}
    assert listed == names


def test_every_dataset_used_by_a_module_exists():
    for spec in build_modules.all_specs():
        assert spec["dataset"], spec["module"]


def test_every_doi_in_catalog_is_well_formed_and_in_registry():
    with (ROOT / "research" / "paper_catalog.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with_doi = [row for row in rows if row["doi"]]
    assert len(with_doi) == len(refs.DOIS) == 9
    for row in with_doi:
        assert re.fullmatch(r"10\.\d{4,9}/\S+", row["doi"]), row["doi"]
        assert row["verified"] == "yes"


def test_source_register_is_current():
    import render_catalogs

    before = (ROOT / "research" / "source_register.md").read_text()
    render_catalogs.write_source_register()
    assert before == (ROOT / "research" / "source_register.md").read_text()


def test_readme_images_exist():
    readme = (ROOT / "README.md").read_text()
    images = re.findall(r'src="([^"]+\.png)"', readme)
    assert len(images) >= 4
    for image in images:
        assert (ROOT / image).exists(), image


def test_readme_names_jupyter_lab():
    assert "jupyter lab" in (ROOT / "README.md").read_text()


def test_every_figure_listed_in_results_exists():
    import json

    for path in (ROOT / "experiments" / "results").glob("*.json"):
        result = json.loads(path.read_text())
        for name in result.get("figures", []):
            assert (ROOT / "experiments" / "figures" / result["module"] / name).exists(), name


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
