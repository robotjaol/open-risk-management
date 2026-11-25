# Changelog

All notable changes. Format follows Keep a Changelog. Versioning follows Semantic Versioning.

## [0.2.0] 2026-11-25

Real data and applied case studies.

### Added

* 4 real open datasets with cards, licenses and checksums, and `tools/fetch_real_data.py` to download them again: German Credit, WTI daily, FX daily, Shiller S&P 500 monthly.
* 4 applied case studies in `12_end_to_end_banking_projects`: var_crisis_research, daily_market_risk_desk, credit_decision_cutoff, historical_stress_replay. Each has pre stated hypotheses or acceptance criteria, saved results, figures and limits.
* Literature review, generated source register, and a DOI column in the paper catalog. 9 DOIs matched against Crossref.
* README with figures, case study findings, badges and a JupyterLab start.
* `make fetch-data`.

### Changed

* Status renderer plans 114 topics, 12 built.
* Dataset catalog and cards cover `raw` and `processed`.

### Known issues

* credit_scoring: acceptance check `auc_within_0.01_of_raw_logistic` is not met.
* The 4 case studies are Validating, not Complete. Their references are verified, but no independent review exists.
* The `german_credit` copy comes from a package and was not compared cell by cell with the UCI file.
* The price definition (average or month end) of the Shiller file is not verified.
* CI workflows have not run on a hosted runner.
* 102 of 114 planned topics are not built. No liquidity, operational risk, capital, ALM or AML case study exists.

## [0.1.0] 2026-11-25

Foundation release.

### Added

* Library `risk_lab`: bond mathematics, credit metrics, logistic regression, WoE and scorecard scaling, ECL, VaR, ES, backtesting, synthetic data generators, results schema.
* 8 modules: probability_of_default, credit_scoring, expected_credit_loss, duration_and_convexity, historical_var, parametric_var, expected_shortfall, backtesting. Each has a 20 section notebook, README, references and saved results.
* 4 synthetic datasets with cards and a catalog.
* Reference registry with verification flags and a generated paper catalog of 19 sources (16 verified records, 3 books not verified).
* Status renderer that checks declared status against evidence.
* Documentation, research notes, unit tests, notebook and repository validation tests, CI workflows.

### Known issues

* credit_scoring: acceptance check `auc_within_0.01_of_raw_logistic` is not met.
* All data is synthetic or illustrative. No real dataset yet.
* CI workflows have not run on a hosted runner.
* 102 of 110 planned topics are not built.
