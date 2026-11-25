"""Spec: credit decision, a PD model on real applicant data turned into an approval cut off with a cost."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "credit_decision_cutoff"

SETUP = setup_code(MODULE) + """
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, train_test_split

from risk_lab.credit.logistic import fit_logistic, predict_proba
from risk_lab.credit.metrics import brier_score, calibration_table, ks_statistic, roc_auc

COST_BAD_APPROVED = 5.0
COST_GOOD_REFUSED = 1.0
BAYES_CUTOFF = COST_GOOD_REFUSED / (COST_GOOD_REFUSED + COST_BAD_APPROVED)
L2 = 1.0"""

S = {}

S[1] = [
    M("""
A bank launches a personal loan product. Applications arrive, and someone must decide **who gets a loan**. A score that ranks applicants is not a decision.
The decision needs a **cut off**: approve everyone whose estimated default probability is at or below some value.

This notebook does the whole path on **real applicant data** (1000 loan applicants from a German source, the Statlog German Credit data, 30 percent labelled bad):

1. Build a default model and measure how well it ranks and how well it is calibrated.
2. Turn the probability into a cut off using the cost of the two kinds of error that the dataset provides: approving a bad loan costs 5, refusing a good loan costs 1.
3. Measure the **reduction in expected cost** against two simple policies (approve everyone, refuse everyone), with an interval, on data the model has not seen.
4. Test how the answer changes when the real bad rate differs from the sample.
5. Decide what to do about attributes that should not drive a credit decision.

**Decision this supports:** a proposed cut off and its expected effect, with the evidence a credit committee and a model validator would ask for.

**About the costs.** The 5 to 1 cost ratio comes with the dataset. It is a convention of that benchmark, not the economics of a bank. Section 15 shows what happens when it changes.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Split real data without leakage, fit a logistic model from scratch and match a library.
2. Report ranking (AUC, KS) and calibration (Brier, decile table) on held out data and say what 300 test rows can and cannot show.
3. Derive the cost minimising cut off from the cost of each error, and verify it numerically.
4. Measure the cost reduction against two baseline policies with a bootstrap interval.
5. Check whether the result holds over 100 different splits.
6. Show how the right cut off moves when the portfolio bad rate differs from the sample bad rate.
7. Remove attributes that should not be used, measure what that costs, and write down the decision.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Bad | The applicant defaulted (coded 2 in the source). The model predicts the probability of bad |
| Cut off | Approve if the predicted probability of bad is at or below it |
| Cost of an error | Approving a bad applicant costs 5 units. Refusing a good applicant costs 1 unit. A correct decision costs 0 |
| Expected cost per applicant | Average cost of the decisions on a set of applicants |
| Baseline policy | Approve all, or refuse all. A model has to beat both |
| Discrimination | Ability to rank bad above good (AUC, KS) |
| Calibration | Agreement between predicted and observed bad rates |
| Prior shift | The bad rate in use differs from the bad rate in the training sample |
| Protected attribute | A characteristic such as sex or national origin that should not decide a credit outcome. The rules differ by country |
"""),
]

S[4] = [
    M("""
**Why logistic regression?** It is the standard application scorecard base, it is transparent, and the earlier modules built it from scratch. The literature on credit scoring benchmarks
(Lessmann et al.) and on deep learning for scoring (Gunnarsson et al.) is a reminder that more complex models do not always win on this kind of tabular data, and that the gain has to be
measured on held out data. This notebook does not claim logistic regression is best. It claims that a transparent model is a reasonable baseline whose decisions can be explained.

**Why a cost based cut off?** A cut off chosen to maximise accuracy treats both errors alike. Here one error costs five times the other.

**Method checks and pre stated expectations (acceptance criteria).**

