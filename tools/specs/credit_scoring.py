"""Spec: credit scorecard with weight of evidence."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "credit_scoring"

SETUP = setup_code(MODULE) + """
from scipy.optimize import brentq

from risk_lab.credit.logistic import fit_logistic, predict_proba, sigmoid, standard_errors
from risk_lab.credit.metrics import (
    brier_score, calibration_table, gini, ks_statistic, population_stability_index, roc_auc,
)
from risk_lab.credit.woe import (
    apply_woe, information_value, make_bin_edges, probability_to_score, scaling_constants, woe_table,
)
from risk_lab.data.synthetic import make_retail_loans"""

S = {}

S[1] = [
    M("""
A lender wants a decision tool that a credit officer, an auditor and a regulator can all read:
**a points based scorecard.** Each borrower characteristic is cut into bins, each bin earns points, and the
total is the score. The score must (a) rank bad borrowers below good ones, (b) map to a known default odds,
and (c) stay stable after launch.

This notebook builds that scorecard from raw data. It uses weight of evidence (WoE) binning, a logistic
regression on the WoE values, and the standard points scaling. It then tests the scorecard on a held out
sample and on a **later, riskier sample** to see what happens when the population drifts.

**Decision this supports:** whether to launch the scorecard, where to set the approval cutoff,
and what monitoring rule triggers a review.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Compute WoE and information value (IV) for a characteristic, by hand and with code.
2. Select characteristics by IV and check that WoE is monotone where business logic requires it.
3. Fit a logistic regression on WoE and convert it into integer scorecard points.
4. Prove that the points reproduce the model probability, and measure the rounding error.
5. Evaluate ranking on test data and on a drifted monitoring sample.
6. Use the population stability index (PSI) as a drift signal and test its limits.
7. Recalibrate the intercept after drift and measure what it fixes and what it cannot fix.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Bin | A range of a characteristic, for example debt to income between 0.20 and 0.30 |
| WoE | ln(share of goods in the bin / share of bads in the bin). Higher means safer |
| IV | Sum over bins of (share of goods - share of bads) * WoE. A measure of the power of one characteristic |
| Scorecard points | Integer points per bin. The score is the sum of points |
| Base score, base odds, PDO | Calibration anchors. Here 600 points at 50 to 1 good to bad odds, and 20 points to double the odds |
| PSI | Population stability index. Compares the distribution of a score or characteristic between two samples |

Odds convention in this notebook: **good to bad**. A score of 600 means 50 goods for every 1 bad,
so PD is 1 / 51.
"""),
]

S[4] = [
    M("""
**Why a WoE scorecard instead of a raw logistic regression?**

| Option | Strength | Weakness |
|---|---|---|
| WoE scorecard | Handles non linear effects with bins. Missing values and outliers get their own bin. Output is a transparent table | Information is lost inside bins. Bin choices need judgement |
| Raw logistic regression | No binning loss. Simple | Linear in each feature. Outliers act directly on the score |
| Machine learning model | Can find interactions | Needs explainability work. Benchmarks do not show a guaranteed advantage on every dataset (see Section 5) |

Acceptance criteria on the test set:

1. Scorecard AUC within 0.01 of the raw logistic regression on the same train and test split.
2. Sum of integer points reproduces the model score within half a point per characteristic times the number of characteristics.
3. Score PSI between development and monitoring reported and compared with a documented rule of thumb.

The IV selection cutoff of 0.02 and the PSI bands 0.10 and 0.25 are **practitioner rules of thumb**.
They are not set by a regulator, and their source is not verified in this build.
"""),
]

S[6] = [
    M(r"""
For one characteristic with bins $b = 1 \dots B$, let $g_b$ and $d_b$ be the number of goods and bads, and
$G = \sum g_b$, $D = \sum d_b$.

$$\mathrm{WoE}_b = \ln\frac{g_b / G}{d_b / D}, \qquad \mathrm{IV} = \sum_b \left(\frac{g_b}{G} - \frac{d_b}{D}\right)\mathrm{WoE}_b$$

Each term of IV is non negative, so IV is non negative. WoE here is smoothed by adding 0.5 to each cell so an empty cell
does not give an infinite value.

The model on WoE inputs $w_{ij}$ (characteristic $j$, borrower $i$):

