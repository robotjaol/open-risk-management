import json
import re
from pathlib import Path

import build_modules
import nbgen
import pytest

from risk_lab.reporting.results import DATA_KINDS, REQUIRED_KEYS

ROOT = Path(__file__).resolve().parents[2]
SPECS = build_modules.all_specs()
IDS = [spec["module"] for spec in SPECS]


def load_notebook(spec):
    return json.loads(nbgen.notebook_path(spec).read_text())


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_notebook_has_twenty_sections_in_order(spec):
    notebook = load_notebook(spec)
    found = []
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            first_line = "".join(cell["source"]).split("\n")[0]
            match = re.match(r"## (\d+)\. (.+)", first_line)
            if match:
                found.append((int(match.group(1)), match.group(2)))
    assert found == list(nbgen.SECTION_NAMES.items())


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_notebook_has_no_error_outputs(spec):
    notebook = load_notebook(spec)
    for cell in notebook["cells"]:
        for output in cell.get("outputs", []):
            assert output.get("output_type") != "error"


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_code_cells_were_executed(spec):
    notebook = load_notebook(spec)
    code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
    assert code_cells
    assert all(c.get("execution_count") for c in code_cells)


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_module_files_exist(spec):
    folder = nbgen.module_dir(spec)
    for name in ["README.md", "references.md"]:
        assert (folder / name).exists()
    assert (ROOT / "experiments" / "results" / f"{spec['module']}.json").exists()
    assert (ROOT / "experiments" / "configurations" / f"{spec['module']}.yaml").exists()
    assert list((ROOT / "experiments" / "figures" / spec["module"]).glob("*.png"))


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_results_file_follows_schema(spec):
    result = json.loads((ROOT / "experiments" / "results" / f"{spec['module']}.json").read_text())
    for key in REQUIRED_KEYS:
        assert key in result
    assert result["data_kind"] in DATA_KINDS
    assert result["limitations"]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_execution_log_is_ok(spec):
    log = json.loads((ROOT / "experiments" / "metadata" / "execution_log.json").read_text())
    key = str(nbgen.notebook_path(spec).relative_to(ROOT))
    assert log[key]["status"] == "ok"


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_readme_result_block_matches_results_file(spec):
    readme = (nbgen.module_dir(spec) / "README.md").read_text()
    block = readme[readme.index(nbgen.RESULTS_START):readme.index(nbgen.RESULTS_END)]
    result = json.loads((ROOT / "experiments" / "results" / f"{spec['module']}.json").read_text())
    assert f"`experiments/results/{result['module']}.json`" in block
    assert result["created"] in block
