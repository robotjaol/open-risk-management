# Getting Started

Audience: someone who knows basic Python and wants to run the modules and read the results. Time to first result: about 10 minutes. Version 0.2.0, 2026-11-25. Maintainer: robotjaol.

This is a how to guide. For definitions see the glossaries. For the rules every module follows see [methodology_standards.md](methodology_standards.md).

## Requirements

Python 3.10 or newer, git, and about 500 MB of disk space for packages. No network access is needed after installation because every dataset is generated locally or committed with a checksum.

## Steps

1. Clone the repository and enter it.

   ```bash
   git clone https://github.com/robotjaol/open-risk-management.git
   cd open-risk-management
   ```

   Expected result: the folders `02_credit_risk`, `03_market_risk`, `12_end_to_end_banking_projects`, `src`, `tools` exist.

2. Create an environment and install the package with development tools.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[development]"
   ```

   Expected result: `python -c "import risk_lab"` prints nothing and exits with code 0.

3. Run the unit tests.

   ```bash
   make test
   ```

   Expected result: all tests pass. The number of tests is printed by pytest.

4. Regenerate the synthetic datasets. This is deterministic, so the files should not change.

   ```bash
   make data
   git status --short datasets
   ```

   Expected result: no modified files under `datasets/synthetic`.

5. Execute every notebook from a clean kernel.

   ```bash
   make notebooks
   ```

   Expected result: one line per notebook that starts with `ok`, 12 in total. Runtime is about 1 minute on a normal laptop.

   To read and run a notebook yourself, start JupyterLab and open one of the notebooks under `02_credit_risk`, `03_market_risk` or `12_end_to_end_banking_projects`.

   ```bash
   jupyter lab
   ```

   Expected result: a browser tab opens. Choose Run, Restart Kernel and Run All Cells. The notebook finishes without an error and writes figures to `experiments/figures/`.

6. Read a module. Open `03_market_risk/historical_var/README.md` first, then the notebook next to it.

7. Optional: download the real datasets again from the original sources.

   ```bash
   make fetch-data
   ```

   Expected result: the files in `datasets/raw` and `datasets/processed` are rewritten. Compare `sha256` in each card. A changed checksum means the source file changed.

8. Rebuild the status page.

   ```bash
   make status
   ```

   Expected result: `docs/project_status.md` and `docs/module_registry.csv` are rewritten, and each module prints `OK`.

## Folder map

| Folder | Content |
|---|---|
| `NN_family/topic/` | README, notebook, references.md for one module |
| `src/risk_lab/` | reusable code that the notebooks import |
| `datasets/` | synthetic and real data, dataset cards, catalog |
| `experiments/` | saved results, configurations, figures, execution log |
| `research/` | literature review, source register, paper catalog, regulatory sources, gaps |
| `tools/` | build scripts for notebooks, data, status and catalogs |
| `tests/` | unit tests, notebook validation, repository validation |

## Troubleshooting

* `ModuleNotFoundError: risk_lab`: step 2 was skipped or the environment is not active.
* `jupyter kernel` error in step 5: run `python -m ipykernel install --user --name python3`.
* A notebook ends with a failed acceptance check: this is allowed and is shown in the module README. `credit_scoring` has one such check on purpose. See [project_status.md](project_status.md).

## Known limits

Results on synthetic data show that code and methods behave as theory predicts. Results on real open data show behaviour on that series. Neither says anything about a real bank. See [limitations_and_disclaimers.md](limitations_and_disclaimers.md).
