"""Spec: parametric and Monte Carlo Value at Risk."""

from nbgen import C, M

from specs._common import PORTFOLIO_CODE, check_sections, setup_code

MODULE = "parametric_var"

SETUP = setup_code(MODULE) + """
from scipy.stats import jarque_bera, norm, t

from risk_lab.market.backtest import exceptions, kupiec_pof
from risk_lab.market.var import (
    delta_normal_var, ewma_var, historical_var, normal_var, portfolio_moments,
    rolling_historical_var, rolling_normal_var, simulate_normal_returns,
    simulate_student_t_returns, student_t_var,
)"""

S = {}

S[1] = [
    M("""
Historical simulation (previous module) reads the tail from past days. A parametric method assumes a distribution,
estimates its few parameters, and **calculates** the quantile. That gives a VaR that updates smoothly, can be decomposed
by asset, and needs few data. The price is a model risk: if the assumed shape is wrong in the tail, the VaR is wrong
exactly where it matters.

This notebook builds three parametric versions on the same three asset portfolio: the variance covariance (delta normal)
method, a Student t version, and EWMA volatility. It adds Monte Carlo, checks it against the closed form, and decomposes
risk by asset.

**Decision this supports:** whether a normal assumption is acceptable for a 99 percent VaR on this portfolio, and what
replaces it if not.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Derive the portfolio standard deviation and the delta normal VaR, and compute a two asset example by hand.
2. Explain why a Student t quantile at the same standard deviation is larger than a normal one at 99 percent.
3. Test whether returns look normal and estimate the tail parameter.
4. Build EWMA volatility and use it for a one day ahead VaR.
5. Simulate scenarios by Monte Carlo and show the error shrinks with the number of scenarios.
6. Decompose portfolio VaR by asset (Euler allocation) and measure diversification.
7. Backtest the parametric VaRs against the historical VaR on the same days.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Delta normal VaR | VaR for a portfolio linear in the risk factors, assuming normal returns |
| Covariance matrix | Variances and covariances of the asset returns |
| Student t | A bell shaped distribution with heavier tails than the normal. Parameter nu (degrees of freedom): small nu means heavy tails |
| EWMA | Exponentially weighted moving average of squared returns. Decay lambda near 1 means slow forgetting |
| Component VaR | Share of portfolio VaR attributed to each asset so that the parts add to the total |
| Diversification benefit | Sum of stand alone VaRs minus the portfolio VaR |
| Monte Carlo VaR | Quantile of simulated portfolio losses |
"""),
]

S[4] = [
    M("""
**Why compare these methods?**

| Method | Strength | Weakness |
|---|---|---|
| Delta normal | Closed form. Fast. Decomposable | Normal tails are too thin for most financial returns. Linear positions only |
| Student t | Heavier tail with one more parameter | Parameter must be estimated. Symmetric |
| EWMA volatility | Reacts to volatility clustering | Decay parameter is a choice. Still assumes a shape for the standardised shock |
| Monte Carlo | Handles nonlinear positions | Sampling error. Needs a model |

Acceptance criteria:

1. Closed form delta normal VaR equals the Monte Carlo VaR within three standard errors at 1,000,000 scenarios.
2. Component VaRs add to the portfolio VaR (sum of parts identity) to 1e-12.
3. Student t Monte Carlo VaR is within 2 percent (relative) of the closed form t VaR.
4. Exception counts and Kupiec p values reported for each parametric model on the same days.
"""),
]