$$\ln\frac{p_i}{1 - p_i} = a + \sum_{j=1}^{k} b_j w_{ij}$$

Because WoE is defined as good over bad, a good model has **negative** $b_j$.

Scaling. Let the score be linear in the log odds of being good:

$$\mathrm{score} = \mathrm{offset} + \mathrm{factor}\cdot\ln\!\big(\text{odds}_{good}\big), \quad \mathrm{factor} = \frac{\mathrm{PDO}}{\ln 2}, \quad \mathrm{offset} = S_0 - \mathrm{factor}\cdot\ln(\text{odds}_0)$$

Since $\ln \text{odds}_{good} = -(a + \sum_j b_j w_{ij})$, the points for bin $w$ of characteristic $j$ are

$$\mathrm{points}_{j}(w) = -\mathrm{factor}\left(b_j w + \frac{a}{k}\right) + \frac{\mathrm{offset}}{k}$$

PSI between an expected (reference) share $e_i$ and an actual share $a_i$ over bins $i$:

$$\mathrm{PSI} = \sum_i (a_i - e_i)\ln\frac{a_i}{e_i}$$
"""),
]

S[7] = [
    M("""
**Part A. WoE and IV by hand** on three bins: goods 700, 200, 100 and bads 100, 100, 100.
"""),
    C("""
goods = np.array([700.0, 200.0, 100.0])
bads = np.array([100.0, 100.0, 100.0])
good_share = goods / goods.sum()
bad_share = bads / bads.sum()
woe_hand = np.log(good_share / bad_share)
iv_hand = np.sum((good_share - bad_share) * woe_hand)
print("WoE by bin:", woe_hand.round(4))
print("IV:", round(float(iv_hand), 5))

# same data through the library
values = np.repeat([1, 2, 3], (goods + bads).astype(int))
target = np.concatenate([np.r_[np.zeros(int(g)), np.ones(int(b))] for g, b in zip(goods, bads)])
edges = np.array([-np.inf, 1.5, 2.5, np.inf])
table = woe_table(values, target, edges, smoothing=0.0)
print("library WoE:", table["woe"].to_numpy().round(4))
assert np.allclose(table["woe"], woe_hand)
assert abs(information_value(table) - iv_hand) < 1e-12"""),
    M("""
**Part B. Scaling anchors.** With base score 600, base odds 50 to 1 and PDO 20, the factor and offset follow.
A PD of 1/51 must score 600. A PD of 1/101 (odds 100 to 1, twice as good) must score 620.
"""),
    C("""
factor, offset = scaling_constants(600, 50, 20)
print("factor:", round(factor, 4), "offset:", round(offset, 4))
print("score at PD 1/51:", round(float(probability_to_score(1 / 51)), 6))
print("score at PD 1/101:", round(float(probability_to_score(1 / 101)), 6))
assert abs(float(probability_to_score(1 / 51)) - 600) < 1e-9
assert abs(float(probability_to_score(1 / 101)) - 620) < 1e-9"""),
]

S[8] = [
    C("""
dev = pd.read_csv(ROOT / "datasets" / "synthetic" / "retail_loans_dev.csv")
monitor = pd.read_csv(ROOT / "datasets" / "synthetic" / "retail_loans_monitoring.csv")
print("development rows:", len(dev), "default rate:", round(dev["default_12m"].mean(), 4))
print("monitoring rows:", len(monitor), "default rate:", round(monitor["default_12m"].mean(), 4))
compare = pd.DataFrame({"dev_mean": dev.mean(numeric_only=True), "monitor_mean": monitor.mean(numeric_only=True)})
compare["relative_change_pct"] = 100 * (compare["monitor_mean"] / compare["dev_mean"] - 1)
print(compare.drop(index=["loan_id"]).round(3))"""),
    M("""
The monitoring sample is generated with a drift setting that moves borrowers toward higher debt, higher utilisation,
lower income and more delinquencies. Its true default process is **unchanged**. Only the mix of borrowers moved.
That is a covariate shift, the easier case. Real drift often changes the relationship itself.
"""),
]

S[9] = [
    M("""
