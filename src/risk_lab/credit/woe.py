"""Weight of evidence, information value and scorecard scaling.

Convention: WoE = ln(share of goods / share of bads) in a bin.
A higher WoE means a safer bin.
"""

import numpy as np
import pandas as pd


def make_bin_edges(values, n_bins=6):
    """Quantile edges with duplicates removed. Outer edges are infinite."""
    values = pd.Series(values).dropna()
    edges = np.unique(np.quantile(values, np.linspace(0, 1, n_bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    return edges


def woe_table(values, target, edges, smoothing=0.5):
    """Bin level counts, WoE and information value.

    smoothing adds a small count to every bin so empty cells do not
    give an infinite WoE.
    """
    values = pd.Series(values).reset_index(drop=True)
    target = pd.Series(target).reset_index(drop=True)
    bins = pd.cut(values, bins=edges, include_lowest=True)
    frame = pd.DataFrame({"bin": bins, "bad": target})
    grouped = frame.groupby("bin", observed=False)["bad"].agg(["count", "sum"])
    grouped = grouped.rename(columns={"count": "total", "sum": "bads"})
    grouped["goods"] = grouped["total"] - grouped["bads"]

    bad_share = (grouped["bads"] + smoothing) / (grouped["bads"].sum() + smoothing * len(grouped))
    good_share = (grouped["goods"] + smoothing) / (
        grouped["goods"].sum() + smoothing * len(grouped)
    )
    grouped["bad_rate"] = grouped["bads"] / grouped["total"]
    grouped["woe"] = np.log(good_share / bad_share)
    grouped["iv_part"] = (good_share - bad_share) * grouped["woe"]
    return grouped.reset_index()


def information_value(table):
    """Total information value of one characteristic."""
    return float(table["iv_part"].sum())


def apply_woe(values, edges, table):
    """Replace raw values with the WoE of their bin."""
    values = pd.Series(values).reset_index(drop=True)
    bins = pd.cut(values, bins=edges, include_lowest=True)
    lookup = dict(zip(table["bin"], table["woe"]))
    return bins.map(lookup).astype(float).to_numpy()


def scaling_constants(base_score=600, base_odds=50, points_to_double_odds=20):
    """Factor and offset for the usual score scaling.

    score = offset + factor * ln(good odds)
    """
    factor = points_to_double_odds / np.log(2)
    offset = base_score - factor * np.log(base_odds)
    return float(factor), float(offset)


def probability_to_score(probability_bad, base_score=600, base_odds=50, points_to_double_odds=20):
    """Convert a default probability into scorecard points."""
    factor, offset = scaling_constants(base_score, base_odds, points_to_double_odds)
    probability_bad = np.clip(np.asarray(probability_bad, dtype=float), 1e-9, 1 - 1e-9)
    good_odds = (1 - probability_bad) / probability_bad
    return offset + factor * np.log(good_odds)
