"""Spec: expected shortfall."""

from nbgen import C, M

from specs._common import PORTFOLIO_CODE, check_sections, setup_code

MODULE = "expected_shortfall"

SETUP = setup_code(MODULE) + """
from scipy.integrate import quad
from scipy.stats import norm, t

from risk_lab.market.backtest import exceptions, kupiec_pof
from risk_lab.market.es import (
    ewma_es, exceedance_z1, historical_es, normal_es, rolling_historical_es, student_t_es,
    tail_mean_above_var,
)
from risk_lab.market.var import (
    ewma_var, ewma_volatility, historical_var, normal_var, rolling_historical_var, student_t_var,
)"""

S = {}

S[1] = [
    M("""
Value at Risk says where the tail starts. It does not say how deep the tail goes. Two portfolios can have the same
99 percent VaR and very different losses on the days that exceed it. **Expected shortfall (ES)** is the average
loss on the days that exceed the VaR, so it measures tail depth.

This notebook builds ES from the definition, verifies the closed forms by numerical integration, backtests ES on a
rolling basis, compares ES with VaR across confidence levels, and shows a small exact example where VaR is not
subadditive and ES is.

**Decision this supports:** whether a desk limit or a capital measure should use ES instead of, or beside, VaR,
and what the estimation and backtesting cost of that choice is.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Define ES as an average of VaR values and compute it by hand, including the fractional weight case.
2. Show that ES is the minimum of the Rockafellar and Uryasev function and that the minimiser is the VaR.
3. Verify the normal and Student t closed forms against numerical integration of the quantile function.
4. Build a rolling ES, and a backtest diagnostic (the Z1 statistic) with a simulated p value.
5. Compare ES and VaR across confidence levels and distributions, and test the claim that a normal 97.5 percent ES is close to a normal 99 percent VaR.
6. Compare the sampling error of ES and VaR with a bootstrap.
7. Reproduce an exact example where VaR is not subadditive and ES is.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| ES at level alpha | Average loss in the worst (1 - alpha) share of outcomes. Also called CVaR or tail VaR when the distribution is continuous |
| Subadditivity | Risk of a combined position is at most the sum of the stand alone risks |
| Coherent risk measure | Satisfies monotonicity, subadditivity, positive homogeneity and translation invariance (Artzner et al.) |
| Elicitability | A statistic is elicitable if it is the minimiser of an expected scoring function. VaR is. ES alone is not |
| Z1 statistic | Average of loss over ES on the days when the loss exceeded VaR, minus 1. About 0 if ES is right |
"""),
]

S[4] = [
    M("""
**Why look at ES?**

| Measure | Strength | Weakness |
|---|---|---|
| VaR | Simple. Easy to backtest by counting exceptions | Ignores the size of losses beyond the quantile. Can fail subadditivity |
| ES | Sees tail depth. Coherent. Basel moved its internal model measure to ES at 97.5 percent | Needs more data to estimate. Harder to backtest |

Acceptance criteria:

1. Hand calculation equals the library, including a fractional tail weight.
2. The Rockafellar and Uryasev minimiser on a grid equals the VaR and the minimum equals the ES.
3. Closed form ES equals numerical integration of the VaR curve to 1e-6.
4. Simulated large sample ES from a known t distribution is within 1 percent of the closed form.
5. Exact two loan example: VaR violates subadditivity, ES does not.
"""),
]