1. The from scratch Newton fit and scikit-learn give a test AUC within 0.01.
2. The training and test sets are disjoint, and the bad share of each is within 0.02 of the full sample.
3. The cut off derived from the costs equals the numerical minimiser of the expected cost under the model's own probabilities.
4. Test AUC is at least 0.70. This threshold was set before the final run.
5. The policy cost at the derived cut off is below the approve all cost, and the 95 percent bootstrap interval of the difference excludes zero.
6. The final model contains no protected attribute columns.
"""),
]

S[6] = [
    M(r"""
**Model.** $P(\text{bad} \mid x) = 1/(1 + e^{-(b_0 + b^\top x)})$, fitted by Newton Raphson with a ridge penalty $\lambda = 1$ on the slopes.

**Cost of a decision.** Let $p$ be the predicted probability of bad. Approving costs $c_B p$ in expectation (with $c_B = 5$) and refusing costs $c_G (1-p)$ (with $c_G = 1$). Approve when

$$c_B\,p \le c_G\,(1-p) \iff p \le \frac{c_G}{c_G + c_B} = \frac{1}{6}$$

so the cost minimising cut off is $\tau^* = 1/6 \approx 0.167$, **if the probabilities are calibrated**.

**Realised cost per applicant** on a set with labels $y_i$ (1 = bad): $\frac{1}{n}\sum_i \left[c_B \, \mathbb{1}(p_i \le \tau, y_i = 1) + c_G \, \mathbb{1}(p_i > \tau, y_i = 0)\right]$.

**Prior shift.** If the model was trained where the bad rate is $\pi_s$ and used where it is $\pi_t$, the calibrated odds are multiplied by
$\dfrac{\pi_t/(1-\pi_t)}{\pi_s/(1-\pi_s)}$. The logistic slopes do not change, only the intercept shifts.
"""),
]

S[7] = [
    M("""
Four applicants with predicted probabilities of bad 0.05, 0.15, 0.30 and 0.60, and true outcomes good, good, bad, bad. Cut off 1/6.
"""),
    C("""
p_small = np.array([0.05, 0.15, 0.30, 0.60])
y_small = np.array([0, 0, 1, 1])
approve = p_small <= BAYES_CUTOFF
cost_each = np.where(approve & (y_small == 1), COST_BAD_APPROVED, 0) + np.where(~approve & (y_small == 0), COST_GOOD_REFUSED, 0)
print("cut off:", round(BAYES_CUTOFF, 4))
print("approve:", approve)
print("cost per applicant:", cost_each, "mean:", cost_each.mean())
print("approve all:", np.where(y_small == 1, COST_BAD_APPROVED, 0).mean(), "refuse all:", np.where(y_small == 0, COST_GOOD_REFUSED, 0).mean())"""),
    M("""
Approving the first two (both good) and refusing the other two costs nothing, because the refused ones are bad. Approve all would cost $(5+5)/4 = 2.5$, and refuse all would cost $2/4 = 0.5$.
The model policy wins here only because the ranking is perfect, which real data will not allow.
"""),
]

S[8] = [
    C("""
data = pd.read_csv(ROOT / "datasets" / "raw" / "german_credit.csv")
target = (data["creditability"] == "bad").astype(int)
features = data.drop(columns="creditability")
print("applicants:", len(data), "columns:", features.shape[1], "missing cells:", int(data.isna().sum().sum()))
print("bad rate:", round(float(target.mean()), 3))
print()
print(features.select_dtypes("number").describe().round(1).T[["mean", "min", "max"]].to_string())
print()
by_account = data.groupby("status_of_existing_checking_account")["creditability"].agg(count="size", bad_rate=lambda s: (s == "bad").mean())
print(by_account.round(3).to_string())"""),
    M("""
The bad rate differs a lot by checking account status, which is a real signal the model can use. The sample is small (1000 rows), so every figure below has wide uncertainty.
The source of the data, its license (CC BY 4.0) and its limits are in its dataset card.
"""),
]

S[9] = [
    C("""
PROTECTED = ["personal_status_and_sex", "foreign_worker"]
all_columns = list(features.columns)
model_columns = [c for c in all_columns if c not in PROTECTED]

