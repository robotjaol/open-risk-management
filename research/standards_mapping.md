# Standards Mapping

Which module touches which standard or framework, and how. "Touches" means the module cites the source for background or compares its own result with a concept in it. It does not mean the module implements a regulatory calculation.

| Module | Sources cited | Concept used | Depth |
|---|---|---|---|
| duration_and_convexity | Hull textbook (not verified), BCBS d457 | interest rate sensitivity as a market risk driver | background, method implemented |
| historical_var | Jorion and Hull textbooks (not verified), Kupiec 1995, Artzner et al. 1999, BCBS d457 | empirical VaR, coherence, exception test | method implemented |
| parametric_var | Jorion and Hull textbooks (not verified), Bollerslev 1986, Kupiec 1995, Artzner et al. 1999 | normal and t VaR, GARCH generator, exception test | method implemented |
| expected_shortfall | Acerbi and Tasche 2002, Rockafellar and Uryasev 2000, Artzner et al. 1999, Nolde and Ziegel 2017, Acerbi and Szekely 2014, BCBS d457 | coherence, ES estimation, ES backtest, move from VaR to ES | method implemented, no regulatory capital calculation |
| backtesting | Kupiec 1995, Christoffersen 1998, Nolde and Ziegel 2017, Acerbi and Szekely 2014, BCBS d457 | exception count tests, traffic light, ES backtest | method implemented, zone limits flagged for recheck |
| probability_of_default | Lessmann et al. 2015, Gunnarsson et al. 2021, BCBS d424, SR 26-2 | model benchmarking, model risk guidance | method implemented |
| credit_scoring | Siddiqi 2006 (not verified), Lessmann et al. 2015, Gunnarsson et al. 2021, SR 26-2 | scorecard practice, monitoring | method implemented, thresholds flagged unverified |
| expected_credit_loss | IFRS 9 section 5.5, IASB review 2024, BCBS d424, SR 26-2 | three stage model, SICR, forward looking scenarios | simplified implementation |
| var_crisis_research | Kupiec 1995, Christoffersen 1998, BCBS d457 | exception and independence tests, VaR model failure in crises | method implemented on real data |
| daily_market_risk_desk | Kupiec 1995, Artzner et al. 1999, BCBS d457 | VaR against a limit, tail contribution, traffic light | method implemented, limit is illustrative |
| credit_decision_cutoff | Lessmann et al. 2015, Gunnarsson et al. 2021, SR 26-2 | model benchmarking, model risk guidance, cost based cut off | method implemented on real data |
| historical_stress_replay | Kupiec 1995, Artzner et al. 1999, BCBS d457 | scenario replay, reverse stress, VaR exception test | method implemented, no supervisory scenario |

The exact reference lists per module are in each module's `references.md`. If this table and a `references.md` differ, the module file is right.

## Not mapped yet

Basel capital calculations, liquidity ratios, interest rate risk in the banking book, operational risk, AML and ICAAP have no module yet. See [project status](../docs/project_status.md).
