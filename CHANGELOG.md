# Changelog

All notable changes. Format follows Keep a Changelog. Versioning follows Semantic Versioning.

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
