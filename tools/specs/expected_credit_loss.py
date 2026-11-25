"""Spec: IFRS 9 style expected credit loss."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "expected_credit_loss"

SETUP = setup_code(MODULE) + """
from risk_lab.credit.ecl import (
    assign_stage, balance_profile, cumulative_pd, expected_loss, loan_ecl, marginal_pd,
    scenario_weighted,
)"""

S = {}

S[1] = [
    M("""
Under IFRS 9 a bank must book a provision **before** a loss happens. The provision is an expected credit loss (ECL),
and its size depends on the stage of the loan:

* **Stage 1.** Credit risk has not risen much since origination. Provision for losses over the next 12 months.
* **Stage 2.** Credit risk has risen significantly. Provision for losses over the whole remaining life.
* **Stage 3.** The loan is credit impaired. Provision for the loss given default on the full exposure.

This notebook builds a simplified ECL engine, applies it to a synthetic loan book of 5000 loans, and measures three things
that decide how a provision behaves: the staging rule, the macro scenario weights, and the jump (cliff) when a loan moves
from stage 1 to stage 2.

**Decision this supports:** how large the provision is, what drives its change, and how sensitive it is to
judgement calls that the standard leaves to the bank.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Compute ECL for one loan from PD, LGD, EAD, discounting and a balance profile, by hand and with code.
2. Assign stages with a significant increase in credit risk (SICR) test and the days past due rules.
3. Reconcile the engine with closed form special cases.
4. Aggregate ECL by stage and segment, and compute coverage ratios.
5. Probability weight macro scenarios and measure the effect of weights.
6. Measure how sensitive the provision is to the SICR thresholds and to loan term (the cliff).
7. State which parts of the engine are IFRS 9 principles and which are this laboratory's assumptions.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| PD | Probability of default. Here a 12 month PD per loan |
| LGD | Loss given default, a share of exposure that is lost |
| EAD | Exposure at default, the amount owed when default happens |
| EIR | Effective interest rate, used to discount expected losses |
| SICR | Significant increase in credit risk since origination. Moves a loan to stage 2 |
| DPD | Days past due |
| Coverage ratio | ECL divided by EAD |
| Marginal PD | Probability of defaulting inside year t. Computed here as the difference of two cumulative PDs |

**What is principle and what is assumption.** IFRS 9 requires an unbiased, probability weighted, discounted amount that
uses reasonable and supportable information. It also contains a rebuttable presumption that a loan more than 30 days past due
has a significant increase in credit risk, and a presumption of default at 90 days past due. The relative threshold of 2,
the absolute threshold of 0.01, the constant hazard PD curve, the mid year default timing and the scenario weights in this
notebook are **assumptions of this laboratory**, not requirements.
"""),
]

S[4] = [
    M("""
**Why this simplified structure?**

| Option | Strength | Weakness |
|---|---|---|
| Constant hazard from a 12 month PD | One input per loan. Transparent | Ignores that real PD term structures depend on age, macro path and segment |
| Full migration matrix or survival model | Realistic term structure | Needs history that this synthetic book does not have |
| Rule based staging (relative and absolute test plus DPD) | Easy to audit | Creates a cliff at the threshold |

Acceptance criteria, all tested in section 12:

1. For a one year loan in stage 1, ECL equals PD * LGD * EAD discounted half a year (closed form).
2. For stage 3, ECL equals LGD * EAD.
3. For every loan, lifetime ECL is at least 12 month ECL.
4. For every loan, ECL does not exceed EAD.
5. Coverage ratio rises from stage 1 to stage 2 to stage 3 in the total book.
6. Scenario weights sum to 1 and the weighted ECL lies between the lowest and highest scenario ECL.
"""),
]

S[6] = [
    M(r"""
**Cumulative and marginal PD** with a constant annual hazard from a 12 month PD $p$:

$$F(t) = 1 - (1 - p)^t, \qquad m_t = F(t) - F(t-1) = p(1-p)^{t-1}$$

**Balance profile.** For an annuity with $T$ years and rate $r$ the yearly payment is