S[6] = [
    M(r"""
**Definition.** For a loss $L$ with continuous distribution and level $\alpha$:

$$\mathrm{ES}_\alpha = \frac{1}{1-\alpha}\int_\alpha^1 \mathrm{VaR}_u \, du = E\big[L \mid L \ge \mathrm{VaR}_\alpha\big]$$

**Empirical form** (Acerbi and Tasche). Sort losses from the largest $\ell_{[1]} \ge \ell_{[2]} \ge \dots$ and let $k = n(1-\alpha)$.
With $m = \lfloor k \rfloor$:

$$\widehat{\mathrm{ES}}_\alpha = \frac{1}{k}\left[\sum_{i=1}^{m} \ell_{[i]} + (k - m)\,\ell_{[m+1]}\right]$$

**Rockafellar and Uryasev.**

$$\mathrm{ES}_\alpha = \min_{c} \left\{ c + \frac{1}{1-\alpha} E\big[(L - c)^+\big] \right\}, \qquad \arg\min_c = \mathrm{VaR}_\alpha$$

**Normal closed form**, standard deviation $\sigma$, mean $\mu$, $z = \Phi^{-1}(\alpha)$:

$$\mathrm{ES}_\alpha = -\mu + \sigma \frac{\varphi(z)}{1-\alpha}$$

**Student t closed form**, standard deviation $\sigma$, degrees of freedom $\nu > 2$, $q = t_{\nu,\alpha}$, scale $s = \sigma\sqrt{(\nu-2)/\nu}$:

$$\mathrm{ES}_\alpha = -\mu + s\,\frac{f_\nu(q)}{1-\alpha}\,\frac{\nu + q^2}{\nu - 1}$$

**Discrete losses.** For outcomes $x_j$ with probabilities $p_j$, ES is the probability weighted average of the worst
$(1-\alpha)$ of the mass. The two loan example in section 15 uses this exactly.
"""),
]

S[7] = [
    M("""
The same 20 returns as in the historical VaR notebook. For 90 percent ES, $k = 20 \\times 0.1 = 2$, so ES is the mean
of the two worst losses. For 92.5 percent, $k = 1.5$: the worst loss counts fully and the second counts half.
"""),
    C("""
small = np.array([0.8, -1.2, 0.3, -0.5, 1.1, -2.6, 0.2, -0.9, 0.6, -0.1,
                  -1.8, 0.4, -0.3, 0.9, -3.4, 0.1, -0.7, 0.5, -1.5, 0.7]) / 100
worst = np.sort(-small)[::-1]
print("worst five losses (percent):", (100 * worst[:5]).round(2))

es90_hand = worst[:2].mean()
print("ES 90 by hand (percent):", round(100 * es90_hand, 4), "library:", round(100 * historical_es(small, 0.90), 4))
assert abs(es90_hand - historical_es(small, 0.90)) < 1e-12

k = 20 * (1 - 0.925)
es925_hand = (worst[0] + 0.5 * worst[1]) / k
print("k:", round(k, 4))
print("ES 92.5 by hand (percent):", round(100 * es925_hand, 4), "library:", round(100 * historical_es(small, 0.925), 4))
assert abs(es925_hand - historical_es(small, 0.925)) < 1e-12"""),
    C("""
# rockafellar and uryasev
losses_small = -small
alpha_small = 0.90
grid = np.linspace(losses_small.min(), losses_small.max(), 20001)
objective = np.array([c + np.mean(np.maximum(losses_small - c, 0)) / (1 - alpha_small) for c in grid])
best = grid[np.argmin(objective)]
print("minimiser c (percent):", round(100 * best, 4), "VaR 90 lower and higher (percent):",
      round(100 * np.quantile(losses_small, 0.9, method="lower"), 4), round(100 * np.quantile(losses_small, 0.9, method="higher"), 4))
print("minimum value (percent):", round(100 * objective.min(), 4), "ES 90 (percent):", round(100 * historical_es(small, 0.90), 4))
assert abs(objective.min() - historical_es(small, alpha_small)) < 1e-6"""),
    M("""
With 20 observations the VaR is not a single point: any value between the two bracketing order statistics minimises the objective.
The minimum value, which is the ES, is still unique. The grid search returns one point inside that flat stretch, so the
printed minimiser lies between the lower and higher VaR shown.
"""),
]

