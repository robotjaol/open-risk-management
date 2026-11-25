# Research Simulation: Does a Calm Period VaR Survive a Crisis

Hypotheses, a written decision rule and real price history from 1986, to test whether a 500 day VaR fails when it matters.

| Item | Value |
|---|---|
| Family | End to End Banking Projects |
| Level | Applied |
| Status | Validating |
| Dataset | `wti_spot_daily and fx_daily_2000` (empirical), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`var_crisis_research.ipynb`](var_crisis_research.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/var_crisis_research.json`](../../experiments/results/var_crisis_research.json) |

## What you learn

- Turn a risk committee worry into hypotheses and a decision rule
- Handle real data problems, such as a negative price, in the open
- Compare a slow and a responsive VaR on the same days
- Test whether a conclusion survives other settings
- Write a finding with its limits

## Run it

```bash
pip install -e ".[development]"
jupyter lab var_crisis_research.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 12_end_to_end_banking_projects/var_crisis_research`.

## Saved results

<!-- results:start -->
Source: `experiments/results/var_crisis_research.json`. Data kind: **empirical**. Dataset: `datasets/raw/wti_spot_daily.csv and datasets/processed/fx_daily_2000.csv`. Observations: 16284. Seed: 42. Created: 2026-11-25T10:36:17+00:00.

| Metric | Value |
|---|---|
| `hypothesis_outcomes_overall.H1` | yes |
| `hypothesis_outcomes_overall.H2` | yes |
| `share_t_ewma_configs_beating_hist500` | 1 |
| `scratch_vs_library_max_gap` | 0 |

Acceptance checks computed by the notebook:

* `scratch_matches_library_no_lookahead_1e-12`: passed
* `windows_inside_data_with_80_days`: passed
* `excluded_wti_days_match_independent_rule`: passed
* `hypotheses_evaluated_for_both_assets`: passed

Limitations recorded with the results:

* two assets only, one FX basket and one commodity
* crisis windows are few and chosen with hindsight about which periods were crises
* exceptions cluster, so exact intervals and Kupiec p values are too optimistic
* single day VaR on linear positions, no ten day horizon and no capital calculation
<!-- results:end -->
