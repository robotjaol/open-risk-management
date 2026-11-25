"""Spec: VaR backtesting."""

from nbgen import C, M

from specs._common import PORTFOLIO_CODE, check_sections, setup_code

MODULE = "backtesting"

SETUP = setup_code(MODULE) + """
import math

from scipy.special import xlogy
from scipy.stats import binom, chi2, t

from risk_lab.market.backtest import (
    basel_traffic_light, christoffersen_conditional_coverage, christoffersen_independence,
    exceptions, kupiec_pof, probability_of_at_most,
)
from risk_lab.market.var import (
    ewma_var, normal_var, rolling_historical_var, rolling_normal_var, student_t_var,
)"""

S = {}

S[1] = [
    M("""
A bank reports a 99 percent one day VaR every day. If the model is right, the loss exceeds the VaR on about 1 day in 100,
and the exceptions are scattered, not bunched. **Backtesting** compares the forecasts with what happened and decides whether the
model is acceptable.

This notebook builds the three standard tests (Kupiec proportion of failures, Christoffersen independence, and the joint
conditional coverage test), applies the Basel style traffic light, and then measures the thing that is often forgotten:
**how likely each test is to catch a bad model.** A test that cannot detect a 2 percent exception rate in 250 days gives no comfort
when it passes.

**Decision this supports:** accept, review or reject a VaR model, and know how much that decision rests on a test with little power.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Compute the Kupiec likelihood ratio and the Christoffersen independence statistic by hand.
2. Reproduce both with an independent implementation and match the library.
3. Derive traffic light zones from binomial probabilities.
4. Apply the tests to five VaR models on the same days and read the results together.
5. Measure the power of each test by simulation, as a function of the true exception rate and the sample length.
6. Show a case where the count test passes and the independence test fails.
7. Write a model decision rule and state its limits.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Exception (hit) | A day when the loss exceeded the VaR forecast. Coded 1, otherwise 0 |
| Unconditional coverage | The exception rate equals 1 - alpha. Tested by Kupiec |
| Independence | Today's exception does not depend on yesterday's. Tested by Christoffersen |
| Conditional coverage | Both properties together. Statistic is the sum of the two likelihood ratios |
| Traffic light | Basel style classification of the exception count over 250 days into green, yellow and red |
| Size of a test | Chance of rejecting a correct model |
| Power of a test | Chance of rejecting a wrong model |
"""),
]

S[4] = [
    M("""
**Why these tests?**

| Test | Detects | Misses |
|---|---|---|
| Kupiec (count) | Too many or too few exceptions in total | Clustering. A model with the right count and all exceptions in one month passes |
| Christoffersen (independence) | Exceptions that bunch together | A wrong count if the exceptions are spread out |
| Conditional coverage | Either problem, with less power on each alone | |
| Traffic light | Large exception counts over 250 days with simple actions | Anything below 5 exceptions. Very low power |

Acceptance criteria:

1. The loop implementations match the library to 1e-9 in the statistic and the p value.
2. Zone boundaries computed from binomial probabilities agree with the library function for 0 to 12 exceptions.
3. Power results are reported for at least two sample lengths and three true exception rates.
4. Decision rule is stated before the results are read, and applied mechanically.

**Decision rule (set before the run):** a model is **accepted** if Kupiec, Christoffersen independence and conditional coverage
p values are all above 0.05 and the last 250 day window is green. Otherwise it is **flagged for review**.
This is a teaching rule, not a regulatory one. With five models and three tests, some failures are expected by chance alone.
"""),
]