S[8] = [
    C(PORTFOLIO_CODE),
    C("""
sample = portfolio.to_numpy()
ALPHA_ES, ALPHA_VAR = 0.975, 0.99
print("tail observations at 97.5 percent:", round(len(sample) * (1 - ALPHA_ES)))
print("tail observations at 99 percent:", round(len(sample) * (1 - ALPHA_VAR)))
print("historical VaR 97.5 (pct):", round(100 * historical_var(sample, 0.975), 4))
print("historical VaR 99 (pct):", round(100 * historical_var(sample, 0.99), 4))
print("historical ES 97.5 (pct):", round(100 * historical_es(sample, 0.975), 4))
print("historical ES 99 (pct):", round(100 * historical_es(sample, 0.99), 4))
print("worst five losses (pct):", (100 * np.sort(-sample)[::-1][:5]).round(3))"""),
]

S[9] = [
    M("""
1. ES uses level 97.5 percent, VaR at 99 percent is shown for comparison. Both are one day.
2. Rolling forecasts use only earlier days. Windows of 500 days.
3. Evaluation days 1000 to 2999.
4. For the t versions, nu is estimated on the first 1000 days and floored at 3.0, as in the parametric module. If the raw estimate sits below the floor, the t results depend on that choice.
"""),
    C("""
start, end = 1000, len(sample)
nu_raw, _, _ = t.fit(sample[:start])
nu_hat = float(max(nu_raw, 3.0))
print("raw nu:", round(float(nu_raw), 3), "used:", nu_hat)"""),
]

S[10] = [
    M("""
Loop versions of the empirical ES and of the Rockafellar and Uryasev minimisation, written without the library.
"""),
    C("""
def my_es(values, alpha):
    losses = sorted((-v for v in values), reverse=True)
    k = (1 - alpha) * len(losses)
    m = int(k)
    total = sum(losses[:m])
    if m < len(losses):
        total += (k - m) * losses[m]
    return total / k


def my_ru(values, alpha, n_grid=4001):
    losses = -np.asarray(values)
    low, high = np.quantile(losses, 0.9), losses.max()
    best_value = np.inf
    best_c = None
    for c in np.linspace(low, high, n_grid):
        value = c + np.mean(np.maximum(losses - c, 0)) / (1 - alpha)
        if value < best_value:
            best_value, best_c = value, c
    return best_c, best_value


es_loop = my_es(sample, ALPHA_ES)
es_lib = historical_es(sample, ALPHA_ES)
c_star, ru_value = my_ru(sample, ALPHA_ES)
print("ES 97.5 loop (pct):", round(100 * es_loop, 6), "library:", round(100 * es_lib, 6))
print("RU minimum (pct):", round(100 * ru_value, 6), "RU minimiser (pct):", round(100 * c_star, 4), "VaR 97.5 (pct):", round(100 * historical_var(sample, ALPHA_ES), 4))
assert abs(es_loop - es_lib) < 1e-12
assert abs(ru_value - es_lib) < 1e-5
print("tail mean above VaR (simpler form, pct):", round(100 * tail_mean_above_var(sample, ALPHA_ES), 6))"""),
]

S[11] = [
    M("""
**Independent check of the closed forms.** Integrate the VaR curve numerically,
$\\frac{1}{1-\\alpha}\\int_\\alpha^1 \\mathrm{VaR}_u\\,du$, and compare with the formula. The integral uses the quantile
functions only, so it does not share algebra with the closed form.
"""),
    C("""
def integrated_es(var_function, alpha):
    value, _ = quad(var_function, alpha, 1.0 - 1e-12, limit=200)
    return value / (1 - alpha)


rows = []
for alpha in [0.90, 0.95, 0.975, 0.99]:
    n_closed = normal_es(0.0, 1.0, alpha)
    n_int = integrated_es(lambda u: normal_var(0.0, 1.0, u), alpha)
    t_closed = student_t_es(0.0, 1.0, 5.0, alpha)
    t_int = integrated_es(lambda u: student_t_var(0.0, 1.0, 5.0, u), alpha)
    rows.append({"alpha": alpha, "normal_closed": n_closed, "normal_integral": n_int, "t5_closed": t_closed, "t5_integral": t_int})
check = pd.DataFrame(rows)
check["max_gap"] = np.maximum((check["normal_closed"] - check["normal_integral"]).abs(), (check["t5_closed"] - check["t5_integral"]).abs())
print(check.round(6).to_string(index=False))
assert check["max_gap"].max() < 1e-6"""),
    C("""
# large sample from known t
rng = np.random.default_rng(SEED)
nu_test = 5.0
draws = rng.standard_t(nu_test, size=4_000_000) * np.sqrt((nu_test - 2) / nu_test)
mc_es = historical_es(-draws, ALPHA_ES)
closed_es = student_t_es(0.0, 1.0, nu_test, ALPHA_ES)
rel = abs(mc_es - closed_es) / closed_es
print("t(5) ES 97.5, simulated:", round(mc_es, 5), "closed form:", round(closed_es, 5), "relative gap:", round(rel, 5))
assert rel < 0.01"""),
]

