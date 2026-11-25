# Dataset Guide

Audience: users who load or add datasets. Reference plus how to. Version 0.1.0.

## What exists

Four synthetic datasets under `datasets/synthetic/`. Each has a CSV, a YAML card with the generator call, seed, columns, generating process, leakage risks, representativeness and a SHA 256 checksum, and a row in [datasets/catalog.csv](../datasets/catalog.csv).

| Dataset | Rows | Used by | Purpose |
|---|---|---|---|
| retail_loans_dev | 15000 | probability_of_default, credit_scoring | default model development, known true coefficients |
| retail_loans_monitoring | 6000 | credit_scoring | same process with population drift, for PSI |
| loan_book | 5000 | expected_credit_loss | PD, LGD, EAD inputs for staging and ECL |
| market_returns | 3000 | historical_var, parametric_var, expected_shortfall, backtesting | daily equity, FX and bond returns from a GARCH(1,1) process with Student t shocks |

Row counts come from the catalog. If the catalog and this table differ, the catalog is right.

## Why synthetic

Fact: the build environment of version 0.1.0 could not reach external data sources, so no real dataset was downloaded. Judgment: synthetic data is also useful because the true process is known, which lets a notebook test whether a method recovers it.

Consequence: a result on synthetic data shows that a method works when its assumptions hold. It does not show that the method works on a real portfolio. Every results file has `data_kind` and every README repeats it.

## Add a dataset

1. Put a generator or a download script in `src/risk_lab/data/` or `tools/`. Do not commit a file you cannot document.
2. Write the file under `datasets/synthetic/`, `datasets/raw/` or `datasets/processed/`. Create `raw` or `processed` only when they hold a real file.
3. Write the YAML card with these fields: title, kind, license, source or generator, target, observation period, features, generating process or collection method, leakage risks, representativeness, rows, columns, sha256.
4. Run `python tools/render_catalogs.py` to refresh the catalog.
5. Run `make test`. The repository validation test fails if a CSV has no card or the checksum differs.

For real data also record: the original URL, the access date, the license text, and a statement of what was changed. Do not commit data whose license forbids redistribution. Commit the download script instead.

## Leakage and drift

Cards list leakage risks. The retail loan sets contain `region`, `age`, `employment_years`, `loan_amount` and `term_months` with zero true effect on purpose, so a model that gives them weight is overfitting. The monitoring sample shifts the input distribution but keeps the default relation, so it tests covariate shift only.

## Check before use

* Real world datasets named in the planned topics (for example public credit and rates data) are not in the repository. Check each license and terms before use.