1. Split the development sample 70 percent train and 30 percent test. Bin edges, WoE tables and the model use **train only**.
2. Candidate characteristics: all eleven numeric columns. `age`, `employment_years`, `loan_amount` and `term_months` have no true effect in the generator. The IV filter should drop them.
3. Quantile bins, six per characteristic. Duplicate edges are merged, so a count like delinquencies gets fewer bins.
"""),
    C("""
rng = np.random.default_rng(SEED)
order = rng.permutation(len(dev))
n_train = int(0.7 * len(dev))
train = dev.iloc[order[:n_train]].reset_index(drop=True)
test = dev.iloc[order[n_train:]].reset_index(drop=True)
y_train = train["default_12m"].to_numpy()
y_test = test["default_12m"].to_numpy()
y_monitor = monitor["default_12m"].to_numpy()

candidates = ["age", "income", "employment_years", "credit_history_years", "dti", "utilization",
              "ltv", "delinq_2y", "loan_amount", "term_months", "interest_rate"]
MIN_IV = 0.02
print("train:", len(train), "test:", len(test), "monitoring:", len(monitor))"""),
]

S[10] = [
    M("""
The function below does the whole build for a chosen number of bins: edges, WoE tables, IV filter, logistic fit,
and points. It uses only train data. Every step uses a function whose maths is in section 6.
"""),
    C("""
def build_scorecard(frame, n_bins=6, min_iv=MIN_IV):
    labels = frame["default_12m"]
    edges, tables, ivs = {}, {}, {}
    for name in candidates:
        edges[name] = make_bin_edges(frame[name], n_bins)
        tables[name] = woe_table(frame[name], labels, edges[name])
        ivs[name] = information_value(tables[name])
    selected = [name for name in candidates if ivs[name] >= min_iv]
    x_train = np.column_stack([apply_woe(frame[n], edges[n], tables[n]) for n in selected])
    fit = fit_logistic(x_train, labels.to_numpy())
    return {"edges": edges, "tables": tables, "iv": ivs, "selected": selected, "fit": fit, "n_bins": n_bins}


def transform(card, frame):
    cols = [apply_woe(frame[n], card["edges"][n], card["tables"][n]) for n in card["selected"]]
    return np.column_stack(cols)


def score_frame(card, frame):
    prob = predict_proba(transform(card, frame), card["fit"]["intercept"], card["fit"]["slopes"])
    return prob, probability_to_score(prob)


card = build_scorecard(train, 6)
iv_table = pd.Series(card["iv"]).sort_values(ascending=False).to_frame("iv")
iv_table["selected"] = iv_table.index.isin(card["selected"])
print(iv_table.round(4))
print("selected:", card["selected"])"""),
    C("""
# coefficients on woe
se = standard_errors(transform(card, train), card["fit"]["intercept"], card["fit"]["slopes"])
coef = pd.DataFrame(
    {"slope": card["fit"]["slopes"], "std_error": se[1:]}, index=card["selected"]
)
print("intercept:", round(card["fit"]["intercept"], 4))
print(coef.round(4))
print("all slopes negative:", bool((coef["slope"] < 0).all()))"""),
    C("""
# points per bin
k = len(card["selected"])
factor, offset = scaling_constants(600, 50, 20)
intercept = card["fit"]["intercept"]
point_rows = []
for name, slope in zip(card["selected"], card["fit"]["slopes"]):
    table = card["tables"][name]
    for row in table.itertuples():
        points = -factor * (slope * row.woe + intercept / k) + offset / k
        point_rows.append(
            {"characteristic": name, "bin": str(row.bin), "count": row.total, "bad_rate": row.bad_rate,
             "woe": row.woe, "points": points}
        )
points_table = pd.DataFrame(point_rows)
points_table["points_int"] = points_table["points"].round().astype(int)
print(points_table.round(3).to_string(index=False))"""),
    C("""
# check points sum
def points_score(frame, use_integer):
    total = np.zeros(len(frame))
    column = "points_int" if use_integer else "points"
    for name in card["selected"]:
        table = card["tables"][name]
        bins = pd.cut(frame[name].reset_index(drop=True), bins=card["edges"][name], include_lowest=True)
        sub = points_table[points_table["characteristic"] == name]
        lookup = dict(zip(table["bin"], sub[column].to_numpy()))
        total += bins.map(lookup).astype(float).to_numpy()
    return total

