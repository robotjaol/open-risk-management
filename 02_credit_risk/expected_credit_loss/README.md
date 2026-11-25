# Expected Credit Loss under IFRS 9 (Simplified)

Stage a loan book, compute ECL, weight macro scenarios and measure the cliff and the sensitivities.

| Item | Value |
|---|---|
| Family | Credit Risk |
| Level | Intermediate |
| Status | Complete |
| Dataset | `loan_book` (synthetic), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`expected_credit_loss.ipynb`](expected_credit_loss.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/expected_credit_loss.json`](../../experiments/results/expected_credit_loss.json) |

## What you learn

- ECL formula with balance profile and discounting
- Stage allocation with SICR and days past due
- Closed form checks and a second implementation as a control
- Scenario weighting and non linearity
- Sensitivity to SICR thresholds and the stage 1 to stage 2 cliff

## Run it

```bash
pip install -e ".[development]"
jupyter lab expected_credit_loss.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 02_credit_risk/expected_credit_loss`.

## Saved results

<!-- results:start -->
Source: `experiments/results/expected_credit_loss.json`. Data kind: **synthetic**. Dataset: `datasets/synthetic/loan_book.csv`. Observations: 5000. Seed: 7. Created: 2026-11-25T05:53:08+00:00.

| Metric | Value |
|---|---|
| `total_ead` | 1.615e+08 |
| `total_ecl` | 6.931e+06 |
| `coverage_pct` | 4.293 |
| `scenario_ecl.upside` | 5.902e+06 |
| `scenario_ecl.base` | 6.931e+06 |
| `scenario_ecl.downside` | 9.719e+06 |
| `scenario_weights.upside` | 0.2 |
| `scenario_weights.base` | 0.5 |
| `scenario_weights.downside` | 0.3 |
| `probability_weighted_ecl` | 7.562e+06 |
| `ecl_at_weighted_mean_pd` | 7.618e+06 |
| `top_5pct_loans_share_of_ecl` | 0.4706 |
| `max_gap_loop_vs_library` | 7.276e-12 |

Acceptance checks computed by the notebook:

* `one_year_closed_form`: passed
* `stage3_equals_lgd_times_ead`: passed
* `lifetime_at_least_12m`: passed
* `ecl_not_above_ead`: passed
* `coverage_rises_with_stage`: passed

Limitations recorded with the results:

* no collateral timing, no cure rates, no prepayment, no off balance sheet exposure
* constant hazard ignores the PD term structure
* synthetic book, not a real portfolio
<!-- results:end -->