train_idx, test_idx = train_test_split(np.arange(len(data)), test_size=0.3, stratify=target, random_state=SEED)
print("train:", len(train_idx), "test:", len(test_idx))
print("bad share: full", round(float(target.mean()), 3), "train", round(float(target.iloc[train_idx].mean()), 3), "test", round(float(target.iloc[test_idx].mean()), 3))
assert len(set(train_idx) & set(test_idx)) == 0


def design(columns, fit_idx):
    # one hot plus scaling
    z = pd.get_dummies(features[columns], drop_first=True, dtype=float)
    numeric = [c for c in columns if features[c].dtype.kind in "if"]
    mean = z.iloc[fit_idx][numeric].mean()
    std = z.iloc[fit_idx][numeric].std()
    z[numeric] = (z[numeric] - mean) / std
    return z


X_all = design(all_columns, train_idx)
X_final = design(model_columns, train_idx)
print("columns with protected attributes:", X_all.shape[1], "without:", X_final.shape[1])
y_train = target.iloc[train_idx].to_numpy()
y_test = target.iloc[test_idx].to_numpy()"""),
    M("""
**Leakage control.** Means and standard deviations for scaling come from the training rows only. The one hot columns use category names, not statistics. The test rows are touched once, at evaluation.
**Protected attributes.** Personal status and sex, and foreign worker status, are excluded from the final model. Age is kept, which is a choice that regulations in some countries would not allow. See the limits section.
"""),
]

S[10] = [
    C("""
fit = fit_logistic(X_final.iloc[train_idx].to_numpy(), y_train, l2=L2)
p_test = predict_proba(X_final.iloc[test_idx].to_numpy(), fit["intercept"], fit["slopes"])
p_train = predict_proba(X_final.iloc[train_idx].to_numpy(), fit["intercept"], fit["slopes"])
print("Newton iterations:", fit["iterations"])
print("mean predicted bad rate, train:", round(float(p_train.mean()), 4), "actual:", round(float(y_train.mean()), 4))
print("mean predicted bad rate, test:", round(float(p_test.mean()), 4), "actual:", round(float(y_test.mean()), 4))


def policy_cost(p, y, cutoff):
    # realised cost per applicant
    approve = p <= cutoff
    cost = np.where(approve & (y == 1), COST_BAD_APPROVED, 0.0) + np.where(~approve & (y == 0), COST_GOOD_REFUSED, 0.0)
    return float(cost.mean())


# expected cost minimiser
order = np.argsort(p_test)
p_sorted = p_test[order]
approved_count = np.arange(len(p_sorted) + 1)
expected_cost = np.array([
    COST_BAD_APPROVED * p_sorted[:k].sum() + COST_GOOD_REFUSED * (1 - p_sorted[k:]).sum() for k in approved_count
]) / len(p_sorted)
k_star = int(np.argmin(expected_cost))
approved_by_rule = int(np.sum(p_sorted <= BAYES_CUTOFF))
print("minimiser approves", k_star, "applicants, the 1/6 rule approves", approved_by_rule)
assert k_star == approved_by_rule"""),
    M("""
The numerical minimiser of the expected cost, computed from the model's own probabilities, approves exactly the applicants with $p \\le 1/6$. That confirms the derivation in section 6.
"""),
]

S[11] = [
    C("""
sk = LogisticRegression(C=1 / L2, max_iter=2000).fit(X_final.iloc[train_idx], y_train)
p_sk = sk.predict_proba(X_final.iloc[test_idx])[:, 1]
auc_scratch = roc_auc(y_test, p_test)
auc_sk = roc_auc(y_test, p_sk)
print("test AUC, scratch:", round(auc_scratch, 4), "scikit-learn:", round(auc_sk, 4), "gap:", f"{abs(auc_scratch - auc_sk):.4f}")
print("largest probability gap:", f"{np.max(np.abs(p_test - p_sk)):.2e}")"""),
]

S[12] = [
    C("""
