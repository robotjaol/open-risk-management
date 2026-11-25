# Research Gaps

An honest list of what is missing, with the reason and a measurable closing condition. Date 2026-11-25.

| Gap | Impact | Closing condition |
|---|---|---|
| No real dataset in any module | results do not show behaviour on real portfolios | at least one module with `data_kind` empirical and a documented license |
| External data sources were unreachable in the build environment | UCI credit data and FRED rates could not be downloaded | a download script plus checksum, run once on a networked machine |
| Three books cited, not verified (Hull, Siddiqi, Jorion) | dependent modules stay Validating | record verified or replaced by primary papers |
| Rule level details of Basel and IFRS 9 not extracted | traffic light zone limits and IFRS 9 paragraph references need recheck | each rule quoted from the primary text with link and date |
| PSI and IV thresholds are practitioner rules of thumb | classification of a score shift as small or large is not backed by a verified source | verified source, or an empirical study on real data |
| ES joint elicitability result (Fissler and Ziegel) not in registry | the backtesting module cites related work only | record added and verified |
| Scorecard loses 0.0202 AUC against the raw logistic model | criterion 1 of credit_scoring fails | study of bin count and monotonic binning, reported with the same threshold |
| No independent review | Complete means internal criteria only | named reviewer and a review record per module |
| Student t degrees of freedom floored at 3.0 | affects all t results | sensitivity of each t result to the floor, reported |
| No LGD, EAD, rating migration, credit VaR, stress testing, liquidity, capital, ALM, operational, model, AML and strategic modules | 102 of 110 planned topics missing | see module registry |

## Not a gap

Synthetic data is a deliberate choice for learning and testing. It becomes a gap only when a result is described as a finding about real portfolios.
