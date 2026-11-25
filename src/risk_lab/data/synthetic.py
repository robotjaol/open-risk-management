"""Synthetic banking datasets with documented generating processes.

Everything here is made up. No row describes a real customer or a real
market. The true parameters are stored so a learner can check how close
an estimate gets to the truth, which is not possible with real data.
"""

import numpy as np
import pandas as pd

# true default process
RETAIL_TRUE_INTERCEPT = -3.1
RETAIL_TRUE_SLOPES = {
    "dti_z": 0.55,
    "utilization_z": 0.40,
    "ltv_z": 0.30,
    "log_income_z": -0.45,
    "credit_history_years_z": -0.25,
    "delinq_2y_z": 0.50,
    "interest_rate_z": 0.20,
}

MARKET_ASSETS = ["equity", "fx", "bond"]
MARKET_PARAMS = {
    "equity": {"long_run_vol": 0.011, "alpha": 0.07, "beta": 0.90, "nu": 6.0, "mean": 0.0004},
    "fx": {"long_run_vol": 0.006, "alpha": 0.05, "beta": 0.91, "nu": 8.0, "mean": 0.0},
    "bond": {"long_run_vol": 0.004, "alpha": 0.05, "beta": 0.91, "nu": 8.0, "mean": 0.0001},
}
MARKET_CORRELATION = [
    [1.0, -0.20, -0.30],
    [-0.20, 1.0, 0.10],
    [-0.30, 0.10, 1.0],
]


# fixed reference scales
REFERENCE_SCALES = {
    "dti": (0.286, 0.15),
    "utilization": (0.385, 0.2),
    "ltv": (0.72, 0.18),
    "log_income": (10.6, 0.55),
    "credit_history_years": (10.5, 6.0),
    "delinq_2y": (0.25, 0.5),
    "interest_rate": (0.095, 0.04),
}


def standardise_features(frame):
    """The seven features that drive default, on the generator's own scale."""
    data = frame.copy()
    data["log_income"] = np.log(data["income"])
    out = {}
    for name, (mean, std) in REFERENCE_SCALES.items():
        out[name + "_z"] = (data[name] - mean) / std
    return pd.DataFrame(out)


def true_default_probability(frame):
    """The exact default probability used by the generator."""
    z = standardise_features(frame)
    logit = RETAIL_TRUE_INTERCEPT
    for name, slope in RETAIL_TRUE_SLOPES.items():
        logit = logit + slope * z[name]
    return 1 / (1 + np.exp(-logit))


def make_retail_loans(n_loans=15000, seed=42, drift=0.0):
    """Retail loans at origination with a 12 month default flag.

    drift shifts the borrower mix toward riskier profiles. Use 0 for the
    development sample and a positive value for a later monitoring sample.
    """
    rng = np.random.default_rng(seed)

    age = rng.integers(21, 70, size=n_loans)
    log_income = rng.normal(10.6 - 0.25 * drift, 0.55, size=n_loans)
    income = np.exp(log_income)
    employment_years = np.clip(rng.gamma(2.5, 3.0, size=n_loans), 0, age - 18)
    credit_history_years = np.clip(rng.gamma(3.0, 3.5, size=n_loans), 0.5, age - 18)
    dti = np.clip(rng.beta(2.2, 5.5, size=n_loans) + 0.06 * drift, 0.01, 0.95)
    utilization = np.clip(rng.beta(2.0, 3.2, size=n_loans) + 0.05 * drift, 0.0, 1.0)
    ltv = np.clip(rng.normal(0.72 + 0.04 * drift, 0.18, size=n_loans), 0.1, 1.2)
    delinq_2y = rng.poisson(0.25 + 0.15 * drift, size=n_loans)
    term_months = rng.choice([12, 24, 36, 48, 60], size=n_loans, p=[0.1, 0.2, 0.3, 0.2, 0.2])
    loan_amount = np.round(np.exp(rng.normal(9.3, 0.6, size=n_loans)), -1)
    interest_rate = np.clip(0.045 + 0.09 * dti + 0.02 * delinq_2y + rng.normal(0, 0.012, n_loans), 0.02, 0.35)
    region = rng.choice(["north", "south", "east", "west"], size=n_loans, p=[0.3, 0.25, 0.25, 0.2])

    frame = pd.DataFrame(
        {
            "loan_id": np.arange(1, n_loans + 1),
            "age": age,
            "income": np.round(income, 0),
            "employment_years": np.round(employment_years, 1),
            "credit_history_years": np.round(credit_history_years, 1),
            "dti": np.round(dti, 4),
            "utilization": np.round(utilization, 4),
            "ltv": np.round(ltv, 4),
            "delinq_2y": delinq_2y,
            "loan_amount": loan_amount,
            "term_months": term_months,
            "interest_rate": np.round(interest_rate, 4),
            "region": region,
        }
    )

    true_probability = true_default_probability(frame)
    frame["default_12m"] = (rng.uniform(size=n_loans) < true_probability).astype(int)
    return frame


