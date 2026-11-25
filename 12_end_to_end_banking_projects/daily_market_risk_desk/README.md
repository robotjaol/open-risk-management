# Daily Activity: The Market Risk Desk Report

A morning in market risk on real exchange rates: data checks, VaR, limit status, tail drivers, backtest and a reduction that is verified by recomputation.

| Item | Value |
|---|---|
| Family | End to End Banking Projects |
| Level | Applied |
| Status | Validating |
| Dataset | `fx_daily_2000` (empirical), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`daily_market_risk_desk.ipynb`](daily_market_risk_desk.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/daily_market_risk_desk.json`](../../experiments/results/daily_market_risk_desk.json) |

## What you learn

- Data quality checks before the report
- VaR, tail mean and tail contributions for a book
- Limit utilisation, status and an escalation log
- Backtest and traffic light zone in the same report
- Sizing and verifying a risk reduction

## Run it

```bash
pip install -e ".[development]"
jupyter lab daily_market_risk_desk.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 12_end_to_end_banking_projects/daily_market_risk_desk`.

## Saved results

<!-- results:start -->
Source: `experiments/results/daily_market_risk_desk.json`. Data kind: **empirical**. Dataset: `datasets/processed/fx_daily_2000.csv`. Observations: 6740. Seed: 42. Created: 2026-11-25T05:53:37+00:00.

| Metric | Value |
|---|---|
| `status_share_of_days.amber` | 0.4814 |
| `status_share_of_days.green` | 0.3253 |
| `status_share_of_days.red` | 0.1933 |
| `exceptions_full_history` | 85 |
| `kupiec_p_full_history` | 0.006424 |
| `data_quality_counts_full_history.stale_all_currencies` | 3 |
| `data_quality_counts_full_history.outlier_over_5_sigma` | 43 |
| `data_quality_counts_full_history.gap_over_5_days` | 0 |
| `red_episodes` | 4 |
| `highest_utilisation_day` | 2013-06-21 |
| `highest_utilisation` | 1.153 |
| `pro_rata_cut_usd` | 2.196e+07 |
| `cheapest_targeted_cut_usd` | 1.825e+07 |
| `cheapest_targeted_currency` | Japan |

Acceptance checks computed by the notebook:

* `scratch_var_equals_library_no_lookahead_1e-12`: passed
* `tail_parts_sum_to_tail_mean`: passed
* `pro_rata_reduction_verified_and_linear`: passed
* `targeted_reduction_verified`: passed
* `data_quality_checks_ran`: passed
* `daily_report_has_all_fields`: passed

Limitations recorded with the results:

* linear spot positions only, no options, forwards, carry or settlement
* one day horizon, no liquidity horizon
* the limit was set after looking at the VaR history
* no intraday data and no daily revaluation of a real book
<!-- results:end -->
