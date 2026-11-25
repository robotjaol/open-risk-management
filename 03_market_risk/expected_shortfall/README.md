# Expected Shortfall

Compute, verify and backtest ES, and see exactly where VaR fails subadditivity.

| Item | Value |
|---|---|
| Family | Market Risk |
| Level | Intermediate |
| Status | Complete |
| Dataset | `market_returns` (synthetic), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`expected_shortfall.ipynb`](expected_shortfall.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/expected_shortfall.json`](../../experiments/results/expected_shortfall.json) |

## What you learn

- ES as an average of VaR values, with fractional tail weight
- Rockafellar and Uryasev minimisation
- Closed forms checked by numerical integration
- Rolling ES and the Z1 backtest with a simulated p value
- Exact VaR subadditivity counterexample

## Run it

```bash
pip install -e ".[development]"
jupyter lab expected_shortfall.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 03_market_risk/expected_shortfall`.

## Saved results

<!-- results:start -->
Source: `experiments/results/expected_shortfall.json`. Data kind: **synthetic**. Dataset: `datasets/synthetic/market_returns.csv`. Observations: 3000. Seed: 42. Created: 2026-11-25T05:53:20+00:00.

| Metric | Value |
|---|---|
| `closed_form_vs_integral_max_gap` | 4.313e-09 |
| `t5_simulated_vs_closed_relative_gap` | 0.001795 |
| `normal_es975_over_var99` | 1.005 |
| `t5_es975_over_var99` | 1.047 |
| `historical_full_sample_pct.var_97_5` | 1.159 |
| `historical_full_sample_pct.es_97_5` | 1.521 |
| `historical_full_sample_pct.var_99` | 1.462 |
| `historical_full_sample_pct.es_99` | 1.835 |
| `z1_simulated_upper_p_value.ewma normal` | 0 |
| `z1_simulated_upper_p_value.ewma student t` | 0.996 |
| `nu_raw_first_1000_days` | 2.07 |
| `nu_used` | 3 |

Acceptance checks computed by the notebook:

* `hand_equals_library`: passed
* `ru_minimum_equals_es`: passed
* `closed_form_equals_integral`: passed
* `simulated_t_within_1pct`: passed
* `var_violates_and_es_satisfies_subadditivity`: passed

Limitations recorded with the results:

* synthetic returns, t model matched to the generator by construction
* ES backtest has low power with about 50 exceedances
* iid bootstrap
<!-- results:end -->
