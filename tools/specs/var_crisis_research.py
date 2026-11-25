"""Spec: research simulation, does a calm period VaR survive a crisis on real data."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "var_crisis_research"

SETUP = setup_code(MODULE) + """
from scipy.stats import binomtest, t

from risk_lab.market.backtest import christoffersen_independence, kupiec_pof
from risk_lab.market.var import ewma_var, rolling_historical_var

ALPHA = 0.99
EXPECTED_RATE = 1 - ALPHA"""

S = {}

S[1] = [
    M("""
A risk committee looks at a backtest of the bank's 99 percent one day VaR. The model passed in the calm years. A member asks the
question that matters for capital: **will the same model hold in a crisis, when the loss is real?**

This notebook is a **research simulation**. It treats the question as a testable claim, fixes the rules for judging it, and runs
it on **real public price history**: daily WTI crude oil spot prices from 1986 and an equal weight basket of six currencies
against the US dollar from 2000.

Hypotheses, stated before the final run:

* **H1.** A 500 day historical VaR at 99 percent has a pooled exception rate above 1 percent in crisis windows, and the Kupiec test
  rejects the 1 percent rate at the 5 percent level, on both assets.
* **H2.** A volatility responsive model (EWMA volatility with a Student t multiplier, 4 degrees of freedom) has a pooled crisis
  exception rate closer to 1 percent than the historical model, on both assets.

A third quantity is reported without a hypothesis: **what the responsive model costs in calm periods**, measured as the ratio of
its average VaR to the historical VaR.

**Honesty note.** The author ran a quick exploratory version of this comparison before writing the rules down. The rules below were
fixed before the final run and are the same ones in the code, but this is not a blind pre registration.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Turn a vague worry ("will the model hold in a crisis?") into hypotheses with a written decision rule.
2. Build returns from real price data and document every day that had to be excluded and why.
3. Implement a rolling historical VaR and an EWMA VaR from scratch and match the library with no look ahead.
4. Compare models on the same days, by period, with Kupiec tests and exact binomial intervals.
5. Test whether the conclusion survives changes in the window length, the decay and the degrees of freedom.
6. State the cost of a more responsive model, not only its benefit.
7. Write the finding in the form a risk committee can act on, with its limits.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Crisis window | A calendar interval fixed in advance from well known market events. It is not chosen by how the model performed |
| Pooled exception rate | Exceptions divided by days, with all days of all crisis windows put together |
| Calm period | Every evaluated day outside the crisis windows |
| Exception | A day when the loss was larger than the one day VaR forecast made the day before |
| Kupiec test | Tests whether the exception rate equals the expected 1 percent |
| Exact interval | Clopper Pearson interval for a binomial rate. Too narrow when exceptions cluster |
| EWMA | Exponentially weighted moving average of squared returns, decay 0.94 here |
| Procyclicality | A risk measure that is low before a crisis and jumps in it, so it asks for capital when capital is scarce |
"""),
]

S[4] = [
    M("""
**Why a research simulation on real data?** The earlier modules showed that VaR code is correct on synthetic data. They could not
show whether a method fails when the world changes, because the generator never changed. Real history contains regime breaks the author did
not design.

**Why these two models?** The historical 500 day window is a common baseline. EWMA with a fat tailed multiplier is the simplest
model that reacts to a volatility jump. Comparing a slow model with a fast model is the cleanest test of the claim.

**Method checks (acceptance criteria).** These check the method, not the finding. A finding can go either way and is still valid.

1. The from scratch VaR for five random days equals the library to 1e-12 using only data before the day (no look ahead).
2. Every crisis window lies inside the data and holds at least 80 evaluated days for each asset.
3. The count of excluded WTI return days equals the count found by an independent rule.
4. The two hypotheses are evaluated with the stated rules for both assets.
"""),
]

S[6] = [
    M(r"""
**Return.** With price $P_t$, the simple return is $r_t = P_t / P_{t-1} - 1$ and the loss is $\ell_t = -r_t$. For a currency quoted as units
per US dollar, $S_t$, the dollar value of one unit is $1/S_t$, so the dollar return of holding it is $r_t = S_{t-1}/S_t - 1$.

