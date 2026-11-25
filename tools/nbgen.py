"""Build a notebook, a module README and a references file from a spec.

Notebook text is written once in tools/specs. Numbers come from running the
notebook, never from this file.
"""

import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

sys.path.insert(0, str(Path(__file__).parent))
import refs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

SECTION_NAMES = {
    1: "Problem Statement",
    2: "Learning Objectives",
    3: "Fundamental Concepts",
    4: "Why This Method?",
    5: "Research Foundation",
    6: "Mathematical Derivation",
    7: "Worked Numerical Example",
    8: "Dataset Exploration",
    9: "Data Preparation",
    10: "Implementation from Scratch",
    11: "Implementation using Libraries",
    12: "Model Evaluation",
    13: "Visualization",
    14: "Interpretation",
    15: "Experiments",
    16: "Results and Comparisons",
    17: "Limitations and Model Risk",
    18: "Practical Banking Application",
    19: "Exercises",
    20: "References",
}

RESULTS_START = "<!-- results:start -->"
RESULTS_END = "<!-- results:end -->"


def M(text):
    return ("md", text.strip("\n"))


def C(code):
    return ("code", code.strip("\n"))


def anchor(number, name):
    return f"{number}-" + name.lower().replace(" ", "-").replace("?", "")


def table_of_contents():
    lines = ["## Table of Contents", ""]
    for number, name in SECTION_NAMES.items():
        lines.append(f"{number}. [{name}](#{anchor(number, name)})")
    return "\n".join(lines)


def header_cell(spec):
    kind_note = {
        "synthetic": "Data are synthetic. Numbers describe the generator, not any real bank.",
        "illustrative": "Numbers come from a small illustrative example defined in this notebook.",
        "empirical": "Data are empirical.",
    }[spec["data_kind"]]
    meta = (
        f"**Family:** {spec['family']} | **Level:** {spec['level']} | "
        f"**Dataset:** `{spec['dataset']}` | **Data kind:** {spec['data_kind']} | "
        f"**Module status:** {spec['status']}"
    )
    return f"# {spec['title']}\n\n{meta}\n\n{spec['tagline']}\n\n> {kind_note}\n\n{table_of_contents()}"


def references_section(spec):
    lines = ["Entries are grouped by type. A reference marked NOT VERIFIED must be checked before it is cited.", ""]
    for record in refs.get(spec["refs"]):
        lines.append(f"- **{record['authors']} ({record['year'] or 'n/a'}).** {record['title']}. {record['venue']}. {refs.link_text(record)}")
        lines.append(f"  - Type: {record['kind']}. Status: {record['status']}. Check: {refs.verification_text(record)}")
    return "\n".join(lines)


def research_section(spec):
    lines = []
    academic = [r for r in refs.get(spec["refs"]) if r["kind"] in ("academic", "book")]
    regulatory = [r for r in refs.get(spec["refs"]) if r["kind"] == "regulatory"]
    if academic:
        lines += ["### Academic and book sources", ""]
        for record in academic:
            lines.append(f"- **{record['title']}** ({record['authors']}, {record['year'] or 'n/a'}). {record['contribution']} [{refs.verification_text(record)}]")
    if regulatory:
        lines += ["", "### Regulatory and standard setter sources", ""]
        for record in regulatory:
            lines.append(f"- **{record['title']}** ({record['authors']}, {record['year']}). Status: {record['status']}. {record['contribution']} [{refs.verification_text(record)}]")
    lines += ["", "**How this notebook uses them.** " + spec["research_note"]]
    lines += [
        "",
        "**Academic findings versus regulatory requirements.** Papers describe what methods can do. "
        "Regulations and accounting standards say what a supervised institution must do. This notebook labels which is which, "
        "and it does not reproduce any paper's experiment. Data differ, so numbers are not comparable with published results.",
    ]
    return "\n".join(lines)


def section_cells(number, spec):
    name = SECTION_NAMES[number]
    heading = new_markdown_cell(f"## {number}. {name}")
    cells = [heading]
    if number == 5:
        cells.append(new_markdown_cell(research_section(spec)))
        return cells
    if number == 20:
        cells.append(new_markdown_cell(references_section(spec)))
        return cells
    for kind, text in spec["sections"][number]:
        cells.append(new_markdown_cell(text) if kind == "md" else new_code_cell(text))
    return cells


def build_notebook(spec):
    cells = [new_markdown_cell(header_cell(spec)), new_code_cell(spec["setup"])]
    for number in SECTION_NAMES:
        cells += section_cells(number, spec)
    notebook = new_notebook(cells=cells)
    notebook.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    notebook.metadata["language_info"] = {"name": "python"}
    return notebook


def module_dir(spec):
    return ROOT / spec["path"]


def notebook_path(spec):
    return module_dir(spec) / f"{spec['module']}.ipynb"


def readme_text(spec):
    learn = "\n".join(f"- {item}" for item in spec["learn"])
    return f"""# {spec['title']}

{spec['tagline']}

| Item | Value |
|---|---|
| Family | {spec['family']} |
| Level | {spec['level']} |
| Status | {spec['status']} |
| Dataset | `{spec['dataset']}` ({spec['data_kind']}), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`{spec['module']}.ipynb`]({spec['module']}.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/{spec['module']}.json`](../../experiments/results/{spec['module']}.json) |

## What you learn

{learn}

## Run it

```bash
pip install -e ".[development]"
jupyter lab {spec['module']}.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py {spec['path']}`.

## Saved results

{RESULTS_START}
Results are written after the notebook runs. Run `python tools/render_results.py`.
{RESULTS_END}
"""


def references_md(spec):
    lines = [f"# References for {spec['title']}", ""]
    for record in refs.get(spec["refs"]):
        lines.append(f"## {record['title']}")
        lines.append("")
        lines.append(f"- Authors: {record['authors']}")
        lines.append(f"- Year: {record['year'] or 'n/a'}")
        lines.append(f"- Venue or issuer: {record['venue']}")
        lines.append(f"- Link: {refs.link_text(record)}")
        lines.append(f"- Type: {record['kind']}")
        lines.append(f"- Status: {record['status']}")
        lines.append(f"- Verification: {refs.verification_text(record)}")
        lines.append(f"- Contribution: {record['contribution']}")
        lines.append("")
    return "\n".join(lines)


def write_module(spec):
    folder = module_dir(spec)
    folder.mkdir(parents=True, exist_ok=True)
    nbformat.write(build_notebook(spec), notebook_path(spec))
    readme_path = folder / "README.md"
    if readme_path.exists() and RESULTS_START in readme_path.read_text():
        old = readme_path.read_text()
        start = old.index(RESULTS_START)
        end = old.index(RESULTS_END) + len(RESULTS_END)
        kept_block = old[start:end]
        new = readme_text(spec)
        new_start = new.index(RESULTS_START)
        new_end = new.index(RESULTS_END) + len(RESULTS_END)
        new = new[:new_start] + kept_block + new[new_end:]
        readme_path.write_text(new)
    else:
        readme_path.write_text(readme_text(spec))
    (folder / "references.md").write_text(references_md(spec))
