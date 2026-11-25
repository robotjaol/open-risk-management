# Regulatory Sources

Each row is a source that a module in version 0.1.0 cites. The registry check confirmed the bibliographic record on 2026-11-25. The full texts were not read for every rule, so rule level claims need the primary text.

| Source | Issuer | Link | Registry status | Used by |
|---|---|---|---|---|
| Basel III: Finalising post-crisis reforms (d424) | BCBS | https://www.bis.org/bcbs/publ/d424.htm | record verified, integrated into the consolidated Basel Framework | probability_of_default, expected_credit_loss |
| Minimum capital requirements for market risk (d457) | BCBS | https://www.bis.org/bcbs/publ/d457.htm | record verified, integrated into the consolidated Basel Framework | duration_and_convexity, historical_var, expected_shortfall, backtesting |
| IFRS 9 Financial Instruments, section 5.5 | IASB | link in catalog | record verified | expected_credit_loss |
| Post implementation review of IFRS 9 impairment | IASB | link in catalog | record verified | expected_credit_loss |
| SR 11-7 Model Risk Management | Federal Reserve | https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm | superseded by SR 26-2 on 17 April 2026 | none |
| SR 26-2 Revised Guidance on Model Risk Management | Federal Reserve | https://www.federalreserve.gov/supervisionreg/srletters/sr2602.htm | current | probability_of_default, credit_scoring, expected_credit_loss |

The column "Used by" must match `research/paper_catalog.csv`. If they differ, the catalog is generated and is right.

## Jurisdiction note

These are global or United States texts. National implementations of Basel and national accounting variants are not covered. A module that depends on a national rule must name it.

## Check before use

* Rule numbers, thresholds and effective dates were not extracted in this version. Read the primary text.
