import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from risk_lab.data import synthetic

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datasets" / "synthetic"


def test_generators_are_deterministic():
    first = synthetic.make_retail_loans(500, seed=1)
    second = synthetic.make_retail_loans(500, seed=1)
    pd.testing.assert_frame_equal(first, second)
    other = synthetic.make_retail_loans(500, seed=2)
    assert not first.equals(other)


def test_retail_default_rate_is_reasonable_and_drift_raises_it():
    base = synthetic.make_retail_loans(8000, seed=3, drift=0.0)
    drifted = synthetic.make_retail_loans(8000, seed=3, drift=1.0)
    assert 0.03 < base["default_12m"].mean() < 0.12
    assert drifted["default_12m"].mean() > base["default_12m"].mean()


def test_noise_columns_do_not_predict_default():
    frame = synthetic.make_retail_loans(15000, seed=4)
    corr = frame[["age", "loan_amount", "term_months"]].corrwith(frame["default_12m"]).abs()
    assert corr.max() < 0.04


def test_market_returns_have_fat_tails_and_correct_shape():
    frame = synthetic.make_market_returns(3000, seed=14)
    assert list(frame.columns) == ["date", "r_equity", "r_fx", "r_bond"]
    assert len(frame) == 3000
    assert 0.008 < frame["r_equity"].std() < 0.016
    assert frame["r_equity"].kurt() > 1.0


def test_loan_book_ranges():
    book = synthetic.make_loan_book(2000, seed=7)
    assert book["pd_current"].between(0, 1).all()
    assert book["lgd"].between(0, 1).all()
    assert (book["ead"] > 0).all()
    assert book["remaining_years"].min() >= 1


@pytest.mark.parametrize("name", ["retail_loans_dev", "retail_loans_monitoring", "loan_book", "market_returns"])
def test_committed_dataset_matches_metadata(name):
    meta = yaml.safe_load((DATA / f"{name}.yaml").read_text())
    csv_path = DATA / f"{name}.csv"
    assert hashlib.sha256(csv_path.read_bytes()).hexdigest() == meta["sha256"]
    frame = pd.read_csv(csv_path)
    assert len(frame) == meta["rows"]
    assert list(frame.columns) == meta["columns"]
    assert int(frame.isna().sum().sum()) == meta["missing_values"]
    assert meta["kind"] == "synthetic"
    assert np.isfinite(frame.select_dtypes("number").to_numpy()).all()