S[6] = [
    M(r"""
**Portfolio variance.** With weights $w$, mean vector $\mu$ and covariance matrix $\Sigma$:

$$\mu_p = w^\top \mu, \qquad \sigma_p^2 = w^\top \Sigma\, w$$

**Delta normal VaR** at level $\alpha$ as a loss fraction:

$$\mathrm{VaR}_\alpha = -\mu_p + z_\alpha\, \sigma_p, \qquad z_\alpha = \Phi^{-1}(\alpha)$$

**Student t.** If returns follow a Student t with $\nu$ degrees of freedom and standard deviation $\sigma$, the scale is
$s = \sigma\sqrt{(\nu - 2)/\nu}$ and

$$\mathrm{VaR}_\alpha = -\mu_p + s \, t_{\nu,\alpha}$$

**EWMA.** With decay $\lambda$:

$$\sigma_t^2 = \lambda\, \sigma_{t-1}^2 + (1 - \lambda)\, r_{t-1}^2$$

The forecast for day $t$ uses returns up to $t-1$.

**Euler decomposition.** For the zero mean part $z_\alpha \sigma_p$, the contribution of asset $i$ is

$$c_i = z_\alpha\, \frac{w_i\, (\Sigma w)_i}{\sigma_p}, \qquad \sum_i c_i = z_\alpha \frac{w^\top \Sigma w}{\sigma_p} = z_\alpha \sigma_p$$

**Monte Carlo.** Draw $L z$ with $z$ standard normal and $\Sigma = L L^\top$ (Cholesky). The standard error of a sample
quantile falls like $1/\sqrt{N}$.
"""),
]

S[7] = [
    M("""
Two assets: weights 0.6 and 0.4, daily volatilities 2 percent and 1 percent, correlation 0.3, zero mean.
"""),
    C("""
w2 = np.array([0.6, 0.4])
vol2 = np.array([0.02, 0.01])
rho = 0.3
cov2 = np.array([[vol2[0] ** 2, rho * vol2[0] * vol2[1]], [rho * vol2[0] * vol2[1], vol2[1] ** 2]])
variance_hand = (w2[0] * vol2[0]) ** 2 + (w2[1] * vol2[1]) ** 2 + 2 * w2[0] * w2[1] * rho * vol2[0] * vol2[1]
sigma_hand = np.sqrt(variance_hand)
z99 = norm.ppf(0.99)
var_hand = z99 * sigma_hand
standalone = z99 * (w2 * vol2)
print("portfolio sigma by hand (percent):", round(100 * sigma_hand, 4))
print("z 99:", round(z99, 4))
print("portfolio VaR 99 by hand (percent):", round(100 * var_hand, 4))
print("sum of stand alone VaRs (percent):", round(100 * standalone.sum(), 4))
print("diversification benefit (percent):", round(100 * (standalone.sum() - var_hand), 4))
_, sigma_lib = portfolio_moments(w2, [0, 0], cov2)
assert abs(sigma_lib - sigma_hand) < 1e-12
assert abs(delta_normal_var(w2, [0, 0], cov2, 0.99) - var_hand) < 1e-12"""),
    C("""
# student t at same sigma
for nu in [4, 6, 10, 30]:
    print("nu", nu, "t VaR 99 over normal VaR 99:", round(student_t_var(0, sigma_hand, nu, 0.99) / var_hand, 4))"""),
    M("""
With the same standard deviation, the 99 percent VaR from a t with few degrees of freedom is larger than the normal one.
At 95 percent the order can reverse, because heavy tailed distributions put more mass far out and less near the centre.
The next cell checks that claim rather than assuming it.
"""),
    C("""
for level in [0.90, 0.95, 0.975, 0.99, 0.999]:
    n_value = normal_var(0, 1, level)
    t_value = student_t_var(0, 1, 5, level)
    print("level", level, "normal", round(n_value, 4), "t(5)", round(t_value, 4), "t above normal:", t_value > n_value)"""),
]

S[8] = [
    C(PORTFOLIO_CODE),
    C("""
sample = portfolio.to_numpy()
asset_returns = returns[assets].to_numpy()
mean_vec = asset_returns.mean(axis=0)
cov_full = np.cov(asset_returns.T)
corr_full = np.corrcoef(asset_returns.T)
print("daily volatility by asset (percent):", dict(zip(assets, (100 * np.sqrt(np.diag(cov_full))).round(3).tolist())))
print("correlation matrix:")
print(pd.DataFrame(corr_full, index=assets, columns=assets).round(3))

jb = jarque_bera(sample)
print("Jarque Bera statistic:", round(float(jb.statistic), 1), "p value:", float(jb.pvalue))
nu_full, loc_full, scale_full = t.fit(sample)
print("t fit on the full sample, nu:", round(float(nu_full), 2), "(in sample, for display only)")

squared = sample**2 - (sample**2).mean()
acf = [float(np.sum(squared[lag:] * squared[:-lag]) / np.sum(squared**2)) for lag in range(1, 6)]
print("autocorrelation of squared returns, lags 1 to 5:", np.round(acf, 3))"""),
]