S[6] = [
    M(r"""
Let $I_t \in \{0, 1\}$ be the exception indicator over $T$ days, $x = \sum I_t$, $p = 1 - \alpha$ the target rate and $\hat p = x/T$.

**Kupiec proportion of failures.**

$$LR_{pof} = -2\ln\frac{(1-p)^{T-x} p^{x}}{(1-\hat p)^{T-x}\hat p^{x}} \;\sim\; \chi^2(1)$$

**Christoffersen independence.** Count transitions $n_{ij}$ from state $i$ yesterday to state $j$ today.
Let $\pi_{01} = n_{01}/(n_{00}+n_{01})$, $\pi_{11} = n_{11}/(n_{10}+n_{11})$, $\pi = (n_{01}+n_{11})/(n_{00}+n_{01}+n_{10}+n_{11})$.

$$LR_{ind} = -2\ln\frac{(1-\pi)^{n_{00}+n_{10}}\pi^{n_{01}+n_{11}}}{(1-\pi_{01})^{n_{00}}\pi_{01}^{n_{01}}(1-\pi_{11})^{n_{10}}\pi_{11}^{n_{11}}} \;\sim\; \chi^2(1)$$

**Conditional coverage.** $LR_{cc} = LR_{pof} + LR_{ind} \sim \chi^2(2)$.

**Traffic light.** Under a correct model $x \sim \mathrm{Binomial}(250, 0.01)$. The cumulative probability $P(X \le x)$ ranks how
unusual a count is. Zone boundaries in the Basel framework are tied to cumulative probabilities. The exact thresholds must be checked
against the current text before use.

**Power by simulation.** Draw $x \sim \mathrm{Binomial}(T, p_{true})$, compute $LR_{pof}$, and count the share of draws above the
$\chi^2(1)$ 95 percent point. The same idea works for the independence test with a Markov chain of exceptions.
"""),
]

S[7] = [
    M("""
**Part A. Kupiec by hand.** T = 250 days, x = 6 exceptions, target p = 0.01.
"""),
    C("""
T, x, p = 250, 6, 0.01
p_hat = x / T
ll_null = x * math.log(p) + (T - x) * math.log(1 - p)
ll_alt = x * math.log(p_hat) + (T - x) * math.log(1 - p_hat)
lr_hand = -2 * (ll_null - ll_alt)
p_value_hand = float(chi2.sf(lr_hand, 1))
print("observed rate:", p_hat, "expected exceptions:", T * p)
print("LR_pof by hand:", round(lr_hand, 4), "p value:", round(p_value_hand, 4))
lib = kupiec_pof(np.r_[np.ones(x), np.zeros(T - x)], p)
print("library LR_pof:", round(lib["lr_pof"], 4), "p value:", round(lib["p_value"], 4))
assert abs(lr_hand - lib["lr_pof"]) < 1e-9"""),
    M("""
**Part B. Independence by hand** on a 20 day sequence with four exceptions, two of them on consecutive days.
"""),
    C("""
seq = np.array([0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
n = {"00": 0, "01": 0, "10": 0, "11": 0}
for before, after in zip(seq[:-1], seq[1:]):
    n[f"{before}{after}"] += 1
print("transition counts:", n)
pi01 = n["01"] / (n["00"] + n["01"])
pi11 = n["11"] / (n["10"] + n["11"])
pi_all = (n["01"] + n["11"]) / sum(n.values())
print("pi01:", round(pi01, 4), "pi11:", round(pi11, 4), "pi:", round(pi_all, 4))

def safe_log(value):
    return math.log(value) if value > 0 else 0.0

ll0 = (n["00"] + n["10"]) * safe_log(1 - pi_all) + (n["01"] + n["11"]) * safe_log(pi_all)
ll1 = (n["00"] * safe_log(1 - pi01) + n["01"] * safe_log(pi01) + n["10"] * safe_log(1 - pi11) + n["11"] * safe_log(pi11))
lr_ind_hand = -2 * (ll0 - ll1)
print("LR_ind by hand:", round(lr_ind_hand, 4), "library:", round(christoffersen_independence(seq)["lr_ind"], 4))
assert abs(lr_ind_hand - christoffersen_independence(seq)["lr_ind"]) < 1e-9"""),
    M("""
**Part C. Traffic light zones from binomial probabilities** for 250 days and a 1 percent rate.
"""),
    C("""
rows = []
for count in range(0, 13):
    rows.append(
        {
            "exceptions": count,
            "cumulative_probability": probability_of_at_most(count),
            "library_zone": basel_traffic_light(count)["zone"],
            "library_add_on": basel_traffic_light(count)["add_on"],
        }
    )
zone_table = pd.DataFrame(rows)
print(zone_table.round(5).to_string(index=False))"""),
    M("""
The cumulative probability crosses 0.95 at 5 exceptions and passes 0.9999 at 10 exceptions.
That is the logic behind the yellow and red limits, as the library encodes them. **Check before use:** the exact zone rule and
the capital multiplier add ons are set by the supervisor. The values printed here come from the library's own table, not from a source verified in this build.
"""),
    C("""
def zone_from_probability(count):
    cum = probability_of_at_most(count)
    if cum < 0.95:
        return "green"
    if cum < 0.9999:
        return "yellow"
    return "red"


matches = [zone_from_probability(c) == basel_traffic_light(c)["zone"] for c in range(0, 13)]
print("zones from probability agree with the library for 0 to 12 exceptions:", all(matches))
assert all(matches)"""),
]

