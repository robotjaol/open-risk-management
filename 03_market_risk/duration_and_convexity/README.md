# Duration and Convexity

Price a fixed coupon bond, measure its rate sensitivity, and test when the approximation fails.

| Item | Value |
|---|---|
| Family | Fundamentals |
| Level | Beginner |
| Status | Validating |
| Dataset | `none (illustrative bonds defined in the notebook)` (illustrative), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`duration_and_convexity.ipynb`](duration_and_convexity.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/duration_and_convexity.json`](../../experiments/results/duration_and_convexity.json) |

## What you learn

- Bond price as a present value, and yield to maturity from a price
- Macaulay and modified duration, convexity and DV01
- Error of first and second order price estimates, with a stated tolerance
- Building and testing a DV01 hedge

## Run it

```bash
pip install -e ".[development]"
jupyter lab duration_and_convexity.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 03_market_risk/duration_and_convexity`.

## Saved results

<!-- results:start -->
Source: `experiments/results/duration_and_convexity.json`. Data kind: **illustrative**. Dataset: `none, bonds defined in the notebook`. Observations: 25. Seed: None. Created: 2026-11-25T05:52:58+00:00.

| Metric | Value |
|---|---|
| `reference_bond.face` | 100 |
| `reference_bond.coupon_rate` | 0.05 |
| `reference_bond.maturity_years` | 10 |
| `reference_bond.ytm` | 0.05 |
| `reference_bond.freq` | 2 |
| `price` | 100 |
| `macaulay_duration` | 7.989 |
| `modified_duration` | 7.795 |
| `convexity` | 73.63 |
| `dv01_per_100_face` | 0.07795 |
| `error_pct_plus_100bp.duration_only` | -0.3558 |
| `error_pct_plus_100bp.duration_plus_convexity` | 0.0123 |
| `error_pct_plus_300bp.duration_only` | -2.998 |
| `error_pct_plus_300bp.duration_plus_convexity` | 0.315 |
| `first_shock_above_tolerance_bp.duration_only` | 52 |
| `first_shock_above_tolerance_bp.duration_plus_convexity` | 196 |
| `tolerance_pct_of_price` | 0.1 |
| `par_bond_closed_form_check` | passed |
| `finite_difference_check_max_gap` | 6.567e-06 |
| `hedge_residual_pct_after_plus_50bp` | 0.3709 |
| `portfolio_dv01_currency` | 2083 |

Acceptance checks computed by the notebook:

* `par_bond_price_equals_100`: passed
* `par_bond_duration_matches_closed_form`: passed
* `loops_match_library`: passed
* `finite_difference_gap_below_1e-4`: passed
* `convexity_widens_safe_shock`: passed

Limitations recorded with the results:

* no curve shape changes
* no embedded options
* illustrative bonds only
<!-- results:end -->
