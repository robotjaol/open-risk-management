# Credit Scoring with Weight of Evidence

Build a points scorecard from WoE bins, prove the points match the model, and test it under drift.

| Item | Value |
|---|---|
| Family | Credit Risk |
| Level | Intermediate |
| Status | Validating |
| Dataset | `retail_loans_dev and retail_loans_monitoring` (synthetic), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`credit_scoring.ipynb`](credit_scoring.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/credit_scoring.json`](../../experiments/results/credit_scoring.json) |

## What you learn

- WoE, IV and bin monotonicity
- Logistic regression on WoE and the points formula
- Prove that integer points reproduce the model score
- AUC, Gini, KS and calibration on test and drifted data
- PSI as a drift signal and its limits
- Intercept recalibration and what it cannot fix

## Run it

```bash
pip install -e ".[development]"
jupyter lab credit_scoring.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 02_credit_risk/credit_scoring`.

## Saved results

<!-- results:start -->
Source: `experiments/results/credit_scoring.json`. Data kind: **synthetic**. Dataset: `datasets/synthetic/retail_loans_dev.csv and retail_loans_monitoring.csv`. Observations: 21000. Seed: 42. Created: 2026-11-25T05:24:18+00:00.

| Metric | Value |
|---|---|
| `scaling.factor` | 28.85 |
| `scaling.offset` | 487.1 |
| `scaling.base_score` | 600 |
| `scaling.base_odds_good_to_bad` | 50 |
| `scaling.pdo` | 20 |
| `raw_logistic_test_auc` | 0.7805 |
| `score_psi_train_vs_test` | 0.002641 |
| `score_psi_train_vs_monitoring` | 0.3481 |
| `max_gap_integer_points` | 3.061 |

Acceptance checks computed by the notebook:

* `auc_within_0.01_of_raw_logistic`: **not met**
* `integer_points_within_rounding_bound`: passed
* `psi_reported`: passed

Limitations recorded with the results:

* synthetic data
* covariate shift only, no concept drift
* no reject inference, no segmentation
<!-- results:end -->
