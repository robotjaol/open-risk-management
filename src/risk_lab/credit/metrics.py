"""Scorecard and probability of default evaluation metrics.

Convention: y is 1 for a bad (default) and 0 for a good. A higher score
or probability means a higher chance of default, unless stated.
"""

import numpy as np
from scipy.stats import rankdata


def roc_auc(y_true, risk_score):
    """Area under the ROC curve through the rank sum formula."""
    y_true = np.asarray(y_true)
    ranks = rankdata(risk_score)
    n_bad = int(y_true.sum())
    n_good = len(y_true) - n_bad
    rank_sum_bad = ranks[y_true == 1].sum()
    return float((rank_sum_bad - n_bad * (n_bad + 1) / 2) / (n_bad * n_good))


def gini(y_true, risk_score):
    """Gini coefficient, equal to 2 * AUC - 1."""
    return 2 * roc_auc(y_true, risk_score) - 1


def ks_statistic(y_true, risk_score):
    """Largest gap between the cumulative bad and good distributions."""
    y_true = np.asarray(y_true)
    order = np.argsort(-np.asarray(risk_score), kind="mergesort")
    sorted_y = y_true[order]
    cum_bad = np.cumsum(sorted_y) / sorted_y.sum()
    cum_good = np.cumsum(1 - sorted_y) / (1 - sorted_y).sum()
    return float(np.max(np.abs(cum_bad - cum_good)))


def brier_score(y_true, probability):
    """Mean squared error of the predicted probability."""
    y_true = np.asarray(y_true, dtype=float)
    return float(np.mean((np.asarray(probability) - y_true) ** 2))


def log_loss(y_true, probability, eps=1e-12):
    """Average negative log likelihood."""
    y_true = np.asarray(y_true, dtype=float)
    p = np.clip(np.asarray(probability), eps, 1 - eps)
    return float(-np.mean(y_true * np.log(p) + (1 - y_true) * np.log(1 - p)))


def calibration_table(y_true, probability, n_bins=10):
    """Mean predicted and observed default rate by probability decile."""
    y_true = np.asarray(y_true, dtype=float)
    probability = np.asarray(probability)
    edges = np.quantile(probability, np.linspace(0, 1, n_bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    edges = np.unique(edges)
    bins = np.digitize(probability, edges[1:-1])
    rows = []
    for index in range(len(edges) - 1):
        mask = bins == index
        if mask.sum() == 0:
            continue
        rows.append(
            {
                "bin": index + 1,
                "count": int(mask.sum()),
                "mean_predicted": float(probability[mask].mean()),
                "observed_rate": float(y_true[mask].mean()),
            }
        )
    return rows


def population_stability_index(expected, actual, n_bins=10, eps=1e-4):
    """PSI between a reference sample and a new sample.

    Bin edges come from the reference sample deciles.
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    edges = np.quantile(expected, np.linspace(0, 1, n_bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    edges = np.unique(edges)
    expected_share = np.histogram(expected, bins=edges)[0] / len(expected)
    actual_share = np.histogram(actual, bins=edges)[0] / len(actual)
    expected_share = np.clip(expected_share, eps, None)
    actual_share = np.clip(actual_share, eps, None)
    return float(np.sum((actual_share - expected_share) * np.log(actual_share / expected_share)))