**Historical VaR.** With window $w$, $\widehat{\mathrm{VaR}}_t = $ empirical $\alpha$ quantile of $\ell_{t-w}, \dots, \ell_{t-1}$.

**EWMA VaR.** $\sigma_t^2 = \lambda \sigma_{t-1}^2 + (1-\lambda) r_{t-1}^2$ and

$$\widehat{\mathrm{VaR}}_t = \sigma_t \, t_\alpha(\nu)\sqrt{(\nu-2)/\nu}$$

with $t_\alpha(\nu)$ the Student t quantile. The factor $\sqrt{(\nu-2)/\nu}$ gives the t distribution unit variance.

**Test.** Over $T$ days with $x$ exceptions, the Kupiec statistic is
$LR = -2\ln[(1-p)^{T-x}p^x] + 2\ln[(1-x/T)^{T-x}(x/T)^x]$, $p = 0.01$, chi squared with one degree of freedom.

**Why 500 days is thin.** At 99 percent, a 500 day window has $500 \times 0.01 = 5$ days beyond the VaR. After a long calm stretch the
five worst days are mild, so the VaR is low just when volatility is about to rise.
"""),
]

S[7] = [
    M("""
A tiny example with a 10 day window and 80 percent VaR so that the numbers can be checked by eye. Ten past losses
(percent): 0.2, -0.4, 0.5, 0.1, -0.3, 0.9, -0.1, 0.3, 0.6, -0.5. Sorted: -0.5, -0.4, -0.3, -0.1, 0.1, 0.2, 0.3, 0.5, 0.6, 0.9.
With linear interpolation the 80 percent quantile sits at position $9 \\times 0.8 = 7.2$ from zero, between 0.5 and 0.6.
"""),
    C("""
past_losses = np.array([0.2, -0.4, 0.5, 0.1, -0.3, 0.9, -0.1, 0.3, 0.6, -0.5])
ordered = np.sort(past_losses)
position = (len(ordered) - 1) * 0.8
low = int(np.floor(position))
by_hand = ordered[low] + (position - low) * (ordered[low + 1] - ordered[low])
print("position:", round(position, 2), "VaR by hand:", round(by_hand, 4))
print("numpy quantile:", round(float(np.quantile(past_losses, 0.8)), 4))
assert abs(by_hand - np.quantile(past_losses, 0.8)) < 1e-12
# exception rule
today_loss = 0.7
print("today loss", today_loss, "exception:", today_loss > by_hand)"""),
    M("""
Today's loss of 0.7 is larger than the VaR of 0.52, so it counts as one exception. The rest of the notebook counts such days on
thousands of real days and asks whether the count is close to 1 in 100.
"""),
]

S[8] = [
    C("""
wti_raw = pd.read_csv(ROOT / "datasets" / "raw" / "wti_spot_daily.csv", parse_dates=["Date"]).set_index("Date")["Price"]
fx_raw = pd.read_csv(ROOT / "datasets" / "processed" / "fx_daily_2000.csv", parse_dates=["Date"]).set_index("Date")
print("WTI days:", len(wti_raw), "from", wti_raw.index.min().date(), "to", wti_raw.index.max().date())
print("WTI price range:", wti_raw.min(), "to", wti_raw.max())
print()
print("WTI days with price at or below zero:")
print(wti_raw[wti_raw <= 0])
print()
print("FX days:", len(fx_raw), "from", fx_raw.index.min().date(), "to", fx_raw.index.max().date())
print("share of missing days per currency:")
print(fx_raw.isna().mean().round(3).to_string())"""),
    M("""
Two facts from the real data matter before any model is fitted. First, the WTI series has one day with a **negative price**, so a
return from that day is not defined. Second, the currency file has holiday gaps, so some days are missing for all currencies at once.
Both are handled openly in the next section.
"""),
]

S[9] = [
    C("""