S[12] = [
    M("""
**Rolling forecasts** at 97.5 percent for four models: historical 500, rolling normal 500, EWMA normal and EWMA t.
For each model the notebook computes the one day VaR 97.5 and ES 97.5, counts VaR exceptions, and computes the Z1 statistic.

**Simulated p value for Z1.** For the two EWMA models the predictive distribution is known: loss on day $t$ is
$\\sigma_t \\varepsilon_t$ with $\\varepsilon$ standardised normal or t. Draw 2000 sets of 2000 shocks, compute Z1 for each set with the
same VaR and ES series, and report the share of simulations with Z1 at least as large as the observed one.
A small share means the observed ES was too low (losses beyond VaR larger than predicted).
"""),
    C("""
def rolling_param_es(returns, window, alpha, nu=None):
    out_var = np.full(len(returns), np.nan)
    out_es = np.full(len(returns), np.nan)
    for day in range(window, len(returns)):
        part = returns[day - window : day]
        if nu is None:
            out_var[day] = normal_var(part.mean(), part.std(ddof=1), alpha)
            out_es[day] = normal_es(part.mean(), part.std(ddof=1), alpha)
        else:
            out_var[day] = student_t_var(part.mean(), part.std(ddof=1), nu, alpha)
            out_es[day] = student_t_es(part.mean(), part.std(ddof=1), nu, alpha)
    return out_var, out_es


models = {
    "historical 500": (rolling_historical_var(sample, 500, ALPHA_ES), rolling_historical_es(sample, 500, ALPHA_ES)),
    "normal rolling 500": rolling_param_es(sample, 500, ALPHA_ES, None),
    "ewma normal": (ewma_var(sample, 0.94, ALPHA_ES, None), ewma_es(sample, 0.94, ALPHA_ES, None)),
    "ewma student t": (ewma_var(sample, 0.94, ALPHA_ES, nu_hat), ewma_es(sample, 0.94, ALPHA_ES, nu_hat)),
}
sigma_ewma = ewma_volatility(sample, 0.94)
rows = []
for name, (var_series, es_series) in models.items():
    hits = exceptions(sample[start:end], var_series[start:end])
    z1 = exceedance_z1(sample[start:end], var_series[start:end], es_series[start:end])
    rows.append(
        {
            "model": name,
            "var_exceptions": int(hits.sum()),
            "expected": (end - start) * (1 - ALPHA_ES),
            "kupiec_p": kupiec_pof(hits, 1 - ALPHA_ES)["p_value"],
            "z1": z1,
            "mean_es_pct": 100 * np.nanmean(es_series[start:end]),
            "mean_es_over_var": np.nanmean(es_series[start:end] / var_series[start:end]),
        }
    )
evaluation = pd.DataFrame(rows).set_index("model")
print(evaluation.round(4))"""),
    C("""
def simulated_z1_p_value(var_series, es_series, sigma_series, kind, observed_z1, n_sim=2000, seed=SEED):
    rng_sim = np.random.default_rng(seed)
    v = var_series[start:end]
    e = es_series[start:end]
    s = sigma_series[start:end]
    values = []
    for _ in range(n_sim):
        if kind == "normal":
            shock = rng_sim.standard_normal(len(v))
        else:
            shock = rng_sim.standard_t(nu_hat, size=len(v)) * np.sqrt((nu_hat - 2) / nu_hat)
        loss = s * shock
        hit = loss > v
        if hit.sum() > 0:
            values.append(np.mean(loss[hit] / e[hit]) - 1)
    values = np.array(values)
    return float(np.mean(values >= observed_z1)), len(values)


p_values = {}
for name, kind in [("ewma normal", "normal"), ("ewma student t", "t")]:
    var_series, es_series = models[name]
    p_value, used = simulated_z1_p_value(var_series, es_series, sigma_ewma, kind, evaluation.loc[name, "z1"])
    p_values[name] = p_value
    print(name, "Z1:", round(float(evaluation.loc[name, "z1"]), 4), "simulated upper p value:", round(p_value, 4), "from", used, "simulations")"""),
]