evaluation = {
    "auc": roc_auc(y_test, p_test),
    "ks": ks_statistic(y_test, p_test),
    "brier": brier_score(y_test, p_test),
    "brier_constant": brier_score(y_test, np.full(len(y_test), y_train.mean())),
}
print({k: round(v, 4) for k, v in evaluation.items()})
calibration = pd.DataFrame(calibration_table(y_test, p_test, n_bins=5))
print()
print(calibration.round(3).to_string())"""),
    C("""
# policies on test
policies = {
    "approve all": policy_cost(p_test, y_test, 1.0),
    "refuse all": policy_cost(p_test, y_test, -1.0),
    "model, cut off 1/6": policy_cost(p_test, y_test, BAYES_CUTOFF),
}
approve_share = float(np.mean(p_test <= BAYES_CUTOFF))
print({k: round(v, 4) for k, v in policies.items()})
print("share approved by the model policy:", round(approve_share, 3))

# bootstrap
rng = np.random.default_rng(SEED)
n_test = len(y_test)
diff_all, diff_none = [], []
for _ in range(4000):
    pick = rng.integers(0, n_test, n_test)
    c_model = policy_cost(p_test[pick], y_test[pick], BAYES_CUTOFF)
    diff_all.append(c_model - policy_cost(p_test[pick], y_test[pick], 1.0))
    diff_none.append(c_model - policy_cost(p_test[pick], y_test[pick], -1.0))
ci_all = np.percentile(diff_all, [2.5, 97.5])
ci_none = np.percentile(diff_none, [2.5, 97.5])
print("cost difference model minus approve all, 95 percent interval:", ci_all.round(3))
print("cost difference model minus refuse all, 95 percent interval:", ci_none.round(3))"""),
]

S[13] = [
    C("""