S[9] = [
    M("""
1. Parameters for rolling forecasts use only data before the forecast day.
2. Evaluation days 1000 to 2999, same as the historical module, so exception counts are comparable.
3. The t parameter nu is estimated on the **first 1000 days only** and then held fixed, so there is no look ahead.
4. Zero mean is used for EWMA, which is common for daily data. The rolling normal VaR uses the sample mean of its window.
"""),
    C("""
ALPHA = 0.99
VALUE = 100_000_000
start, end = 1000, len(sample)
nu_raw, _, _ = t.fit(sample[:start])
nu_hat = float(max(nu_raw, 3.0))
print("raw t fit on the first", start, "days, nu:", round(float(nu_raw), 3))
print("nu used (floor at 3.0):", round(nu_hat, 2))"""),
    M("""
**Read this before trusting the t results.** If the raw estimate is at or below the floor of 3.0, the floor is binding.
The fitted nu then describes the unconditional distribution of returns, which mixes two effects: fat tailed shocks and
volatility clustering. It is not the shock nu of the generator (6 to 8 per asset). A fixed t model therefore stands in for both effects.
The floor keeps the variance formula finite and the VaR stable. It is a judgement call and the t results depend on it.
"""),
]

S[10] = [
    M("""
Closed form and Monte Carlo written without the library helpers. The simulation uses a Cholesky factor and a
standard normal generator. It is repeated 20 times at each size to measure the spread of the estimate.
"""),
    C("""
def my_delta_normal(weights, mean, cov, alpha):
    mu_p = float(weights @ mean)
    sigma_p = float(np.sqrt(weights @ cov @ weights))
    return -mu_p + norm.ppf(alpha) * sigma_p


def my_monte_carlo(weights, mean, cov, alpha, n_scenarios, rng):
    chol = np.linalg.cholesky(cov)
    z = rng.standard_normal((n_scenarios, len(weights)))
    scenario_returns = mean + z @ chol.T
    loss = -(scenario_returns @ weights)
    return float(np.quantile(loss, alpha))


closed = my_delta_normal(weights, mean_vec, cov_full, ALPHA)
lib_closed = delta_normal_var(weights, mean_vec, cov_full, ALPHA)
assert abs(closed - lib_closed) < 1e-12
print("delta normal VaR 99 (percent):", round(100 * closed, 4))

rng = np.random.default_rng(SEED)
rows = []
for n_scen in [1_000, 10_000, 100_000, 1_000_000]:
    reps = 20 if n_scen < 1_000_000 else 8
    estimates = np.array([my_monte_carlo(weights, mean_vec, cov_full, ALPHA, n_scen, rng) for _ in range(reps)])
    rows.append(
        {"n_scenarios": n_scen, "mean_estimate_pct": 100 * estimates.mean(), "sd_of_estimate_pct": 100 * estimates.std(ddof=1),
         "mean_error_pct": 100 * (estimates.mean() - closed)}
    )
mc_table = pd.DataFrame(rows)
print(mc_table.round(5).to_string(index=False))"""),
    C("""
last = mc_table.iloc[-1]
se_last = last["sd_of_estimate_pct"] / np.sqrt(8)
print("error at 1,000,000 scenarios (percent):", round(float(last["mean_error_pct"]), 5))
print("standard error of the mean of 8 runs (percent):", round(float(se_last), 5))
mc_within = bool(abs(last["mean_error_pct"]) <= 3 * se_last)
print("within three standard errors:", mc_within)
sd_ratio = mc_table["sd_of_estimate_pct"].iloc[0] / mc_table["sd_of_estimate_pct"].iloc[2]
print("sd at 1,000 over sd at 100,000 (theory about 10):", round(float(sd_ratio), 2))"""),
]