S[13] = [
    C("""
levels = np.linspace(0.90, 0.999, 100)
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
axes[0].plot(levels, [normal_var(0, 1, a) for a in levels], color=COLORS["main"], label="normal VaR")
axes[0].plot(levels, [normal_es(0, 1, a) for a in levels], color=COLORS["main"], linestyle="--", label="normal ES")
axes[0].plot(levels, [student_t_var(0, 1, 5, a) for a in levels], color=COLORS["second"], label="t(5) VaR")
axes[0].plot(levels, [student_t_es(0, 1, 5, a) for a in levels], color=COLORS["second"], linestyle="--", label="t(5) ES")
axes[0].set_xlabel("confidence level")
axes[0].set_ylabel("multiple of standard deviation")
axes[0].set_title("VaR and ES, unit standard deviation")
axes[0].legend()

axes[1].plot(levels, [normal_es(0, 1, a) / normal_var(0, 1, a) for a in levels], color=COLORS["main"], label="normal")
axes[1].plot(levels, [student_t_es(0, 1, 5, a) / student_t_var(0, 1, 5, a) for a in levels], color=COLORS["second"], label="t(5)")
axes[1].set_xlabel("confidence level")
axes[1].set_ylabel("ES over VaR")
axes[1].set_title("Ratio of ES to VaR")
axes[1].legend()

axes[2].hist(100 * -sample, bins=90, color=COLORS["grey"], alpha=0.7)
axes[2].axvline(100 * historical_var(sample, ALPHA_ES), color=COLORS["third"], linestyle="--", label="VaR 97.5")
axes[2].axvline(100 * historical_es(sample, ALPHA_ES), color=COLORS["second"], linestyle="--", label="ES 97.5")
axes[2].set_xlim(0, 100 * np.max(-sample) * 1.02)
axes[2].set_xlabel("loss (percent)")
axes[2].set_title("Portfolio losses with VaR and ES")
axes[2].legend()
save_figure(fig, MODULE, "var_es_comparison.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots()
dates = portfolio.index
ax.plot(dates[start:end], 100 * models["historical 500"][0][start:end], color=COLORS["main"], label="VaR 97.5")
ax.plot(dates[start:end], 100 * models["historical 500"][1][start:end], color=COLORS["second"], label="ES 97.5")
ax.set_ylabel("percent of value")
ax.set_title("Rolling historical VaR and ES, window 500")
ax.legend()
save_figure(fig, MODULE, "rolling_var_es.png")
plt.show()"""),
]