S[8] = [
    M("""
The five models from the parametric module are rebuilt here, with the same parameters, so this notebook runs on its own.
The t degrees of freedom are estimated on the first 1000 days and floored at 3.0.
"""),
    C(PORTFOLIO_CODE),
    C("""
sample = portfolio.to_numpy()
ALPHA = 0.99
start, end = 1000, len(sample)
nu_raw, _, _ = t.fit(sample[:start])
nu_hat = float(max(nu_raw, 3.0))
print("raw nu:", round(float(nu_raw), 3), "used:", nu_hat)

rolling_t = np.full(len(sample), np.nan)
for day in range(500, len(sample)):
    part = sample[day - 500 : day]
    rolling_t[day] = student_t_var(part.mean(), part.std(ddof=1), nu_hat, ALPHA)

var_models = {
    "historical 500": rolling_historical_var(sample, 500, ALPHA),
    "normal rolling 500": rolling_normal_var(sample, 500, ALPHA),
    "student t rolling 500": rolling_t,
    "ewma normal": ewma_var(sample, 0.94, ALPHA, None),
    "ewma student t": ewma_var(sample, 0.94, ALPHA, nu_hat),
}
hits = {name: exceptions(sample[start:end], series[start:end]) for name, series in var_models.items()}
print({name: int(h.sum()) for name, h in hits.items()}, "of", end - start, "days")"""),
]

S[9] = [
    M("""
Preparation is the alignment step. Each forecast for day $t$ uses data to $t-1$. Exceptions are computed on days 1000 to 2999 for all models, so the tests use the same days.
The hits for each model are binary arrays of length 2000.
"""),
    C("""
print("hit array lengths:", {name: len(h) for name, h in hits.items()})
print("all hits binary:", all(set(np.unique(h)) <= {0, 1} for h in hits.values()))
print("expected exceptions per model:", (end - start) * (1 - ALPHA))"""),
]

S[10] = [
    M("""
Both tests written with plain loops and `math.log`, then compared with the library for every model.
"""),
    C("""
def my_kupiec(hit_list, rate):
    total = len(hit_list)
    count = int(sum(hit_list))
    def loglik(prob):
        value = 0.0
        if count > 0:
            value += count * math.log(prob)
        if total - count > 0:
            value += (total - count) * math.log(1 - prob)
        return value
    stat = max(-2 * (loglik(rate) - loglik(count / total)), 0.0)
    return stat, float(chi2.sf(stat, 1))


def my_independence(hit_list):
    n00 = n01 = n10 = n11 = 0
    for before, after in zip(hit_list[:-1], hit_list[1:]):
        if before == 0 and after == 0:
            n00 += 1
        elif before == 0 and after == 1:
            n01 += 1
        elif before == 1 and after == 0:
            n10 += 1
        else:
            n11 += 1
    pi01 = n01 / (n00 + n01) if n00 + n01 > 0 else 0.0
    pi11 = n11 / (n10 + n11) if n10 + n11 > 0 else 0.0
    pi_all = (n01 + n11) / (n00 + n01 + n10 + n11)
    def lg(value):
        return math.log(value) if value > 0 else 0.0
    null = (n00 + n10) * lg(1 - pi_all) + (n01 + n11) * lg(pi_all)
    alt = n00 * lg(1 - pi01) + n01 * lg(pi01) + n10 * lg(1 - pi11) + n11 * lg(pi11)
    stat = max(-2 * (null - alt), 0.0)
    return stat, float(chi2.sf(stat, 1))


worst_gap = 0.0
for name, h in hits.items():
    k_stat, k_p = my_kupiec(list(h), 1 - ALPHA)
    i_stat, i_p = my_independence(list(h))
    lib_k = kupiec_pof(h, 1 - ALPHA)
    lib_i = christoffersen_independence(h)
    worst_gap = max(worst_gap, abs(k_stat - lib_k["lr_pof"]), abs(k_p - lib_k["p_value"]), abs(i_stat - lib_i["lr_ind"]), abs(i_p - lib_i["p_value"]))
print("largest gap between loops and library, all models and tests:", f"{worst_gap:.2e}")
assert worst_gap < 1e-9"""),
]

