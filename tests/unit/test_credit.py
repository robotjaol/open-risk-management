import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from risk_lab.credit import ecl, logistic, metrics, woe


def test_auc_matches_sklearn_with_ties():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 500)
    score = np.round(rng.normal(size=500) + y * 0.8, 1)
    assert metrics.roc_auc(y, score) == pytest.approx(roc_auc_score(y, score), abs=1e-12)


def test_gini_is_two_auc_minus_one():
    y = np.array([0, 0, 1, 1, 0, 1])
    score = np.array([0.1, 0.4, 0.35, 0.8, 0.2, 0.9])
    assert metrics.gini(y, score) == pytest.approx(2 * metrics.roc_auc(y, score) - 1)


def test_perfect_separation_gives_ks_one():
    y = np.array([0, 0, 0, 1, 1, 1])
    score = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    assert metrics.ks_statistic(y, score) == pytest.approx(1.0)


def test_brier_known_value():
    assert metrics.brier_score([1, 0], [0.8, 0.3]) == pytest.approx((0.04 + 0.09) / 2)


def test_psi_is_zero_for_same_sample_and_positive_for_shift():
    rng = np.random.default_rng(1)
    base = rng.normal(size=5000)
    assert metrics.population_stability_index(base, base) == pytest.approx(0.0, abs=1e-12)
    shifted = rng.normal(loc=0.5, size=5000)
    assert metrics.population_stability_index(base, shifted) > 0.1


def test_logistic_scratch_matches_sklearn_without_penalty():
    rng = np.random.default_rng(2)
    features = rng.normal(size=(4000, 3))
    true = np.array([0.8, -0.5, 0.3])
    probability = 1 / (1 + np.exp(-(-1.0 + features @ true)))
    target = (rng.uniform(size=4000) < probability).astype(int)

    mine = logistic.fit_logistic(features, target)
    reference = LogisticRegression(C=1e10, solver="lbfgs", max_iter=1000).fit(features, target)
    assert mine["intercept"] == pytest.approx(reference.intercept_[0], abs=1e-4)
    assert np.allclose(mine["slopes"], reference.coef_[0], atol=1e-4)


def test_standard_errors_are_positive():
    rng = np.random.default_rng(3)
    features = rng.normal(size=(1000, 2))
    target = (rng.uniform(size=1000) < 0.3).astype(int)
    fit = logistic.fit_logistic(features, target)
    errors = logistic.standard_errors(features, fit["intercept"], fit["slopes"])
    assert np.all(errors > 0)


def test_woe_sign_and_iv_of_uninformative_feature():
    rng = np.random.default_rng(4)
    x = rng.normal(size=20000)
    y = (rng.uniform(size=20000) < 0.1).astype(int)
    edges = woe.make_bin_edges(x, 5)
    table = woe.woe_table(x, y, edges)
    assert woe.information_value(table) < 0.01

    y_signal = (rng.uniform(size=20000) < 1 / (1 + np.exp(2 - 1.5 * x))).astype(int)
    table_signal = woe.woe_table(x, y_signal, edges)
    assert woe.information_value(table_signal) > 0.3
    # high x means more bads, so WoE falls
    assert table_signal["woe"].iloc[0] > table_signal["woe"].iloc[-1]


def test_score_scaling_doubles_odds_every_pdo():
    base = woe.probability_to_score(1 / 51, 600, 50, 20)
    plus_pdo = woe.probability_to_score(1 / 101, 600, 50, 20)
    assert float(base) == pytest.approx(600.0, abs=1e-6)
    assert float(plus_pdo) == pytest.approx(620.0, abs=1e-6)


def test_expected_loss_formula():
    assert ecl.expected_loss(0.02, 0.45, 100000) == pytest.approx(900.0)


def test_marginal_pd_sums_to_cumulative():
    marginal = ecl.marginal_pd(0.03, 5)
    assert marginal.sum() == pytest.approx(ecl.cumulative_pd(0.03, 5))


def test_stage_three_ecl_is_lgd_times_ead():
    assert ecl.loan_ecl(1.0, 0.4, 50000, 5, 0.08, stage=3) == pytest.approx(20000.0)


def test_stage_two_ecl_is_larger_than_stage_one():
    args = (0.04, 0.45, 100000, 6, 0.08)
    assert ecl.loan_ecl(*args, stage=2) > ecl.loan_ecl(*args, stage=1)


def test_stage_one_ecl_hand_calculation_bullet():
    # one year horizon: PD * LGD * EAD / (1 + EIR)^0.5
    value = ecl.loan_ecl(0.02, 0.5, 100000, 3, 0.10, stage=1, repayment="bullet")
    assert value == pytest.approx(0.02 * 0.5 * 100000 / 1.1**0.5, rel=1e-12)


def test_assign_stage_rules():
    stage = ecl.assign_stage(
        pd_origination=[0.02, 0.02, 0.02, 0.02],
        pd_current=[0.021, 0.08, 0.02, 0.5],
        days_past_due=[0, 0, 45, 120],
    )
    assert stage.tolist() == [1, 2, 2, 3]


def test_scenario_weights_must_sum_to_one():
    assert ecl.scenario_weighted([10, 20, 30], [0.5, 0.3, 0.2]) == pytest.approx(17.0)
    with pytest.raises(ValueError):
        ecl.scenario_weighted([1, 2], [0.5, 0.6])


def test_balance_profile_annuity_ends_near_zero():
    balances = ecl.balance_profile(100000, 5, 0.08, "annuity")
    payment = 100000 * 0.08 / (1 - 1.08**-5)
    last_after_payment = balances[-1] * 1.08 - payment
    assert last_after_payment == pytest.approx(0.0, abs=1e-6)
