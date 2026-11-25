"""Fixed coupon bond mathematics.

All rates are decimals (0.05 means 5 percent). Time is in years.
Compounding follows the coupon frequency, so a yield of 0.05 with
freq=2 means 5 percent per year, compounded twice a year.
"""

import numpy as np
from scipy.optimize import brentq


def bond_cashflows(face, coupon_rate, maturity_years, freq=2):
    """Return payment times (years) and payment amounts."""
    periods = int(round(maturity_years * freq))
    coupon = face * coupon_rate / freq
    times = np.arange(1, periods + 1) / freq
    cashflows = np.full(periods, coupon, dtype=float)
    cashflows[-1] += face
    return times, cashflows


def bond_price(ytm, face, coupon_rate, maturity_years, freq=2):
    """Price as the present value of all cash flows."""
    times, cashflows = bond_cashflows(face, coupon_rate, maturity_years, freq)
    periods = times * freq
    discount = (1 + ytm / freq) ** periods
    return float(np.sum(cashflows / discount))


def macaulay_duration(ytm, face, coupon_rate, maturity_years, freq=2):
    """Weighted average time of cash flows, in years."""
    times, cashflows = bond_cashflows(face, coupon_rate, maturity_years, freq)
    periods = times * freq
    present_values = cashflows / (1 + ytm / freq) ** periods
    price = present_values.sum()
    return float(np.sum(times * present_values) / price)


def modified_duration(ytm, face, coupon_rate, maturity_years, freq=2):
    """Percentage price change for a one unit change in yield."""
    mac = macaulay_duration(ytm, face, coupon_rate, maturity_years, freq)
    return mac / (1 + ytm / freq)


def convexity(ytm, face, coupon_rate, maturity_years, freq=2):
    """Second order price sensitivity, in years squared."""
    times, cashflows = bond_cashflows(face, coupon_rate, maturity_years, freq)
    k = times * freq
    present_values = cashflows / (1 + ytm / freq) ** k
    price = present_values.sum()
    weights = k * (k + 1) / (freq**2 * (1 + ytm / freq) ** 2)
    return float(np.sum(weights * present_values) / price)


def dv01(ytm, face, coupon_rate, maturity_years, freq=2):
    """Price change in currency for a one basis point yield rise (positive number)."""
    price = bond_price(ytm, face, coupon_rate, maturity_years, freq)
    mod_dur = modified_duration(ytm, face, coupon_rate, maturity_years, freq)
    return float(mod_dur * price * 1e-4)


def price_change_estimate(price, mod_duration, conv, delta_yield, use_convexity=True):
    """Taylor estimate of the new price after a yield change."""
    change = -mod_duration * price * delta_yield
    if use_convexity:
        change += 0.5 * conv * price * delta_yield**2
    return price + change


def yield_to_maturity(price, face, coupon_rate, maturity_years, freq=2):
    """Solve for the yield that reproduces a market price."""

    def gap(ytm):
        return bond_price(ytm, face, coupon_rate, maturity_years, freq) - price

    return float(brentq(gap, -0.5, 1.0))
