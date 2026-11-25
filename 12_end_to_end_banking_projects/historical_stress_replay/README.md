# Stress Testing: Replaying History on Today's Portfolio

Real monthly history from 1871 replayed on a 60/40 portfolio, a reverse stress frontier, and a test of how much a 20 year VaR understated the worst months.

| Item | Value |
|---|---|
| Family | End to End Banking Projects |
| Level | Applied |
| Status | Validating |
| Dataset | `sp500_shiller_monthly` (empirical), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`historical_stress_replay.ipynb`](historical_stress_replay.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/historical_stress_replay.json`](../../experiments/results/historical_stress_replay.json) |

## What you learn

- Build total returns from raw price, dividend and yield data
- Replay worst historical windows on today's portfolio
- Solve and verify a reverse stress frontier
- Measure how far a rolling VaR fell short of the worst months
- Say what a history based stress test cannot show

## Run it

```bash
pip install -e ".[development]"
jupyter lab historical_stress_replay.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 12_end_to_end_banking_projects/historical_stress_replay`.

## Saved results

<!-- results:start -->
Source: `experiments/results/historical_stress_replay.json`. Data kind: **empirical**. Dataset: `datasets/raw/sp500_shiller_monthly.csv`. Observations: 1829. Seed: 42. Created: 2026-11-25T05:53:44+00:00.

| Metric | Value |
|---|---|
| `valid_months` | 1830 |
| `excluded_trailing_rows` | 39 |
| `last_valid_month` | 2023-06-01 |
| `todays_yield` | 0.0375 |
| `var_exceptions` | 26 |
| `var_expected_exceptions` | 15.89 |
| `var_months_evaluated` | 1589 |
| `kupiec_p` | 0.01957 |
| `worst_monthly_loss_historical_portfolio` | 0.155 |
| `worst_monthly_loss_date` | 1929-11-01 |
| `var_in_force_at_worst_month` | 0.04506 |
| `worst_replayed_month_loss` | 0.1549 |
| `loss_appetite` | 0.2 |

Acceptance checks computed by the notebook:

* `bond_approximation_p99_below_0.1_percent`: passed
* `equity_hand_check_matches`: passed
* `scratch_var_equals_library_no_lookahead_1e-12`: passed
* `reverse_stress_frontier_gives_exact_appetite`: passed
* `worst_windows_start_12_months_apart`: passed
* `excluded_rows_are_trailing_and_valid_months_consecutive`: passed

Limitations recorded with the results:

* US equity and US rates only, one portfolio
* monthly data hides intra month moves, so the worst day is not seen
* price definition (monthly average or month end) is not verified, an average would understate tail months
* history based replay cannot show a month unlike any in the file
* no credit spread, inflation or liquidity effect, and no correlation break scenario
* the yield series of the 19th century is a reconstruction by the data author
<!-- results:end -->