def make_loan_book(n_loans=5000, seed=7):
    """A mixed loan book for impairment (ECL) exercises.

    Columns hold balances, rates, PDs at origination and today, days past
    due and an LGD. A share of loans is deliberately deteriorated.
    """
    rng = np.random.default_rng(seed)
    segment = rng.choice(["retail", "sme", "mortgage"], size=n_loans, p=[0.5, 0.3, 0.2])
    base_pd = {"retail": 0.03, "sme": 0.045, "mortgage": 0.01}
    base_lgd = {"retail": 0.55, "sme": 0.45, "mortgage": 0.20}
    base_term = {"retail": (1, 6), "sme": (2, 9), "mortgage": (8, 25)}
    base_eir = {"retail": 0.11, "sme": 0.085, "mortgage": 0.055}

    pd_origination = np.array([base_pd[s] for s in segment]) * rng.lognormal(0, 0.45, n_loans)
    pd_origination = np.clip(pd_origination, 0.002, 0.35)

    deterioration = rng.lognormal(0.05, 0.55, n_loans)
    shock = rng.uniform(size=n_loans) < 0.12
    deterioration = np.where(shock, deterioration * rng.uniform(2.0, 6.0, n_loans), deterioration)
    pd_current = np.clip(pd_origination * deterioration, 0.002, 0.95)

    dpd = np.zeros(n_loans, dtype=int)
    late = rng.uniform(size=n_loans) < (0.04 + 0.5 * np.clip(pd_current - 0.05, 0, 0.5))
    dpd[late] = rng.choice([5, 15, 35, 45, 65, 95, 120, 180], size=late.sum(), p=[0.15, 0.15, 0.2, 0.15, 0.1, 0.1, 0.1, 0.05])

    low = np.array([base_term[s][0] for s in segment])
    high = np.array([base_term[s][1] for s in segment])
    remaining_years = rng.integers(low, high + 1)
    eir = np.array([base_eir[s] for s in segment]) + rng.normal(0, 0.01, n_loans)
    ead = np.round(np.exp(rng.normal(10.0, 0.9, n_loans)), -1)
    lgd = np.clip(np.array([base_lgd[s] for s in segment]) + rng.normal(0, 0.07, n_loans), 0.05, 0.95)

    return pd.DataFrame(
        {
            "loan_id": np.arange(1, n_loans + 1),
            "segment": segment,
            "ead": ead,
            "remaining_years": remaining_years,
            "eir": np.round(eir, 4),
            "pd_origination": np.round(pd_origination, 5),
            "pd_current": np.round(pd_current, 5),
            "days_past_due": dpd,
            "lgd": np.round(lgd, 4),
        }
    )


def make_market_returns(n_days=3000, seed=14, start="2012-01-02"):
    """Daily returns for three assets from GARCH(1,1) with Student t shocks.

    A volatility burst is added around day 2200 so tail behaviour can be
    studied. Correlation between shocks is constant.
    """
    rng = np.random.default_rng(seed)
    chol = np.linalg.cholesky(np.array(MARKET_CORRELATION))
    n_assets = len(MARKET_ASSETS)

    shocks = np.zeros((n_days, n_assets))
    for index, name in enumerate(MARKET_ASSETS):
        nu = MARKET_PARAMS[name]["nu"]
        raw = rng.standard_t(nu, size=n_days) * np.sqrt((nu - 2) / nu)
        shocks[:, index] = raw
    # apply correlation
    shocks = shocks @ chol.T

    returns = np.zeros((n_days, n_assets))
    for index, name in enumerate(MARKET_ASSETS):
        params = MARKET_PARAMS[name]
        long_run_var = params["long_run_vol"] ** 2
        omega = long_run_var * (1 - params["alpha"] - params["beta"])
        variance = long_run_var
        for day in range(n_days):
            burst = 2.2 if 2200 <= day < 2260 else 1.0
            base_sigma = np.sqrt(variance)
            returns[day, index] = params["mean"] + base_sigma * burst * shocks[day, index]
            # burst is not fed back
            epsilon = base_sigma * shocks[day, index]
            variance = omega + params["alpha"] * epsilon**2 + params["beta"] * variance

    dates = pd.bdate_range(start=start, periods=n_days)
    frame = pd.DataFrame(np.round(returns, 6), columns=[f"r_{n}" for n in MARKET_ASSETS])
    frame.insert(0, "date", dates.strftime("%Y-%m-%d"))
    return frame