$$A = \frac{E\,r}{1 - (1 + r)^{-T}}$$

and the balance at the start of year $t$ follows $B_{t+1} = B_t(1 + r) - A$ with $B_1 = E$.

**ECL** over a horizon of $H$ years, with defaults assumed at the middle of each year:

$$\mathrm{ECL} = \sum_{t=1}^{H} m_t \cdot \mathrm{LGD} \cdot B_t \cdot (1 + r)^{-(t - 0.5)}$$

Stage 1 uses $H = 1$. Stage 2 uses $H = T$. Stage 3 uses $\mathrm{ECL} = \mathrm{LGD} \cdot E$.

**Scenario weighting.** With scenarios $s$ and weights $w_s$ that sum to 1:

$$\mathrm{ECL} = \sum_s w_s \cdot \mathrm{ECL}_s$$

Because ECL is not linear in PD, the ECL at the weighted average PD is generally **not** equal to the weighted average of the ECLs.
"""),
]

S[7] = [
    M("""
One loan: EAD 100,000, three years left, EIR 8 percent, annuity repayment, 12 month PD 3 percent, LGD 45 percent.
The table builds each year by hand.
"""),
    C("""
ead, term, eir, pd12, lgd = 100000.0, 3, 0.08, 0.03, 0.45
payment = ead * eir / (1 - (1 + eir) ** (-term))
rows = []
balance = ead
for year in range(1, term + 1):
    cum_now = 1 - (1 - pd12) ** year
    cum_before = 1 - (1 - pd12) ** (year - 1)
    marginal = cum_now - cum_before
    discount = (1 + eir) ** (-(year - 0.5))
    rows.append(
        {"year": year, "balance_start": balance, "marginal_pd": marginal, "discount": discount,
         "loss": marginal * lgd * balance * discount}
    )
    balance = balance * (1 + eir) - payment
by_hand = pd.DataFrame(rows)
print("annual payment:", round(payment, 2))
print(by_hand.round(4).to_string(index=False))
ecl_stage1_hand = by_hand["loss"].iloc[0]
ecl_stage2_hand = by_hand["loss"].sum()
print("stage 1 ECL:", round(ecl_stage1_hand, 2))
print("stage 2 ECL:", round(ecl_stage2_hand, 2))
print("stage 3 ECL:", round(lgd * ead, 2))"""),
    C("""
assert abs(loan_ecl(pd12, lgd, ead, term, eir, 1) - ecl_stage1_hand) < 1e-8
assert abs(loan_ecl(pd12, lgd, ead, term, eir, 2) - ecl_stage2_hand) < 1e-8
assert abs(loan_ecl(pd12, lgd, ead, term, eir, 3) - lgd * ead) < 1e-8
print("library matches the hand table for all three stages")"""),
]

S[8] = [
    C("""
book = pd.read_csv(ROOT / "datasets" / "synthetic" / "loan_book.csv")
print("loans:", len(book), "total EAD:", f"{book['ead'].sum():,.0f}")
print(book.groupby("segment").agg(loans=("loan_id", "size"), ead=("ead", "sum"), mean_pd=("pd_current", "mean"),
                                  mean_lgd=("lgd", "mean"), mean_term=("remaining_years", "mean")).round(3))
print("share with days past due > 0:", round((book["days_past_due"] > 0).mean(), 4))
print(book["days_past_due"].value_counts().sort_index())"""),
]

S[9] = [
    M("""
Stage allocation uses `assign_stage`. A loan is in stage 3 at 90 days past due or more. It is in stage 2 at 30 days past due
or more, or when the current PD is at least twice the origination PD **and** at least 0.01 above it.
Everything else is stage 1. Requiring both the ratio and the gap avoids moving very low PD loans on small absolute changes.
"""),
    C("""
book["stage"] = assign_stage(book["pd_origination"], book["pd_current"], book["days_past_due"])
stage_counts = book["stage"].value_counts().sort_index()
print(stage_counts)
print(pd.crosstab(book["segment"], book["stage"]))
print("EAD share by stage:")
print((book.groupby("stage")["ead"].sum() / book["ead"].sum()).round(4))"""),
]

S[10] = [
    M("""
