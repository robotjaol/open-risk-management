"""Spec: historical simulation Value at Risk."""

from nbgen import C, M

from specs._common import PORTFOLIO_CODE, check_sections, setup_code

MODULE = "historical_var"

SETUP = setup_code(MODULE) + """
from scipy.stats import kurtosis, skew

from risk_lab.market.backtest import exceptions, kupiec_pof
from risk_lab.market.var import historical_var, rolling_historical_var"""

S = {}

S[1] = [
    M("""
A trading desk holds equity, foreign exchange and bond positions worth 100 million. Risk management must report
one number every morning: **the loss that should be exceeded on only 1 day in 100 over the next trading day.**
That is the 1 day 99 percent Value at Risk (VaR).

Historical simulation answers it with no distribution assumption. It sorts past portfolio returns and reads the quantile.
This notebook builds it, tests how sensitive it is to the window length and the confidence level, quantifies its
sampling error, and shows how it behaves when volatility jumps.

**Decision this supports:** whether historical VaR with a given window is an acceptable daily limit measure, and what
its main weakness is.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Compute historical VaR by hand on a small sample and show the effect of the quantile convention.
2. Build a rolling one day ahead VaR with no look ahead, and verify it against a second implementation.
3. Measure exceptions (days where loss exceeded VaR) and test them against the 1 percent target.
4. Quantify the sampling error of a tail quantile with a bootstrap.
5. Compare VaR across windows and confidence levels, and explain the trade off.
6. Compare square root of time scaling with actual 10 day returns.
7. State what historical VaR cannot see.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Return | Simple daily return of the portfolio. 0.01 is a 1 percent gain |
| Loss | Negative of return |
| VaR at level alpha | The alpha quantile of the loss distribution. Reported as a positive loss |
| Exception | A day when the realised loss is larger than the VaR forecast for that day |
| Window | Number of past days used to estimate the quantile |
| Look ahead | Using information from the forecast day or later. Forbidden in a backtest |

If VaR at 99 percent is correct, exceptions occur with probability 0.01 each day and are independent across days.
"""),
]

S[4] = [
    M("""
**Why historical simulation?**

| Method | Strength | Weakness |
|---|---|---|
| Historical simulation | No distribution assumption. Captures fat tails and correlations already in the data | Slow to react to volatility changes. Needs a long window for a 99 percent tail. Past tail is all it knows |
| Parametric (normal or t) | Smooth, quick to update | Needs a distribution. Wrong shape means wrong tail |
| Monte Carlo | Handles nonlinear positions | Needs a model and many scenarios |

Parametric and Monte Carlo versions are in the next modules. Acceptance criteria for this notebook:

1. The loop implementation and the library agree to 1e-12.
2. The rolling VaR matches a pandas rolling quantile shifted by one day (no look ahead).
3. Bootstrap interval is reported for every confidence level.
4. Exception counts, Kupiec test p values and clusters are reported for each window.

The module does not claim that any window is correct. It reports which windows pass the Kupiec test on this data.
"""),
]

S[6] = [
    M(r"""
Let $r_1, \dots, r_n$ be portfolio returns and $\ell_i = -r_i$ the losses. Sort the losses in ascending order
$\ell_{(1)} \le \dots \le \ell_{(n)}$. The VaR at level $\alpha$ is the empirical quantile

$$\mathrm{VaR}_\alpha = \ell_{(k)}, \qquad k = \lceil n\alpha \rceil$$

in the simplest convention. Most software interpolates linearly between order statistics:

$$\mathrm{VaR}_\alpha = (1 - g)\,\ell_{(j)} + g\,\ell_{(j+1)}, \quad j = \lfloor (n-1)\alpha \rfloor + 1,\ g = (n-1)\alpha - \lfloor (n-1)\alpha \rfloor$$

The number of observations beyond the VaR is about $n(1 - \alpha)$. For $n = 500$ and $\alpha = 0.99$ that is 5 observations,
so the estimate rests on very few days.

**Sampling error.** The asymptotic standard error of an empirical quantile $q$ is

$$\mathrm{se}(q) = \frac{\sqrt{\alpha(1-\alpha)/n}}{f(q)}$$

where $f$ is the loss density at $q$. In the far tail $f(q)$ is small, so the error is large. The bootstrap below measures it
without needing $f$.

**Exceptions.** If the model is right, the number of exceptions over $T$ days is Binomial$(T, 1-\alpha)$.
"""),
]