S[11] = [
    M("""
Library functions: Monte Carlo from `simulate_normal_returns` and `simulate_student_t_returns`, the Student t closed form,
and the Euler decomposition. For a multivariate t with one shared mixing variable, the portfolio return is a univariate t with the
same degrees of freedom, so the closed form applies to the portfolio.
"""),
    C("""
sim_normal = simulate_normal_returns(mean_vec, cov_full, 1_000_000, seed=SEED)
mc_normal = float(np.quantile(-(sim_normal @ weights), ALPHA))
mu_p, sigma_p = portfolio_moments(weights, mean_vec, cov_full)

sim_t = simulate_student_t_returns(mean_vec, cov_full, nu_hat, 1_000_000, seed=SEED)
mc_t = float(np.quantile(-(sim_t @ weights), ALPHA))
closed_t = student_t_var(mu_p, sigma_p, nu_hat, ALPHA)
rel_gap_t = abs(mc_t - closed_t) / closed_t
print("normal closed form (pct):", round(100 * closed, 4), "Monte Carlo (pct):", round(100 * mc_normal, 4))
print("t closed form (pct):", round(100 * closed_t, 4), "Monte Carlo (pct):", round(100 * mc_t, 4))
print("relative gap, t:", round(rel_gap_t, 4))
assert rel_gap_t < 0.02"""),
    C("""
# euler components
sigma_vec = cov_full @ weights
components = norm.ppf(ALPHA) * weights * sigma_vec / sigma_p
print("sum of components minus z * sigma:", f"{components.sum() - norm.ppf(ALPHA) * sigma_p:.2e}")
assert abs(components.sum() - norm.ppf(ALPHA) * sigma_p) < 1e-12
standalone_vars = norm.ppf(ALPHA) * weights * np.sqrt(np.diag(cov_full))
print("sum of stand alone VaRs (pct):", round(100 * standalone_vars.sum(), 4), "portfolio (pct):", round(100 * norm.ppf(ALPHA) * sigma_p, 4))"""),
]

S[12] = [
    M("""
Four parametric forecasts and the historical forecast are evaluated on days 1000 to 2999 at 99 percent.
"""),
    C("""
var_models = {}
var_models["historical 500"] = rolling_historical_var(sample, 500, ALPHA)
var_models["normal rolling 500"] = rolling_normal_var(sample, 500, ALPHA)
var_models["ewma normal"] = ewma_var(sample, 0.94, ALPHA, nu=None)
var_models["ewma student t"] = ewma_var(sample, 0.94, ALPHA, nu=nu_hat)

rolling_t = np.full(len(sample), np.nan)
for day in range(500, len(sample)):
    window = sample[day - 500 : day]
    rolling_t[day] = student_t_var(window.mean(), window.std(ddof=1), nu_hat, ALPHA)
var_models["student t rolling 500"] = rolling_t

rows = []
hits_models = {}
for name, series in var_models.items():
    hits = exceptions(sample[start:end], series[start:end])
    hits_models[name] = hits
    test = kupiec_pof(hits, 1 - ALPHA)
    rows.append(
        {
            "model": name,
            "exceptions": int(hits.sum()),
            "expected": (end - start) * (1 - ALPHA),
            "rate_pct": 100 * hits.mean(),
            "kupiec_p": test["p_value"],
            "burst_exceptions_60d": int(exceptions(sample[2200:2260], series[2200:2260]).sum()),
            "mean_var_pct": 100 * np.nanmean(series[start:end]),
            "var_sd_pct": 100 * np.nanstd(series[start:end]),
        }
    )
evaluation = pd.DataFrame(rows).set_index("model")
print(evaluation.round(4))"""),
    C("""
criteria = {
    "monte_carlo_normal_within_3_se": mc_within,
    "components_sum_to_total": bool(abs(components.sum() - norm.ppf(ALPHA) * sigma_p) < 1e-12),
    "t_monte_carlo_within_2pct": bool(rel_gap_t < 0.02),
    "exceptions_and_kupiec_reported": True,
}
print(criteria)
assert all(criteria.values())"""),
]