S[11] = [
    M("""
A second check with `scipy.stats.binom`: the Kupiec likelihood ratio written as a difference of binomial log probabilities.
This uses a different code path for the likelihood.
"""),
    C("""
gap_binom = 0.0
for name, h in hits.items():
    total, count = len(h), int(h.sum())
    lr = -2 * (binom.logpmf(count, total, 1 - ALPHA) - binom.logpmf(count, total, count / total))
    gap_binom = max(gap_binom, abs(lr - kupiec_pof(h, 1 - ALPHA)["lr_pof"]))
print("largest gap, Kupiec via binomial log pmf:", f"{gap_binom:.2e}")
assert gap_binom < 1e-9"""),
]

S[12] = [
    M("""
Full evaluation. For the traffic light, two views: the **last 250 days** of the evaluation period, and the share of all
overlapping 250 day windows in each zone.
"""),
    C("""
rows = []
zone_share = {}
for name, h in hits.items():
    pof = kupiec_pof(h, 1 - ALPHA)
    ind = christoffersen_independence(h)
    cc = christoffersen_conditional_coverage(h, 1 - ALPHA)
    last = int(h[-250:].sum())
    cumulative = np.concatenate([[0], np.cumsum(h)])
    window_counts = cumulative[250:] - cumulative[:-250]
    zones = [basel_traffic_light(int(c))["zone"] for c in window_counts]
    zone_share[name] = {z: zones.count(z) / len(zones) for z in ["green", "yellow", "red"]}
    rows.append(
        {
            "model": name,
            "exceptions": int(h.sum()),
            "expected": len(h) * (1 - ALPHA),
            "kupiec_p": pof["p_value"],
            "independence_p": ind["p_value"],
            "conditional_p": cc["p_value"],
            "last_250_count": last,
            "last_250_zone": basel_traffic_light(last)["zone"],
            "windows_green": zone_share[name]["green"],
            "windows_yellow": zone_share[name]["yellow"],
            "windows_red": zone_share[name]["red"],
        }
    )
evaluation = pd.DataFrame(rows).set_index("model")
print(evaluation.round(4).to_string())"""),
    C("""
# decision rule from section 4
evaluation["accepted"] = (
    (evaluation["kupiec_p"] > 0.05) & (evaluation["independence_p"] > 0.05)
    & (evaluation["conditional_p"] > 0.05) & (evaluation["last_250_zone"] == "green")
)
print(evaluation[["exceptions", "kupiec_p", "independence_p", "conditional_p", "last_250_zone", "accepted"]].round(4).to_string())"""),
]

S[13] = [
    C("""
fig, axes = plt.subplots(1, 2, figsize=(14, 4.4))
names = list(hits.keys())
for index, name in enumerate(names):
    days = np.where(hits[name] == 1)[0] + start
    axes[0].scatter(portfolio.index[days], np.full(len(days), index), s=14, color=COLORS["main"])
axes[0].set_yticks(range(len(names)))
axes[0].set_yticklabels(names)
axes[0].axvspan(portfolio.index[2200], portfolio.index[2259], color=COLORS["second"], alpha=0.15)
axes[0].set_title("Exception days by model (shaded: volatility burst)")

for name, color in zip(names, [COLORS["grey"], COLORS["main"], COLORS["third"], COLORS["second"], "#8064a2"]):
    axes[1].plot(np.cumsum(hits[name]), color=color, label=name)
axes[1].plot(np.arange(end - start) * (1 - ALPHA), color="black", linestyle=":", label="expected")
axes[1].set_xlabel("evaluation day")
axes[1].set_ylabel("cumulative exceptions")
axes[1].set_title("Cumulative exceptions against expected")
axes[1].legend(fontsize=8)
save_figure(fig, MODULE, "exception_timeline.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots()
width = 0.25
positions = np.arange(len(names))
ax.bar(positions - width, evaluation["kupiec_p"], width, color=COLORS["main"], label="Kupiec")
ax.bar(positions, evaluation["independence_p"], width, color=COLORS["third"], label="independence")
ax.bar(positions + width, evaluation["conditional_p"], width, color=COLORS["second"], label="conditional coverage")
ax.axhline(0.05, color="black", linestyle=":")
ax.set_xticks(positions)
ax.set_xticklabels(names, rotation=20)
ax.set_ylabel("p value")
ax.set_title("Backtest p values (dotted line: 0.05)")
ax.legend()
save_figure(fig, MODULE, "backtest_p_values.png")
plt.show()"""),
]