S[7] = [
    M("""
Twenty daily returns are listed. The 90 percent VaR is wanted. With linear interpolation the position in the sorted losses
is $(n - 1)\\alpha = 19 \\times 0.9 = 17.1$ counted from zero, so the answer lies between the 18th and the 19th smallest loss.
"""),
    C("""
small = np.array([0.8, -1.2, 0.3, -0.5, 1.1, -2.6, 0.2, -0.9, 0.6, -0.1,
                  -1.8, 0.4, -0.3, 0.9, -3.4, 0.1, -0.7, 0.5, -1.5, 0.7]) / 100
losses_small = np.sort(-small)
print("sorted losses (percent):", (losses_small * 100).round(2))
position = (len(small) - 1) * 0.9
lower = int(np.floor(position))
fraction = position - lower
by_hand = (1 - fraction) * losses_small[lower] + fraction * losses_small[lower + 1]
print("position:", round(position, 2), "fraction:", round(fraction, 2))
print("VaR 90 by hand (percent):", round(by_hand * 100, 4))
print("VaR 90 from library (percent):", round(historical_var(small, 0.90) * 100, 4))
assert abs(by_hand - historical_var(small, 0.90)) < 1e-12"""),
    C("""
# convention matters
for method in ["lower", "linear", "higher"]:
    print(method, round(float(np.quantile(-small, 0.90, method=method)) * 100, 3))"""),
    M("""
The three conventions give 1.80, 1.88 and 2.60 percent, so they differ by up to 0.8 percentage points on 20
observations. On a large sample the difference shrinks, but the 99 percent tail of a 250 day window has about
2.5 observations, so the convention can still matter at that window size.
"""),
]

S[8] = [
    M("""
Data: three synthetic daily return series (equity, FX, bond) built from GARCH(1,1) volatility with Student t shocks
and a volatility burst around day 2200. The portfolio holds 50 percent equity, 30 percent FX and 20 percent bond,
rebalanced daily. These weights and the 100 million value are assumptions.
"""),
    C(PORTFOLIO_CODE),
    C("""
stats = pd.Series(
    {
        "mean_daily_pct": portfolio.mean() * 100,
        "std_daily_pct": portfolio.std() * 100,
        "skew": skew(portfolio),
        "excess_kurtosis": kurtosis(portfolio),
        "worst_day_pct": portfolio.min() * 100,
        "best_day_pct": portfolio.max() * 100,
    }
)
print(stats.round(4))
print("burst starts around:", portfolio.index[2200].date(), "and ends around:", portfolio.index[2259].date())
yearly = portfolio.groupby(portfolio.index.year).std() * 100
print("daily volatility by year (percent):")
print(yearly.round(3))"""),
]

S[9] = [
    M("""
Preparation rules:

1. Losses are the negative of portfolio returns.
2. A VaR forecast for day $t$ uses returns up to day $t - 1$ only.
3. Windows 250, 500 and 1000 days are compared over the **same evaluation period**, days 1000 to 2999, so the exception counts are comparable.
4. Portfolio value 100 million.
"""),
    C("""
losses = -portfolio.to_numpy()
VALUE = 100_000_000
ALPHA = 0.99
windows = [250, 500, 1000]
start, end = 1000, len(portfolio)
print("evaluation days:", end - start, "expected exceptions at 1 percent:", (end - start) * 0.01)"""),
]

S[10] = [
    M("""
A loop version with no library call, then the rolling forecast built from it.
"""),
    C("""
def my_var(values, alpha):
    ordered = sorted(-v for v in values)
    position = (len(ordered) - 1) * alpha
    low = int(position)
    frac = position - low
    if low + 1 < len(ordered):
        return (1 - frac) * ordered[low] + frac * ordered[low + 1]
    return ordered[low]


def my_rolling(values, window, alpha):
    out = [np.nan] * len(values)
    for t in range(window, len(values)):
        out[t] = my_var(values[t - window : t], alpha)
    return np.array(out)


sample = portfolio.to_numpy()
mine_500 = my_rolling(sample, 500, ALPHA)
lib_500 = rolling_historical_var(sample, 500, ALPHA)
valid = ~np.isnan(lib_500)
gap_loop = float(np.max(np.abs(mine_500[valid] - lib_500[valid])))
print("max gap loop vs library:", f"{gap_loop:.2e}")
assert gap_loop < 1e-12"""),
]

