# Literature Review

Scope: the sources that the built modules cite, grouped by the question they help answer, and what the saved results of this repository say next to them. Date 2026-11-25. Every entry is in [source_register.md](source_register.md) with its DOI or link and its verification status. Labels: Fact is stated by the source record or by a saved result. Inference is my reading. Gap is something the registry does not cover.

Rule for this page: a statement about what a paper says is limited to what the verified record and the one line summary in the registry support. The full texts were not read for every claim.

## 1. How to measure tail risk

* Fact. Artzner, Delbaen, Eber and Heath (1999) state the axioms of a coherent risk measure and discuss why quantile based measures such as VaR can fail subadditivity.
* Fact. Acerbi and Tasche (2002) compare definitions of expected shortfall and show which one is coherent for any loss distribution. Rockafellar and Uryasev (2000) introduce CVaR minimisation through linear programming, and CVaR equals ES for continuous losses.
* Fact. The Basel market risk standard (BCBS d457, 2019) uses expected shortfall in the internal models approach.
* Fact in this repository. The `expected_shortfall` module estimates ES by several methods and checks subadditivity on synthetic data. The `daily_market_risk_desk` case reports VaR and the tail mean together, and splits the tail mean by currency so that the largest contributor is visible.
* Inference. For a desk, the practical gain of the tail mean is the split by position. A VaR number alone does not say which position to cut.

## 2. How to test a VaR model

* Fact. Kupiec (1995) introduces the proportion of failures test and discusses its low power on short samples. Christoffersen (1998) defines tests for coverage and for independence of interval forecast failures. Nolde and Ziegel (2017) compare traditional and comparative backtests and discuss elicitability. Acerbi and Szekely (2014) propose ES backtests.
* Fact in this repository. The `backtesting` module shows the power of the Kupiec test by simulation on synthetic data.
* Fact in this repository, real data. In `var_crisis_research`, a 500 day historical VaR at 99 percent had pooled crisis exception rates of 5.3 percent for WTI and 3.5 percent for the FX basket, against an expected 1 percent. A VaR from an EWMA t(4) model had 1.3 percent on both. The Christoffersen independence p value of the 500 day historical VaR is 4.6e-05 for WTI, so the failures cluster.
* Inference. The clustering result is what the independence test was designed to find: a model that is calibrated on average but fails in runs.
* Limit. The crisis windows were chosen by date before the hypotheses were fixed, but an exploratory version of the analysis was run first by the author. This is stated in the case README.

## 3. Credit scoring and decision rules

* Fact. Lessmann, Baesens, Seow and Thomas (2015) benchmark 41 classifiers on eight real credit scoring data sets. Gunnarsson et al. (2021) compare deep learning with conventional and ensemble methods and conclude that deep learning looks inappropriate there, with XGBoost preferred when classification performance is the main goal.
* Fact in this repository. The `credit_decision_cutoff` case fits a regularised logistic regression on the German Credit data (1000 applicants). The held out AUC is 0.796, and 0.796 with scikit-learn. This repository did not test ensemble methods, so it neither supports nor contradicts the two papers above.
* Fact in this repository. With the dataset's cost matrix (a bad loan accepted costs 5, a good loan refused costs 1) the Bayes cut off is 1/6. At that cut off the model costs 0.52 per applicant on the test sample, against 1.50 for approving all and 0.70 for refusing all. The 95 percent bootstrap interval of the difference to approve all is -1.27 to -0.70, and to refuse all it is -0.29 to -0.05. In 100 repeated splits the model beat refuse all in 99 of them.
* Fact in this repository. If the bad rate of the portfolio falls to 5 percent and the cut off is not corrected, the model costs 0.51 per applicant, and approving everyone costs 0.25. With the corrected cut off the model costs 0.23.
* Inference. A score is only useful with a decision rule and a base rate. A good AUC does not protect against a wrong cut off.

## 4. Provisioning and model risk

* Fact. IFRS 9 section 5.5 sets 12 month ECL when credit risk has not increased significantly, lifetime ECL after a significant increase, and lifetime ECL for credit impaired assets. The IASB post implementation review (2024) discusses judgement areas such as staging.
* Fact. SR 26-2 (2026) is current US model risk guidance and supersedes SR 11-7. The letter says it is most relevant to organisations above 30 billion dollars in assets.
* Fact in this repository. The `expected_credit_loss` module implements a simplified three stage calculation on synthetic data. It does not implement a regulatory model.

## 5. Stress testing

* Gap. The registry holds no paper on stress testing. The `historical_stress_replay` case implements scenario replay and a reverse stress test from first principles and uses BCBS d457, Kupiec (1995) and Artzner et al. (1999) only for the VaR part.
* Fact in this repository. On monthly US data from 1871 (Shiller series), a 60/40 equity and 10 year bond portfolio replayed with the worst 12 month window of 1931 to 1932 and today's 3.75 percent yield loses 36.0 percent, which is USD 36.0 million on USD 100 million. The worst single month replayed loses 15.5 percent. An equity fall of 33.5 percent in one month with no rate move would reach the illustrative 20 percent loss appetite, and the worst historical month in the file is a fall of 26.2 percent.
* Fact in this repository. The 240 month rolling VaR at 99 percent was exceeded 26 times in 1589 months, against 15.9 expected (Kupiec p = 0.020).
* Limit. The data card does not say whether the monthly price is an average or a month end value. An average would understate tail months.

## 6. What the evidence base lacks

| Gap | Effect |
|---|---|
| No paper on stress testing, liquidity, capital planning, operational risk | the planned topics in these families have no sources yet |
| Three books not verified (Hull, Siddiqi, Jorion) | modules that cite them stay Validating |
| Fissler and Ziegel on joint elicitability of VaR and ES | not in the registry |
| Full texts not read for every claim | rule level statements need the primary text |

See [research_gaps.md](research_gaps.md) for the closing conditions.
