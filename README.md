# Open Risk Management

A paper driven, open learning lab for risk management, with banking as the main specialization. Every module is a notebook with saved results, a reference list, and checks that decide its status. Version 0.1.0.

**Current state, stated plainly:** 8 of 110 planned topics are built (credit risk 3, market risk 5). All data is synthetic or illustrative. 4 modules are Complete by the repository criteria, 4 are Validating. Nothing here has been independently reviewed. Read [limitations_and_disclaimers.md](docs/limitations_and_disclaimers.md) before relying on any number.

## Built modules

| Module | Status | Data | What it shows |
|---|---|---|---|
| [probability_of_default](02_credit_risk/probability_of_default/README.md) | Complete | synthetic | logistic regression from scratch, AUC, Gini, KS, Brier, calibration |
| [credit_scoring](02_credit_risk/credit_scoring/README.md) | Validating | synthetic | WoE and IV, scorecard scaling, PSI under drift. One acceptance check fails and is reported |
| [expected_credit_loss](02_credit_risk/expected_credit_loss/README.md) | Complete | synthetic | IFRS 9 style three stage ECL with scenario weighting |
| [duration_and_convexity](03_market_risk/duration_and_convexity/README.md) | Validating | illustrative | bond sensitivity, hedging with DV01 |
| [historical_var](03_market_risk/historical_var/README.md) | Validating | synthetic | empirical VaR, rolling windows, bootstrap |
| [parametric_var](03_market_risk/parametric_var/README.md) | Validating | synthetic | normal, t and EWMA VaR, Monte Carlo cross check |
| [expected_shortfall](03_market_risk/expected_shortfall/README.md) | Complete | synthetic | ES estimators, closed forms, subadditivity |
| [backtesting](03_market_risk/backtesting/README.md) | Complete | synthetic | Kupiec, Christoffersen, traffic light, test power |

The live table, with evidence columns, is [docs/project_status.md](docs/project_status.md). Status is computed, not typed: see [methodology_standards.md](docs/methodology_standards.md).

## Quick start

```bash
git clone https://github.com/robotjaol/open-risk-management.git
cd open-risk-management
python -m venv .venv && source .venv/bin/activate
pip install -e ".[development]"
make test
make notebooks
```

Full steps with expected results: [getting_started.md](docs/getting_started.md).

## Layout

```
NN_family/topic/    README, notebook, references for one module
src/risk_lab/       tested library code
datasets/           synthetic data, cards, catalog
experiments/        saved results, configurations, figures, execution log
research/           paper catalog, regulatory sources, standards mapping, gaps
docs/               guides, glossaries, status
tools/              notebook, status and catalog generators
tests/              unit, notebook and repository validation
```

## Documentation

[Learning roadmap](docs/learning_roadmap.md), [mathematical reference](docs/mathematical_reference.md), [banking glossary](docs/banking_glossary.md), [regulatory glossary](docs/regulatory_glossary.md), [dataset guide](docs/dataset_guide.md), [architecture assessment](docs/architecture_assessment.md).

## Principles

1. No result without executed code. 2. No citation that is not in the registry, and unverified sources are labelled. 3. Synthetic results are never presented as findings about real portfolios. 4. A failed check is reported, not edited away. 5. No empty placeholder folders.

## Contributing, security, citation

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [CITATION.cff](CITATION.cff). License: MIT.

## Disclaimer

Educational and research use only. Not financial, legal or regulatory advice.
