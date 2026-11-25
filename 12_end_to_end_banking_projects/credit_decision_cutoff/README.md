# Practical Method: From a Default Model to an Approval Cut Off

A default model on 1000 real loan applicants, turned into a cost based cut off with a measured reduction in expected cost.

| Item | Value |
|---|---|
| Family | End to End Banking Projects |
| Level | Applied |
| Status | Validating |
| Dataset | `german_credit` (empirical), see [`datasets/README.md`](../../datasets/README.md) |
| Notebook | [`credit_decision_cutoff.ipynb`](credit_decision_cutoff.ipynb) |
| Bibliography | [`references.md`](references.md) |
| Saved results | [`experiments/results/credit_decision_cutoff.json`](../../experiments/results/credit_decision_cutoff.json) |

## What you learn

- Split, fit and evaluate a default model on real applicant data without leakage
- Derive a cut off from the cost of each error and verify it numerically
- Measure the cost reduction against simple policies with an interval
- See how a different portfolio bad rate changes the decision
- Handle protected attributes openly

## Run it

```bash
pip install -e ".[development]"
jupyter lab credit_decision_cutoff.ipynb
```

To rebuild and execute from a clean kernel: `python tools/build_modules.py` then `python tools/run_notebooks.py 12_end_to_end_banking_projects/credit_decision_cutoff`.

## Saved results

<!-- results:start -->
Source: `experiments/results/credit_decision_cutoff.json`. Data kind: **empirical**. Dataset: `datasets/raw/german_credit.csv`. Observations: 1000. Seed: 42. Created: 2026-11-25T10:36:24+00:00.

| Metric | Value |
|---|---|
| `test_evaluation.auc` | 0.7961 |
| `test_evaluation.ks` | 0.4889 |
| `test_evaluation.brier` | 0.16 |
| `test_evaluation.brier_constant` | 0.21 |
| `policy_cost_per_applicant.approve all` | 1.5 |
| `policy_cost_per_applicant.refuse all` | 0.7 |
| `policy_cost_per_applicant.model, cut off 1/6` | 0.5233 |
| `approve_share_at_cutoff` | 0.3767 |
| `bayes_cutoff` | 0.1667 |
| `cutoff_chosen_by_cross_validation` | 0.15 |
| `repeated_splits.n` | 100 |
| `repeated_splits.auc_mean` | 0.7758 |
| `repeated_splits.auc_std` | 0.02417 |
| `repeated_splits.share_model_beats_refuse_all` | 0.99 |
| `repeated_splits.share_model_beats_approve_all` | 1 |
| `repeated_splits.model_cost_mean` | 0.5556 |
| `repeated_splits.refuse_all_cost_mean` | 0.7 |
| `repeated_splits.approve_all_cost_mean` | 1.5 |
| `protected_attributes_effect.auc_with` | 0.7939 |
| `protected_attributes_effect.auc_without` | 0.7961 |
| `protected_attributes_effect.cost_with` | 0.5333 |
| `protected_attributes_effect.cost_without` | 0.5233 |
| `newton_iterations` | 7 |
| `test_auc_scikit_learn` | 0.796 |

Acceptance checks computed by the notebook:

* `scratch_and_sklearn_auc_within_0.01`: passed
* `split_disjoint_and_stratified`: passed
* `derived_cutoff_equals_numerical_minimiser`: passed
* `test_auc_at_least_0.70`: passed
* `model_cost_below_approve_all_with_interval_excluding_zero`: passed
* `no_protected_columns_in_final_model`: passed

Limitations recorded with the results:

* 1000 applicants from one old source, 300 in the test set, so intervals are wide
* costs count only two errors, not profit on good loans
* no reject inference, so performance on refused applicants is unknown
* age is kept as a feature, which some regulations do not allow
* no out of time test, the data has no dates
<!-- results:end -->
