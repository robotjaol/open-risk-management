"""Spec: probability of default with logistic regression."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "probability_of_default"

SETUP = setup_code(MODULE) + """
from risk_lab.credit.logistic import fit_logistic, predict_proba, sigmoid, standard_errors
from risk_lab.credit.metrics import (
    brier_score, calibration_table, gini, ks_statistic, log_loss, roc_auc,
)
from risk_lab.data.synthetic import (
    RETAIL_TRUE_INTERCEPT, RETAIL_TRUE_SLOPES, standardise_features, true_default_probability,
)"""

S = {}

S[1] = [
    M("""
A retail lender receives a loan application. It must decide whether to lend, at what price, and how much
capital and provision to hold. All three decisions need one number: **the probability that this borrower
defaults within 12 months (PD)**.

This notebook estimates PD with logistic regression on a synthetic loan sample. Because the sample comes from a
known generating process, the notebook can do something real data never allows: compare the estimated model with
the true probabilities and the true coefficients.

**Decision this supports:** whether a PD model is good enough to rank borrowers, to price risk, and to feed
provisioning, and which of those three uses the evidence supports.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Write the logistic regression likelihood, its gradient and Hessian, and take one Newton step by hand.
2. Fit the model with a NumPy implementation, scikit-learn and statsmodels, and show the three agree.
3. Measure discrimination (AUC, Gini, KS), calibration (Brier, deciles) and compare with the best possible model.
4. Read coefficients as odds ratios and compare them with known true values.
5. Measure how sample size and regularisation change accuracy.
6. Turn PD into risk grades and an approval cutoff, and state what the numbers do not prove.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Default | Event defined by the dataset: 1 if the loan defaults within 12 months of origination |
| PD | Probability of default over a horizon. Here 12 months |
| Odds | p / (1 - p). Logistic regression is linear in the log odds |
| Odds ratio | exp(coefficient). Multiplier on the odds for a one unit rise in the feature |
| Discrimination | Ability to rank bad borrowers above good ones. AUC, Gini, KS |
| Calibration | Whether predicted PD matches observed default rate. A model can rank well and still be miscalibrated |
| Gini | 2 * AUC - 1 |
| KS | Largest gap between cumulative bad and good distributions across the score |

Discrimination and calibration are different properties. Ranking is enough for an approve or decline cutoff.
Provisioning and pricing need calibrated probabilities.
"""),
]

S[4] = [
    M("""
**Why logistic regression for PD?**

| Option | Strength | Weakness |
|---|---|---|
| Logistic regression | Output is a probability. Coefficients are readable. Easy to document and validate | Linear in the log odds unless features are transformed |
| Gradient boosting or neural network | Can capture interactions | Harder to explain and validate. Benchmarks of credit scoring methods report that gains over well built simpler models depend on the data and are not guaranteed (see Section 5) |
| Single rule or expert grade | Cheap | No measured accuracy |

Logistic regression is the baseline every other method must beat. Acceptance criteria used in this notebook,
on a test set not used for fitting:

1. AUC at least 0.70 (a teaching threshold, not a regulatory one).
2. Test AUC within 0.02 of the AUC of the true generating probability.
3. Mean predicted PD within 10 percent (relative) of the observed default rate.
"""),
]

S[6] = [
    M(r"""
Observation $i$ has features $x_i$ and outcome $y_i \in \{0,1\}$. The model is

$$p_i = \Pr(y_i = 1 \mid x_i) = \frac{1}{1 + e^{-(\beta_0 + x_i^\top \beta)}}$$

The log likelihood is

$$\ell(\beta) = \sum_{i=1}^{n} \left[ y_i \ln p_i + (1 - y_i)\ln(1 - p_i) \right]$$

Gradient and Hessian, with $X$ the design matrix with a column of ones and $W = \mathrm{diag}\big(p_i(1-p_i)\big)$:

$$\nabla \ell = X^\top (y - p), \qquad H = -X^\top W X$$

Newton Raphson update:

$$\beta^{new} = \beta + (X^\top W X)^{-1} X^\top (y - p)$$

The inverse of $X^\top W X$ at the solution is the large sample covariance matrix of the estimates, so
standard errors are the square roots of its diagonal.

Interpretation: $e^{\beta_j}$ is the factor by which the **odds** of default change for a one unit rise in feature $j$.
"""),
]

S[7] = [
    M("""
