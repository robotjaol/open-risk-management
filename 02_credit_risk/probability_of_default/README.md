# Probability of Default with Logistic Regression

Estimate 12 month PD, measure ranking and calibration, and compare with the true generating process.

| Item | Value |
|---|---|
| Family | Credit Risk |
| Level | Beginner to Intermediate |
| Status | Complete |
| Dataset | `retail_loans_dev` (synthetic), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`probability_of_default.ipynb`](probability_of_default.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/probability_of_default.json`](../../experiments/results/probability_of_default.json) |

## What you learn

- Logistic regression likelihood, gradient and Newton Raphson
- Fit with NumPy, statsmodels and scikit-learn and reconcile them
- AUC, Gini, KS, Brier, log loss and calibration by decile
- Compare with the true generating model
- Effect of sample size and ridge penalty
- Risk grades and approval cutoffs

## Run it

```bash
pip install -e ".[development]"
jupyter lab probability_of_default.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 02_credit_risk/probability_of_default`.

## Saved results

<!-- results:start -->
Source: `experiments/results/probability_of_default.json`. Data kind: **synthetic**. Dataset: `datasets/synthetic/retail_loans_dev.csv`. Observations: 15000. Seed: 42. Created: 2026-11-25T10:35:47+00:00.

| Metric | Value |
|---|---|
| `test_auc.constant` | 0.5 |
| `test_auc.dti only` | 0.654 |
| `test_auc.model B (all numeric)` | 0.7848 |
| `test_auc.model A (7 drivers)` | 0.7855 |
| `test_auc.oracle (true PD)` | 0.7853 |
| `test_gini.constant` | 0 |
| `test_gini.dti only` | 0.308 |
| `test_gini.model B (all numeric)` | 0.5695 |
| `test_gini.model A (7 drivers)` | 0.571 |
| `test_gini.oracle (true PD)` | 0.5707 |
| `test_ks.constant` | 0 |
| `test_ks.dti only` | 0.2318 |
| `test_ks.model B (all numeric)` | 0.4683 |
| `test_ks.model A (7 drivers)` | 0.4725 |
| `test_ks.oracle (true PD)` | 0.4538 |
| `test_brier.constant` | 0.05836 |
| `test_brier.dti only` | 0.0573 |
| `test_brier.model B (all numeric)` | 0.05321 |
| `test_brier.model A (7 drivers)` | 0.05319 |
| `test_brier.oracle (true PD)` | 0.05297 |
| `observed_test_default_rate` | 0.06222 |
| `mean_predicted_pd_model_a` | 0.06318 |
| `mean_pd_gap_pct_of_observed` | 1.532 |
| `newton_iterations_model_a` | 8 |
| `coefficient_gap_vs_statsmodels` | 8.327e-17 |
| `slopes_within_1_96_se` | 7 |

Acceptance checks computed by the notebook:

* `auc_at_least_0.70`: passed
* `auc_within_0.02_of_oracle`: passed
* `mean_pd_within_10pct_of_observed`: passed

Limitations recorded with the results:

* the fitted model has the true functional form, so results are optimistic
* synthetic data, no real portfolio behaviour
* no out of time test in this module
<!-- results:end -->
