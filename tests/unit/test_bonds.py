import numpy as np
import pytest

from risk_lab.finance import bonds


def test_par_bond_prices_at_face():
    price = bonds.bond_price(0.05, 100, 0.05, 10, freq=2)
    assert price == pytest.approx(100.0, abs=1e-9)


def test_zero_coupon_duration_equals_maturity():
    duration = bonds.macaulay_duration(0.04, 100, 0.0, 7, freq=1)
    assert duration == pytest.approx(7.0, abs=1e-9)


def test_zero_coupon_price_closed_form():
    price = bonds.bond_price(0.04, 100, 0.0, 5, freq=1)
    assert price == pytest.approx(100 / 1.04**5, rel=1e-12)


def test_modified_duration_matches_numeric_derivative():
    args = (100, 0.06, 8)
    ytm = 0.05
    step = 1e-6
    up = bonds.bond_price(ytm + step, *args)
    down = bonds.bond_price(ytm - step, *args)
    price = bonds.bond_price(ytm, *args)
    numeric = -(up - down) / (2 * step) / price
    assert bonds.modified_duration(ytm, *args) == pytest.approx(numeric, rel=1e-6)


def test_convexity_matches_numeric_second_derivative():
    args = (100, 0.06, 8)
    ytm = 0.05
    step = 1e-4
    up = bonds.bond_price(ytm + step, *args)
    down = bonds.bond_price(ytm - step, *args)
    price = bonds.bond_price(ytm, *args)
    numeric = (up - 2 * price + down) / step**2 / price
    assert bonds.convexity(ytm, *args) == pytest.approx(numeric, rel=1e-4)


def test_yield_round_trip():
    price = bonds.bond_price(0.037, 100, 0.045, 12)
    assert bonds.yield_to_maturity(price, 100, 0.045, 12) == pytest.approx(0.037, abs=1e-10)


def test_convexity_improves_estimate_for_large_shock():
    args = (100, 0.05, 20)
    ytm = 0.05
    price = bonds.bond_price(ytm, *args)
    mod_dur = bonds.modified_duration(ytm, *args)
    conv = bonds.convexity(ytm, *args)
    actual = bonds.bond_price(ytm + 0.02, *args)
    linear = bonds.price_change_estimate(price, mod_dur, conv, 0.02, use_convexity=False)
    curved = bonds.price_change_estimate(price, mod_dur, conv, 0.02, use_convexity=True)
    assert abs(curved - actual) < abs(linear - actual)


def test_dv01_is_positive_and_small():
    value = bonds.dv01(0.05, 100, 0.05, 10)
    assert 0 < value < 0.2
    assert np.isfinite(value)