**Part A. One Newton step on eight observations.** Start from all coefficients at zero, so every predicted
probability is 0.5.
"""),
    C("""
x = np.array([-2.0, -1.0, -1.0, 0.0, 0.0, 1.0, 1.0, 2.0])
y = np.array([0, 0, 1, 0, 1, 0, 1, 1])
design = np.column_stack([np.ones(len(x)), x])
beta = np.zeros(2)
p = sigmoid(design @ beta)
gradient = design.T @ (y - p)
weights = p * (1 - p)
hessian_neg = design.T @ (design * weights[:, None])
step = np.linalg.solve(hessian_neg, gradient)
print("probabilities at start:", p)
print("gradient:", gradient)
print("information matrix:\\n", hessian_neg)
print("step:", step)
print("beta after one step:", beta + step)"""),
    C("""
# full fit, same data
tiny = fit_logistic(x.reshape(-1, 1), y)
print("converged intercept:", round(tiny["intercept"], 6), "slope:", round(float(tiny["slopes"][0]), 6))
print("iterations:", tiny["iterations"])
assert tiny["iterations"] < 15"""),
    M("""
**Part B. Reading a coefficient.** Take a borrower whose debt to income ratio is one standard deviation above
average and who is average on every other feature. The true model gives the logit below.
"""),
    C("""
logit = RETAIL_TRUE_INTERCEPT + RETAIL_TRUE_SLOPES["dti_z"] * 1.0
print("logit:", round(logit, 4))
print("PD:", round(float(sigmoid(logit)), 4))
print("PD of an average borrower:", round(float(sigmoid(RETAIL_TRUE_INTERCEPT)), 4))
print("odds ratio for one sd of dti:", round(float(np.exp(RETAIL_TRUE_SLOPES["dti_z"])), 4))"""),
]

S[8] = [
    C("""
loans = pd.read_csv(ROOT / "datasets" / "synthetic" / "retail_loans_dev.csv")
print("shape:", loans.shape)
print("default rate:", round(loans["default_12m"].mean(), 4))
print("missing values:", int(loans.isna().sum().sum()))
print(loans.describe().T[["mean", "std", "min", "50%", "max"]].round(3))"""),
    C("""
by_region = loans.groupby("region")["default_12m"].agg(["count", "mean"]).round(4)
by_delinq = loans.groupby(loans["delinq_2y"].clip(upper=3))["default_12m"].agg(["count", "mean"]).round(4)
print(by_region)
print(by_delinq)

from scipy.stats import chi2_contingency
table = pd.crosstab(loans["region"], loans["default_12m"])
print("region chi square p value:", round(chi2_contingency(table)[1], 4))"""),
    C("""
numeric = loans.drop(columns=["loan_id", "region"])
corr_target = numeric.corr()["default_12m"].drop("default_12m").sort_values()
print(corr_target.round(3))"""),
]

S[9] = [
    M("""
Steps, in order:

1. Split 70 percent train and 30 percent test with a fixed seed. The test set is not used for any fitting choice.
2. Build two feature sets. **Model A** uses the seven features that drive default in the generator, scaled with the
   generator's reference scales. A real modeller would not know these. They are used here so coefficients can be
   compared with the truth. **Model B** uses every numeric column, scaled with train means and standard deviations,
   as a real modeller would.
3. Region is dropped from both sets. Its contribution is tested in section 8 and is expected to be zero.
"""),
    C("""
rng = np.random.default_rng(SEED)
order = rng.permutation(len(loans))
n_train = int(0.7 * len(loans))
train = loans.iloc[order[:n_train]].reset_index(drop=True)
test = loans.iloc[order[n_train:]].reset_index(drop=True)
print("train rows:", len(train), "defaults:", int(train["default_12m"].sum()))
print("test rows:", len(test), "defaults:", int(test["default_12m"].sum()))

# model A features
xa_train = standardise_features(train)
xa_test = standardise_features(test)
names_a = list(xa_train.columns)

# model B features
def make_b(frame):
    out = frame[["age", "employment_years", "credit_history_years", "dti", "utilization", "ltv",
                 "delinq_2y", "term_months", "interest_rate"]].copy()
    out["log_income"] = np.log(frame["income"])
    out["log_loan_amount"] = np.log(frame["loan_amount"])
    return out

