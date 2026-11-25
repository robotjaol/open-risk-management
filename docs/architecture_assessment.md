# Architecture Assessment

Audience: contributors who must decide what to build next. Explanation document. Date 2026-11-25. Author: robotjaol with Claude. This assessment is self review, not independent audit.

## Decision

Keep the spec driven design: one specification file per module generates the notebook, README and references, and a results file feeds the README and the status page. Build breadth only after the shared library and the evidence checks are stable. Do not add modules by copying a notebook by hand.

## Structure

| Layer | Location | Role |
|---|---|---|
| Specification | `tools/specs/*.py` | content of a module as data and code cells |
| Generator | `tools/nbgen.py`, `tools/build_modules.py` | writes notebook, README, references.md |
| Runner | `tools/run_notebooks.py` | executes every notebook in a clean kernel, writes the execution log |
| Library | `src/risk_lab` | tested code the notebooks import |
| Evidence | `experiments/results`, `experiments/configurations`, `experiments/figures`, `experiments/metadata` | saved outputs |
| Renderers | `tools/render_results.py`, `render_status.py`, `render_catalogs.py` | README result blocks, status page, catalogs |
| Tests | `tests/unit`, `tests/notebook_validation`, `tests/repo_validation` | code, notebook and repository rules |

## Strengths

1. One reference registry feeds notebooks, references.md and the paper catalog, so citations cannot drift apart.
2. Status is computed from evidence. A declared Complete without passing checks is reported by `render_status.py`.
3. Each method has an independent second implementation and the gap is saved.
4. Everything is deterministic from seeds.

## Weaknesses

1. Specification files are long Python files. Editing a notebook means editing a string inside code. Risk: review is harder than reviewing a notebook diff. Mitigation: keep cells short and keep logic in `src/risk_lab`.
2. Generated and hand written content mix in READMEs. The result block between markers is overwritten on every render, so edits inside the markers are lost.
3. The same synthetic return set feeds four market modules. A flaw in the generator would affect all four. Mitigation: add a second generator and real data.
4. Both workflows ran green on a hosted runner for the v0.2.0 commit (2026-11-25). They have one run so far, so stability over time is not shown.
5. Library coverage is thin: no LGD or EAD estimation, no Monte Carlo engine for portfolios, no stress testing helpers.
6. The status evidence check cannot detect an acceptance criterion that is too weak. A reviewer must read the criteria.

## Priorities

1. Keep both CI workflows green on the default branch over several commits. Measure: no red run in the next 10 pushes.
2. Add loss_given_default and exposure_at_default, which complete the ECL inputs. Measure: ECL module can use estimated rather than assumed inputs.
3. Add one real public dataset with a documented license. Measure: one module has `data_kind` empirical with a passing check.
4. Verify the three book references or replace them with primary papers. Measure: `unverified_references` empty for the modules that cite them.
5. Add independent review for any module before it keeps the status Complete.

## Check before use

* Priorities are professional judgment. The size of each task is not estimated.
