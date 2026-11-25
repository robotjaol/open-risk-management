# Backtesting Value at Risk

Kupiec, Christoffersen and the traffic light, with a measured answer to how often each test catches a bad model.

| Item | Value |
|---|---|
| Family | Market Risk |
| Level | Intermediate |
| Status | Complete |
| Dataset | `market_returns` (synthetic), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`backtesting.ipynb`](backtesting.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/backtesting.json`](../../experiments/results/backtesting.json) |

## What you learn

- Kupiec and Christoffersen statistics by hand and by library
- Traffic light zones from binomial probabilities
- Backtesting several models on the same days
- Power of each test by simulation
- A mechanical model decision rule and its limits

## Run it

```bash
pip install -e ".[development]"
jupyter lab backtesting.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 03_market_risk/backtesting`.

## Saved results

<!-- results:start -->
Source: `experiments/results/backtesting.json`. Data kind: **synthetic**. Dataset: `datasets/synthetic/market_returns.csv`. Observations: 2000. Seed: 42. Created: 2026-11-25T05:53:24+00:00.

| Metric | Value |
|---|---|
| `max_gap_loops_vs_library` | 0 |
| `max_gap_binomial_check` | 1.99e-13 |
| `zone_boundaries_agree_with_probability_rule` | yes |
| `nu_raw_first_1000_days` | 2.07 |
| `nu_used` | 3 |

Acceptance checks computed by the notebook:

* `loops_match_library_1e-9`: passed
* `binomial_check_1e-9`: passed
* `zone_boundaries_agree_with_probability_rule`: passed
* `power_for_two_lengths_and_three_rates`: passed

Limitations recorded with the results:

* low power at 250 days
* 15 p values from one sample, no multiple testing correction
* synthetic data
<!-- results:end -->
