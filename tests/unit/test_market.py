import numpy as np
import pytest
from scipy import integrate
from scipy.stats import binom, norm, t

from risk_lab.market import backtest, es, var


def test_normal_var_known_value():
    assert var.normal_var(0.0, 0.01, 0.99) == pytest.approx(0.01 * 2.326347874, rel=1e-8)


def test_student_t_var_approaches_normal_for_large_nu():
    assert var.student_t_var(0, 0.01, 5000, 0.99) == pytest.approx(var.normal_var(0, 0.01, 0.99), rel=2e-3)


def test_student_t_var_is_larger_far_in_the_tail():
    assert var.student_t_var(0, 0.01, 4, 0.999) > var.normal_var(0, 0.01, 0.999)


def test_historical_var_matches_quantile_of_known_losses():
    returns = -np.arange(1, 101) / 100.0
    assert var.historical_var(returns, 0.95) == pytest.approx(np.quantile(np.arange(1, 101) / 100.0, 0.95))


def test_delta_normal_two_assets_hand_calculation():
    weights = [0.6, 0.4]
    covariance = np.array([[0.04, 0.006], [0.006, 0.01]])
    variance = 0.36 * 0.04 + 0.16 * 0.01 + 2 * 0.6 * 0.4 * 0.006
    expected = np.sqrt(variance) * norm.ppf(0.99)
    assert var.delta_normal_var(weights, [0, 0], covariance, 0.99) == pytest.approx(expected)


def test_t_simulation_has_requested_covariance():
    covariance = np.array([[0.0004, 0.0001], [0.0001, 0.0002]])
    draws = var.simulate_student_t_returns([0, 0], covariance, 8, 400000, seed=5)
    assert np.allclose(np.cov(draws.T), covariance, rtol=0.05)


def test_normal_es_matches_numeric_integration():
    alpha = 0.975
    quantile = norm.ppf(alpha)
    area, _ = integrate.quad(lambda z: z * norm.pdf(z), quantile, np.inf)
    assert es.normal_es(0, 1, alpha) == pytest.approx(area / (1 - alpha), rel=1e-8)


def test_student_t_es_matches_numeric_integration():
    nu, alpha = 6, 0.975
    quantile = t.ppf(alpha, nu)
    area, _ = integrate.quad(lambda x: x * t.pdf(x, nu), quantile, np.inf)
    scale = np.sqrt((nu - 2) / nu)
    assert es.student_t_es(0, 1, nu, alpha) == pytest.approx(scale * area / (1 - alpha), rel=1e-7)


def test_historical_es_is_at_least_var():
    rng = np.random.default_rng(6)
    returns = rng.standard_t(5, 3000) * 0.01
    assert es.historical_es(returns, 0.975) >= var.historical_var(returns, 0.975)


def test_historical_es_fractional_weight():
    # 40 losses, alpha 0.9 gives k = 4 exactly: mean of top four
    losses = np.arange(1, 41, dtype=float)
    assert es.historical_es(-losses, 0.9) == pytest.approx(np.mean([40, 39, 38, 37]))
    # alpha 0.95 gives k = 2
    assert es.historical_es(-losses, 0.95) == pytest.approx(39.5)
    # 30 losses at alpha 0.95 gives k = 1.5: (30 + 0.5 * 29) / 1.5
    losses = np.arange(1, 31, dtype=float)
    assert es.historical_es(-losses, 0.95) == pytest.approx((30 + 0.5 * 29) / 1.5)


def test_kupiec_hand_calculation():
    # n = 250, x = 5, p = 0.01
    n, x, p = 250, 5, 0.01
    hits = np.array([1] * x + [0] * (n - x))
    q = x / n
    expected = -2 * (
        (n - x) * np.log(1 - p) + x * np.log(p) - (n - x) * np.log(1 - q) - x * np.log(q)
    )
    result = backtest.kupiec_pof(hits, p)
    assert result["lr_pof"] == pytest.approx(expected, rel=1e-10)
    assert 0 < result["p_value"] < 1


def test_kupiec_zero_exceptions_is_finite():
    result = backtest.kupiec_pof(np.zeros(250, dtype=int), 0.01)
    assert np.isfinite(result["lr_pof"])
    assert result["lr_pof"] == pytest.approx(-2 * 250 * np.log(0.99))


def test_kupiec_perfect_rate_gives_zero():
    hits = np.zeros(200, dtype=int)
    hits[:2] = 1
    assert backtest.kupiec_pof(hits, 0.01)["lr_pof"] == pytest.approx(0.0, abs=1e-10)


def test_christoffersen_detects_clustering():
    clustered = np.zeros(1000, dtype=int)
    for start in range(50, 1000, 100):
        clustered[start : start + 3] = 1
    spread = np.zeros(1000, dtype=int)
    spread[::100] = 1
    assert backtest.christoffersen_independence(clustered)["p_value"] < 0.01
    assert backtest.christoffersen_independence(spread)["p_value"] > 0.5


def test_conditional_coverage_is_sum_of_parts():
    rng = np.random.default_rng(8)
    hits = (rng.uniform(size=800) < 0.02).astype(int)
    result = backtest.christoffersen_conditional_coverage(hits, 0.01)
    assert result["lr_cc"] == pytest.approx(result["lr_pof"] + result["lr_ind"])


def test_traffic_light_zones():
    assert backtest.basel_traffic_light(4)["zone"] == "green"
    assert backtest.basel_traffic_light(5)["zone"] == "yellow"
    assert backtest.basel_traffic_light(9)["zone"] == "yellow"
    assert backtest.basel_traffic_light(10)["zone"] == "red"
    assert backtest.basel_traffic_light(10)["add_on"] == 1.0


def test_probability_of_at_most_matches_binomial():
    assert backtest.probability_of_at_most(4) == pytest.approx(binom.cdf(4, 250, 0.01))


def test_exceptions_ignore_nan_days():
    returns = np.array([-0.05, -0.001, -0.03, 0.01])
    var_series = np.array([np.nan, 0.02, 0.02, 0.02])
    assert backtest.exceptions(returns, var_series).tolist() == [0, 1, 0]


def test_ewma_var_matches_manual_recursion():
    rng = np.random.default_rng(9)
    returns = rng.normal(0, 0.01, 200)
    series = var.ewma_var(returns, decay=0.94, alpha=0.99)
    sigma = var.ewma_volatility(returns, 0.94)
    assert series[100] == pytest.approx(sigma[100] * norm.ppf(0.99))
    assert np.isnan(series[0])


def test_ewma_es_matches_normal_es_for_unit_sigma():
    returns = np.random.default_rng(10).normal(0, 0.01, 100)
    sigma = var.ewma_volatility(returns, 0.94)
    series = es.ewma_es(returns, 0.94, 0.975)
    assert series[60] == pytest.approx(es.normal_es(0, sigma[60], 0.975))


def test_rolling_normal_var_uses_only_past_data():
    returns = np.random.default_rng(11).normal(0, 0.01, 700)
    series = var.rolling_normal_var(returns, 500, 0.99)
    assert np.isnan(series[499])
    sample = returns[0:500]
    assert series[500] == pytest.approx(var.normal_var(sample.mean(), sample.std(ddof=1), 0.99))