A loop version of the engine, written separately from `loan_ecl`, applied to every loan. It is slow but easy to read.
It is then compared with the library on the whole book.
"""),
    C("""
def my_ecl(pd12, lgd, ead, term, eir, stage):
    if stage == 3:
        return lgd * ead
    horizon = 1 if stage == 1 else term
    payment = ead * eir / (1 - (1 + eir) ** (-term))
    balance = ead
    total = 0.0
    for year in range(1, horizon + 1):
        marginal = (1 - (1 - pd12) ** year) - (1 - (1 - pd12) ** (year - 1))
        total += marginal * lgd * balance * (1 + eir) ** (-(year - 0.5))
        balance = balance * (1 + eir) - payment
    return total


mine = np.array(
    [my_ecl(r.pd_current, r.lgd, r.ead, int(r.remaining_years), r.eir, int(r.stage)) for r in book.itertuples()]
)
lib = np.array(
    [loan_ecl(r.pd_current, r.lgd, r.ead, int(r.remaining_years), r.eir, int(r.stage)) for r in book.itertuples()]
)
print("max gap between loop engine and library:", f"{np.max(np.abs(mine - lib)):.2e}")
assert np.max(np.abs(mine - lib)) < 1e-6
print("total ECL:", f"{lib.sum():,.0f}")"""),
]

S[11] = [
    M("""
For each loan compute three arrays at once: the 12 month ECL (stage 1 treatment), the lifetime ECL (stage 2 treatment)
and the default ECL (stage 3 treatment). Any staging rule then just picks from these arrays, which makes sensitivity
tests cheap. A PD multiplier scales the PD for macro scenarios.
"""),
    C("""
def all_treatments(frame, pd_multiplier=1.0):
    e1 = np.zeros(len(frame))
    e2 = np.zeros(len(frame))
    e3 = np.zeros(len(frame))
    for i, r in enumerate(frame.itertuples()):
        p = min(r.pd_current * pd_multiplier, 0.999)
        term = int(r.remaining_years)
        e1[i] = loan_ecl(p, r.lgd, r.ead, term, r.eir, 1)
        e2[i] = loan_ecl(p, r.lgd, r.ead, term, r.eir, 2)
        e3[i] = loan_ecl(p, r.lgd, r.ead, term, r.eir, 3)
    return e1, e2, e3


def pick(stages, e1, e2, e3):
    return np.where(stages == 1, e1, np.where(stages == 2, e2, e3))


e1, e2, e3 = all_treatments(book)
book["ecl"] = pick(book["stage"].to_numpy(), e1, e2, e3)
assert np.max(np.abs(book["ecl"].to_numpy() - lib)) < 1e-6
print("treatment arrays reproduce the library ECL")"""),
]

S[12] = [
    M("""
Each acceptance criterion from section 4 is tested on the full book. A failed check stops the notebook.
"""),
    C("""
# closed form checks
one_year = loan_ecl(0.04, 0.5, 1000.0, 1, 0.1, 1)
closed = 0.04 * 0.5 * 1000.0 / (1 + 0.1) ** 0.5
c1 = abs(one_year - closed) < 1e-9
c2 = abs(loan_ecl(0.5, 0.4, 2000.0, 5, 0.07, 3) - 0.4 * 2000.0) < 1e-9

# book wide checks
c3 = bool(np.all(e2 >= e1 - 1e-9))
c4 = bool(np.all(book["ecl"] <= book["ead"] + 1e-9))

summary = book.groupby("stage").agg(loans=("loan_id", "size"), ead=("ead", "sum"), ecl=("ecl", "sum"))
summary["coverage_pct"] = 100 * summary["ecl"] / summary["ead"]
c5 = bool(summary["coverage_pct"].is_monotonic_increasing)
print(summary.round(2))
print("total coverage (percent):", round(100 * book["ecl"].sum() / book["ead"].sum(), 3))
checks = {
    "one_year_closed_form": c1,
    "stage3_equals_lgd_times_ead": c2,
    "lifetime_at_least_12m": c3,
    "ecl_not_above_ead": c4,
    "coverage_rises_with_stage": c5,
}
print(checks)
assert all(checks.values())"""),
    C("""