# wti returns
has_previous = wti_raw.shift().notna()
valid = (wti_raw > 0) & (wti_raw.shift() > 0)
excluded_days = wti_raw.index[has_previous & ~valid]
wti_ret = wti_raw.pct_change()[valid]
print("excluded WTI return days:", [d.date().isoformat() for d in excluded_days])
print("WTI returns:", len(wti_ret))

# independent exclusion count
nonpositive = wti_raw.index[wti_raw <= 0]
expected_excluded = set(nonpositive) | {wti_raw.index[wti_raw.index.get_loc(d) + 1] for d in nonpositive}
print("independent rule gives:", len(expected_excluded), "days")

# fx basket
currencies = ["Euro", "Japan", "United Kingdom", "Switzerland", "Canada", "Singapore"]
fx = fx_raw[currencies].dropna()
assert fx["Euro"].mean() < 1 and fx["United Kingdom"].mean() < 1, "quote is not per US dollar"
fx_each = fx.shift() / fx - 1
fx_each = fx_each.dropna()
basket_ret = fx_each.mean(axis=1)
print("FX basket returns:", len(basket_ret), "days dropped for gaps:", len(fx_raw) - len(fx))

assets = {"WTI": wti_ret, "FX basket": basket_ret}
windows = {
    "gfc": ("2008-09-01", "2009-06-30"),
    "oil_collapse": ("2014-06-01", "2016-02-29"),
    "covid": ("2020-02-20", "2020-06-30"),
    "ukraine": ("2022-02-24", "2022-12-31"),
}"""),
    M("""
**Decisions recorded.** (1) Days with an undefined return are dropped, not repaired. Repairing would invent a number for the most extreme
day in the file. (2) Missing currency days are dropped for all currencies, so a return can span a holiday. (3) The basket holds equal dollar amounts of six currencies,
rebalanced daily. The Indonesian rupiah is not in the source. (4) The crisis windows are fixed calendar dates taken from well known
events. The dates are the author's judgment, not from a verified source.
"""),
]

S[10] = [
    C("""
def hist_var_scratch(x, i, window, alpha):
    # sort past losses
    past = np.sort(-x[i - window:i])
    position = (window - 1) * alpha
    low = int(np.floor(position))
    return past[low] + (position - low) * (past[low + 1] - past[low])


def ewma_var_scratch(x, i, decay, nu, alpha):
    # variance recursion
    variance = x[:30].var()
    for k in range(1, i + 1):
        variance = decay * variance + (1 - decay) * x[k - 1] ** 2
    multiplier = t.ppf(alpha, nu) * np.sqrt((nu - 2) / nu)
    return np.sqrt(variance) * multiplier


# library series
def model_series(r):
    x = r.to_numpy()
    raw = {
        "hist250": rolling_historical_var(x, 250, ALPHA),
        "hist500": rolling_historical_var(x, 500, ALPHA),
        "hist1000": rolling_historical_var(x, 1000, ALPHA),
        "ewma_normal": ewma_var(x, 0.94, ALPHA),
        "ewma_t4": ewma_var(x, 0.94, ALPHA, nu=4),
    }
    return pd.DataFrame(raw, index=r.index)


var_tables = {name: model_series(r) for name, r in assets.items()}

rng = np.random.default_rng(SEED)
worst_gap = 0.0
for name, r in assets.items():
    x = r.to_numpy()
    for i in rng.integers(1500, len(x), size=5):
        gap_h = abs(hist_var_scratch(x, i, 500, ALPHA) - var_tables[name]["hist500"].iloc[i])
        gap_e = abs(ewma_var_scratch(x, i, 0.94, 4, ALPHA) - var_tables[name]["ewma_t4"].iloc[i])
        worst_gap = max(worst_gap, gap_h, gap_e)
print("largest gap, scratch against library:", f"{worst_gap:.2e}")
assert worst_gap < 1e-12"""),
    M("""
The scratch version of each VaR uses only data strictly before day $i$ (`x[i-window:i]` and a recursion that stops at $x_{i-1}$). It
matches the library for five random days per asset, so the series are free of look ahead.
"""),
]

S[11] = [
    C("""