S[11] = [
    M("""
Second implementation: pandas rolling quantile on the loss series, shifted by one day so day $t$ uses data to $t - 1$.
If the library had a look ahead error, this check would fail.
"""),
    C("""
loss_series = pd.Series(losses, index=portfolio.index)
var_by_window = {}
pandas_gap_max = 0.0
for window in windows:
    own = rolling_historical_var(sample, window, ALPHA)
    pandas_version = loss_series.rolling(window).quantile(ALPHA).shift(1).to_numpy()
    both = ~np.isnan(own) & ~np.isnan(pandas_version)
    gap = np.max(np.abs(own[both] - pandas_version[both]))
    print("window", window, "max gap vs pandas:", f"{gap:.2e}")
    assert gap < 1e-12
    pandas_gap_max = max(pandas_gap_max, float(gap))
    var_by_window[window] = own"""),
]

S[12] = [
    C("""
rows = []
hits_by_window = {}
for window in windows:
    var_series = var_by_window[window]
    hits = exceptions(sample[start:end], var_series[start:end])
    hits_by_window[window] = hits
    test = kupiec_pof(hits, 1 - ALPHA)
    burst = exceptions(sample[2200:2260], var_series[2200:2260])
    rows.append(
        {
            "window": window,
            "exceptions": int(hits.sum()),
            "expected": (end - start) * (1 - ALPHA),
            "exception_rate_pct": 100 * hits.mean(),
            "kupiec_p_value": test["p_value"],
            "exceptions_in_burst_60d": int(burst.sum()),
            "mean_var_pct": 100 * np.nanmean(var_series[start:end]),
            "var_std_pct": 100 * np.nanstd(var_series[start:end]),
        }
    )
evaluation = pd.DataFrame(rows).set_index("window")
print(evaluation.round(4))"""),
    C("""
# clustering of exceptions
for window in windows:
    days = np.where(hits_by_window[window] == 1)[0] + start
    in_burst = int(np.sum((days >= 2200) & (days < 2260)))
    print("window", window, "exception days:", len(days), "of which inside the burst:", in_burst)"""),
]

S[13] = [
    C("""
fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
dates = portfolio.index
axes[0].plot(dates[start:end], 100 * portfolio.iloc[start:end], color=COLORS["grey"], linewidth=0.6, label="return")
axes[0].plot(dates[start:end], -100 * var_by_window[500][start:end], color=COLORS["main"], label="minus VaR 99, window 500")
hit_days = np.where(hits_by_window[500] == 1)[0] + start
axes[0].scatter(dates[hit_days], 100 * portfolio.iloc[hit_days], color=COLORS["second"], s=14, zorder=3, label="exception")
axes[0].set_ylabel("percent")
axes[0].set_title("Returns, VaR and exceptions")
axes[0].legend(loc="lower left")

for window, color in zip(windows, [COLORS["second"], COLORS["main"], COLORS["third"]]):
    axes[1].plot(dates[start:end], 100 * var_by_window[window][start:end], color=color, label=f"window {window}")
axes[1].set_ylabel("VaR 99 (percent of value)")
axes[1].set_title("VaR by window length")
axes[1].legend()
save_figure(fig, MODULE, "rolling_var_and_exceptions.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots()
ax.hist(100 * portfolio, bins=80, color=COLORS["main"], alpha=0.7)
for level, color in zip([0.95, 0.99], [COLORS["third"], COLORS["second"]]):
    ax.axvline(-100 * historical_var(sample, level), color=color, linestyle="--", label=f"VaR {int(level * 100)}")
ax.set_xlabel("daily return (percent)")
ax.set_title("Return distribution with full sample VaR")
ax.legend()
save_figure(fig, MODULE, "return_histogram.png")
plt.show()"""),
]