S[13] = [
    C("""
fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
standard = np.sort((sample - sample.mean()) / sample.std(ddof=1))
probs = (np.arange(1, len(standard) + 1) - 0.5) / len(standard)
axes[0].plot(norm.ppf(probs), standard, ".", color=COLORS["main"], markersize=3, label="data")
axes[0].plot(norm.ppf(probs), norm.ppf(probs), color=COLORS["grey"], linestyle=":", label="normal")
t_line = t.ppf(probs, nu_full) * np.sqrt((nu_full - 2) / nu_full)
axes[0].plot(norm.ppf(probs), t_line, color=COLORS["second"], linestyle="--", label="t, fit on full sample")
axes[0].set_xlabel("normal quantile")
axes[0].set_ylabel("standardised return quantile")
axes[0].set_title("Quantile plot")
axes[0].legend()

for name, color in zip(["historical 500", "normal rolling 500", "ewma normal", "ewma student t"],
                       [COLORS["grey"], COLORS["main"], COLORS["second"], COLORS["third"]]):
    axes[1].plot(portfolio.index[start:end], 100 * var_models[name][start:end], color=color, linewidth=0.9, label=name)
axes[1].set_ylabel("VaR 99 (percent of value)")
axes[1].set_title("One day VaR by model")
axes[1].legend()
save_figure(fig, MODULE, "qq_and_var_models.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots()
ax.errorbar(mc_table["n_scenarios"], mc_table["mean_estimate_pct"], yerr=mc_table["sd_of_estimate_pct"], marker="o", color=COLORS["main"], label="Monte Carlo, plus or minus 1 sd")
ax.axhline(100 * closed, color=COLORS["second"], linestyle="--", label="closed form")
ax.set_xscale("log")
ax.set_xlabel("scenarios")
ax.set_ylabel("VaR 99 (percent)")
ax.set_title("Monte Carlo against closed form")
ax.legend()
save_figure(fig, MODULE, "monte_carlo_convergence.png")
plt.show()"""),
]

S[14] = [
    M("""
What the printed numbers say:

* **Observed.** The Jarque Bera p value and the excess kurtosis of the portfolio show whether the normal shape is rejected. The squared return autocorrelations show whether volatility clusters.
* **Observed.** The normal and t closed form VaRs at 99 percent are compared with the historical VaR on the full sample. The exception table shows which model's count is close to the expected 20.
* **Inference.** If the normal model has more exceptions than the expected count, heavier tails or volatility clustering are plausible causes. This notebook tests both with the t and EWMA variants but does not prove either one.
* **Decomposition.** Component VaRs show where the risk sits. An asset with a small weight can still contribute a large share if it is volatile or positively correlated with the rest.
"""),
    C("""
hist_full = historical_var(sample, ALPHA)
print("full sample VaR 99 (pct): historical", round(100 * hist_full, 4), "normal", round(100 * closed, 4), "t", round(100 * closed_t, 4))
print("normal below historical on the full sample:", closed < hist_full)
print("excess kurtosis of the portfolio:", round(float(pd.Series(sample).kurt()), 3))
print("rejects normality at 5 percent:", bool(jb.pvalue < 0.05))
print("autocorrelation of squared returns at lag 1:", round(acf[0], 3))
share = pd.Series(components / components.sum(), index=assets)
print("share of risk by asset:")
print(share.round(4))
print("weights:", dict(zip(assets, weights.tolist())))"""),
]