def exception_series(r, var_series):
    # one if loss above VaR
    valid = var_series.notna()
    return pd.Series((-r[valid] > var_series[valid]).astype(int), index=r.index[valid])


def crisis_flag(index):
    flag = pd.Series(False, index=index)
    for start, end in windows.values():
        flag[start:end] = True
    return flag


# common evaluation days
hits = {}
evaluation_days = {}
for name, r in assets.items():
    table = var_tables[name]
    common = table.dropna().index
    evaluation_days[name] = common
    hits[name] = {model: exception_series(r.loc[common], table.loc[common, model]) for model in table.columns}
    print(name, "evaluation days:", len(common), common.min().date(), "to", common.max().date())"""),
    M("""
All five models are scored on the **same days**, those after the longest window (1000 days) has filled. Scoring models on different days
would hide differences in the sample, not in the model.
"""),
]

S[12] = [
    C("""
def rate_row(asset, model, period, h):
    n = int(len(h))
    k = int(h.sum())
    kup = kupiec_pof(h.to_numpy(), EXPECTED_RATE)
    low, high = binomtest(k, n, EXPECTED_RATE).proportion_ci(method="exact")
    return {"asset": asset, "model": model, "period": period, "days": n, "exceptions": k,
            "rate": k / n, "kupiec_p": kup["p_value"], "ci_low": low, "ci_high": high}


rows = []
for name in assets:
    flag = crisis_flag(hits[name]["hist500"].index)
    for model, h in hits[name].items():
        for label, (start, end) in windows.items():
            rows.append(rate_row(name, model, label, h[start:end]))
        rows.append(rate_row(name, model, "crisis_pooled", h[flag]))
        rows.append(rate_row(name, model, "calm", h[~flag]))
evaluation = pd.DataFrame(rows)
view = evaluation[evaluation["period"].isin(["crisis_pooled", "calm"])]
print(view.round(4).to_string(index=False))"""),
    C("""
# hypothesis rules
outcomes = {}
for name in assets:
    sub = evaluation[(evaluation["asset"] == name) & (evaluation["period"] == "crisis_pooled")].set_index("model")
    h1 = bool(sub.loc["hist500", "rate"] > EXPECTED_RATE and sub.loc["hist500", "kupiec_p"] < 0.05)
    gap_hist = abs(sub.loc["hist500", "rate"] - EXPECTED_RATE)
    gap_ewma = abs(sub.loc["ewma_t4", "rate"] - EXPECTED_RATE)
    outcomes[name] = {"H1": h1, "H2": bool(gap_ewma < gap_hist),
                      "gap_hist500": float(gap_hist), "gap_ewma_t4": float(gap_ewma)}
overall = {"H1": all(v["H1"] for v in outcomes.values()), "H2": all(v["H2"] for v in outcomes.values())}
print(pd.DataFrame(outcomes).T.to_string())
print("overall:", overall)"""),
    C("""
# cost in calm periods
cost_rows = []
for name in assets:
    flag = crisis_flag(var_tables[name].dropna().index)
    table = var_tables[name].dropna()
    cost_rows.append({
        "asset": name,
        "calm_mean_var_ratio_ewma_t4_to_hist500": float(table.loc[~flag.values, "ewma_t4"].mean() / table.loc[~flag.values, "hist500"].mean()),
        "crisis_mean_var_ratio_ewma_t4_to_hist500": float(table.loc[flag.values, "ewma_t4"].mean() / table.loc[flag.values, "hist500"].mean()),
    })
cost_table = pd.DataFrame(cost_rows)
print(cost_table.round(3).to_string(index=False))

# clustering on full series
independence = {}
for name in assets:
    independence[name] = {m: christoffersen_independence(h.to_numpy())["p_value"] for m, h in hits[name].items()}
