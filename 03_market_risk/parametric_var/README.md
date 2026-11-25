# Parametric and Monte Carlo Value at Risk

Delta normal, Student t, EWMA and Monte Carlo VaR, with Euler risk decomposition and a backtest.

| Item | Value |
|---|---|
| Family | Market Risk |
| Level | Intermediate |
| Status | Validating |
| Dataset | `market_returns` (synthetic), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`parametric_var.ipynb`](parametric_var.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/parametric_var.json`](../../experiments/results/parametric_var.json) |

## What you learn

- Portfolio variance, delta normal VaR and Student t VaR
- EWMA volatility and one day ahead forecasts
- Monte Carlo with Cholesky and its convergence
- Euler component VaR and diversification
- Backtest of parametric against historical VaR

## Run it

```bash
pip install -e ".[development]"
jupyter lab parametric_var.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 03_market_risk/parametric_var`.

## Saved results

<!-- results:start -->
Source: `experiments/results/parametric_var.json`. Data kind: **synthetic**. Dataset: `datasets/synthetic/market_returns.csv`. Observations: 3000. Seed: 42. Created: 2026-11-25T05:53:16+00:00.

| Metric | Value |
|---|---|
| `full_sample_var_99_pct.historical` | 1.462 |
| `full_sample_var_99_pct.normal` | 1.32 |
| `full_sample_var_99_pct.student_t` | 1.491 |
| `nu_estimated_first_1000_days` | 3 |
| `nu_raw_first_1000_days` | 2.07 |
| `jarque_bera_p_value` | 0 |
| `excess_kurtosis` | 5.753 |
| `acf_squared_returns_lag1` | 0.09148 |
| `monte_carlo_normal_within_3_se` | yes |
| `t_monte_carlo_relative_gap` | 0.0009716 |
| `component_var_pct.r_equity` | 1.313 |
| `component_var_pct.r_fx` | 0.05604 |
| `component_var_pct.r_bond` | -0.02446 |

Acceptance checks computed by the notebook:

* `monte_carlo_normal_within_3_se`: passed
* `components_sum_to_total`: passed
* `t_monte_carlo_within_2pct`: passed
* `exceptions_and_kupiec_reported`: passed

Limitations recorded with the results:

* synthetic returns from a GARCH with Student t shocks, so a t model is well matched by construction
* linear positions only
* single confidence level in the backtest
<!-- results:end -->