S[14] = [
    M("""
How to read the output. **Observed** means taken directly from printed numbers.

* **Observed.** In the check table the closed forms and the numerical integral agree to the tolerance. That supports the closed forms but does not support using them on real returns.
* **Observed.** The simulated t sample matches the closed form within 1 percent. Estimation error of ES in a finite sample is a separate matter, measured in Experiment B.
* **Observed.** The Z1 value and the simulated p value say whether the ES forecast was too low on the exceedance days. A small p value means ES was too low. A large p value means the test found no evidence of that, which is not proof the model is right.
* **Inference.** The ratio of ES to VaR grows with the tail weight of the distribution. The figure shows this ratio for a normal and a t with 5 degrees of freedom.
* **Observed, EWMA t model.** It can show more VaR exceptions than expected at 97.5 percent and still a negative Z1. With a low nu the t VaR multiplier at 97.5 percent can be below the normal one while the ES multiplier is above it. The next cell prints both multipliers.
"""),
    C("""
print("normal ES 97.5 over normal VaR 99:", round(normal_es(0, 1, 0.975) / normal_var(0, 1, 0.99), 4))
print("t(5) ES 97.5 over t(5) VaR 99:", round(student_t_es(0, 1, 5, 0.975) / student_t_var(0, 1, 5, 0.99), 4))
print("historical ES 97.5 over historical VaR 99, full sample:", round(historical_es(sample, 0.975) / historical_var(sample, 0.99), 4))
mult_n = normal_var(0, 1, 0.975)
mult_t = student_t_var(0, 1, nu_hat, 0.975)
print("VaR 97.5 multiplier of sigma, normal:", round(mult_n, 4), "t with nu used:", round(mult_t, 4), "t below normal:", mult_t < mult_n)
print("ES 97.5 multiplier of sigma, normal:", round(normal_es(0, 1, 0.975), 4), "t with nu used:", round(student_t_es(0, 1, nu_hat, 0.975), 4))
print("ratio ES over VaR at 97.5, normal and t(5):", round(normal_es(0, 1, 0.975) / normal_var(0, 1, 0.975), 4), round(student_t_es(0, 1, 5, 0.975) / student_t_var(0, 1, 5, 0.975), 4))"""),
]

S[15] = [
    M("""
**Experiment A: normal ES 97.5 against normal VaR 99.** Printed in section 14. The two are close for a normal distribution and
differ for a heavier tail. The difference is the point of the experiment: switching measure changes the capital of a desk
differently depending on the tail.

**Experiment B: sampling error.** Bootstrap the full sample 2000 times and compare the relative width of the 95 percent interval
for historical VaR 97.5 and historical ES 97.5. The iid bootstrap ignores volatility clustering, so both intervals are optimistic.

**Experiment C: subadditivity.** Two independent loans. Each loses 100 with probability 0.04 and 0 otherwise.
Compute VaR and ES at 95 percent exactly from the discrete distribution.
"""),
    C("""
rng_b = np.random.default_rng(SEED + 1)
n_boot = 2000
var_boot = np.empty(n_boot)
es_boot = np.empty(n_boot)
for b in range(n_boot):
    resample = rng_b.choice(sample, size=len(sample), replace=True)
    var_boot[b] = historical_var(resample, ALPHA_ES)
    es_boot[b] = historical_es(resample, ALPHA_ES)
rows = []
for name, values, point in [("VaR 97.5", var_boot, historical_var(sample, ALPHA_ES)), ("ES 97.5", es_boot, historical_es(sample, ALPHA_ES))]:
    low, high = np.quantile(values, [0.025, 0.975])
    rows.append({"measure": name, "point_pct": 100 * point, "low_pct": 100 * low, "high_pct": 100 * high, "relative_width_pct": 100 * (high - low) / point})
boot_table = pd.DataFrame(rows)
print(boot_table.round(3).to_string(index=False))"""),
    C("""
def discrete_var(values, probs, alpha):
    order = np.argsort(values)
    values, probs = np.asarray(values)[order], np.asarray(probs)[order]
    cumulative = np.cumsum(probs)
    return float(values[np.argmax(cumulative >= alpha - 1e-12)])


def discrete_es(values, probs, alpha):
    order = np.argsort(values)
    values, probs = np.asarray(values)[order], np.asarray(probs)[order]
    cumulative = np.cumsum(probs)
    tail_mass = np.clip(np.minimum(probs, cumulative - alpha), 0, None)
    return float(np.sum(values * tail_mass) / (1 - alpha))


one_values, one_probs = [0.0, 100.0], [0.96, 0.04]
two_values, two_probs = [0.0, 100.0, 200.0], [0.96**2, 2 * 0.96 * 0.04, 0.04**2]
a = 0.95
rows = [
    {"position": "loan A alone", "var_95": discrete_var(one_values, one_probs, a), "es_95": discrete_es(one_values, one_probs, a)},
    {"position": "loan B alone", "var_95": discrete_var(one_values, one_probs, a), "es_95": discrete_es(one_values, one_probs, a)},
    {"position": "A plus B", "var_95": discrete_var(two_values, two_probs, a), "es_95": discrete_es(two_values, two_probs, a)},
]
sub = pd.DataFrame(rows)
print(sub.round(3).to_string(index=False))
var_sum = 2 * sub.loc[0, "var_95"]
es_sum = 2 * sub.loc[0, "es_95"]
var_violates = sub.loc[2, "var_95"] > var_sum
es_ok = sub.loc[2, "es_95"] <= es_sum + 1e-12
print("sum of stand alone VaR:", var_sum, "VaR of the sum:", sub.loc[2, "var_95"], "VaR violates subadditivity:", bool(var_violates))
print("sum of stand alone ES:", es_sum, "ES of the sum:", round(sub.loc[2, "es_95"], 3), "ES subadditive:", bool(es_ok))
assert var_violates and es_ok"""),
]