xb_train_raw = make_b(train)
xb_test_raw = make_b(test)
mean_b = xb_train_raw.mean()
std_b = xb_train_raw.std()
xb_train = (xb_train_raw - mean_b) / std_b
xb_test = (xb_test_raw - mean_b) / std_b
names_b = list(xb_train.columns)
y_train = train["default_12m"].to_numpy()
y_test = test["default_12m"].to_numpy()
print("model A features:", names_a)
print("model B features:", names_b)"""),
]

S[10] = [
    M("""
The NumPy implementation in `risk_lab.credit.logistic` follows section 6 exactly: Newton Raphson, no optimiser library.
"""),
    C("""
fit_a = fit_logistic(xa_train.to_numpy(), y_train)
fit_b = fit_logistic(xb_train.to_numpy(), y_train)
se_a = standard_errors(xa_train.to_numpy(), fit_a["intercept"], fit_a["slopes"])
print("iterations A:", fit_a["iterations"], "iterations B:", fit_b["iterations"])

compare = pd.DataFrame(
    {
        "true": [RETAIL_TRUE_INTERCEPT] + [RETAIL_TRUE_SLOPES[n] for n in names_a],
        "estimate": [fit_a["intercept"]] + list(fit_a["slopes"]),
        "std_error": list(se_a),
    },
    index=["intercept"] + names_a,
)
compare["error"] = compare["estimate"] - compare["true"]
compare["abs_error_in_se"] = compare["error"].abs() / compare["std_error"]
print(compare.round(4))"""),
]

S[11] = [
    M("""
Two library fits on the same data. They must agree with the NumPy fit. Any gap points to a bug or to a
different optimiser tolerance.
"""),
    C("""
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

sm_fit = sm.Logit(y_train, sm.add_constant(xa_train.to_numpy())).fit(disp=0)
sk_fit = LogisticRegression(C=np.inf, max_iter=1000, tol=1e-10).fit(xa_train.to_numpy(), y_train)

mine = np.concatenate([[fit_a["intercept"]], fit_a["slopes"]])
gap_sm = np.max(np.abs(sm_fit.params - mine))
gap_sk = np.max(np.abs(np.concatenate([sk_fit.intercept_, sk_fit.coef_[0]]) - mine))
gap_se = np.max(np.abs(sm_fit.bse - se_a))
print("max coefficient gap vs statsmodels:", f"{gap_sm:.2e}")
print("max coefficient gap vs scikit-learn:", f"{gap_sk:.2e}")
print("max standard error gap vs statsmodels:", f"{gap_se:.2e}")
assert gap_sm < 1e-5
assert gap_sk < 1e-3
assert gap_se < 1e-5"""),
    C("""
# model B significance
sm_b = sm.Logit(y_train, sm.add_constant(xb_train.to_numpy())).fit(disp=0)
table_b = pd.DataFrame(
    {"coef": sm_b.params[1:], "p_value": sm_b.pvalues[1:]}, index=names_b
).sort_values("p_value")
print(table_b.round(4))"""),
]

S[12] = [
    M("""
Everything below uses the **test** set. Baselines:

* **Constant PD**: every borrower gets the train default rate. Zero discrimination by construction.
* **Oracle**: the true generating probability. No model fitted on this data can beat it on average, so it is the ceiling.
* **Single feature**: logistic regression on debt to income alone.
"""),
    C("""
p_a = predict_proba(xa_test.to_numpy(), fit_a["intercept"], fit_a["slopes"])
p_b = predict_proba(xb_test.to_numpy(), fit_b["intercept"], fit_b["slopes"])
oracle = true_default_probability(test).to_numpy()
base_rate = float(y_train.mean())
p_const = np.full(len(test), base_rate)

dti_fit = fit_logistic(xa_train[["dti_z"]].to_numpy(), y_train)
p_dti = predict_proba(xa_test[["dti_z"]].to_numpy(), dti_fit["intercept"], dti_fit["slopes"])

candidates = {
    "constant": p_const,
    "dti only": p_dti,
    "model B (all numeric)": p_b,
    "model A (7 drivers)": p_a,
    "oracle (true PD)": oracle,
}
rows = []
for name, prob in candidates.items():
    auc = roc_auc(y_test, prob) if np.ptp(prob) > 0 else 0.5
    rows.append(
        {
            "model": name,
            "auc": auc,
            "gini": 2 * auc - 1,
            "ks": ks_statistic(y_test, prob) if np.ptp(prob) > 0 else 0.0,
            "brier": brier_score(y_test, prob),
            "log_loss": log_loss(y_test, prob),
            "mean_pd": float(np.mean(prob)),
        }
    )
