# Methodology Standards

Audience: contributors and reviewers. This is a reference document. It defines what a module must contain and when it may claim a status.

## Module contents

Every module folder has four things: a README, a notebook, `references.md`, and saved outputs under `experiments/` (results JSON, configuration YAML, figures).

## Notebook sections

The notebook has 20 sections in this fixed order: Problem Statement, Learning Objectives, Fundamental Concepts, Why This Method?, Research Foundation, Mathematical Derivation, Worked Numerical Example, Dataset Exploration, Data Preparation, Implementation from Scratch, Implementation using Libraries, Model Evaluation, Visualization, Interpretation, Experiments, Results and Comparisons, Limitations and Model Risk, Practical Banking Application, Exercises, References. The names are defined in `tools/nbgen.py` and checked by `tests/notebook_validation`. Sections 5 and 20 are generated from the reference registry in `tools/refs.py`, so a notebook cannot cite something that is not in the registry.

## Evidence rules

1. Every number in a README or doc comes from executed code. The README result block is rendered from `experiments/results/<module>.json` by `tools/render_results.py`.
2. Every results file carries `data_kind`, one of synthetic, illustrative or empirical. A synthetic result is never described as a finding about real portfolios.
3. Every method is implemented a second way (closed form, loop against library, finite difference, simulation or numerical integration) and the gap is saved.
4. Acceptance criteria are written before the result is read and stored as booleans in the results file. A failed criterion is reported, not edited away. `credit_scoring` is the example in version 0.2.0.
5. Seeds are fixed and stored.

## References

A reference has `verified = true` only if its bibliographic record was matched against an independent index or the publisher page on the date in `tools/refs.py`. This does not mean the full text was read for every claim. Books are not verified in version 0.2.0.

## Status rules

| Status | Meaning |
|---|---|
| Planned | listed in the plan, no directory |
| Researching | sources being collected |
| Implementing | code being written |
| Validating | notebook runs, but at least one condition for Complete is open |
| Complete | notebook runs from a clean kernel, saved results exist, at least one computed acceptance check exists and all pass, every cited reference is verified |

`tools/render_status.py` tests these conditions and prints the reason when a declared status is not supported. A module that cites an unverified book stays Validating.

## Code rules

Plain code, clear names, comments of at most three words, no decorative symbols. Ruff must pass with the repository configuration.

## What these standards do not guarantee

Passing every rule shows internal consistency. It does not show that a method fits a real bank. That needs real data and independent validation. See [limitations_and_disclaimers.md](limitations_and_disclaimers.md).