S[15] = [
    M("""
**Experiment A: EWMA decay.** Decay 0.90, 0.94, 0.97 and 0.99, normal and t, 99 percent.

**Experiment B: t degrees of freedom.** VaR 99 for nu from 3 to 30 at the portfolio standard deviation, against the normal.

**Experiment C: correlation.** Portfolio VaR when the correlation matrix is replaced by identity (zero correlation), by the estimated one,
and by all ones (perfect correlation). This brackets the diversification effect.
"""),
    C("""
rows = []
for decay in [0.90, 0.94, 0.97, 0.99]:
    for label, nu_value in [("normal", None), ("t", nu_hat)]:
        series = ewma_var(sample, decay, ALPHA, nu=nu_value)
        hits = exceptions(sample[start:end], series[start:end])
        rows.append({"decay": decay, "shape": label, "exceptions": int(hits.sum()), "kupiec_p": kupiec_pof(hits, 1 - ALPHA)["p_value"],
                     "burst_exceptions_60d": int(exceptions(sample[2200:2260], series[2200:2260]).sum())})
decay_table = pd.DataFrame(rows)
print(decay_table.round(4).to_string(index=False))"""),
    C("""
rows = []
for nu_value in [3, 4, 5, 6, 8, 12, 30]:
    rows.append({"nu": nu_value, "t_var_pct": 100 * student_t_var(mu_p, sigma_p, nu_value, ALPHA)})
nu_table = pd.DataFrame(rows)
nu_table["normal_var_pct"] = 100 * closed
nu_table["ratio"] = nu_table["t_var_pct"] / nu_table["normal_var_pct"]
print(nu_table.round(4).to_string(index=False))"""),
    C("""
vols = np.sqrt(np.diag(cov_full))
cases = {"zero correlation": np.eye(3), "estimated": corr_full, "perfect correlation": np.ones((3, 3))}
rows = []
for name, corr in cases.items():
    cov_case = np.outer(vols, vols) * corr
    rows.append({"case": name, "var_pct": 100 * delta_normal_var(weights, mean_vec, cov_case, ALPHA)})
corr_table = pd.DataFrame(rows)
print(corr_table.round(4).to_string(index=False))"""),
]

S[16] = [
    C("""
print(evaluation.round(4))
print()
print(criteria)
metrics = {
    "full_sample_var_99_pct": {"historical": 100 * hist_full, "normal": 100 * closed, "student_t": 100 * closed_t},
    "nu_estimated_first_1000_days": nu_hat,
    "nu_raw_first_1000_days": float(nu_raw),
    "jarque_bera_p_value": float(jb.pvalue),
    "excess_kurtosis": float(pd.Series(sample).kurt()),
    "acf_squared_returns_lag1": acf[0],
    "monte_carlo_convergence": mc_table.to_dict(orient="records"),
    "monte_carlo_normal_within_3_se": mc_within,
    "t_monte_carlo_relative_gap": float(rel_gap_t),
    "component_var_pct": dict(zip(assets, (100 * components).tolist())),
    "evaluation_by_model": evaluation.reset_index().to_dict(orient="records"),
    "ewma_decay_experiment": decay_table.to_dict(orient="records"),
    "nu_experiment": nu_table.to_dict(orient="records"),
    "correlation_experiment": corr_table.to_dict(orient="records"),
    "acceptance_criteria": criteria,
}
config = {"weights": dict(zip(assets, weights.tolist())), "alpha": ALPHA, "evaluation_days": [start, end],
          "ewma_decay": 0.94, "nu_hat": nu_hat, "n_scenarios": 1_000_000, "portfolio_value": VALUE, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Delta normal, Student t, EWMA and Monte Carlo VaR with Euler decomposition and Kupiec backtest",
    data_kind="synthetic",
    dataset="datasets/synthetic/market_returns.csv",
    n_obs=int(len(sample)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "linear portfolio, daily rebalanced fixed weights",
        "t degrees of freedom estimated on the first 1000 days and held fixed",
        "zero mean for EWMA",
        "multivariate t with a common mixing variable",
    ],
    metrics=metrics,
    baseline={"model": "historical 500", "exceptions": int(evaluation.loc["historical 500", "exceptions"])},
    limitations=[
        "synthetic returns from a GARCH with Student t shocks, so a t model is well matched by construction",
        "linear positions only",
        "single confidence level in the backtest",
    ],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
**Limitations**

1. **Matched by design.** The data come from a Student t GARCH generator. A t or EWMA model is therefore close to the truth. On real data the best model is not known in advance, and these results should not be expected to carry over.
2. **Linear positions only.** Options and other non linear instruments need full revaluation or a quadratic approximation.
3. **Constant correlation.** The generator keeps correlation fixed. In real stress, correlations often rise, which Experiment C brackets but does not model.
4. **Estimation error.** The covariance matrix and nu are estimated. Their error is not propagated into the VaR here.
5. **One confidence level.** The backtest uses 99 percent. A model can pass at 99 and fail at 97.5.
6. **Monte Carlo.** Error falls as 1 over the square root of the number of scenarios, so halving the error needs four times the scenarios.
7. **Tail ordering depends on the level.** At the same standard deviation a t quantile is above the normal one at 99 percent but below it at 90 and 95 percent (section 7). A comparison at one level does not carry to another.
8. **Binding floor on nu.** The t degrees of freedom are floored at 3.0 and may be at that floor. The t results depend on this choice (see section 9).

**Model risk.** The distribution choice is a model decision. The main control is an out of sample backtest, run on the same days for every candidate, as in section 12.
"""),
]