S[16] = [
    C("""
print(evaluation.round(4))
print()
print(boot_table.round(3).to_string(index=False))
metrics = {
    "closed_form_vs_integral_max_gap": float(check["max_gap"].max()),
    "t5_simulated_vs_closed_relative_gap": float(rel),
    "normal_es975_over_var99": float(normal_es(0, 1, 0.975) / normal_var(0, 1, 0.99)),
    "t5_es975_over_var99": float(student_t_es(0, 1, 5, 0.975) / student_t_var(0, 1, 5, 0.99)),
    "historical_full_sample_pct": {"var_97_5": 100 * historical_var(sample, 0.975), "es_97_5": 100 * historical_es(sample, 0.975),
                                    "var_99": 100 * historical_var(sample, 0.99), "es_99": 100 * historical_es(sample, 0.99)},
    "evaluation_by_model": evaluation.reset_index().to_dict(orient="records"),
    "z1_simulated_upper_p_value": p_values,
    "bootstrap_interval": boot_table.to_dict(orient="records"),
    "subadditivity_example": sub.to_dict(orient="records"),
    "nu_raw_first_1000_days": float(nu_raw),
    "nu_used": nu_hat,
    "acceptance_criteria": {
        "hand_equals_library": True,
        "ru_minimum_equals_es": True,
        "closed_form_equals_integral": bool(check["max_gap"].max() < 1e-6),
        "simulated_t_within_1pct": bool(rel < 0.01),
        "var_violates_and_es_satisfies_subadditivity": bool(var_violates and es_ok),
    },
}
config = {"alpha_es": ALPHA_ES, "alpha_var": ALPHA_VAR, "window": 500, "ewma_decay": 0.94, "nu_used": nu_hat,
          "evaluation_days": [start, end], "n_boot": n_boot, "z1_simulations": 2000, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Empirical and closed form ES, numerical integration check, rolling ES, Z1 backtest with simulated p value, exact subadditivity example",
    data_kind="synthetic",
    dataset="datasets/synthetic/market_returns.csv",
    n_obs=int(len(sample)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "portfolio of fixed weights 50, 30, 20 percent",
        "Z1 simulation conditions on the observed EWMA volatility path",
        "t degrees of freedom floored at 3.0",
    ],
    metrics=metrics,
    baseline={"measure": "VaR 97.5 historical 500", "exceptions": int(evaluation.loc["historical 500", "var_exceptions"])},
    limitations=[
        "synthetic returns, t model matched to the generator by construction",
        "ES backtest has low power with about 50 exceedances",
        "iid bootstrap",
    ],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
**Limitations**

1. **Estimation needs tail data.** At 97.5 percent the full sample has 75 tail days, a 500 day window has about 12. ES from 12 observations is noisy. Experiment B quantifies this for the full sample only.
2. **Backtesting.** ES alone is not elicitable, a point discussed by Nolde and Ziegel. The Z1 diagnostic is therefore read together with the VaR exceedances. A published result on joint elicitability of VaR and ES exists but is not in this module's reference list, so check it before citing. With about 50 exceedances the Z1 test has limited power.
3. **Z1 simulation conditions on the forecast path.** It uses the observed EWMA volatility for each day, as the original test design does, but it ignores parameter uncertainty.
4. **Matched model.** The data come from a Student t GARCH. The t EWMA model is close to the truth by construction, so its good showing says little about real data.
5. **Floor on nu.** If the raw estimate is below 3.0 the floor is binding and the t results depend on it.
6. **Subadditivity example is discrete and small.** It shows VaR can fail the property. It does not show how often this happens in a real book.
7. **Regulatory detail.** The Basel standard sets ES at 97.5 percent with liquidity horizons and other rules not modelled here.

**Model risk.** Moving from VaR to ES shifts risk from the tail location to tail shape. A model that is right about the quantile and wrong about the tail looks fine on VaR exceptions and is wrong on ES.
"""),
]