evaluation = pd.DataFrame(rows).set_index("model")
print(evaluation.round(4))
print("observed test default rate:", round(float(y_test.mean()), 4))"""),
    C("""
auc_a = float(evaluation.loc["model A (7 drivers)", "auc"])
auc_oracle = float(evaluation.loc["oracle (true PD)", "auc"])
mean_gap_pct = 100 * (float(np.mean(p_a)) - float(y_test.mean())) / float(y_test.mean())
criteria = {
    "auc_at_least_0.70": auc_a >= 0.70,
    "auc_within_0.02_of_oracle": (auc_oracle - auc_a) <= 0.02,
    "mean_pd_within_10pct_of_observed": abs(mean_gap_pct) <= 10,
}
print("mean PD gap (percent of observed rate):", round(mean_gap_pct, 2))
print(criteria)"""),
]

S[13] = [
    C("""
cal = pd.DataFrame(calibration_table(y_test, p_a, n_bins=10))
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))

axes[0].plot([0, cal["mean_predicted"].max() * 1.1], [0, cal["mean_predicted"].max() * 1.1], color=COLORS["grey"], linestyle=":")
axes[0].plot(cal["mean_predicted"], cal["observed_rate"], marker="o", color=COLORS["main"])
axes[0].set_xlabel("mean predicted PD")
axes[0].set_ylabel("observed default rate")
axes[0].set_title("Calibration by decile, model A")

order_a = np.argsort(-p_a)
cum_bad = np.cumsum(y_test[order_a]) / y_test.sum()
cum_good = np.cumsum(1 - y_test[order_a]) / (1 - y_test).sum()
axes[1].plot(cum_good, cum_bad, color=COLORS["main"], label="model A")
order_o = np.argsort(-oracle)
axes[1].plot(np.cumsum(1 - y_test[order_o]) / (1 - y_test).sum(), np.cumsum(y_test[order_o]) / y_test.sum(), color=COLORS["third"], linestyle="--", label="oracle")
axes[1].plot([0, 1], [0, 1], color=COLORS["grey"], linestyle=":")
axes[1].set_xlabel("cumulative share of goods")
axes[1].set_ylabel("cumulative share of bads")
axes[1].set_title("ROC curve")
axes[1].legend()

axes[2].hist(p_a[y_test == 0], bins=40, alpha=0.6, color=COLORS["main"], label="good", density=True)
axes[2].hist(p_a[y_test == 1], bins=40, alpha=0.6, color=COLORS["second"], label="bad", density=True)
axes[2].set_xlabel("predicted PD")
axes[2].set_title("Score distribution")
axes[2].legend()
save_figure(fig, MODULE, "pd_evaluation.png")
plt.show()
print(cal.round(4).to_string(index=False))"""),
]

S[14] = [
    M("""
How to read the output of the next cell:

* **Coefficients** within about two standard errors of the truth show the estimator is behaving. Some misses are expected by chance: with a 95 percent interval, about one coefficient in twenty can miss.
* **Model B** contains features that have no true effect. Their p values should be spread over 0 to 1, not clustered near 0.
* **Model A against the oracle**: model A has the right functional form by construction, so any gap is the price of estimating coefficients from a finite sample. On a finite test set the gap can even be slightly negative, because the test labels are random draws and the oracle is only best on average, not on every sample.
"""),
    C("""
inside = int((compare["abs_error_in_se"].iloc[1:] <= 1.96).sum())
print("slopes within 1.96 standard errors of truth:", inside, "of", len(names_a))
noise = ["age", "employment_years", "log_loan_amount", "term_months"]
print("p values of features with zero true effect:")
print(table_b.loc[noise, "p_value"].round(3))
print("AUC gap to oracle:", round(auc_oracle - auc_a, 4))
print("Brier gap to oracle:", round(float(evaluation.loc["model A (7 drivers)", "brier"] - evaluation.loc["oracle (true PD)", "brier"]), 5))"""),
]

S[15] = [
    M("""
**Experiment A: sample size.** Draw random subsets of the train set at four sizes, 30 times each. Fit model A.
Record test AUC and the root mean squared error (RMSE) of the seven slopes against the truth.

**Experiment B: ridge penalty.** At 1000 training rows, repeat with L2 penalties 0, 10, 100 and 1000 on the slopes.
"""),
    C("""
