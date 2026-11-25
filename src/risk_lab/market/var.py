"""Value at Risk estimators.

Convention: returns are simple returns (0.01 is a 1 percent gain).
VaR and ES are reported as positive loss fractions of portfolio value.
alpha is the confidence level, for example 0.99.
"""

import numpy as np
from scipy.stats import norm, t


def historical_var(returns, alpha=0.99):
    """Empirical quantile of losses."""
    losses = -np.asarray(returns, dtype=float)
    return float(np.quantile(losses, alpha))


def normal_var(mean, sigma, alpha=0.99):
    """Parametric VaR with normal returns."""
    return float(-mean + sigma * norm.ppf(alpha))


def student_t_var(mean, sigma, nu, alpha=0.99):
    """Parametric VaR with Student t returns.

    sigma is the standard deviation of returns, so the t scale is
    sigma * sqrt((nu - 2) / nu). Needs nu > 2.
    """
    scale = sigma * np.sqrt((nu - 2) / nu)
    return float(-mean + scale * t.ppf(alpha, nu))


def portfolio_moments(weights, mean_returns, covariance):
    """Mean and standard deviation of a weighted portfolio."""
    weights = np.asarray(weights, dtype=float)
    mean = float(weights @ np.asarray(mean_returns))
    variance = float(weights @ np.asarray(covariance) @ weights)
    return mean, float(np.sqrt(variance))


def delta_normal_var(weights, mean_returns, covariance, alpha=0.99, portfolio_value=1.0):
    """Variance covariance VaR for a linear portfolio, in currency."""
    mean, sigma = portfolio_moments(weights, mean_returns, covariance)
    return portfolio_value * normal_var(mean, sigma, alpha)


def ewma_volatility(returns, decay=0.94):
    """Exponentially weighted volatility. Entry t uses data up to t - 1."""
    returns = np.asarray(returns, dtype=float)
    variance = np.empty(len(returns))
    variance[0] = returns[:30].var()
    for index in range(1, len(returns)):
        variance[index] = decay * variance[index - 1] + (1 - decay) * returns[index - 1] ** 2
    return np.sqrt(variance)


def simulate_normal_returns(mean, covariance, n_scenarios, seed=0):
    """Monte Carlo scenarios from a multivariate normal."""
    rng = np.random.default_rng(seed)
    return rng.multivariate_normal(mean, covariance, size=n_scenarios)


def simulate_student_t_returns(mean, covariance, nu, n_scenarios, seed=0):
    """Monte Carlo scenarios from a multivariate Student t.

    covariance is the covariance of returns, so it is rescaled.
    """
    rng = np.random.default_rng(seed)
    mean = np.asarray(mean, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    shape = covariance * (nu - 2) / nu
    normal_part = rng.multivariate_normal(np.zeros(len(mean)), shape, size=n_scenarios)
    chi_part = rng.chisquare(nu, size=n_scenarios) / nu
    return mean + normal_part / np.sqrt(chi_part)[:, None]


def rolling_historical_var(returns, window=500, alpha=0.99):
    """One day ahead VaR for each day after the first full window.

    The result has the same length as returns. Early days are NaN.
    """
    returns = np.asarray(returns, dtype=float)
    out = np.full(len(returns), np.nan)
    for index in range(window, len(returns)):
        out[index] = historical_var(returns[index - window : index], alpha)
    return out


def rolling_normal_var(returns, window=500, alpha=0.99):
    """One day ahead normal VaR from the sample mean and volatility of the window."""
    returns = np.asarray(returns, dtype=float)
    out = np.full(len(returns), np.nan)
    for index in range(window, len(returns)):
        sample = returns[index - window : index]
        out[index] = normal_var(sample.mean(), sample.std(ddof=1), alpha)
    return out


def ewma_var(returns, decay=0.94, alpha=0.99, nu=None, warmup=30):
    """One day ahead VaR from EWMA volatility with zero mean.

    nu=None uses the normal. A number uses a Student t with that many
    degrees of freedom. The first warmup days are NaN.
    """
    returns = np.asarray(returns, dtype=float)
    sigma = ewma_volatility(returns, decay)
    if nu is None:
        multiplier = norm.ppf(alpha)
    else:
        multiplier = t.ppf(alpha, nu) * np.sqrt((nu - 2) / nu)
    out = sigma * multiplier
    out[:warmup] = np.nan
    return out