S[14] = [
    M("""
How to read the output below. The statements marked **observed** come from the printed numbers. Statements marked
**inference** are explanations that this notebook does not prove.

* **Observed.** The standard deviation of the VaR series falls as the window grows, so longer windows give a smoother VaR.
* **Observed.** Compare each window's exception count with the expected 20. The Kupiec test looks only at the count. A p value above 0.05 means the count is not unusual, not that the model is right.
* **Observed.** In the 60 day burst, about 0.6 exceptions would be expected if VaR were right. The printed burst counts are far above that for every window, so exceptions cluster. The count based Kupiec test cannot see this. The Christoffersen test in the backtesting module can.
* **Inference.** A short window can show more exceptions than a long one. The likely reason is noise: a 99 percent VaR from 250 days rests on about 2.5 tail days, so the estimate often lands too low. Faster reaction does not offset that noise on this dataset.
"""),
    C("""
best = evaluation["kupiec_p_value"].idxmax()
print("window with the highest Kupiec p value:", best)
print("windows that pass Kupiec at 5 percent:", [w for w in windows if evaluation.loc[w, "kupiec_p_value"] > 0.05])
print("VaR volatility falls as window grows:", bool(evaluation["var_std_pct"].is_monotonic_decreasing))
print("exceptions inside the 60 day burst by window:", dict(zip(windows, evaluation["exceptions_in_burst_60d"].tolist())))
print("expected inside the burst if VaR were right:", 60 * (1 - ALPHA))"""),
]

S[15] = [
    M("""
**Experiment A: confidence level and sampling error.** Historical VaR on the full 3000 day sample at four levels, with a
bootstrap interval from 2000 resamples (iid, seed fixed). The number of tail observations is $n(1-\\alpha)$.

**Experiment B: horizon scaling.** Compare the square root of time rule with the VaR of actual overlapping 10 day returns.
Overlapping windows are not independent, so the 10 day interval below is indicative only.
"""),
    C("""
rng = np.random.default_rng(SEED)
levels = [0.95, 0.975, 0.99, 0.999]
n_boot = 2000
rows = []
for level in levels:
    point = historical_var(sample, level)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        resample = rng.choice(sample, size=len(sample), replace=True)
        boot[b] = historical_var(resample, level)
    low, high = np.quantile(boot, [0.025, 0.975])
    rows.append(
        {
            "level": level,
            "tail_obs": len(sample) * (1 - level),
            "var_pct": 100 * point,
            "boot_low_pct": 100 * low,
            "boot_high_pct": 100 * high,
            "relative_width_pct": 100 * (high - low) / point,
        }
    )
level_table = pd.DataFrame(rows)
print(level_table.round(3).to_string(index=False))"""),
    C("""
# ten day scaling
gross = (1 + portfolio).cumprod().to_numpy()
ten_day = gross[10:] / gross[:-10] - 1
var_1 = historical_var(sample, 0.99)
var_10_actual = historical_var(ten_day, 0.99)
var_10_scaled = var_1 * np.sqrt(10)
print("1 day VaR 99 (percent):", round(100 * var_1, 3))
print("10 day VaR 99 by sqrt of time (percent):", round(100 * var_10_scaled, 3))
print("10 day VaR 99 from overlapping 10 day returns (percent):", round(100 * var_10_actual, 3))
print("ratio actual over scaled:", round(var_10_actual / var_10_scaled, 3))"""),
]

S[16] = [
    C("""
print(evaluation.round(4))
print()
print(level_table.round(3).to_string(index=False))
metrics = {
    "full_sample_var_99_pct": 100 * var_1,
    "full_sample_var_99_currency": float(VALUE * var_1),
    "evaluation_by_window": evaluation.reset_index().to_dict(orient="records"),
    "confidence_level_table": level_table.to_dict(orient="records"),
    "ten_day_var_99_sqrt_time_pct": 100 * var_10_scaled,
    "ten_day_var_99_overlapping_pct": 100 * var_10_actual,
    "windows_passing_kupiec_5pct": [int(w) for w in windows if evaluation.loc[w, "kupiec_p_value"] > 0.05],
    "max_gap_loop_vs_library": gap_loop,
    "acceptance_criteria": {
        "loop_matches_library_1e-12": bool(gap_loop < 1e-12),
        "rolling_matches_pandas_no_lookahead": bool(pandas_gap_max < 1e-12),
        "bootstrap_interval_for_every_level": bool(len(level_table) == len(levels)),
        "exceptions_and_kupiec_for_every_window": bool(len(evaluation) == len(windows)),
    },
}
config = {"weights": dict(zip(assets, weights.tolist())), "windows": windows, "alpha": ALPHA, "n_boot": n_boot,
          "evaluation_days": [start, end], "portfolio_value": VALUE, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Historical simulation VaR, rolling windows, bootstrap interval, exception counts and Kupiec test",
    data_kind="synthetic",
    dataset="datasets/synthetic/market_returns.csv",
    n_obs=int(len(portfolio)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "portfolio weights 50, 30, 20 percent rebalanced daily",
        "iid bootstrap ignores volatility clustering",
        "volatility burst around day 2200 is part of the generator",
    ],
    metrics=metrics,
    baseline={"note": "window 250 against 500 against 1000 on the same evaluation days"},
    limitations=[
        "synthetic returns from a GARCH generator",
        "no position level revaluation, linear portfolio only",
        "iid bootstrap understates uncertainty when volatility clusters",
    ],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
**Limitations**

1. **Slow reaction.** Historical VaR weighs all days in the window equally, so it lags volatility. The burst experiment shows the cost.
2. **Few tail points.** At 99 percent a 250 day window uses about 2.5 days. The bootstrap interval in Experiment A shows how wide that is.
3. **Ghost effects.** When an extreme day leaves the window, VaR drops sharply with no change in the market.
4. **Not coherent.** VaR can fail subadditivity (Artzner et al.). The expected shortfall module shows a worked counterexample.
5. **No tail size information.** VaR says nothing about how bad losses are beyond the quantile.
6. **iid bootstrap.** Resampling days ignores volatility clustering, so the intervals are too narrow in clustered periods. A bootstrap also cannot go beyond the worst observed day, so for the 99.9 percent level it understates the uncertainty.
7. **Square root of time.** It assumes independent returns with constant volatility. Compare it with the overlapping 10 day estimate above.
8. **Synthetic data.** The generator has constant correlation and known tails. Real markets are less tidy.

**Model risk.** Choosing the window is a model decision with measurable consequences. The window must be documented and tested
on out of sample exceptions, which is what this notebook demonstrates.
"""),
]