prob_test, score_test = score_frame(card, test)
exact = points_score(test, False)
rounded = points_score(test, True)
print("max gap, unrounded points vs model score:", f"{np.max(np.abs(exact - score_test)):.2e}")
print("max gap, integer points vs model score:", round(float(np.max(np.abs(rounded - score_test))), 3))
assert np.max(np.abs(exact - score_test)) < 1e-6
assert np.max(np.abs(rounded - score_test)) <= 0.5 * k"""),
]

S[11] = [
    M("""
Library cross check. A scikit-learn logistic regression on the same WoE columns must give the same coefficients.
Then a raw feature logistic regression (the baseline for acceptance criterion 1) is fitted on standardised raw columns.
"""),
    C("""
from sklearn.linear_model import LogisticRegression

xw_train = transform(card, train)
sk = LogisticRegression(C=np.inf, max_iter=2000, tol=1e-10).fit(xw_train, y_train)
mine = np.concatenate([[card["fit"]["intercept"]], card["fit"]["slopes"]])
gap = np.max(np.abs(np.concatenate([sk.intercept_, sk.coef_[0]]) - mine))
print("max coefficient gap vs scikit-learn:", f"{gap:.2e}")
assert gap < 1e-3

raw_train = train[card["selected"]]
raw_mean, raw_std = raw_train.mean(), raw_train.std()
raw_fit = fit_logistic(((raw_train - raw_mean) / raw_std).to_numpy(), y_train)
p_raw_test = predict_proba(((test[card["selected"]] - raw_mean) / raw_std).to_numpy(), raw_fit["intercept"], raw_fit["slopes"])
print("raw logistic test AUC:", round(roc_auc(y_test, p_raw_test), 4))"""),
]

S[12] = [
    M("""
Score is high for good borrowers, so the risk score used for AUC, Gini and KS is the negative of the score.
"""),
    C("""
prob_train, score_train = score_frame(card, train)
prob_monitor, score_monitor = score_frame(card, monitor)

def summary(name, y, prob, score):
    return {
        "sample": name,
        "n": len(y),
        "observed_default_rate": float(np.mean(y)),
        "mean_predicted_pd": float(np.mean(prob)),
        "auc": roc_auc(y, -score),
        "gini": gini(y, -score),
        "ks": ks_statistic(y, -score),
        "brier": brier_score(y, prob),
    }

evaluation = pd.DataFrame(
    [summary("train", y_train, prob_train, score_train),
     summary("test", y_test, prob_test, score_test),
     summary("monitoring", y_monitor, prob_monitor, score_monitor)]
).set_index("sample")
print(evaluation.round(4))"""),
    C("""
auc_card = float(evaluation.loc["test", "auc"])
auc_raw = roc_auc(y_test, p_raw_test)
psi_score = population_stability_index(score_train, score_monitor)
psi_test = population_stability_index(score_train, score_test)
criteria = {
    "auc_within_0.01_of_raw_logistic": abs(auc_card - auc_raw) <= 0.01,
    "integer_points_within_rounding_bound": bool(np.max(np.abs(rounded - score_test)) <= 0.5 * k),
    "psi_reported": True,
}
print("scorecard test AUC:", round(auc_card, 4), "raw logistic test AUC:", round(auc_raw, 4))
print("score PSI, train vs test:", round(psi_test, 4))
print("score PSI, train vs monitoring:", round(psi_score, 4))
print(criteria)"""),
]

S[13] = [
    C("""
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
axes[0].hist(score_train, bins=40, alpha=0.6, density=True, color=COLORS["main"], label="train")
axes[0].hist(score_monitor, bins=40, alpha=0.6, density=True, color=COLORS["second"], label="monitoring")
axes[0].set_xlabel("score")
axes[0].set_title("Score distribution")
axes[0].legend()

iv_plot = iv_table["iv"].sort_values()
colors = [COLORS["main"] if s else COLORS["grey"] for s in iv_table.loc[iv_plot.index, "selected"]]
axes[1].barh(iv_plot.index, iv_plot.values, color=colors)
axes[1].axvline(MIN_IV, color=COLORS["second"], linestyle="--")
axes[1].set_xlabel("information value")
axes[1].set_title("IV by characteristic")