print()
print(pd.DataFrame(independence).round(4).to_string())"""),
]

S[13] = [
    C("""
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
periods = ["gfc", "oil_collapse", "covid", "ukraine", "crisis_pooled", "calm"]
models_plot = ["hist500", "ewma_t4"]
colors = {"hist500": COLORS["second"], "ewma_t4": COLORS["main"]}
for ax, name in zip(axes, assets):
    for j, model in enumerate(models_plot):
        sub = evaluation[(evaluation["asset"] == name) & (evaluation["model"] == model)].set_index("period").loc[periods]
        positions = np.arange(len(periods)) + (j - 0.5) * 0.38
        ax.bar(positions, sub["rate"] * 100, width=0.38, color=colors[model], label=model)
    ax.axhline(1.0, color="black", linewidth=1, linestyle="--")
    ax.set_xticks(np.arange(len(periods)))
    ax.set_xticklabels(periods, rotation=30, ha="right")
    ax.set_title(name)
axes[0].set_ylabel("exception rate (percent)")
axes[0].legend()
fig.suptitle("Exception rate by period, 99 percent VaR, dashed line is the expected 1 percent")
fig.tight_layout()
save_figure(fig, MODULE, "exception_rate_by_period.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots(figsize=(10, 4.2))
r = assets["WTI"]
table = var_tables["WTI"].dropna()
zoom = slice("2007-06-01", "2010-06-30")
ax.plot(r.loc[table.index][zoom].index, -r.loc[table.index][zoom] * 100, color=COLORS["grey"], linewidth=0.6, label="daily loss")
ax.plot(table[zoom].index, table["hist500"][zoom] * 100, color=COLORS["second"], label="hist500 VaR")
ax.plot(table[zoom].index, table["ewma_t4"][zoom] * 100, color=COLORS["main"], label="ewma_t4 VaR")
start, end = windows["gfc"]
ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color="#f0e0a0", alpha=0.4, label="crisis window")
ax.set_ylabel("percent of price")
ax.set_title("WTI daily loss and 99 percent VaR around the 2008 crisis")
ax.legend(loc="upper left")
save_figure(fig, MODULE, "wti_gfc_var_paths.png")
plt.show()"""),
]

S[14] = [
    C("""
for name in assets:
    sub = evaluation[(evaluation["asset"] == name) & (evaluation["period"].isin(["crisis_pooled", "calm"]))]
    h = sub[sub["model"] == "hist500"].set_index("period")
    e = sub[sub["model"] == "ewma_t4"].set_index("period")
    print(f"{name}: hist500 crisis rate {h.loc['crisis_pooled', 'rate'] * 100:.2f} percent "
          f"({int(h.loc['crisis_pooled', 'exceptions'])} of {int(h.loc['crisis_pooled', 'days'])} days), "
          f"calm rate {h.loc['calm', 'rate'] * 100:.2f} percent. "
          f"ewma_t4 crisis rate {e.loc['crisis_pooled', 'rate'] * 100:.2f} percent, calm rate {e.loc['calm', 'rate'] * 100:.2f} percent.")
print()
print("H1 supported on both assets:", overall["H1"])
print("H2 supported on both assets:", overall["H2"])"""),
    M("""
**How to read it.** A 99 percent model should be wrong on 1 day in 100 in every kind of period. When the historical model is
wrong several times more often in a crisis than in calm years, its VaR is a measure of the **past**, not of current risk. The responsive
model repairs most of that gap in a crisis, and the cost sits on the other side of the table: its VaR is higher or lower than the historical
VaR in calm times by the ratio printed in the cost table. Whether that cost is acceptable is a **business decision**, not a statistical one.

Clusters matter too. Exceptions in a crisis come in bunches, so the exact intervals above are narrower than the true uncertainty, and the
Kupiec test over pooled days is more likely to reject than its nominal 5 percent. The Christoffersen p values by model show how much
clustering remains.
"""),
]

S[15] = [
    C("""
def pooled_rates(r, series):
    common = series.dropna().index
    flag = crisis_flag(common)
    h = exception_series(r.loc[common], series.loc[common])
    return float(h[flag].mean()), float(h[~flag].mean()), int(len(common))


