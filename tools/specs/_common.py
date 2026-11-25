"""Shared pieces for the module specs."""

from nbgen import SECTION_NAMES


def setup_code(module):
    return f"""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from risk_lab.reporting.results import find_root, save_config, save_result
from risk_lab.visualization.style import COLORS, apply_style, save_figure

apply_style()
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 20)
MODULE = "{module}"
ROOT = find_root()
SEED = 42"""


PORTFOLIO_CODE = """# load returns
returns = pd.read_csv(ROOT / "datasets" / "synthetic" / "market_returns.csv", parse_dates=["date"])
returns = returns.set_index("date")
assets = ["r_equity", "r_fx", "r_bond"]
weights = np.array([0.5, 0.3, 0.2])
portfolio = returns[assets].to_numpy() @ weights
portfolio = pd.Series(portfolio, index=returns.index, name="portfolio")
print("days:", len(portfolio))
print("weights:", dict(zip(assets, weights.tolist())))"""


def check_sections(spec):
    """Every section except 5 and 20 must have content."""
    missing = [n for n in SECTION_NAMES if n not in (5, 20) and not spec["sections"].get(n)]
    if missing:
        raise ValueError(f"{spec['module']} missing sections {missing}")
    return spec