example = card["tables"]["dti"]
axes[2].bar(range(len(example)), example["woe"], color=COLORS["main"])
axes[2].set_xticks(range(len(example)))
axes[2].set_xticklabels([f"bin {i + 1}" for i in range(len(example))])
axes[2].set_ylabel("WoE")
axes[2].set_title("WoE by bin, debt to income")
save_figure(fig, MODULE, "scorecard_overview.png")
plt.show()"""),
    C("""
cal_test = pd.DataFrame(calibration_table(y_test, prob_test, 10))
cal_monitor = pd.DataFrame(calibration_table(y_monitor, prob_monitor, 10))
fig, ax = plt.subplots()
lim = max(cal_monitor["mean_predicted"].max(), cal_monitor["observed_rate"].max()) * 1.05
ax.plot([0, lim], [0, lim], color=COLORS["grey"], linestyle=":")
ax.plot(cal_test["mean_predicted"], cal_test["observed_rate"], marker="o", color=COLORS["main"], label="test")
ax.plot(cal_monitor["mean_predicted"], cal_monitor["observed_rate"], marker="s", color=COLORS["second"], label="monitoring")
ax.set_xlabel("mean predicted PD")
ax.set_ylabel("observed default rate")
ax.set_title("Calibration by decile")
ax.legend()
save_figure(fig, MODULE, "calibration_test_vs_monitoring.png")
plt.show()"""),
]

S[14] = [
    M("""
What to read from the output below:

* **WoE monotonicity.** For a characteristic where more risk should mean more default (debt to income, utilisation), WoE should fall as the bin rises. A reversal needs a business reason or a re binning.
* **Characteristics with no true effect** should fall below the IV cutoff. A noise variable can pass by chance. The IV table shows how close each one is.
* **Monitoring sample.** The score distribution shifts toward lower scores, so PSI rises. Ranking ability (AUC) is a separate question from calibration, and the notebook measures both.

**Outcome of acceptance criterion 1 on the executed run: not met.** The scorecard ranks worse than the raw logistic
regression by about 0.02 AUC, which is above the 0.01 tolerance fixed in section 4 before the run. The threshold is
not changed after the fact. The likely cause is information lost inside six quantile bins, and Experiment A shows AUC
moves with the number of bins. Two characteristics also have non monotone WoE, which suggests bins that are too fine
for the number of bads per bin. Merging bins (coarse classing) is the standard remedy and is left as an exercise.
"""),
    C("""
rows = []
for name in card["selected"]:
    woe_values = card["tables"][name]["woe"].to_numpy()
    rows.append(
        {
            "characteristic": name,
            "bins": len(woe_values),
            "woe_falls_with_bin": bool(np.all(np.diff(woe_values) <= 0)),
            "woe_rises_with_bin": bool(np.all(np.diff(woe_values) >= 0)),
        }
    )
mono = pd.DataFrame(rows)
mono["monotone"] = mono["woe_falls_with_bin"] | mono["woe_rises_with_bin"]
print(mono.to_string(index=False))
noise = ["age", "employment_years", "loan_amount", "term_months"]
print("noise characteristics selected:", [n for n in noise if n in card["selected"]])
print("noise IV values:", {n: round(card["iv"][n], 4) for n in noise})
print("calibration gap on monitoring (pred minus observed):",
      round(float(evaluation.loc["monitoring", "mean_predicted_pd"] - evaluation.loc["monitoring", "observed_default_rate"]), 4))"""),
]

S[15] = [
    M("""
**Experiment A: number of bins.** Rebuild the scorecard with 3, 5, 8 and 12 bins. Record selected count, total IV
of selected characteristics and test AUC.

**Experiment B: drift strength.** Generate fresh samples of 6000 loans with drift 0, 0.5, 1.0 and 1.5 from the same
generator (new seeds), score them with the **fixed** scorecard, and record PSI, AUC and the calibration gap.
"""),
    C("""
rows = []
for n_bins in [3, 5, 8, 12]:
    alt = build_scorecard(train, n_bins)
    prob_alt, score_alt = score_frame(alt, test)
    rows.append(
        {
            "n_bins": n_bins,
            "selected": len(alt["selected"]),
            "iv_sum_selected": sum(alt["iv"][n] for n in alt["selected"]),
            "test_auc": roc_auc(y_test, -score_alt),
        }
    )