true_slopes = np.array([RETAIL_TRUE_SLOPES[n] for n in names_a])
sizes = [300, 1000, 3000, len(train)]
repeat = 30
rng_exp = np.random.default_rng(SEED + 1)
rows = []
for size in sizes:
    reps = 1 if size == len(train) else repeat
    for rep in range(reps):
        pick = rng_exp.choice(len(train), size=size, replace=False)
        fit = fit_logistic(xa_train.to_numpy()[pick], y_train[pick])
        prob = predict_proba(xa_test.to_numpy(), fit["intercept"], fit["slopes"])
        rows.append(
            {
                "n_train": size,
                "auc": roc_auc(y_test, prob),
                "slope_rmse": float(np.sqrt(np.mean((fit["slopes"] - true_slopes) ** 2))),
            }
        )
size_table = pd.DataFrame(rows).groupby("n_train").agg(
    auc_mean=("auc", "mean"), auc_sd=("auc", "std"), slope_rmse=("slope_rmse", "mean")
)
print(size_table.round(4))"""),
    C("""
rows = []
for penalty in [0, 10, 100, 1000]:
    for rep in range(repeat):
        pick = rng_exp.choice(len(train), size=1000, replace=False)
        fit = fit_logistic(xa_train.to_numpy()[pick], y_train[pick], l2=penalty)
        prob = predict_proba(xa_test.to_numpy(), fit["intercept"], fit["slopes"])
        rows.append(
            {
                "l2": penalty,
                "auc": roc_auc(y_test, prob),
                "brier": brier_score(y_test, prob),
                "slope_rmse": float(np.sqrt(np.mean((fit["slopes"] - true_slopes) ** 2))),
            }
        )
ridge_table = pd.DataFrame(rows).groupby("l2").mean()
print(ridge_table.round(4))"""),
    C("""
fig, ax = plt.subplots()
ax.errorbar(size_table.index, size_table["auc_mean"], yerr=size_table["auc_sd"].fillna(0), marker="o", color=COLORS["main"], label="test AUC, model A")
ax.axhline(auc_oracle, color=COLORS["third"], linestyle="--", label="oracle AUC")
ax.set_xscale("log")
ax.set_xlabel("training rows")
ax.set_ylabel("test AUC")
ax.set_title("Accuracy against sample size")
ax.legend()
save_figure(fig, MODULE, "auc_by_sample_size.png")
plt.show()"""),
    C("""
print("slope RMSE falls as n grows:", bool(size_table["slope_rmse"].is_monotonic_decreasing))
print("l2 with lowest slope RMSE at n=1000:", int(ridge_table["slope_rmse"].idxmin()))"""),
]

S[16] = [
    C("""
summary = evaluation[["auc", "gini", "ks", "brier", "log_loss"]].round(4)
print(summary)
print()
print(criteria)
metrics = {
    "test_auc": evaluation["auc"].to_dict(),
    "test_gini": evaluation["gini"].to_dict(),
    "test_ks": evaluation["ks"].to_dict(),
    "test_brier": evaluation["brier"].to_dict(),
    "observed_test_default_rate": float(y_test.mean()),
    "mean_predicted_pd_model_a": float(np.mean(p_a)),
    "mean_pd_gap_pct_of_observed": mean_gap_pct,
    "newton_iterations_model_a": fit_a["iterations"],
    "coefficient_gap_vs_statsmodels": float(gap_sm),
    "slopes_within_1_96_se": inside,
    "acceptance_criteria": criteria,
    "sample_size_experiment": size_table.reset_index().to_dict(orient="records"),
    "ridge_experiment_n1000": ridge_table.reset_index().to_dict(orient="records"),
}
config = {"n_loans": len(loans), "train_share": 0.7, "seed": SEED, "features_model_a": names_a, "features_model_b": names_b}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Logistic regression by Newton Raphson, checked against statsmodels and scikit-learn, evaluated on a held out test set",
    data_kind="synthetic",
    dataset="datasets/synthetic/retail_loans_dev.csv",
    n_obs=int(len(loans)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "default follows a logistic model of seven standardised features",
        "region, age, employment_years, loan_amount and term_months have zero true effect",
        "no time dimension, one cross section",
        "acceptance thresholds are teaching choices",
    ],
    metrics=metrics,
    baseline={"constant_pd_auc": 0.5, "dti_only_auc": float(evaluation.loc["dti only", "auc"]), "oracle_auc": auc_oracle},
    limitations=[
        "the fitted model has the true functional form, so results are optimistic",
        "synthetic data, no real portfolio behaviour",
        "no out of time test in this module",
    ],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