S[18] = [
    M("""
A desk head asks how the capital relevant number changes if the internal measure moves from 99 percent VaR to 97.5 percent ES.
The table shows both in currency on the 100 million portfolio, for three models. A ratio above 1 means the ES number is larger.
The Basel standard also applies scaling and horizon rules that this notebook does not model: **check before use**.
"""),
    C("""
VALUE = 100_000_000
mu_s, sigma_s = float(sample.mean()), float(sample.std(ddof=1))
rows = [
    {"model": "normal", "var99": normal_var(mu_s, sigma_s, 0.99), "es975": normal_es(mu_s, sigma_s, 0.975)},
    {"model": "student t (nu used)", "var99": student_t_var(mu_s, sigma_s, nu_hat, 0.99), "es975": student_t_es(mu_s, sigma_s, nu_hat, 0.975)},
    {"model": "historical", "var99": historical_var(sample, 0.99), "es975": historical_es(sample, 0.975)},
]
report = pd.DataFrame(rows)
report["var99_ccy"] = VALUE * report["var99"]
report["es975_ccy"] = VALUE * report["es975"]
report["es_over_var"] = report["es975"] / report["var99"]
print(report[["model", "var99_ccy", "es975_ccy", "es_over_var"]].round(3).to_string(index=False))"""),
]

S[19] = [
    M("""
1. Compute ES at 99 percent for the portfolio and compare with ES at 97.5 percent. How many tail observations does each use?
2. Show by simulation that for a normal distribution ES 97.5 is within 1 percent of VaR 99. Find the confidence level at which ES of a t(5) equals the normal VaR 99.
3. Modify the two loan example: make the default probability 0.06 each. Does VaR 95 still violate subadditivity? Explain.
4. Estimate the power of the Z1 test: simulate data from a t(4) distribution, forecast with a normal model, and count how often the test rejects at 5 percent.
5. Use a 250 day window for rolling ES and compare the exceedance count and the Z1 statistic with the 500 day window.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "03_market_risk/expected_shortfall",
        "title": "Expected Shortfall",
        "family": "Market Risk",
        "level": "Intermediate",
        "dataset": "market_returns",
        "data_kind": "synthetic",
        "status": "Complete",
        "tagline": "Compute, verify and backtest ES, and see exactly where VaR fails subadditivity.",
        "refs": ["acerbi2002", "rockafellar2000", "artzner1999", "nolde2017", "acerbi2014", "bcbs_d457"],
        "research_note": (
            "Artzner et al. define coherence and give the subadditivity requirement. Rockafellar and Uryasev give the minimisation form used in "
            "section 7. Acerbi and Tasche give the empirical ES with the fractional tail weight. Acerbi and Szekely define the backtest family that "
            "contains the Z1 statistic, and Nolde and Ziegel discuss elicitability and regulatory backtesting. The Basel market risk standard is cited only for "
            "the move to ES at 97.5 percent. The notebook re derives each formula by hand or by numerical integration rather than relying on the papers."
        ),
        "learn": [
            "ES as an average of VaR values, with fractional tail weight",
            "Rockafellar and Uryasev minimisation",
            "Closed forms checked by numerical integration",
            "Rolling ES and the Z1 backtest with a simulated p value",
            "Exact VaR subadditivity counterexample",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