bins_table = pd.DataFrame(rows)
print(bins_table.round(4).to_string(index=False))"""),
    C("""
rows = []
for index, drift in enumerate([0.0, 0.5, 1.0, 1.5]):
    sample = make_retail_loans(n_loans=6000, seed=500 + index, drift=drift)
    prob_s, score_s = score_frame(card, sample)
    y_s = sample["default_12m"].to_numpy()
    rows.append(
        {
            "drift": drift,
            "psi_score": population_stability_index(score_train, score_s),
            "auc": roc_auc(y_s, -score_s),
            "observed_rate": float(y_s.mean()),
            "mean_predicted": float(prob_s.mean()),
        }
    )
drift_table = pd.DataFrame(rows)
drift_table["calibration_gap"] = drift_table["mean_predicted"] - drift_table["observed_rate"]
print(drift_table.round(4).to_string(index=False))"""),
    C("""
fig, ax = plt.subplots()
ax.plot(drift_table["drift"], drift_table["psi_score"], marker="o", color=COLORS["main"], label="score PSI")
ax.axhline(0.10, color=COLORS["grey"], linestyle=":")
ax.axhline(0.25, color=COLORS["grey"], linestyle=":")
ax.set_xlabel("drift setting")
ax.set_ylabel("PSI")
ax.set_title("Score PSI against drift strength")
ax.legend()
save_figure(fig, MODULE, "psi_by_drift.png")
plt.show()"""),
]

S[16] = [
    C("""
print(evaluation.round(4))
print()
print(criteria)
print("selected characteristics:", card["selected"])
print("points range (min and max total):", round(float(score_test.min()), 1), round(float(score_test.max()), 1))"""),
    C("""