by_segment = book.groupby(["segment", "stage"]).agg(ead=("ead", "sum"), ecl=("ecl", "sum"))
by_segment["coverage_pct"] = 100 * by_segment["ecl"] / by_segment["ead"]
print(by_segment.round(2))"""),
]

S[13] = [
    C("""
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
stage_ecl = summary["ecl"] / 1e6
axes[0].bar(stage_ecl.index.astype(str), stage_ecl.values, color=[COLORS["main"], COLORS["third"], COLORS["second"]])
axes[0].set_xlabel("stage")
axes[0].set_ylabel("ECL (millions)")
axes[0].set_title("ECL by stage")

counts = summary["loans"]
axes[1].bar(counts.index.astype(str), counts.values, color=[COLORS["main"], COLORS["third"], COLORS["second"]])
axes[1].set_xlabel("stage")
axes[1].set_ylabel("loans")
axes[1].set_title("Loans by stage")

sorted_ecl = np.sort(book["ecl"].to_numpy())[::-1]
axes[2].plot(np.arange(1, len(sorted_ecl) + 1) / len(sorted_ecl), np.cumsum(sorted_ecl) / sorted_ecl.sum(), color=COLORS["main"])
axes[2].plot([0, 1], [0, 1], color=COLORS["grey"], linestyle=":")
axes[2].set_xlabel("share of loans, largest ECL first")
axes[2].set_ylabel("share of total ECL")
axes[2].set_title("Concentration of ECL")
save_figure(fig, MODULE, "ecl_overview.png")
plt.show()"""),
]

S[14] = [
    M("""
How to read the numbers:

* **Coverage ratio by stage.** Stage 1 is small because only 12 months of losses count. Stage 2 is larger because the full life counts and PDs are higher. Stage 3 equals the average LGD of those loans.
* **Concentration.** If a small share of loans holds most of the ECL, the provision depends on a few LGD and PD judgements.
* **Stage 3.** These loans are already in default, so ECL is not an estimate of a probability. It is an estimate of loss severity, and LGD carries all the uncertainty.
"""),
    C("""
top_share = float(sorted_ecl[: int(0.05 * len(sorted_ecl))].sum() / sorted_ecl.sum())
stage3 = book[book["stage"] == 3]
print("share of total ECL held by the top 5 percent of loans:", round(top_share, 4))
print("stage 3 share of total ECL:", round(float(stage3["ecl"].sum() / book["ecl"].sum()), 4))
print("stage 3 coverage equals EAD weighted LGD:", round(float(stage3["ecl"].sum() / stage3["ead"].sum()), 4),
      round(float((stage3["lgd"] * stage3["ead"]).sum() / stage3["ead"].sum()), 4))"""),
]

S[15] = [
    M("""
**Experiment A: scenario weights.** Three scenarios multiply every loan's PD: upside 0.8, base 1.0, downside 1.6.
Weights 0.2, 0.5 and 0.3 are an assumption. Staging is held at the base case, which is a simplification. The experiment
also compares the weighted ECL with the ECL at the weighted average PD multiplier.

**Experiment B: SICR thresholds.** Vary the relative threshold (1.5, 2, 3) and the absolute threshold (0.005, 0.01, 0.02).

**Experiment C: the cliff.** Same loan, stage 1 against stage 2, for different remaining terms.
"""),
    C("""
multipliers = {"upside": 0.8, "base": 1.0, "downside": 1.6}
weights = {"upside": 0.2, "base": 0.5, "downside": 0.3}
stages_base = book["stage"].to_numpy()
scenario_totals = {}
for name, mult in multipliers.items():
    s1, s2, s3 = all_treatments(book, mult)
    scenario_totals[name] = float(pick(stages_base, s1, s2, s3).sum())