**Limitations**

1. **Correct specification.** The data come from a logistic model and Model A uses the true features. Real data have no such luxury. Expect a larger gap between a fitted model and the best possible model.
2. **No time dimension.** Real PD models face changing economic conditions. Out of time performance is tested in `credit_scoring`, which uses a shifted sample.
3. **Class balance.** Default is the rare class. With few defaults, coefficient error rises sharply. Experiment A quantifies it here.
4. **Point in time versus through the cycle.** This PD is conditional on features at origination. Whether it behaves like a point in time or a cycle average PD depends on the features and is not tested here.
5. **Thresholds** (AUC 0.70, 0.02 gap, 10 percent) are teaching choices.

**Model risk.** Main risks are using a ranking tool for pricing without checking calibration, and extrapolating
beyond the feature ranges of the sample. Independent validation would repeat the fit, test stability and review
the default definition. This notebook is not an independent validation.
"""),
]

S[18] = [
    M("""
**Risk grades.** Lenders seldom act on a raw probability. They map PD to a small number of grades, often called a
master scale, then attach pricing and limits to the grades. The grades below use test set PD quintiles.
This is a simplified teaching version. Real master scales fix PD boundaries in advance so grades keep their meaning
across time.

**Approval cutoff.** For each cutoff on PD, the table shows the approval rate, the bad rate among approved
loans and the bad rate among rejected loans.
"""),
    C("""
grades = pd.qcut(pd.Series(p_a), q=5, labels=["A", "B", "C", "D", "E"])
grade_table = pd.DataFrame({"grade": grades, "pd": p_a, "default": y_test}).groupby("grade", observed=True).agg(
    loans=("default", "size"), mean_pd=("pd", "mean"), observed_rate=("default", "mean")
)
print(grade_table.round(4))"""),
    C("""
rows = []
for quantile in [0.5, 0.7, 0.8, 0.9, 1.0]:
    cutoff = np.quantile(p_a, quantile)
    approved = p_a <= cutoff
    rows.append(
        {
            "approval_rate": float(approved.mean()),
            "cutoff_pd": float(cutoff),
            "bad_rate_approved": float(y_test[approved].mean()),
            "bad_rate_rejected": float(y_test[~approved].mean()) if (~approved).any() else np.nan,
        }
    )
print(pd.DataFrame(rows).round(4).to_string(index=False))"""),
]

S[19] = [
    M("""
1. Add `region` as four dummy variables to model B and test whether any is significant. Explain what a significant result would mean for this dataset.
2. Re-run with seed 7 for the split. Report the range of test AUC across five seeds.
3. In Experiment A, find the training size where the mean AUC is within 0.01 of the oracle. State how many defaults that size contains.
4. Replace `interest_rate` with the ratio `loan_amount / income`. Does AUC change? Explain why interest rate has a true effect in this generator although it is itself driven by dti and delinquencies.
5. Argue for or against using this model to set provisions without recalibration. Use the calibration table.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "02_credit_risk/probability_of_default",
        "title": "Probability of Default with Logistic Regression",
        "family": "Credit Risk",
        "level": "Beginner to Intermediate",
        "dataset": "retail_loans_dev",
        "data_kind": "synthetic",
        "status": "Complete",
        "tagline": "Estimate 12 month PD, measure ranking and calibration, and compare with the true generating process.",
        "refs": ["lessmann2015", "gunnarsson2021", "bcbs_d424", "sr262"],
        "research_note": (
            "Lessmann et al. and Gunnarsson et al. are used only to frame the choice of logistic regression as the baseline "
            "for credit scoring. Their experiments use real credit datasets and are not reproduced here. "
            "SR 26-2 is cited for the model risk language in the limitations. The Basel entry is context for how PD "
            "feeds capital, which this notebook does not compute."
        ),
        "learn": [
            "Logistic regression likelihood, gradient and Newton Raphson",
            "Fit with NumPy, statsmodels and scikit-learn and reconcile them",
            "AUC, Gini, KS, Brier, log loss and calibration by decile",
            "Compare with the true generating model",
            "Effect of sample size and ridge penalty",
            "Risk grades and approval cutoffs",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