S[14] = [
    M("""
Read the table with these cautions:

* **Observed.** The decision column applies the rule from section 4 mechanically. It is a screening result on one sample of 2000 days.
* **Inference.** Five models and three tests mean 15 p values. At a 5 percent size, about one in twenty correct models would fail one test by chance. A single failure is a reason to look, not proof of a bad model.
* **Observed.** Compare the independence p value with the Kupiec p value for each model. A model can pass the count test and fail the independence test, which means the average is right and the timing is wrong.
* **Observed.** The traffic light on the last 250 days is one window. The share of green, yellow and red windows shows how the zone changes over the sample.
* **Observed.** The two sided tests also pass a model that has **fewer** exceptions than expected, within the test's tolerance. Such a model is conservative, which costs capital. The next cell lists the models below the expected count.
"""),
    C("""
print("models passing Kupiec:", [n for n in names if evaluation.loc[n, "kupiec_p"] > 0.05])
print("models passing independence:", [n for n in names if evaluation.loc[n, "independence_p"] > 0.05])
print("models passing conditional coverage:", [n for n in names if evaluation.loc[n, "conditional_p"] > 0.05])
print("models with Kupiec pass and independence fail:", [n for n in names if evaluation.loc[n, "kupiec_p"] > 0.05 and evaluation.loc[n, "independence_p"] <= 0.05])
print("accepted by the rule:", [n for n in names if evaluation.loc[n, "accepted"]])
print("models with fewer exceptions than expected:", [n for n in names if evaluation.loc[n, "exceptions"] < evaluation.loc[n, "expected"]])
share_in_burst = {n: int(hits[n][2200 - start : 2260 - start].sum()) for n in names}
print("exceptions inside the 60 day burst:", share_in_burst, "expected about", round(60 * (1 - ALPHA), 2))"""),
]

S[15] = [
    M("""
**Experiment A: power of the Kupiec test.** For true exception rates 1, 1.5, 2 and 3 percent and sample lengths 250, 500, 1000, 2000 and 4000 days,
draw the exception count from a binomial and record the share of draws that reject at 5 percent. At a true rate of 1 percent this share
is the actual size of the test.

**Experiment B: the traffic light under a wrong model.** Distribution of zones over 250 days for the same true rates.

**Experiment C: clustering.** Simulate exceptions as a two state Markov chain with an overall rate of 1 percent and a chance of
1, 10, 20 and 30 percent of an exception following an exception. **Prediction written before the run:** the count test stays near its
size and the independence test reacts. **What the run showed:** the independence test reacts strongly, but the count test also rejects more often
than 5 percent, because clustering widens the spread of the exception count around its mean. The prediction was only half right.

**Size of the test.** At a true rate of 1 percent the rejection rate is the actual size of the test. With only 2.5 expected exceptions in 250 days the
chi square approximation is rough, so the actual size can differ from the nominal 5 percent. The table reports it.
"""),
    C("""
def lr_pof_vector(counts, total, rate):
    p_hat = counts / total
    null = xlogy(counts, rate) + xlogy(total - counts, 1 - rate)
    alt = xlogy(counts, p_hat) + xlogy(total - counts, 1 - p_hat)
    return np.maximum(-2 * (null - alt), 0.0)


critical_1 = chi2.ppf(0.95, 1)
rng = np.random.default_rng(SEED)
n_sim = 20000
rows = []
for total in [250, 500, 1000, 2000, 4000]:
    for true_rate in [0.01, 0.015, 0.02, 0.03]:
        counts = rng.binomial(total, true_rate, size=n_sim)
        reject = float(np.mean(lr_pof_vector(counts, total, 0.01) > critical_1))
        rows.append({"days": total, "true_rate": true_rate, "kupiec_rejection_rate": reject})
power_table = pd.DataFrame(rows)
print(power_table.pivot(index="days", columns="true_rate", values="kupiec_rejection_rate").round(3))"""),
    C("""
zone_rows = []
for true_rate in [0.01, 0.015, 0.02, 0.03]:
    counts = rng.binomial(250, true_rate, size=n_sim)
    zones = np.array([basel_traffic_light(int(c))["zone"] for c in counts])
    zone_rows.append({"true_rate": true_rate, "green": float(np.mean(zones == "green")),
                      "yellow": float(np.mean(zones == "yellow")), "red": float(np.mean(zones == "red"))})
zone_power = pd.DataFrame(zone_rows)
print(zone_power.round(3).to_string(index=False))"""),
    C("""
def lr_ind_vector(h):
    before, after = h[:, :-1], h[:, 1:]
    n00 = np.sum((before == 0) & (after == 0), axis=1).astype(float)
    n01 = np.sum((before == 0) & (after == 1), axis=1).astype(float)
    n10 = np.sum((before == 1) & (after == 0), axis=1).astype(float)
    n11 = np.sum((before == 1) & (after == 1), axis=1).astype(float)
    pi01 = np.divide(n01, n00 + n01, out=np.zeros_like(n01), where=(n00 + n01) > 0)
    pi11 = np.divide(n11, n10 + n11, out=np.zeros_like(n11), where=(n10 + n11) > 0)
    pi_all = (n01 + n11) / (n00 + n01 + n10 + n11)
    null = xlogy(n01 + n11, pi_all) + xlogy(n00 + n10, 1 - pi_all)
    alt = xlogy(n01, pi01) + xlogy(n00, 1 - pi01) + xlogy(n11, pi11) + xlogy(n10, 1 - pi11)
    return np.maximum(-2 * (null - alt), 0.0)


# vector check against library
test_h = (rng.random((3, 1000)) < 0.02).astype(int)
vec = lr_ind_vector(test_h)
lib_vals = np.array([christoffersen_independence(row)["lr_ind"] for row in test_h])
print("vector against library, max gap:", f"{np.max(np.abs(vec - lib_vals)):.2e}")
assert np.max(np.abs(vec - lib_vals)) < 1e-9

def markov_hits(n_paths, total, rate, stay):
    pi11 = stay
    pi01 = rate * (1 - pi11) / (1 - rate)
    out = np.zeros((n_paths, total), dtype=int)
    out[:, 0] = rng.random(n_paths) < rate
    for day in range(1, total):
        prob = np.where(out[:, day - 1] == 1, pi11, pi01)
        out[:, day] = rng.random(n_paths) < prob
    return out

rows = []
for stay in [0.01, 0.10, 0.20, 0.30]:
    paths = markov_hits(5000, 1000, 0.01, stay)
    kup = float(np.mean(lr_pof_vector(paths.sum(axis=1).astype(float), 1000, 0.01) > critical_1))
    ind = float(np.mean(lr_ind_vector(paths) > critical_1))
    rows.append({"p_hit_after_hit": stay, "overall_rate": float(paths.mean()), "kupiec_rejection": kup, "independence_rejection": ind})
cluster_power = pd.DataFrame(rows)
print(cluster_power.round(3).to_string(index=False))"""),
]

