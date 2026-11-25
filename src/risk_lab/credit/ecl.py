"""Expected credit loss building blocks (IFRS 9 style, simplified).

Every parameter here is a modelling assumption of this laboratory.
IFRS 9 sets principles, not these exact thresholds or formulas.
"""

import numpy as np


def expected_loss(pd_value, lgd, ead):
    """One period expected loss: PD * LGD * EAD."""
    return pd_value * lgd * ead


def cumulative_pd(pd_12m, years):
    """Cumulative default probability under a constant annual hazard."""
    return 1 - (1 - pd_12m) ** years


def marginal_pd(pd_12m, horizon_years):
    """Default probability inside each year, for years 1 to horizon."""
    years = np.arange(1, horizon_years + 1)
    cumulative = cumulative_pd(pd_12m, years)
    previous = np.concatenate([[0.0], cumulative[:-1]])
    return cumulative - previous


def balance_profile(ead, term_years, eir, repayment="annuity"):
    """Balance at the start of each year for years 1 to term.

    annuity: equal yearly payments. bullet: balance stays flat.
    """
    balances = np.zeros(term_years)
    balance = ead
    if repayment == "annuity" and eir > 0:
        payment = ead * eir / (1 - (1 + eir) ** (-term_years))
    elif repayment == "annuity":
        payment = ead / term_years
    else:
        payment = 0.0
    for year in range(term_years):
        balances[year] = balance
        if repayment == "annuity":
            balance = balance * (1 + eir) - payment
    return balances


def loan_ecl(pd_12m, lgd, ead, term_years, eir, stage, repayment="annuity"):
    """ECL for one loan.

    Stage 1 uses a 12 month horizon. Stage 2 uses the remaining life.
    Stage 3 is already in default, so PD is 1 and ECL is LGD * EAD.
    Defaults are assumed to happen in the middle of each year.
    """
    if stage == 3:
        return float(lgd * ead)
    horizon = 1 if stage == 1 else term_years
    horizon = max(1, min(horizon, term_years))
    pds = marginal_pd(pd_12m, horizon)
    balances = balance_profile(ead, term_years, eir, repayment)[:horizon]
    years = np.arange(1, horizon + 1)
    discount = (1 + eir) ** (-(years - 0.5))
    return float(np.sum(pds * lgd * balances * discount))


def assign_stage(
    pd_origination,
    pd_current,
    days_past_due,
    relative_threshold=2.0,
    absolute_threshold=0.01,
    dpd_stage2=30,
    dpd_stage3=90,
):
    """Stage allocation with a simple significant increase in credit risk test.

    Stage 3: days past due at or above dpd_stage3.
    Stage 2: days past due at or above dpd_stage2, or the PD rose by both
    the relative and the absolute threshold.
    Stage 1: everything else.
    """
    pd_origination = np.asarray(pd_origination, dtype=float)
    pd_current = np.asarray(pd_current, dtype=float)
    days_past_due = np.asarray(days_past_due)

    ratio_trigger = pd_current >= relative_threshold * pd_origination
    gap_trigger = (pd_current - pd_origination) >= absolute_threshold
    sicr = (ratio_trigger & gap_trigger) | (days_past_due >= dpd_stage2)

    stage = np.ones(len(pd_current), dtype=int)
    stage[sicr] = 2
    stage[days_past_due >= dpd_stage3] = 3
    return stage


def scenario_weighted(values_by_scenario, weights):
    """Probability weighted average across macro scenarios."""
    weights = np.asarray(weights, dtype=float)
    if abs(weights.sum() - 1.0) > 1e-9:
        raise ValueError("scenario weights must sum to 1")
    values = np.asarray(values_by_scenario, dtype=float)
    return float(np.sum(values * weights))
