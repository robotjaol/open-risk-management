"""VaR backtests: Kupiec, Christoffersen and the Basel traffic light."""

import numpy as np
from scipy.special import xlogy
from scipy.stats import binom, chi2


def exceptions(returns, var_series):
    """1 on days when the loss was larger than the VaR. NaN VaR days are dropped."""
    losses = -np.asarray(returns, dtype=float)
    var_series = np.asarray(var_series, dtype=float)
    valid = ~np.isnan(var_series)
    return (losses[valid] > var_series[valid]).astype(int)


def _binomial_loglik(count, total, probability):
    """log of p^count * (1 - p)^(total - count), safe at zero."""
    return xlogy(count, probability) + xlogy(total - count, 1 - probability)


def kupiec_pof(hits, expected_rate):
    """Kupiec proportion of failures test (unconditional coverage).

    expected_rate is 1 - alpha, for example 0.01 for a 99 percent VaR.
    """
    hits = np.asarray(hits)
    total = len(hits)
    count = int(hits.sum())
    observed_rate = count / total
    log_null = _binomial_loglik(count, total, expected_rate)
    log_alt = _binomial_loglik(count, total, observed_rate)
    statistic = float(-2 * (log_null - log_alt))
    statistic = max(statistic, 0.0)
    return {
        "n_obs": total,
        "exceptions": count,
        "expected_exceptions": total * expected_rate,
        "observed_rate": observed_rate,
        "lr_pof": statistic,
        "p_value": float(chi2.sf(statistic, 1)),
    }


def christoffersen_independence(hits):
    """Christoffersen test that exceptions do not cluster."""
    hits = np.asarray(hits)
    previous, current = hits[:-1], hits[1:]
    n00 = int(np.sum((previous == 0) & (current == 0)))
    n01 = int(np.sum((previous == 0) & (current == 1)))
    n10 = int(np.sum((previous == 1) & (current == 0)))
    n11 = int(np.sum((previous == 1) & (current == 1)))

    pi01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0.0
    pi11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0.0
    pi_all = (n01 + n11) / (n00 + n01 + n10 + n11)

    log_null = _binomial_loglik(n01 + n11, n00 + n01 + n10 + n11, pi_all)
    log_alt = _binomial_loglik(n01, n00 + n01, pi01) + _binomial_loglik(n11, n10 + n11, pi11)
    statistic = max(float(-2 * (log_null - log_alt)), 0.0)
    return {
        "n00": n00,
        "n01": n01,
        "n10": n10,
        "n11": n11,
        "lr_ind": statistic,
        "p_value": float(chi2.sf(statistic, 1)),
    }


def christoffersen_conditional_coverage(hits, expected_rate):
    """Joint test of coverage and independence (two degrees of freedom)."""
    pof = kupiec_pof(hits, expected_rate)
    ind = christoffersen_independence(hits)
    statistic = pof["lr_pof"] + ind["lr_ind"]
    return {
        "lr_cc": float(statistic),
        "p_value": float(chi2.sf(statistic, 2)),
        "lr_pof": pof["lr_pof"],
        "lr_ind": ind["lr_ind"],
    }


def basel_traffic_light(exception_count):
    """Zone for 250 days of a 99 percent VaR, with the capital multiplier add on.

    Zone limits and add on values follow the published Basel backtesting
    framework. Check them against the current text before real use.
    """
    add_on = {5: 0.40, 6: 0.50, 7: 0.65, 8: 0.75, 9: 0.85}
    if exception_count <= 4:
        return {"zone": "green", "add_on": 0.0}
    if exception_count <= 9:
        return {"zone": "yellow", "add_on": add_on[int(exception_count)]}
    return {"zone": "red", "add_on": 1.0}


def probability_of_at_most(count, total=250, expected_rate=0.01):
    """Chance of seeing count or fewer exceptions if the model is right."""
    return float(binom.cdf(count, total, expected_rate))
