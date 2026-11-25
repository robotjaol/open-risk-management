# Historical Simulation Value at Risk

Compute rolling historical VaR, test its exceptions, and measure its sampling error and lag.

| Item | Value |
|---|---|
| Family | Market Risk |
| Level | Beginner to Intermediate |
| Status | Validating |
| Dataset | `market_returns` (synthetic), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`historical_var.ipynb`](historical_var.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/historical_var.json`](../../experiments/results/historical_var.json) |

## What you learn

- Empirical quantile VaR and quantile conventions
- Rolling forecast with no look ahead, verified by a second implementation
- Exceptions, Kupiec test and exception clustering
- Bootstrap interval for a tail quantile
- Window length trade off and square root of time scaling

## Run it

```bash
pip install -e ".[development]"
jupyter lab historical_var.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 03_market_risk/historical_var`.

## Saved results

<!-- results:start -->
Source: `experiments/results/historical_var.json`. Data kind: **synthetic**. Dataset: `datasets/synthetic/market_returns.csv`. Observations: 3000. Seed: 42. Created: 2026-11-25T05:53:12+00:00.

| Metric | Value |
|---|---|
| `full_sample_var_99_pct` | 1.462 |
| `full_sample_var_99_currency` | 1.462e+06 |
| `ten_day_var_99_sqrt_time_pct` | 4.623 |
| `ten_day_var_99_overlapping_pct` | 3.868 |
| `max_gap_loop_vs_library` | 3.469e-18 |

Acceptance checks computed by the notebook:

* `loop_matches_library_1e-12`: passed
* `rolling_matches_pandas_no_lookahead`: passed
* `bootstrap_interval_for_every_level`: passed
* `exceptions_and_kupiec_for_every_window`: passed

Limitations recorded with the results:

* synthetic returns from a GARCH generator
* no position level revaluation, linear portfolio only
* iid bootstrap understates uncertainty when volatility clusters
<!-- results:end -->