S[16] = [
    C("""
print(evaluation.round(4).to_string())
print()
print(power_table.pivot(index="days", columns="true_rate", values="kupiec_rejection_rate").round(3))
print()
print(cluster_power.round(3).to_string(index=False))
metrics = {
    "evaluation_by_model": evaluation.reset_index().to_dict(orient="records"),
    "decision_rule": "accepted if Kupiec, independence and conditional coverage p above 0.05 and last 250 day zone is green",
    "accepted_models": [n for n in names if evaluation.loc[n, "accepted"]],
    "max_gap_loops_vs_library": float(worst_gap),
    "max_gap_binomial_check": float(gap_binom),
    "zone_boundaries_agree_with_probability_rule": bool(all(matches)),
    "kupiec_power": power_table.to_dict(orient="records"),
    "traffic_light_under_wrong_model_250d": zone_power.to_dict(orient="records"),
    "clustering_power": cluster_power.to_dict(orient="records"),
    "nu_raw_first_1000_days": float(nu_raw),
    "nu_used": nu_hat,
    "acceptance_criteria": {
        "loops_match_library_1e-9": bool(worst_gap < 1e-9),
        "binomial_check_1e-9": bool(gap_binom < 1e-9),
        "zone_boundaries_agree_with_probability_rule": bool(all(matches)),
        "power_for_two_lengths_and_three_rates": bool(power_table["days"].nunique() >= 2 and power_table["true_rate"].nunique() >= 3),
    },
}
config = {"alpha": ALPHA, "window": 500, "ewma_decay": 0.94, "nu_used": nu_hat, "evaluation_days": [start, end],
          "power_simulations": n_sim, "markov_paths": 5000, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Kupiec, Christoffersen independence and conditional coverage tests, traffic light zones from binomial probabilities, simulated power",
    data_kind="synthetic",
    dataset="datasets/synthetic/market_returns.csv",
    n_obs=int(end - start),
    seed=SEED,
    parameters=config,
    assumptions=[
        "tests applied to clean (hypothetical) portfolio returns, not to actual trading P&L",
        "exceptions are iid under the null",
        "decision rule fixed before the results were read",
        "zone boundaries as encoded in the library, not verified against the current Basel text",
    ],
    metrics=metrics,
    baseline={"note": "historical 500 is the reference model"},
    limitations=[
        "low power at 250 days",
        "15 p values from one sample, no multiple testing correction",
        "synthetic data",
    ],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
**Limitations**

1. **Power and size.** The Kupiec table shows what a pass is worth. At 250 days a true exception rate of 2 percent is rejected in only about a quarter of simulated samples, so passing the test is weak evidence. Longer samples help, as the table shows. At 250 days the actual size is also above the nominal 5 percent, so the test both under detects and over rejects.
2. **Multiple testing.** Five models, three tests and several windows give many p values. No correction is applied.
3. **iid null.** The tests assume exceptions are independent under a correct model. The independence test checks only the first order dependence between consecutive days.
4. **Clean versus actual P&L.** Regulators compare VaR with both hypothetical and actual P&L. This notebook uses hypothetical returns from a fixed portfolio only.
5. **Count only.** These tests say nothing about the size of the exceedances. The expected shortfall module adds the Z1 diagnostic.
6. **Zone rules unverified.** The traffic light boundaries and add ons come from the library's own table. The probabilities behind them are computed here, but the exact supervisory rule must be checked.
7. **One confidence level.** Passing at 99 percent says nothing about 97.5 percent.
8. **Decision rule is a teaching rule.** It is not a regulatory test and not a validation standard.

**Model risk.** A backtest approves or flags a model. A weak backtest therefore creates model risk of its own: a wrong model that passes. The power numbers measure that risk.
"""),
]