metrics = {
    "selected_characteristics": card["selected"],
    "iv": {k_: float(v_) for k_, v_ in card["iv"].items()},
    "scaling": {"factor": factor, "offset": offset, "base_score": 600, "base_odds_good_to_bad": 50, "pdo": 20},
    "evaluation": evaluation.reset_index().to_dict(orient="records"),
    "raw_logistic_test_auc": float(auc_raw),
    "score_psi_train_vs_test": float(psi_test),
    "score_psi_train_vs_monitoring": float(psi_score),
    "max_gap_integer_points": float(np.max(np.abs(rounded - score_test))),
    "number_of_bins_experiment": bins_table.to_dict(orient="records"),
    "drift_experiment": drift_table.to_dict(orient="records"),
    "monotone_characteristics": mono.to_dict(orient="records"),
    "acceptance_criteria": criteria,
}
config = {"n_bins": 6, "min_iv": MIN_IV, "base_score": 600, "base_odds": 50, "pdo": 20, "train_share": 0.7, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="WoE binning, logistic regression on WoE, linear points scaling, evaluation on test and drifted samples",
    data_kind="synthetic",
    dataset="datasets/synthetic/retail_loans_dev.csv and retail_loans_monitoring.csv",
    n_obs=int(len(dev) + len(monitor)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "good to bad odds convention",
        "IV cutoff 0.02 and PSI bands 0.10 and 0.25 are practitioner rules of thumb, not verified",
        "monitoring sample has covariate shift only, the true default process is unchanged",
    ],
    metrics=metrics,
    baseline={"raw_logistic_test_auc": float(auc_raw)},
    limitations=[
        "synthetic data",
        "covariate shift only, no concept drift",
        "no reject inference, no segmentation",
    ],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
**Limitations**

1. **Binning loss.** Information inside each bin is thrown away. On the executed run the scorecard ranked about 0.02 AUC below the raw logistic regression, so acceptance criterion 1 was not met. Experiment A shows the effect moves with the number of bins. This is one dataset only.
2. **Rules of thumb.** IV 0.02 and PSI bands 0.10 and 0.25 are conventions. A PSI below the band does not prove the model still works, and a PSI above it does not prove the model failed. Experiment B shows ranking can survive a large PSI.
3. **Covariate shift only.** Real deterioration often changes how features relate to default. A scorecard can then lose AUC while PSI looks fine.
4. **No reject inference.** A real scorecard is built only on approved loans, which biases the sample. This dataset has no rejected applicants.
5. **No segmentation, no interaction terms.** One scorecard for the whole book.
6. **Rounding.** Integer points are a presentation choice. The rounding bound is tested above.

**Model risk.** The main operational risk is trusting PSI as the only monitor. A monitoring pack also needs
observed default rate against predicted PD, rank order stability, and characteristic level drift.
Independent validation is still required before any real use.
"""),
]

S[18] = [
    M("""
**Cutoff policy.** Choose a score cutoff. The table lists approval rate and bad rate among the approved loans
on the test sample.

**Recalibration after drift.** On the monitoring sample, shift the intercept so that mean predicted PD equals the
observed default rate. This fixes **level** only. It cannot restore ranking if ranking has degraded.
Recalibrating on the same sample it is scored on is for illustration. Real practice uses an out of time sample.
"""),
    C("""
rows = []
for cutoff in [540, 560, 580, 600, 620, 640]:
    approved = score_test >= cutoff
    rows.append(
        {
            "cutoff": cutoff,
            "approval_rate": float(approved.mean()),
            "bad_rate_approved": float(y_test[approved].mean()) if approved.any() else np.nan,
            "bad_rate_rejected": float(y_test[~approved].mean()) if (~approved).any() else np.nan,
        }
    )
print(pd.DataFrame(rows).round(4).to_string(index=False))"""),
    C("""
logit_monitor = np.log(prob_monitor / (1 - prob_monitor))
target_rate = float(y_monitor.mean())
shift = brentq(lambda d: np.mean(sigmoid(logit_monitor + d)) - target_rate, -5, 5)
prob_recal = sigmoid(logit_monitor + shift)
print("intercept shift:", round(float(shift), 4))
print("mean predicted before:", round(float(prob_monitor.mean()), 4), "after:", round(float(prob_recal.mean()), 4), "observed:", round(target_rate, 4))
print("Brier before:", round(brier_score(y_monitor, prob_monitor), 5), "after:", round(brier_score(y_monitor, prob_recal), 5))
print("AUC unchanged:", round(roc_auc(y_monitor, prob_monitor), 4), round(roc_auc(y_monitor, prob_recal), 4))
recal_brier_before = brier_score(y_monitor, prob_monitor)
recal_brier_after = brier_score(y_monitor, prob_recal)"""),
]

S[19] = [
    M("""
1. Set the IV cutoff to 0.05 and to 0.10. Which characteristics drop out? What happens to test AUC?
2. Merge the first two bins of one characteristic by hand and measure the change in IV and AUC. State when merging is justified.
3. Change the base score to 500, base odds to 20 to 1 and PDO to 40. Re derive the factor and offset by hand and confirm with `scaling_constants`.
4. Build a second monitoring sample with drift 1.0 but a changed true relationship (for example flip the sign of the dti effect in a copy of the generator). Compare PSI and AUC with Experiment B and explain the difference.
5. Merge bins of `credit_history_years` and `utilization` until WoE is monotone. Does acceptance criterion 1 now pass? Report the AUC before and after.
6. Write a one page monitoring rule for this scorecard with three metrics, a threshold for each and the action taken when a threshold is crossed.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "02_credit_risk/credit_scoring",
        "title": "Credit Scoring with Weight of Evidence",
        "family": "Credit Risk",
        "level": "Intermediate",
        "dataset": "retail_loans_dev and retail_loans_monitoring",
        "data_kind": "synthetic",
        "status": "Validating",
        "tagline": "Build a points scorecard from WoE bins, prove the points match the model, and test it under drift.",
        "refs": ["siddiqi2006", "lessmann2015", "gunnarsson2021", "sr262"],
        "research_note": (
            "The scorecard construction follows the practitioner method described in the scorecard literature. The Siddiqi book "
            "is not verified in this build, so IV and PSI thresholds are labelled rules of thumb. Lessmann et al. and "
            "Gunnarsson et al. are used only to justify a simple baseline. SR 26-2 frames the model risk language. "
            "The module stays Validating for two reasons: the Siddiqi book is not verified, and acceptance criterion 1 was not met on the executed run."
        ),
        "learn": [
            "WoE, IV and bin monotonicity",
            "Logistic regression on WoE and the points formula",
            "Prove that integer points reproduce the model score",
            "AUC, Gini, KS and calibration on test and drifted data",
            "PSI as a drift signal and its limits",
            "Intercept recalibration and what it cannot fix",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