weighted = scenario_weighted(list(scenario_totals.values()), list(weights.values()))
mean_mult = sum(multipliers[k_] * weights[k_] for k_ in multipliers)
a1, a2, a3 = all_treatments(book, mean_mult)
at_mean_pd = float(pick(stages_base, a1, a2, a3).sum())
scen = pd.DataFrame({"multiplier": multipliers, "weight": weights, "ecl": scenario_totals})
print(scen.round(2))
print("probability weighted ECL:", f"{weighted:,.0f}")
print("ECL at the weighted average PD multiplier:", f"{at_mean_pd:,.0f}")
print("difference (weighted minus at mean PD):", f"{weighted - at_mean_pd:,.0f}")
assert min(scenario_totals.values()) <= weighted <= max(scenario_totals.values())"""),
    C("""
rows = []
for rel in [1.5, 2.0, 3.0]:
    for gap in [0.005, 0.01, 0.02]:
        st = assign_stage(book["pd_origination"], book["pd_current"], book["days_past_due"], relative_threshold=rel, absolute_threshold=gap)
        total = float(pick(st, e1, e2, e3).sum())
        rows.append({"relative": rel, "absolute": gap, "stage2_share": float((st == 2).mean()), "total_ecl": total})
sicr = pd.DataFrame(rows)
base_total = float(book["ecl"].sum())
sicr["change_vs_base_pct"] = 100 * (sicr["total_ecl"] / base_total - 1)
print(sicr.round(4).to_string(index=False))"""),
    C("""
rows = []
for term_years in [1, 2, 3, 5, 10, 20]:
    s1 = loan_ecl(0.03, 0.45, 100000.0, term_years, 0.08, 1)
    s2 = loan_ecl(0.03, 0.45, 100000.0, term_years, 0.08, 2)
    rows.append({"remaining_years": term_years, "stage1_ecl": s1, "stage2_ecl": s2, "jump_ratio": s2 / s1})
cliff = pd.DataFrame(rows)
print(cliff.round(3).to_string(index=False))"""),
]

S[16] = [
    C("""
print(summary.round(2))
print()
print(scen.round(2))
print()
print(checks)
metrics = {
    "total_ead": float(book["ead"].sum()),
    "total_ecl": float(book["ecl"].sum()),
    "coverage_pct": float(100 * book["ecl"].sum() / book["ead"].sum()),
    "by_stage": summary.reset_index().to_dict(orient="records"),
    "scenario_ecl": scenario_totals,
    "scenario_weights": weights,
    "probability_weighted_ecl": weighted,
    "ecl_at_weighted_mean_pd": at_mean_pd,
    "sicr_sensitivity": sicr.to_dict(orient="records"),
    "cliff_by_remaining_years": cliff.to_dict(orient="records"),
    "top_5pct_loans_share_of_ecl": top_share,
    "acceptance_checks": checks,
    "max_gap_loop_vs_library": float(np.max(np.abs(mine - lib))),
}
config = {
    "relative_threshold": 2.0, "absolute_threshold": 0.01, "dpd_stage2": 30, "dpd_stage3": 90,
    "scenario_multipliers": multipliers, "scenario_weights": weights,
    "default_timing": "middle of year", "pd_term_structure": "constant annual hazard",
}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Simplified IFRS 9 three stage ECL with constant hazard PD, annuity balance profile, mid year default timing and scenario weighting",
    data_kind="synthetic",
    dataset="datasets/synthetic/loan_book.csv",
    n_obs=int(len(book)),
    seed=7,
    parameters=config,
    assumptions=[
        "12 month PD per loan is given and a constant hazard extends it to lifetime",
        "thresholds, scenario multipliers and weights are laboratory assumptions",
        "staging held at the base case in every scenario",
        "balance at the start of each year is the exposure at default",
    ],
    metrics=metrics,
    baseline={"all_loans_treated_as_stage_1_ecl": float(e1.sum()), "note": "12 month ECL with no staging"},
    limitations=[
        "no collateral timing, no cure rates, no prepayment, no off balance sheet exposure",
        "constant hazard ignores the PD term structure",
        "synthetic book, not a real portfolio",
    ],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