taus = np.linspace(0.02, 0.9, 89)
curve = [policy_cost(p_test, y_test, tau) for tau in taus]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(taus, curve, color=COLORS["main"], label="model policy, test")
ax.axhline(policies["approve all"], color=COLORS["second"], linestyle="--", label="approve all")
ax.axhline(policies["refuse all"], color=COLORS["grey"], linestyle="--", label="refuse all")
ax.axvline(BAYES_CUTOFF, color="black", linestyle=":", label="cut off 1/6")
ax.set_xlabel("cut off on predicted probability of bad")
ax.set_ylabel("cost per applicant")
ax.set_title("Cost per applicant against the cut off, 300 held out applicants")
ax.legend()
save_figure(fig, MODULE, "cost_by_cutoff.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots(figsize=(6.5, 4))
names = list(policies)
ax.bar(names, [policies[n] for n in names], color=[COLORS["second"], COLORS["grey"], COLORS["main"]])
ax.set_ylabel("cost per applicant")
ax.set_title("Expected cost by policy, test sample")
save_figure(fig, MODULE, "policy_cost_comparison.png")
plt.show()"""),
]

S[14] = [
    C("""
print(f"The model ranks held out applicants with AUC {evaluation['auc']:.3f} and KS {evaluation['ks']:.3f}.")
print(f"At the cut off 1/6 it approves {approve_share * 100:.0f} percent of applicants. Cost per applicant: model {policies['model, cut off 1/6']:.3f}, "
      f"approve all {policies['approve all']:.3f}, refuse all {policies['refuse all']:.3f}.")
print(f"Reduction against approve all: {policies['approve all'] - policies['model, cut off 1/6']:.3f} per applicant "
      f"(95 percent interval of the difference {ci_all[0]:.3f} to {ci_all[1]:.3f}).")
print(f"Reduction against refuse all: {policies['refuse all'] - policies['model, cut off 1/6']:.3f} per applicant "
      f"(95 percent interval of the difference {ci_none[0]:.3f} to {ci_none[1]:.3f}).")"""),
    M("""
**How to read it.** On this sample, where 30 percent of applicants are bad, and with the 5 to 1 costs, the cheapest simple policy is to **refuse everyone**, because a bad loan costs five times a lost good one. At a lower bad rate that changes, as the prior shift table shows. The model has to beat that
policy to be worth using, not only the policy of approving everyone. Refusing everyone is also not a business. The costs here count only the two errors. They do not count the profit on good loans, so refusing everyone looks better
than it is. This is why the baseline comparison needs a statement of what the cost leaves out.

With 300 test applicants, the interval is wide. The point estimate is a good guide to direction and a poor guide to size.
"""),
]

S[15] = [
    M("""
Four experiments. (A) Does the result hold over many splits? (B) Is a cut off chosen from data better than the derived 1/6? (C) What does excluding the protected attributes cost? (D) What if the bad rate in use is not the sample bad rate?
"""),
    C("""
# a repeated splits
split_rows = []
for seed in range(100):
    tr, te = train_test_split(np.arange(len(data)), test_size=0.3, stratify=target, random_state=seed)
    z = design(model_columns, tr)
    f = fit_logistic(z.iloc[tr].to_numpy(), target.iloc[tr].to_numpy(), l2=L2)
    p = predict_proba(z.iloc[te].to_numpy(), f["intercept"], f["slopes"])
    y = target.iloc[te].to_numpy()
    split_rows.append({"seed": seed, "auc": roc_auc(y, p), "model": policy_cost(p, y, BAYES_CUTOFF),
                       "approve_all": policy_cost(p, y, 1.0), "refuse_all": policy_cost(p, y, -1.0)})
splits = pd.DataFrame(split_rows)
print(splits[["auc", "model", "approve_all", "refuse_all"]].describe().loc[["mean", "std", "min", "max"]].round(3).to_string())
share_beats_refuse = float((splits["model"] < splits["refuse_all"]).mean())
share_beats_approve = float((splits["model"] < splits["approve_all"]).mean())
print("share of splits where the model beats refuse all:", share_beats_refuse, "approve all:", share_beats_approve)"""),
    C("""
# b chosen cut off
fold_p = np.zeros(len(train_idx))
for fit_rows, hold_rows in KFold(5, shuffle=True, random_state=SEED).split(train_idx):
    f = fit_logistic(X_final.iloc[train_idx].iloc[fit_rows].to_numpy(), y_train[fit_rows], l2=L2)
    fold_p[hold_rows] = predict_proba(X_final.iloc[train_idx].iloc[hold_rows].to_numpy(), f["intercept"], f["slopes"])
grid = np.arange(0.05, 0.61, 0.01)
fold_costs = [policy_cost(fold_p, y_train, g) for g in grid]
chosen = float(grid[int(np.argmin(fold_costs))])
print("cut off chosen by cross validation on train:", round(chosen, 2), "derived:", round(BAYES_CUTOFF, 3))
print("test cost at chosen:", round(policy_cost(p_test, y_test, chosen), 4), "at derived:", round(policy_cost(p_test, y_test, BAYES_CUTOFF), 4))

# c protected attributes
f_all = fit_logistic(X_all.iloc[train_idx].to_numpy(), y_train, l2=L2)
p_all = predict_proba(X_all.iloc[test_idx].to_numpy(), f_all["intercept"], f_all["slopes"])
protected_effect = {"auc_with": roc_auc(y_test, p_all), "auc_without": auc_scratch,
                    "cost_with": policy_cost(p_all, y_test, BAYES_CUTOFF), "cost_without": policies["model, cut off 1/6"]}
print({k: round(v, 4) for k, v in protected_effect.items()})"""),
    C("""
# d prior shift
sample_rate = float(y_train.mean())
shift_rows = []
for rate in [0.05, 0.10, 0.20, 0.30]:
    k = (rate / (1 - rate)) / (sample_rate / (1 - sample_rate))
    odds = p_test / (1 - p_test) * k
    p_shift = odds / (1 + odds)
    weight = np.where(y_test == 1, rate / y_test.mean(), (1 - rate) / (1 - y_test.mean()))
    def weighted_cost(approve):
        cost = np.where(approve & (y_test == 1), COST_BAD_APPROVED, 0.0) + np.where(~approve & (y_test == 0), COST_GOOD_REFUSED, 0.0)
        return float(np.sum(cost * weight) / np.sum(weight))
    shift_rows.append({
        "portfolio_bad_rate": rate,
        "approve_share_adjusted_cutoff": float(np.mean(p_shift <= BAYES_CUTOFF)),
        "cost_model_adjusted": weighted_cost(p_shift <= BAYES_CUTOFF),
        "cost_model_unadjusted": weighted_cost(p_test <= BAYES_CUTOFF),
        "cost_approve_all": weighted_cost(np.ones(len(y_test), dtype=bool)),
        "cost_refuse_all": weighted_cost(np.zeros(len(y_test), dtype=bool)),
    })
shift_table = pd.DataFrame(shift_rows)
print(shift_table.round(3).to_string(index=False))"""),
]

S[16] = [
    C("""
criteria = {
    "scratch_and_sklearn_auc_within_0.01": bool(abs(auc_scratch - auc_sk) < 0.01),
    "split_disjoint_and_stratified": bool(len(set(train_idx) & set(test_idx)) == 0
        and abs(y_train.mean() - target.mean()) < 0.02 and abs(y_test.mean() - target.mean()) < 0.02),
    "derived_cutoff_equals_numerical_minimiser": bool(k_star == approved_by_rule),
    "test_auc_at_least_0.70": bool(evaluation["auc"] >= 0.70),
    "model_cost_below_approve_all_with_interval_excluding_zero": bool(policies["model, cut off 1/6"] < policies["approve all"] and ci_all[1] < 0),
    "no_protected_columns_in_final_model": bool(not any(col.startswith(tuple(PROTECTED)) for col in X_final.columns)),
}
print(criteria)

metrics = {
    "test_evaluation": evaluation,
    "calibration_deciles_5_bins": calibration.round(4).to_dict(orient="records"),
    "policy_cost_per_applicant": policies,
    "approve_share_at_cutoff": approve_share,
    "cost_difference_vs_approve_all_ci95": ci_all.tolist(),
    "cost_difference_vs_refuse_all_ci95": ci_none.tolist(),
    "bayes_cutoff": BAYES_CUTOFF,
    "cutoff_chosen_by_cross_validation": chosen,
    "repeated_splits": {"n": 100, "auc_mean": float(splits["auc"].mean()), "auc_std": float(splits["auc"].std()),
                        "share_model_beats_refuse_all": share_beats_refuse, "share_model_beats_approve_all": share_beats_approve,
                        "model_cost_mean": float(splits["model"].mean()), "refuse_all_cost_mean": float(splits["refuse_all"].mean()),
                        "approve_all_cost_mean": float(splits["approve_all"].mean())},
    "protected_attributes_effect": protected_effect,
    "prior_shift": shift_table.to_dict(orient="records"),
    "newton_iterations": int(fit["iterations"]),
    "test_auc_scikit_learn": float(auc_sk),
    "acceptance_criteria": criteria,
}
config = {"test_size": 0.3, "l2": L2, "cost_bad_approved": COST_BAD_APPROVED, "cost_good_refused": COST_GOOD_REFUSED,
          "protected_excluded": PROTECTED, "bootstrap_resamples": 4000, "repeated_splits": 100, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Logistic PD model on real applicant data, cost based cut off from error costs, bootstrap cost reduction, repeated splits, prior shift",
    data_kind="empirical",
    dataset="datasets/raw/german_credit.csv",
    n_obs=int(len(data)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "the 5 to 1 error costs come with the dataset and are not a bank's economics",
        "probabilities are treated as calibrated when the cut off is derived",
        "protected attributes are excluded, age is kept",
    ],
    metrics=metrics,
    baseline="approve all and refuse all",
    limitations=[
        "1000 applicants from one old source, 300 in the test set, so intervals are wide",
        "costs count only two errors, not profit on good loans",
        "no reject inference, so performance on refused applicants is unknown",
        "age is kept as a feature, which some regulations do not allow",
        "no out of time test, the data has no dates",
    ],
    figures=["cost_by_cutoff.png", "policy_cost_comparison.png"],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
1. **Small and old.** 1000 applicants, one source, no dates. Behaviour of today's applicants is not known from it.
2. **Wide intervals.** With 300 test rows the cost difference has a wide interval. The repeated splits show how much the answer moves with the split.
3. **Costs.** The 5 to 1 ratio is a benchmark convention. It leaves out the profit on good loans, so refusing everyone looks too good, and it leaves out the cost of recovery work, so bad loans look too cheap or too dear depending on the case.
4. **Calibration.** The derived cut off assumes the probabilities are right. The calibration table has five bins of 60 applicants and cannot show small errors.
5. **Selection bias.** The data contain applicants who were granted a loan and then observed. Refused applicants are absent, so the model's behaviour on them is unknown. Reject inference is not done.
6. **Protected attributes.** Removing the columns does not remove proxies. Other variables such as age, job or housing can carry the same information. A fairness review is a separate piece of work and is not done here.
7. **Age.** Age is kept. Some jurisdictions restrict its use in credit decisions. Check the rule that applies.
8. **Model risk.** One model, one specification, no challenger beyond scikit-learn on the same features. Governance guidance (SR 26-2) asks for independent validation, which does not exist for this notebook.
"""),
]

S[18] = [
    M("""
**What this looks like at work.** An analyst in credit risk or a scorecard team prepares a **cut off recommendation** for the credit committee. The pack has five parts.

1. The model: inputs, performance on held out data, calibration and stability across splits.
2. The policy: the proposed cut off, the approval share it implies, and the expected cost against the two baselines with an interval.
3. The sensitivity: what happens if the real bad rate or the cost ratio is different (section 15).
4. The controls: protected attributes excluded, proxies reviewed, monitoring plan (PSI on inputs and on the score, as in the credit scoring module), a date for revalidation.
5. The decision requested, written as one sentence: for example "approve at or below this probability for six months, then review with observed outcomes".

**What the committee must still provide.** The real cost of a bad loan (loss given default and recovery cost) and the real margin on a good loan. Without them the cut off is a demonstration. With them the same code gives a decision.
"""),
]

S[19] = [
    M("""
1. Change the cost ratio to 3 to 1 and to 10 to 1. How does the cut off, the approval share and the gain against refuse all change?
2. Add a margin of 0.4 units on every approved good loan. Redo the policy comparison. Is refusing everyone still the cheapest simple policy?
3. Fit a gradient boosting model and compare AUC and cost over the 100 splits. Is the gain larger than the spread across splits?
4. Replace the five bin calibration table by isotonic calibration on the training folds. Does the cost at 1/6 improve?
5. Write the one sentence decision request for the committee using your own cost figures.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "12_end_to_end_banking_projects/credit_decision_cutoff",
        "title": "Practical Method: From a Default Model to an Approval Cut Off",
        "family": "End to End Banking Projects",
        "level": "Applied",
        "dataset": "german_credit",
        "data_kind": "empirical",
        "status": "Validating",
        "tagline": "A default model on 1000 real loan applicants, turned into a cost based cut off with a measured reduction in expected cost.",
        "refs": ["lessmann2015", "gunnarsson2021", "sr262"],
        "research_note": (
            "Lessmann et al. (2015) and Gunnarsson et al. (2021) benchmark credit scoring methods and support the use of a simple transparent baseline that is then measured on held out data. "
            "SR 26-2 is the supervisory guidance on model risk management that frames the controls section. The module does not reproduce a published result."
        ),
        "learn": [
            "Split, fit and evaluate a default model on real applicant data without leakage",
            "Derive a cut off from the cost of each error and verify it numerically",
            "Measure the cost reduction against simple policies with an interval",
            "See how a different portfolio bad rate changes the decision",
            "Handle protected attributes openly",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
