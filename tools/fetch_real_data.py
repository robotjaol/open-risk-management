"""Download real public datasets and write cards. Run: python tools/fetch_real_data.py

Needs network access to raw.githubusercontent.com and pypi.org.
Writes datasets/raw and datasets/processed with one YAML card per file.
"""

import hashlib
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "datasets" / "raw"
PROCESSED = ROOT / "datasets" / "processed"
BASE = "https://raw.githubusercontent.com/datasets"
PDDL = "ODC-PDDL-1.0 (Open Data Commons Public Domain Dedication and License)"
FX_COUNTRIES = [
    "Euro", "Japan", "United Kingdom", "Switzerland", "Canada",
    "Singapore", "Thailand", "Malaysia", "South Korea", "India",
]


def sha256_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url, target):
    with urllib.request.urlopen(url, timeout=60) as response:
        target.write_bytes(response.read())


def write_card(folder, name, frame, meta):
    path = folder / f"{name}.csv"
    frame.to_csv(path, index=False)
    card = dict(meta)
    card["name"] = name
    card["file"] = str(path.relative_to(ROOT))
    card["rows"] = int(len(frame))
    card["columns"] = list(frame.columns)
    card["sha256"] = sha256_of(path)
    card["access_date"] = str(date.today())
    (folder / f"{name}.yaml").write_text(yaml.safe_dump(card, sort_keys=False, width=100))
    print("wrote", path.relative_to(ROOT), len(frame))


def get_wti(scratch):
    target = scratch / "wti.csv"
    download(f"{BASE}/oil-prices/main/data/wti-daily.csv", target)
    frame = pd.read_csv(target)
    write_card(RAW, "wti_spot_daily", frame, {
        "title": "WTI Cushing spot price, daily, USD per barrel",
        "kind": "empirical",
        "license": PDDL,
        "source": "US Energy Information Administration series RWTCd, via github.com/datasets/oil-prices",
        "source_url": f"{BASE}/oil-prices/main/data/wti-daily.csv",
        "target": "none",
        "observation_period": f"{frame['Date'].min()} to {frame['Date'].max()}",
        "changes": "none, file copied as downloaded",
        "leakage_risks": "Not applicable, there is no prediction target.",
        "representativeness": "One commodity spot price. Contains the negative price of April 2020, so log returns are undefined on those days.",
    })


def get_sp500(scratch):
    target = scratch / "sp500.csv"
    download(f"{BASE}/s-and-p-500/main/data/data.csv", target)
    frame = pd.read_csv(target)
    write_card(RAW, "sp500_shiller_monthly", frame, {
        "title": "S&P 500 composite, monthly, with dividends, earnings, CPI and 10 year rate",
        "kind": "empirical",
        "license": PDDL,
        "source": "Robert Shiller dataset extended with FRED data, via github.com/datasets/s-and-p-500",
        "source_url": f"{BASE}/s-and-p-500/main/data/data.csv",
        "target": "none",
        "observation_period": f"{frame['Date'].min()} to {frame['Date'].max()}",
        "changes": "none, file copied as downloaded",
        "leakage_risks": "Not applicable, there is no prediction target.",
        "representativeness": "US equity index only. Monthly values are averages or end points as defined by the source.",
    })


def get_fx(scratch):
    target = scratch / "fx.csv"
    download(f"{BASE}/exchange-rates/main/data/daily.csv", target)
    frame = pd.read_csv(target)
    frame = frame[frame["Country"].isin(FX_COUNTRIES) & (frame["Date"] >= "2000-01-01")]
    wide = frame.pivot(index="Date", columns="Country", values="Exchange rate").reset_index()
    write_card(PROCESSED, "fx_daily_2000", wide, {
        "title": "Daily exchange rates, 10 currencies, from 2000, wide format",
        "kind": "empirical",
        "license": PDDL,
        "source": "Federal Reserve Bank of St. Louis (FRED) exchange rates, via github.com/datasets/exchange-rates",
        "source_url": f"{BASE}/exchange-rates/main/data/daily.csv",
        "target": "none",
        "observation_period": f"{wide['Date'].min()} to {wide['Date'].max()}",
        "changes": "kept 10 countries and dates from 2000-01-01, pivoted to one column per country. Quote convention differs by currency as in the source. Missing days (holidays) are left empty.",
        "leakage_risks": "Not applicable, there is no prediction target.",
        "representativeness": "Ten currencies only. The Indonesian rupiah is not in the source.",
    })


def get_macro():
    import statsmodels.api as sm

    frame = sm.datasets.macrodata.load_pandas().data
    write_card(RAW, "us_macro_quarterly", frame, {
        "title": "US macroeconomic quarterly data 1959Q1 to 2009Q3",
        "kind": "empirical",
        "license": "public domain, as stated in the statsmodels dataset copyright note",
        "source": "statsmodels.datasets.macrodata (US Bureau of Economic Analysis and related US government series)",
        "source_url": "https://www.statsmodels.org/stable/datasets/generated/macrodata.html",
        "target": "none",
        "observation_period": f"{int(frame['year'].min())}Q1 to {int(frame['year'].max())}Q3",
        "changes": "none, loaded from the installed statsmodels package",
        "leakage_risks": "Not applicable, there is no prediction target.",
        "representativeness": "US data that ends in 2009. It contains the 2008 crisis but not recent years.",
    })


def get_german_credit(scratch):
    subprocess.run(
        [sys.executable, "-m", "pip", "download", "scorecardpy==0.1.9.7", "--no-deps", "-d", str(scratch), "-q"],
        check=True,
    )
    archive = next(scratch.glob("scorecardpy-*.tar.gz"))
    with tarfile.open(archive) as tar:
        member = next(m for m in tar.getmembers() if m.name.endswith("data/germancredit.csv"))
        tar.extract(member, scratch, filter="data")
        frame = pd.read_csv(scratch / member.name)
    write_card(RAW, "german_credit", frame, {
        "title": "Statlog (German Credit Data), 1000 loan applicants, decoded labels",
        "kind": "empirical",
        "license": "CC BY 4.0",
        "source": "Hofmann, H. (1994). Statlog (German Credit Data). UCI Machine Learning Repository. https://doi.org/10.24432/C5NC77",
        "source_url": "https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
        "obtained_via": "scorecardpy 0.1.9.7 (MIT) sdist, file scorecardpy/data/germancredit.csv, which holds the same table with text labels instead of A11 style codes. Row and column counts match the UCI page. A cell by cell comparison with the UCI file was not run.",
        "target": "creditability (good or bad). UCI codes 1 = good and 2 = bad. UCI gives a cost matrix where a bad loan accepted costs 5 and a good loan refused costs 1.",
        "observation_period": "none, cross section, collected in Germany, year not stated on the UCI page",
        "changes": "none, file copied from the package",
        "leakage_risks": "No feature is built from the target. Personal status and sex and foreign worker are protected style attributes and must not be used for decisions in practice.",
        "representativeness": "1000 applicants of one German source, 30 percent bad by construction of the sample. Not representative of any current portfolio.",
    })


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        scratch = Path(folder)
        get_wti(scratch)
        get_sp500(scratch)
        get_fx(scratch)
        get_german_credit(scratch)
    get_macro()


if __name__ == "__main__":
    main()
