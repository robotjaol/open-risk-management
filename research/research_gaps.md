# Research Gaps

An honest list of what is missing, with the reason and a measurable closing condition. Date 2026-11-25.

| Gap | Impact | Closing condition |
|---|---|---|
| Real data covers market and one credit sample only | no real data for liquidity, operational, capital or ALM topics | at least one case study per risk family with a documented license |
| German Credit is small, old and from one source | credit findings may not carry over to a current portfolio | a second, larger public credit dataset with a documented license |
| German Credit copy comes from the scorecardpy package | the table was not compared cell by cell with UCI | a checksum comparison with the file from the UCI archive |
| Shiller price definition not verified | an average price would understate tail months | the source documentation checked and the card updated |
| FRED and UCI hosts unreachable from the build shell | some public series were not downloaded | a download script run once on a networked machine |
| Three books cited, not verified (Hull, Siddiqi, Jorion) | dependent modules stay Validating | record verified or replaced by primary papers |
| No paper on stress testing in the registry | the stress case relies on first principles | at least one verified source on scenario design and reverse stress testing |
| Rule level details of Basel and IFRS 9 not extracted | traffic light zone limits and IFRS 9 paragraph references need recheck | each rule quoted from the primary text with link and date |
| PSI and IV thresholds are practitioner rules of thumb | classification of a score shift as small or large is not backed by a verified source | verified source, or an empirical study on real data |
| ES joint elicitability result (Fissler and Ziegel) not in registry | the backtesting module cites related work only | record added and verified |
| Scorecard loses 0.0202 AUC against the raw logistic model | criterion 1 of credit_scoring fails | study of bin count and monotonic binning, reported with the same threshold |
| Case study hypotheses were fixed after an exploratory run | the p values are not pre registered results | a new period or dataset where the hypotheses are fixed before any run |
| Illustrative limits and loss appetite in the case studies | the red share and the stress margin depend on them | the same case run with a limit from a real policy, and the sensitivity tables read together |
| No independent review | Complete means internal criteria only | named reviewer and a review record per module |
| Student t degrees of freedom floored at 3.0 in the synthetic market modules | affects those t results | sensitivity of each t result to the floor, reported |
| 102 of 114 planned topics missing | see module registry | built one by one under the same criteria |

## Not a gap

Synthetic data is a deliberate choice for learning and testing. It becomes a gap only when a result is described as a finding about real portfolios.
