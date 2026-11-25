"""Build docs/module_registry.csv and docs/project_status.md from specs and saved results.

Run: python tools/render_status.py
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_modules  # noqa: E402
import nbgen  # noqa: E402
import refs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ["Planned", "Researching", "Implementing", "Validating", "Complete"]

PLAN = {
    "00_fundamentals": [
        "01_introduction_to_risk_management", "02_banking_fundamentals", "03_financial_mathematics",
        "04_linear_algebra", "05_probability_and_statistics", "06_financial_economics",
        "07_time_series_analysis", "08_portfolio_theory", "09_python_for_risk_analytics",
    ],
    "01_enterprise_risk_management": [
        "risk_identification", "risk_assessment", "risk_measurement", "risk_response",
        "risk_monitoring", "risk_reporting", "risk_governance", "risk_appetite_framework",
    ],
    "02_credit_risk": [
        "credit_fundamentals", "credit_analysis", "credit_scoring", "probability_of_default",
        "loss_given_default", "exposure_at_default", "expected_credit_loss", "rating_migration",
        "credit_portfolio_risk", "credit_var", "ifrs9", "npl_management", "advanced_credit_models",
    ],
    "03_market_risk": [
        "market_risk_fundamentals", "historical_var", "parametric_var", "monte_carlo_var",
        "expected_shortfall", "backtesting", "stress_testing", "duration_and_convexity",
        "interest_rate_risk",
    ],
    "04_liquidity_risk": [
        "liquidity_fundamentals", "liquidity_gap_analysis", "liquidity_coverage_ratio",
        "net_stable_funding_ratio", "liquidity_stress_testing", "deposit_runoff", "contingency_funding",
    ],
    "05_operational_risk": [
        "operational_risk_fundamentals", "operational_loss_modeling", "rcsa", "risk_control_matrix",
        "key_risk_indicators", "scenario_analysis", "business_continuity", "operational_resilience",
    ],
    "06_capital_and_regulatory_risk": [
        "basel_framework", "capital_adequacy", "risk_weighted_assets", "standardized_approach",
        "internal_ratings_based", "leverage_ratio", "icaap", "regulatory_reporting",
    ],
    "07_asset_liability_management": [
        "alm_fundamentals", "irrbb", "gap_analysis", "economic_value_of_equity", "earnings_at_risk",
        "duration_gap", "balance_sheet_simulation",
    ],
    "08_model_risk_management": [
        "model_governance", "model_validation", "model_calibration", "model_monitoring", "model_drift",
        "ai_model_risk",
    ],
    "09_compliance_aml_and_fraud": [
        "kyc_cdd_edd", "aml", "transaction_monitoring", "fraud_detection", "sanctions_screening",
        "financial_crime_analytics",
    ],
    "10_strategic_and_emerging_risks": [
        "strategic_risk", "cyber_risk", "third_party_risk", "climate_risk", "esg_risk", "systemic_risk",
    ],
    "11_advanced_quantitative_methods": [
        "monte_carlo_simulation", "extreme_value_theory", "bayesian_statistics", "copula_models",
        "stochastic_processes", "optimization", "machine_learning_for_risk",
    ],
    "12_end_to_end_banking_projects": [
        "credit_risk_engine", "market_risk_engine", "liquidity_risk_dashboard",
        "operational_risk_framework", "basel_capital_calculator", "ifrs9_ecl_engine",
        "aml_monitoring_system", "alm_simulator", "integrated_bank_risk_platform",
    ],
    "13_risk_management_in_other_industries": [
        "insurance", "manufacturing", "energy_and_oil_gas", "technology", "healthcare",
        "supply_chain", "project_management",
    ],
}


def load_result(module):
    path = ROOT / "experiments" / "results" / f"{module}.json"
    return json.loads(path.read_text()) if path.exists() else None


def execution_status(spec):
    path = ROOT / "experiments" / "metadata" / "execution_log.json"
    if not path.exists():
        return "not run"
    log = json.loads(path.read_text())
    key = str(nbgen.notebook_path(spec).relative_to(ROOT))
    return log.get(key, {}).get("status", "not run")


def acceptance(result):
    flags = {}
    if result:
        for key, value in result["metrics"].items():
            if key.startswith("acceptance") and isinstance(value, dict):
                flags.update({k: v for k, v in value.items() if isinstance(v, bool)})
    return flags


def unverified_refs(spec):
    return [r["key"] for r in refs.get(spec["refs"]) if not r["verified"]]


def status_problems(spec):
    """Return a list of reasons why the declared status is not supported by evidence."""
    problems = []
    if spec["status"] not in STATUSES:
        problems.append(f"status {spec['status']} is not allowed")
    result = load_result(spec["module"])
    if result is None:
        problems.append("no saved results file")
    if execution_status(spec) != "ok":
        problems.append("notebook has no clean execution record")
    if spec["status"] == "Complete":
        flags = acceptance(result)
        if not flags:
            problems.append("Complete needs computed acceptance checks")
        failed = [k for k, v in flags.items() if not v]
        if failed:
            problems.append(f"acceptance checks not met: {failed}")
        if unverified_refs(spec):
            problems.append(f"unverified references: {unverified_refs(spec)}")
    return problems


def built_index():
    index = {}
    for spec in build_modules.all_specs():
        family, topic = spec["path"].split("/")
        index[(family, topic)] = spec
    return index


def write_registry(specs):
    path = ROOT / "docs" / "module_registry.csv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "module", "status", "data_kind", "dataset", "notebook", "acceptance_passed",
                         "acceptance_total", "unverified_references"])
        index = built_index()
        for family, topics in PLAN.items():
            for topic in topics:
                spec = index.get((family, topic))
                if spec is None:
                    writer.writerow([f"{family}/{topic}", "", "Planned", "", "", "", "", "", ""])
                    continue
                flags = acceptance(load_result(spec["module"]))
                writer.writerow([spec["path"], spec["module"], spec["status"], spec["data_kind"], spec["dataset"],
                                 execution_status(spec), sum(flags.values()), len(flags),
                                 ";".join(unverified_refs(spec))])
    return path


def write_status(specs):
    index = built_index()
    total_planned = sum(len(t) for t in PLAN.values())
    lines = [
        "# Project Status",
        "",
        "Generated by `python tools/render_status.py` from the module specifications, the saved results and the execution log. "
        "Do not edit by hand. A status is only as good as the evidence listed beside it.",
        "",
        "Status values: Planned, Researching, Implementing, Validating, Complete. "
        "**Complete** requires: notebook executes from a clean kernel, a saved results file, computed acceptance checks that all pass, "
        "and every cited reference verified.",
        "",
        f"Modules built: {len(specs)} of {total_planned} planned topics.",
        "",
        "## Built modules",
        "",
        "| Module | Status | Data | Notebook run | Acceptance checks passed | Unverified references |",
        "|---|---|---|---|---|---|",
    ]
    for spec in specs:
        flags = acceptance(load_result(spec["module"]))
        unverified = ", ".join(unverified_refs(spec)) or "none"
        lines.append(
            f"| [{spec['path']}](../{spec['path']}/README.md) | {spec['status']} | {spec['data_kind']} | "
            f"{execution_status(spec)} | {sum(flags.values())} of {len(flags)} | {unverified} |"
        )
    problems = {s["module"]: status_problems(s) for s in specs}
    bad = {k: v for k, v in problems.items() if v}
    lines += ["", "## Evidence check", ""]
    if bad:
        for module, items in bad.items():
            lines.append(f"* `{module}`: {'; '.join(items)}")
    else:
        lines.append("Every declared status is supported by the evidence above.")
    lines += ["", "## Planned topics by family", "", "| Family | Built | Planned |", "|---|---|---|"]
    for family, topics in PLAN.items():
        built = [t for t in topics if (family, t) in index]
        lines.append(f"| {family} | {len(built)} | {len(topics) - len(built)} |")
    lines += [
        "",
        "Planned topics have no directory yet. A directory is created only when a module with a notebook, results and references exists.",
        "The full list is in [`module_registry.csv`](module_registry.csv).",
        "",
    ]
    path = ROOT / "docs" / "project_status.md"
    path.write_text("\n".join(lines))
    return path


def main():
    specs = build_modules.all_specs()
    print("wrote", write_registry(specs).name)
    print("wrote", write_status(specs).name)
    for spec in specs:
        issues = status_problems(spec)
        print(spec["module"], spec["status"], "OK" if not issues else issues)


if __name__ == "__main__":
    main()
