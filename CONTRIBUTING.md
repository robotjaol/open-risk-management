# Contributing

Thank you for helping. This guide is a how to. Read [methodology_standards.md](docs/methodology_standards.md) first.

## Set up

1. Fork and clone the repository.
2. `pip install -e ".[development]"`
3. `make test` and confirm all tests pass before you change anything.

## Add or change a module

1. Write or edit the specification in `tools/specs/<module>.py`. Put reusable logic in `src/risk_lab` with a unit test in `tests/unit`.
2. Add every source to `tools/refs.py` first. New entries start with `verified = False`. Set it to `True` only after checking the record against an independent index or the publisher page, and write that source in the `source` field.
3. Write acceptance criteria before you look at the result. Store them as booleans under `acceptance_criteria` in the saved metrics.
4. Run the pipeline in this order.

   ```bash
   python tools/build_modules.py <module>
   python tools/run_notebooks.py <module>
   python tools/render_results.py
   python tools/render_catalogs.py
   python tools/render_status.py
   ```

5. Run `make test`, `make test-notebooks` and `make lint`. All must pass.
6. Do not edit text between the `results:start` and `results:end` markers by hand. It is overwritten.

## Rules for results

* Numbers in text come from executed code.
* A failed acceptance check stays visible. Do not change a threshold after seeing the result. If a threshold was wrong, say so in the module and keep the original.
* A module with an unverified reference cannot be Complete.
* Label data as synthetic, illustrative or empirical.

## Code style

Plain code, clear names, comments of at most three words, no decorative symbols. Ruff configuration is in `pyproject.toml`.

## Commits and pull requests

Small commits with a clear subject line. A pull request states: what changed, which module, which checks ran, what is still open.

## Report a problem

Open an issue with the module name, the command you ran and the output. For a security problem see [SECURITY.md](SECURITY.md).