grid_rows = []
for name, r in assets.items():
    x = r.to_numpy()
    configs = {}
    for window in [250, 500, 1000]:
        configs[f"hist{window}"] = pd.Series(rolling_historical_var(x, window, ALPHA), index=r.index)
    for decay in [0.94, 0.97]:
        for nu in [None, 3.5, 4, 6, 10]:
            label = f"ewma{decay}_nu{nu}"
            configs[label] = pd.Series(ewma_var(x, decay, ALPHA, nu=nu), index=r.index)
    start_day = max(s.dropna().index.min() for s in configs.values())
    for label, series in configs.items():
        series = series[series.index >= start_day]
        crisis_rate, calm_rate, days = pooled_rates(r, series)
        grid_rows.append({"asset": name, "config": label, "crisis_rate": crisis_rate, "calm_rate": calm_rate, "days": days})
grid = pd.DataFrame(grid_rows)
grid["crisis_gap"] = (grid["crisis_rate"] - EXPECTED_RATE).abs()
print(grid.pivot(index="config", columns="asset", values="crisis_rate").round(4).to_string())
print()
print(grid.pivot(index="config", columns="asset", values="calm_rate").round(4).to_string())"""),
    C("""
# does h2 survive
baseline = grid[grid["config"] == "hist500"].set_index("asset")["crisis_gap"]
ewma_rows = grid[grid["config"].str.startswith("ewma") & ~grid["config"].str.endswith("None")]
closer = ewma_rows.assign(closer=ewma_rows.apply(lambda row: row["crisis_gap"] < baseline[row["asset"]], axis=1))
share_closer = float(closer["closer"].mean())
print("t based ewma configurations that beat hist500 on crisis gap:", closer["closer"].sum(), "of", len(closer))
print("share:", round(share_closer, 3))"""),
    M("""
This grid tests whether H2 depends on the one setting fixed in advance (decay 0.94 and 4 degrees of freedom). If most settings agree, the
conclusion is not an artefact of that choice. Note that the evaluation days here start at the first day where every configuration exists, so the sample can differ slightly from the main table.
"""),
]

S[16] = [
    C("""
criteria = {
    "scratch_matches_library_no_lookahead_1e-12": bool(worst_gap < 1e-12),
    "windows_inside_data_with_80_days": bool(all(
        len(hits[name]["hist500"][start:end]) >= 80 for name in assets for start, end in windows.values()
    )),
    "excluded_wti_days_match_independent_rule": bool(set(excluded_days) == expected_excluded),
    "hypotheses_evaluated_for_both_assets": bool(all(set(v) >= {"H1", "H2"} for v in outcomes.values())),
}
print(criteria)