**Limitations**

1. **Constant hazard.** A real lifetime PD depends on loan age, macro path and segment. A constant hazard understates stage 2 ECL when risk rises with time and overstates it when risk falls.
2. **Stage held at base case across scenarios.** In practice SICR is assessed with forward looking information, so staging itself is scenario dependent.
3. **Cliff.** The jump ratio table shows stage 2 ECL can be several times stage 1 ECL for the same loan. The rule based staging transmits a small PD change into a large provision change.
4. **No collateral cash flow timing, cures, prepayments or undrawn commitments.** LGD is a given number.
5. **Parameters are assumptions.** Thresholds, scenario multipliers and weights are lab choices. IFRS 9 leaves the design to the entity, and the IASB post implementation review reports wide practice differences.
6. **Synthetic book.** Segment shares, PDs and LGDs are invented.

**Check against the standard.** Paragraph level references to IFRS 9 are not stated here because they were not verified.
Read section 5.5 of the standard before using any rule in practice.

**Model risk.** The engine is simple and reconciled, but the risk lies in inputs: PD, LGD and the scenario weights drive the result.
Overlay and governance decisions are outside this notebook.
"""),
]

S[18] = [
    M("""
**What staging adds.** The naive alternative is to give every loan a 12 month provision. The difference between the staged
provision and the naive one is the amount that the lifetime rule adds for stage 2 plus the move to full loss for stage 3.
A finance team reads this as the provision cost of credit deterioration in the book.

**Which loans drive it.** The table lists the ten loans with the largest ECL and how much of the total they hold.
"""),
    C("""
naive = float(e1.sum())
staged = float(book["ecl"].sum())
print("12 month ECL on every loan:", f"{naive:,.0f}")
print("staged ECL:", f"{staged:,.0f}")
print("added by staging:", f"{staged - naive:,.0f}", "which is", round(100 * (staged / naive - 1), 1), "percent more")
top = book.sort_values("ecl", ascending=False).head(10)[["loan_id", "segment", "stage", "ead", "lgd", "pd_current", "ecl"]]
print(top.round(3).to_string(index=False))
print("share of total ECL in these ten loans:", round(float(top["ecl"].sum() / staged), 4))"""),
]

S[19] = [
    M("""
1. Change the stage 2 days past due trigger from 30 to 15 days. How many loans move and what is the change in total ECL?
2. Replace the constant hazard with a hazard that rises 10 percent per year. Re derive the marginal PD and recompute the hand table in section 7.
3. Add a fourth scenario with weight 0.1 and multiplier 2.5, and rescale the others so the weights sum to 1. Report the change in weighted ECL.
4. Take the loan in section 7 and find the PD at which stage 2 ECL equals 2 times stage 1 ECL.
5. Suppose LGD is uncertain by plus or minus 10 points. Report the range of total ECL and say which stage it affects most.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "02_credit_risk/expected_credit_loss",
        "title": "Expected Credit Loss under IFRS 9 (Simplified)",
        "family": "Credit Risk",
        "level": "Intermediate",
        "dataset": "loan_book",
        "data_kind": "synthetic",
        "status": "Complete",
        "tagline": "Stage a loan book, compute ECL, weight macro scenarios and measure the cliff and the sensitivities.",
        "refs": ["ifrs9", "iasb_pir2024", "bcbs_d424", "sr262"],
        "research_note": (
            "IFRS 9 section 5.5 defines the principles. The IASB post implementation review summarises how entities apply them and "
            "where practice differs. Neither document gives numeric thresholds, so every number used here is labelled as an assumption. "
            "Paragraph numbers are not quoted because they were not verified."
        ),
        "learn": [
            "ECL formula with balance profile and discounting",
            "Stage allocation with SICR and days past due",
            "Closed form checks and a second implementation as a control",
            "Scenario weighting and non linearity",
            "Sensitivity to SICR thresholds and the stage 1 to stage 2 cliff",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
