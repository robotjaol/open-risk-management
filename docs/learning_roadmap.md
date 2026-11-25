# Learning Roadmap

Audience: a learner who wants an order for the modules. This is an explanation document. Only built modules have links. Topics marked Planned have no directory yet.

## Principle

Learn the measurement first, then the validation of the measurement, then the regulation that uses it. A VaR number without a backtest, or a PD without a discrimination and calibration check, is not a result.

## Path 1: market risk (built modules, about 5 modules)

1. [duration_and_convexity](../03_market_risk/duration_and_convexity/README.md): price sensitivity of a bond to yield, and where the linear approximation fails.
2. [historical_var](../03_market_risk/historical_var/README.md): empirical quantile of portfolio losses, rolling windows, bootstrap uncertainty.
3. [parametric_var](../03_market_risk/parametric_var/README.md): normal and Student t models, EWMA volatility, Monte Carlo cross check, component VaR.
4. [expected_shortfall](../03_market_risk/expected_shortfall/README.md): tail average loss, subadditivity, closed forms, and why a normal model understates the tail.
5. [backtesting](../03_market_risk/backtesting/README.md): Kupiec, Christoffersen, traffic light zones, test power.

Done when: you can explain, for the synthetic return set, why the 99 percent normal VaR is lower than the historical VaR and what the exception counts say about each model.

## Path 2: credit risk (built modules, 3 modules)

1. [probability_of_default](../02_credit_risk/probability_of_default/README.md): logistic regression from scratch, AUC, Gini, KS, Brier, calibration.
2. [credit_scoring](../02_credit_risk/credit_scoring/README.md): weight of evidence, information value, scorecard scaling, population stability index.
3. [expected_credit_loss](../02_credit_risk/expected_credit_loss/README.md): three stage ECL, significant increase in credit risk, scenario weighting.

Done when: you can say why the scorecard in module 2 lost AUC against the raw logistic model and whether the loss matters for ranking.

## Planned topics

The full list of 110 planned topics is in [module_registry.csv](module_registry.csv). Suggested order when they are built: fundamentals (probability, linear algebra, financial mathematics), then loss given default and exposure at default (they complete the ECL inputs), then Monte Carlo VaR and stress testing, then liquidity, capital and asset liability management, then operational risk and model risk.

## Assumptions

* The learner can read Python and basic statistics. Fact: modules do not teach Python syntax.
* The order above is a professional judgment, not a standard.