metrics = {
    "assets": {name: {"returns": int(len(r)), "evaluation_days": int(len(evaluation_days[name]))} for name, r in assets.items()},
    "excluded_wti_return_days": [d.date().isoformat() for d in excluded_days],
    "crisis_windows": windows,
    "hypothesis_outcomes_by_asset": outcomes,
    "hypothesis_outcomes_overall": overall,
    "evaluation_table": evaluation.to_dict(orient="records"),
    "cost_in_calm_and_crisis": cost_table.to_dict(orient="records"),
    "christoffersen_independence_p": independence,
    "sensitivity_grid": grid.to_dict(orient="records"),
    "share_t_ewma_configs_beating_hist500": share_closer,
    "scratch_vs_library_max_gap": float(worst_gap),
    "acceptance_criteria": criteria,
}
config = {"alpha": ALPHA, "windows": windows, "currencies": currencies, "hist_windows": [250, 500, 1000],
          "ewma_decay": 0.94, "ewma_nu": 4, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Pre stated hypotheses on exception rates of a historical and an EWMA t VaR in crisis windows, Kupiec tests, exact intervals, sensitivity grid",
    data_kind="empirical",
    dataset="datasets/raw/wti_spot_daily.csv and datasets/processed/fx_daily_2000.csv",
    n_obs=int(sum(len(r) for r in assets.values())),
    seed=SEED,
    parameters=config,
    assumptions=[
        "crisis windows are calendar dates chosen by the author from well known events",
        "equal dollar weight FX basket rebalanced daily",
        "days with undefined WTI returns are dropped",
        "the author ran an exploratory version before fixing the rules",
    ],
    metrics=metrics,
    baseline="500 day historical VaR at 99 percent",
    limitations=[
        "two assets only, one FX basket and one commodity",
        "crisis windows are few and chosen with hindsight about which periods were crises",
        "exceptions cluster, so exact intervals and Kupiec p values are too optimistic",
        "single day VaR on linear positions, no ten day horizon and no capital calculation",
    ],
    figures=["exception_rate_by_period.png", "wti_gfc_var_paths.png"],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
1. **Few events.** Four crisis windows are four draws from history. The pooled test treats their days as independent, which they are not.
2. **Hindsight in the windows.** The author knew which periods were crises. The dates were fixed from events, not from VaR failures, but the choice is still not blind.
3. **Exploration before rules.** An exploratory run came before the written rules. The rules were not changed after it, but the author cannot prove a blind test.
4. **Two assets.** An oil price and a currency basket say little about a loan book or an interest rate book.
5. **The worst day is missing.** The negative oil price day is dropped because a return is undefined. A real desk must handle that day, and a model that cannot represent it has a **model risk** that no backtest on the remaining days will show.
6. **Single day, linear positions.** No ten day horizon, no options, no liquidity horizon.
7. **Fixed settings.** Decay 0.94 and 4 degrees of freedom were set in advance, not estimated. The sensitivity grid tests part of this.
8. **Procyclicality is not solved.** A responsive VaR is higher in crises. If it drives capital or limits, it can force selling at the worst time. This notebook does not measure that effect.
"""),
]

S[18] = [
    M("""
**Who does this work.** Market risk analysts in the second line of defence run backtests and write the model performance note. Model validation
repeats them independently. The committee decides.

**A usable note for the committee.**

1. State the model and the period tested.
2. State the exception rate in calm and in stress, with the count of days, as in the table above.
3. State what the responsive alternative would have done, including its cost in calm periods.
4. State the limits (above) in two lines.
5. Ask for a decision: keep, add an overlay, or move to the responsive model, with a review date.

**Typical actions when a model fails in stress.** Add a stressed period to the calibration window. Run both models and use the larger VaR. Lower the limit
usage trigger. Document the decision and the owner. None of these is recommended here, because the evidence in this notebook covers two assets only.
"""),
]

S[19] = [
    M("""
1. Add a third model, a 250 day window with an exponentially weighted historical simulation, and test H2 for it.
2. Replace the calendar windows by a rule based on realised volatility (for example the top decile of 20 day volatility) and repeat. Does H1 survive?
3. Use blocks of 20 days to bootstrap the pooled crisis exception rate and compare the interval with the exact one.
4. Add the 2020 negative oil price day by using price differences instead of returns for that day. How large is the loss compared with the VaR?
5. Run the test on a currency pair that is not in the basket. What changes?
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "12_end_to_end_banking_projects/var_crisis_research",
        "title": "Research Simulation: Does a Calm Period VaR Survive a Crisis",
        "family": "End to End Banking Projects",
        "level": "Applied",
        "dataset": "wti_spot_daily and fx_daily_2000",
        "data_kind": "empirical",
        "status": "Validating",
        "tagline": "Hypotheses, a written decision rule and real price history from 1986, to test whether a 500 day VaR fails when it matters.",
        "refs": ["kupiec1995", "christoffersen1998", "bcbs_d457"],
        "research_note": (
            "Kupiec (1995) and Christoffersen (1998) supply the tests. The Basel market risk standard is the supervisory setting in which exception counts matter. "
            "The module does not reproduce a published experiment. It poses its own question on public data and reports the answer with its limits."
        ),
        "learn": [
            "Turn a risk committee worry into hypotheses and a decision rule",
            "Handle real data problems, such as a negative price, in the open",
            "Compare a slow and a responsive VaR on the same days",
            "Test whether a conclusion survives other settings",
            "Write a finding with its limits",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