S[18] = [
    M("""
A model validation team writes a short opinion per model. The table below turns the numbers into one line per model using
the rule from section 4, and adds the power context: how often a test at this sample length would have caught a true rate of 2 percent.
"""),
    C("""
power_2pct = float(power_table[(power_table["days"] == end - start) & (power_table["true_rate"] == 0.02)]["kupiec_rejection_rate"].iloc[0])
print("Kupiec rejection rate at", end - start, "days when the true rate is 2 percent:", round(power_2pct, 3))
opinion = evaluation[["exceptions", "kupiec_p", "independence_p", "conditional_p", "last_250_zone", "accepted"]].copy()
opinion["opinion"] = np.where(opinion["accepted"], "accept on this sample", "flag for review")
print(opinion.round(4).to_string())"""),
]

S[19] = [
    M("""
1. Change the rule so that a model must also have at most 1.5 times the expected exceptions. Which models change status?
2. Compute the power of the Kupiec test at 250 days for a true rate of 2 percent using the exact binomial distribution instead of simulation. Compare with the simulated number.
3. Build a three model comparison that tests the best and worst model against each other on the same days. What would a pairwise test need?
4. Add a test for dependence at lag 2. What does it say about the burst period?
5. Redo the power experiment with a 97.5 percent VaR. How many days are needed for 80 percent power against a true rate of 3.5 percent?
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "03_market_risk/backtesting",
        "title": "Backtesting Value at Risk",
        "family": "Market Risk",
        "level": "Intermediate",
        "dataset": "market_returns",
        "data_kind": "synthetic",
        "status": "Complete",
        "tagline": "Kupiec, Christoffersen and the traffic light, with a measured answer to how often each test catches a bad model.",
        "refs": ["kupiec1995", "christoffersen1998", "nolde2017", "acerbi2014", "bcbs_d457"],
        "research_note": (
            "Kupiec (1995) is the source of the proportion of failures test and Christoffersen (1998) of the independence and conditional coverage tests. "
            "The Basel market risk standard defines the supervisory use of exception counts. The module derives the zone boundaries from "
            "binomial probabilities and labels the exact supervisory thresholds as check before use. Nolde and Ziegel and Acerbi and Szekely are listed for "
            "the expected shortfall backtests that go beyond this module."
        ),
        "learn": [
            "Kupiec and Christoffersen statistics by hand and by library",
            "Traffic light zones from binomial probabilities",
            "Backtesting several models on the same days",
            "Power of each test by simulation",
            "A mechanical model decision rule and its limits",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
