"""Expected Shortfall estimators.

ES at level alpha is the average loss in the worst (1 - alpha) share of
outcomes. Reported as a positive loss fraction.
"""

import numpy as np
from scipy.stats import norm, t


def historical_es(returns, alpha=0.975):
    """Tail average using the Acerbi and Tasche integral form.

    Takes the worst k = (1 - alpha) * n losses, with a fractional weight
    on the last one when k is not a whole number.
    """
    losses = np.sort(-np.asarray(returns, dtype=float))[::-1]
    k = (1 - alpha) * len(losses)
    whole = int(np.floor(k))
    total = losses[:whole].sum()
    if whole < len(losses):
        total += (k - whole) * losses[whole]
    return float(total / k)


def tail_mean_above_var(returns, alpha=0.975):
    """Plain average of losses at or beyond the VaR. Simpler, slightly different."""
    losses = -np.asarray(returns, dtype=float)
    var_value = np.quantile(losses, alpha)
    return float(losses[losses >= var_value].mean())


def normal_es(mean, sigma, alpha=0.975):
    """Closed form ES for normal returns."""
    z = norm.ppf(alpha)
    return float(-mean + sigma * norm.pdf(z) / (1 - alpha))


def student_t_es(mean, sigma, nu, alpha=0.975):
    """Closed form ES for Student t returns with standard deviation sigma."""
    scale = sigma * np.sqrt((nu - 2) / nu)
    q = t.ppf(alpha, nu)
    tail = t.pdf(q, nu) * (nu + q**2) / ((nu - 1) * (1 - alpha))
    return float(-mean + scale * tail)


def rolling_historical_es(returns, window=500, alpha=0.975):
    """One day ahead ES for each day after the first full window."""
    returns = np.asarray(returns, dtype=float)
    out = np.full(len(returns), np.nan)
    for index in range(window, len(returns)):
        out[index] = historical_es(returns[index - window : index], alpha)
    return out


def exceedance_z1(returns, var_series, es_series):
    """Acerbi and Szekely style Z1 diagnostic.

    Average of loss / ES on the days when the loss beat the VaR, minus 1.
    Near 0 is consistent. Clearly above 0 means ES was too low.
    Returns NaN when there are no exceedances.
    """
    losses = -np.asarray(returns, dtype=float)
    var_series = np.asarray(var_series, dtype=float)
    es_series = np.asarray(es_series, dtype=float)
    valid = ~np.isnan(var_series) & ~np.isnan(es_series)
    hit = valid & (losses > var_series)
    if hit.sum() == 0:
        return float("nan")
    return float(np.mean(losses[hit] / es_series[hit]) - 1)


def ewma_es(returns, decay=0.94, alpha=0.975, nu=None, warmup=30):
    """One day ahead ES from EWMA volatility with zero mean."""
    from risk_lab.market.var import ewma_volatility

    returns = np.asarray(returns, dtype=float)
    sigma = ewma_volatility(returns, decay)
    if nu is None:
        multiplier = norm.pdf(norm.ppf(alpha)) / (1 - alpha)
    else:
        q = t.ppf(alpha, nu)
        multiplier = np.sqrt((nu - 2) / nu) * t.pdf(q, nu) * (nu + q**2) / ((nu - 1) * (1 - alpha))
    out = sigma * multiplier
    out[:warmup] = np.nan
    return out
