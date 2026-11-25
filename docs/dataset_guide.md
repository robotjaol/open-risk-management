# Dataset Guide

Audience: users who load or add datasets. Reference plus how to. Version 0.2.0.

## What exists

Synthetic data under `datasets/synthetic/` and real open data under `datasets/raw/` and `datasets/processed/`. Each file has a YAML card with the source or generator call, columns, leakage risks, representativeness and a SHA 256 checksum, and a row in [datasets/catalog.csv](../datasets/catalog.csv). If the catalog and the tables below differ, the catalog is right.

| Dataset | Kind | Rows | Used by | Purpose |
|---|---|---|---|---|
| retail_loans_dev | synthetic | 15000 | probability_of_default, credit_scoring | default model development, known true coefficients |
| retail_loans_monitoring | synthetic | 6000 | credit_scoring | same process with population drift, for PSI |
| loan_book | synthetic | 5000 | expected_credit_loss | PD, LGD, EAD inputs for staging and ECL |
| market_returns | synthetic | 3000 | method modules in market risk | daily returns from a GARCH(1,1) process with Student t shocks |
| german_credit | real | 1000 | credit_decision_cutoff | applicant level default data with a cost matrix |
| wti_spot_daily | real | 9547 | var_crisis_research | daily oil price including the negative price of April 2020 |
| fx_daily_2000 | real, processed | 7015 | var_crisis_research, daily_market_risk_desk | daily exchange rates of 10 currencies from 2000 |
| sp500_shiller_monthly | real | 1869 | historical_stress_replay | monthly equity price, dividend and 10 year yield from 1871 |

## Why both kinds

Judgment: synthetic data is useful because the true process is known, so a notebook can test whether a method recovers it. Real data shows what happens when the assumptions do not hold: the 500 day VaR failing in crises, drift in a portfolio, a negative oil price.

Consequence: a result on synthetic data shows that a method works when its assumptions hold. A result on real open data shows behaviour on that series. Neither is a finding about a bank. Every results file has `data_kind` (synthetic, illustrative or empirical) and every README repeats it.

## Known data issues

* WTI has two days with a negative or zero price in April 2020. Log returns are undefined there, so the two return days are excluded by a stated rule and the case counts them.
* The Shiller file has trailing months with zero dividend and zero yield. They are excluded and counted.
* The card of the Shiller file does not say whether the price is a monthly average or a month end value.
* `german_credit` is small (1000 rows), old, and from one German source. Personal status and foreign worker are protected style attributes and must not be used for decisions in practice.

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

* Licenses were taken from the source pages and package metadata on the access date in each card. Check the terms again before you redistribute a file.
* Public credit and rates data named in planned topics (for example FRED series) were not downloaded because the build environment could not reach those hosts.