S[18] = [
    M("""
A risk report for the 100 million portfolio: the VaR in currency for each method, and the risk contribution of each asset.
Component VaRs are the numbers a desk head uses to decide what to reduce first.
"""),
    C("""
report = pd.DataFrame(
    {
        "asset": assets,
        "weight": weights,
        "value": weights * VALUE,
        "standalone_var_ccy": VALUE * standalone_vars,
        "component_var_ccy": VALUE * components,
        "share_of_risk": components / components.sum(),
    }
)
print(report.round(4).to_string(index=False))
print("portfolio delta normal VaR 99:", f"{VALUE * closed:,.0f}")
print("portfolio t VaR 99:", f"{VALUE * closed_t:,.0f}")
print("portfolio historical VaR 99:", f"{VALUE * hist_full:,.0f}")
print("diversification benefit (ccy):", f"{VALUE * (standalone_vars.sum() - norm.ppf(ALPHA) * sigma_p):,.0f}")"""),
]

S[19] = [
    M("""
1. Move 20 points of weight from equity to bond. Predict the sign of the change in portfolio VaR and in each component, then check.
2. Estimate nu on the whole sample instead of the first 1000 days. Explain why the exception count is no longer a fair test.
3. Add a one day horizon scaling to 10 days with the square root of time and compare with the overlapping 10 day historical VaR from the previous module.
4. Implement a filtered historical simulation: divide returns by EWMA volatility, take the empirical quantile of the standardised returns, and multiply by today's volatility. Backtest it.
5. Show with a small calculation that for a portfolio of two perfectly correlated assets the portfolio VaR equals the sum of the stand alone VaRs.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "03_market_risk/parametric_var",
        "title": "Parametric and Monte Carlo Value at Risk",
        "family": "Market Risk",
        "level": "Intermediate",
        "dataset": "market_returns",
        "data_kind": "synthetic",
        "status": "Validating",
        "tagline": "Delta normal, Student t, EWMA and Monte Carlo VaR, with Euler risk decomposition and a backtest.",
        "refs": ["jorion_var", "hull_rmfi", "bollerslev1986", "kupiec1995", "artzner1999"],
        "research_note": (
            "Bollerslev defines the GARCH process that generates the synthetic returns, which is why volatility clustering and fat tails "
            "appear in the data. The textbooks are the usual source for the delta normal and EWMA formulas, but they are not verified in this build, "
            "so every formula is checked in the notebook by a hand calculation or a simulation."
        ),
        "learn": [
            "Portfolio variance, delta normal VaR and Student t VaR",
            "EWMA volatility and one day ahead forecasts",
            "Monte Carlo with Cholesky and its convergence",
            "Euler component VaR and diversification",
            "Backtest of parametric against historical VaR",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
