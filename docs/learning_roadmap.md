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

## Path 3: applied work on real data (4 case studies)

Read these after paths 1 and 2. Each one follows a job task: state the question, fix the hypotheses or acceptance criteria, run, decide.

1. [var_crisis_research](../12_end_to_end_banking_projects/var_crisis_research/README.md): research simulation. Does a 500 day historical VaR hold in a crisis, and what does a faster model cost in calm periods?
2. [daily_market_risk_desk](../12_end_to_end_banking_projects/daily_market_risk_desk/README.md): daily activity. A VaR report against a limit, data quality checks, a traffic light, and a reduction decision.
3. [credit_decision_cutoff](../12_end_to_end_banking_projects/credit_decision_cutoff/README.md): practical method. Turn a score into an approval cut off with a cost matrix, then test what happens when the portfolio changes.
4. [historical_stress_replay](../12_end_to_end_banking_projects/historical_stress_replay/README.md): stress testing. Replay history on today's portfolio and solve the reverse stress question.

Done when: you can say which result in each case depends on an assumption that you could change, and read the sensitivity table that shows by how much.

## Planned topics

The full list of 114 planned topics is in [module_registry.csv](module_registry.csv). Suggested order when they are built: fundamentals (probability, linear algebra, financial mathematics), then loss given default and exposure at default (they complete the ECL inputs), then Monte Carlo VaR and stress testing, then liquidity, capital and asset liability management, then operational risk and model risk.

## Assumptions

* The learner can read Python and basic statistics. Fact: modules do not teach Python syntax.
* The order above is a professional judgment, not a standard.