S[18] = [
    M("""
A desk limit is set as VaR 99 not above 1.5 percent of portfolio value. The table converts the rolling VaR to currency
and counts the days when the limit would have been breached. The 1.5 percent limit is **illustrative**.

Regulatory note, **check before use**: older Basel market risk rules (Basel II.5) set capital from a 10 day 99 percent VaR
with a multiplier. The current Basel market risk framework moved the internal model measure to expected shortfall at 97.5 percent.
Confirm the current text in the Basel Framework before using any of these figures for capital.
"""),
    C("""
limit_pct = 0.015
var500 = var_by_window[500]
currency = VALUE * var500[start:end]
breach_days = int(np.sum(var500[start:end] > limit_pct))
print("VaR 99 in currency, mean:", f"{np.nanmean(currency):,.0f}", "max:", f"{np.nanmax(currency):,.0f}")
print("limit in currency:", f"{VALUE * limit_pct:,.0f}")
print("days where VaR is above the limit:", breach_days, "of", end - start)
print("10 day VaR in currency by sqrt of time, latest day:", f"{VALUE * var500[-1] * np.sqrt(10):,.0f}")"""),
]

S[19] = [
    M("""
1. Change the weights to 100 percent equity. Recompute the exception counts. Which window now passes Kupiec?
2. Replace the iid bootstrap with a block bootstrap of 20 day blocks. Compare the interval widths for the 99 percent level.
3. Use 'lower' and 'higher' quantile conventions in the rolling VaR and report how the exception count at window 250 changes.
4. Weight recent days more: use an exponentially weighted historical simulation with decay 0.99. Is the burst handled better? (The next module covers EWMA volatility.)
5. Find the smallest window for which the 99 percent bootstrap interval is narrower than 25 percent of the point estimate.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "03_market_risk/historical_var",
        "title": "Historical Simulation Value at Risk",
        "family": "Market Risk",
        "level": "Beginner to Intermediate",
        "dataset": "market_returns",
        "data_kind": "synthetic",
        "status": "Validating",
        "tagline": "Compute rolling historical VaR, test its exceptions, and measure its sampling error and lag.",
        "refs": ["jorion_var", "hull_rmfi", "kupiec1995", "artzner1999", "bcbs_d457"],
        "research_note": (
            "Kupiec supplies the exception count test used here. Artzner et al. supply the coherence argument behind the "
            "subadditivity limitation. The Basel market risk standard is cited for context on the move from VaR to expected shortfall. "
            "The two textbooks are not verified in this build, which is why the module stays at Validating."
        ),
        "learn": [
            "Empirical quantile VaR and quantile conventions",
            "Rolling forecast with no look ahead, verified by a second implementation",
            "Exceptions, Kupiec test and exception clustering",
            "Bootstrap interval for a tail quantile",
            "Window length trade off and square root of time scaling",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
