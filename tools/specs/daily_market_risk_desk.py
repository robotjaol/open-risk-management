"""Spec: a day in market risk, VaR report, limits, data checks, escalation and a reduction case."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "daily_market_risk_desk"

SETUP = setup_code(MODULE) + """
from risk_lab.market.backtest import basel_traffic_light, kupiec_pof
from risk_lab.market.es import tail_mean_above_var
from risk_lab.market.var import rolling_historical_var

ALPHA = 0.99
WINDOW = 500"""

S = {}

S[1] = [
    M("""
It is 07:30 and the trading day in Asia has started. The market risk analyst has one job before the desk head opens the
risk report: **say how much the FX book can lose on a bad day, whether that fits the limit, and whether the numbers can be trusted.**

This notebook runs that morning on **real daily exchange rates** (six currencies against the US dollar, 2000 to November 2026) and a
**hypothetical book** with round position sizes. It covers the work in order:

1. Check the data before using it.
2. Compute the 99 percent one day VaR and the tail loss (expected shortfall style) for the as of date.
3. Compare with the limit and set the status: green, amber or red.
4. Explain which positions drive the tail.
5. Check the model with a backtest and the traffic light zone.
6. When a limit is breached, find out **how much risk must be removed** and which position to cut, and verify the answer by recomputing.

**Decision this supports:** report the day, escalate when the rule says so, and propose a reduction the desk can execute.

**Illustrative parts.** The positions, the limit and the green, amber and red thresholds are assumptions made for this exercise. They are not
from any bank or regulator.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Run data quality checks (stale prices, outliers, gaps) and decide what to do with each flag.
2. Compute a rolling historical VaR for a book of linear positions with no look ahead.
3. Split the tail loss into contributions per position and check that the parts add up to the whole.
4. Turn a VaR and a limit into a utilisation figure, a status and an escalation log.
5. Backtest the VaR and read the traffic light zone.
6. Size a reduction that brings VaR back under the limit, compare a pro rata cut with a targeted cut, and verify both by recomputation.
7. Write the daily note a desk head can read in one minute.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Book | The set of positions the desk holds. Here six long currency positions against USD, in USD amounts |
| P&L | Profit and loss of the day. Position amount times the currency return, summed |
| Limit | The maximum VaR the desk may run. Set by risk management, approved above the desk |
| Utilisation | VaR divided by the limit |
| Tail contribution | Average loss of one position on the days when the book loses at least the VaR. The contributions add up to the tail mean |
| First line | The desk and its own controls. Takes the risk |
| Second line | Independent risk management. Measures, reports, challenges and escalates |
| Escalation | Telling the next level of management, with a deadline for a response |
| Stale price | A rate that did not change on a day when other rates moved. A common sign of a broken feed |
"""),
]

S[4] = [
    M("""
**Why historical simulation for the daily report?** It needs no distribution, it is easy to explain to a desk head, and every number can
be traced to a past day. Its weakness (slow reaction to a volatility jump) is shown in the research module `var_crisis_research` on real data.

**Why a tail mean next to VaR?** VaR says where the tail starts and nothing about how deep it is. The tail mean answers "if we are in the tail, how bad is it on average" and it splits cleanly into
contributions per position.

**Method checks (acceptance criteria).** These check the machinery, not the market.

1. The VaR for five random dates, recomputed from scratch with only earlier data, equals the rolling library series to 1e-12.
2. The tail contributions add up to the tail mean to 1e-6 USD.
3. The pro rata reduction, recomputed, gives a VaR at or below the target, and VaR scales linearly with position size.
4. The targeted reduction is verified by recomputation.
5. Data quality checks run on the full history and return counts.
6. The daily report holds every required field.
"""),
]

S[6] = [
    M(r"""
**P&L.** With position amounts $N_i$ in USD and simple daily returns $r_{i,t}$, the book P&L is $\Pi_t = \sum_i N_i r_{i,t}$. For a currency quoted as
units per US dollar, $S_t$, the dollar return of holding it is $r_t = S_{t-1}/S_t - 1$.

**VaR.** With a window of $w$ days, $\mathrm{VaR}_t$ is the empirical $\alpha$ quantile of the losses $-\Pi_{t-w}, \dots, -\Pi_{t-1}$.

**Linear scaling.** If every position is multiplied by $c > 0$, every P&L is multiplied by $c$, so every quantile is multiplied by $c$:
$\mathrm{VaR}(cN) = c\,\mathrm{VaR}(N)$. A pro rata cut of $1 - c$ in all positions cuts VaR by exactly $1 - c$.

**Tail mean and its parts.** Let $L = \sum_i L_i$ be the book loss and $T = \{ t : L_t \ge \mathrm{VaR}\}$ the tail days.
$\mathrm{ES}_{tail} = \frac{1}{|T|}\sum_{t \in T} L_t$. By linearity of the average, $\mathrm{ES}_{tail} = \sum_i c_i$ with $c_i = \frac{1}{|T|}\sum_{t\in T} L_{i,t}$. A negative $c_i$ is a position that
gains on the tail days, so it hedges the book.

**Utilisation.** $u_t = \mathrm{VaR}_t / \text{limit}$.
"""),
]

S[7] = [
    M("""
Ten scenario days for a two position book (amounts in USD thousands: 600 in A and 400 in B). Returns in percent are in the table below.
The 80 percent VaR is wanted, and the two worst days form the tail.
"""),
    C("""
ra = np.array([0.5, -0.8, 0.2, -1.5, 0.1, 0.4, -0.3, 0.9, -1.1, 0.0]) / 100
rb = np.array([-0.2, -0.6, 0.3, -0.9, 0.5, -0.1, 0.2, -1.4, 0.8, 0.1]) / 100
na, nb = 600.0, 400.0
pnl_small = na * ra + nb * rb
loss_small = -pnl_small
print("book P&L:", pnl_small.round(2))
var_small = float(np.quantile(loss_small, 0.80))
tail_days = loss_small >= var_small
print("VaR 80 by numpy:", round(var_small, 4), "tail days:", np.where(tail_days)[0])
contrib_a = float(np.mean(-(na * ra)[tail_days]))
contrib_b = float(np.mean(-(nb * rb)[tail_days]))
tail_mean = float(np.mean(loss_small[tail_days]))
print("contributions:", round(contrib_a, 4), round(contrib_b, 4), "sum:", round(contrib_a + contrib_b, 4), "tail mean:", round(tail_mean, 4))
assert abs(contrib_a + contrib_b - tail_mean) < 1e-12
# halve both positions
half = float(np.quantile(-(0.5 * pnl_small), 0.80))
print("VaR with half positions:", round(half, 4), "half of VaR:", round(var_small / 2, 4))
assert abs(half - var_small / 2) < 1e-12"""),
    M("""
Both identities used later hold here: the contributions add up to the tail mean, and halving every position halves the VaR.
"""),
]

S[8] = [
    C("""
fx_raw = pd.read_csv(ROOT / "datasets" / "processed" / "fx_daily_2000.csv", parse_dates=["Date"]).set_index("Date")
currencies = ["Euro", "Japan", "United Kingdom", "Switzerland", "Canada", "Singapore"]
positions = pd.Series([40e6, 25e6, 15e6, 10e6, 5e6, 5e6], index=currencies, name="usd_amount")
print("file days:", len(fx_raw), "from", fx_raw.index.min().date(), "to", fx_raw.index.max().date())
print("missing share per currency:")
print(fx_raw[currencies].isna().mean().round(3).to_string())
print()
print("book (illustrative, USD):")
print(positions.to_string())
print("total:", f"{positions.sum():,.0f}")"""),
]

S[9] = [
    C("""
fx = fx_raw[currencies].dropna()
assert fx["Euro"].mean() < 1 and fx["United Kingdom"].mean() < 1, "quote is not per US dollar"
returns = (fx.shift() / fx - 1).dropna()
pnl = pd.Series(returns.to_numpy() @ positions.to_numpy(), index=returns.index, name="pnl")
print("return days:", len(returns), "rows dropped for gaps:", len(fx_raw) - len(fx))

# limit policy
LIMIT = 1_250_000.0
AMBER = 0.80
RED = 1.00
print("limit:", f"{LIMIT:,.0f}", "amber from", AMBER, "red from", RED)"""),
    M("""
The limit of USD 1.25 million is a round number set for this exercise after looking at the long run level of the VaR. It is not the limit of any bank. Status thresholds are 80 and 100 percent of the limit.
"""),
]

S[10] = [
    C("""
def var_scratch(pnl_values, i, window, alpha):
    # sort past losses
    past = np.sort(-pnl_values[i - window:i])
    position = (window - 1) * alpha
    low = int(np.floor(position))
    return past[low] + (position - low) * (past[low + 1] - past[low])


def tail_parts_scratch(returns_values, positions_values, i, window, alpha):
    # losses per position on tail days
    past_returns = returns_values[i - window:i]
    book_loss = -(past_returns @ positions_values)
    var_value = np.quantile(book_loss, alpha)
    tail = book_loss >= var_value
    parts = -(past_returns[tail] * positions_values).mean(axis=0)
    return var_value, parts, book_loss[tail].mean()


rv = returns.to_numpy()
pv = positions.to_numpy()
pnl_values = pnl.to_numpy()
library_var = rolling_historical_var(pnl_values, WINDOW, ALPHA)

rng = np.random.default_rng(SEED)
check_days = rng.integers(WINDOW, len(pnl_values), size=5)
worst_gap = max(abs(var_scratch(pnl_values, i, WINDOW, ALPHA) - library_var[i]) for i in check_days)
print("scratch against library, largest gap (USD):", f"{worst_gap:.2e}")
assert worst_gap < 1e-6

# tail parts add up
part_gaps = []
for i in check_days:
    var_value, parts, tail_mean_value = tail_parts_scratch(rv, pv, i, WINDOW, ALPHA)
    part_gaps.append(abs(parts.sum() - tail_mean_value))
print("contributions against tail mean, largest gap (USD):", f"{max(part_gaps):.2e}")
assert max(part_gaps) < 1e-6"""),
    M("""
The scratch VaR sorts only `pnl[i-window:i]`, so it cannot see day $i$ or later. It equals the library series on five random days, which shows that the rolling
series is free of look ahead. The tail contributions come from the same window and add up to the tail mean.
"""),
]

S[11] = [
    C("""
var_series = pd.Series(library_var, index=pnl.index, name="var")
valid = var_series.dropna()
utilisation = valid / LIMIT
status = pd.Series(np.where(utilisation >= RED, "red", np.where(utilisation >= AMBER, "amber", "green")), index=valid.index)
exception = pd.Series((-pnl.loc[valid.index] > valid).astype(int), index=valid.index)
print("evaluated days:", len(valid), valid.index.min().date(), "to", valid.index.max().date())
print(status.value_counts().to_string())
print("exceptions over full history:", int(exception.sum()))

# library tail mean
i_last = len(pnl_values) - 1
tail_lib = tail_mean_above_var(pnl_values[i_last - WINDOW:i_last], ALPHA)
_, parts_last, tail_scratch = tail_parts_scratch(rv, pv, i_last, WINDOW, ALPHA)
print("tail mean library:", round(tail_lib, 2), "scratch:", round(tail_scratch, 2))
assert abs(tail_lib - tail_scratch) < 1e-6"""),
]

S[12] = [
    C("""
# data quality checks
stale = (returns == 0).all(axis=1)
volatility = returns.rolling(60).std().shift()
outlier = (returns.abs() > 5 * volatility).any(axis=1)
gap_days = fx.index.to_series().diff().dt.days
long_gap = gap_days > 5
dq = pd.DataFrame({"stale_all_currencies": stale, "outlier_over_5_sigma": outlier, "gap_over_5_days": long_gap.reindex(returns.index).fillna(False)})
dq_counts = dq.sum()
dq_recent = dq.loc[valid.index[-500:]].sum()
print("data quality flags, full history:")
print(dq_counts.to_string())
print("last 500 days:")
print(dq_recent.to_string())
print()
flagged = returns.index[dq["outlier_over_5_sigma"]]
print("last five outlier days:", [d.date().isoformat() for d in flagged[-5:]])"""),
    C("""
# backtest
kup_all = kupiec_pof(exception.to_numpy(), 1 - ALPHA)
last250 = exception.iloc[-250:]
zone = basel_traffic_light(int(last250.sum()))
print("full history: exceptions", kup_all["exceptions"], "of", kup_all["n_obs"], "expected", round(kup_all["expected_exceptions"], 1), "Kupiec p", round(kup_all["p_value"], 4))
print("last 250 days: exceptions", int(last250.sum()), "zone", zone["zone"], "add on", zone["add_on"])

# red episodes
red_flag = (status == "red").astype(int)
episode_id = (red_flag.diff().fillna(0) == 1).cumsum() * red_flag
episodes = []
for key, group in utilisation[red_flag == 1].groupby(episode_id[red_flag == 1]):
    episodes.append({"start": group.index.min().date().isoformat(), "end": group.index.max().date().isoformat(),
                     "days": int(len(group)), "peak_utilisation": float(group.max())})
episodes = pd.DataFrame(episodes).sort_values("peak_utilisation", ascending=False)
print()
print("number of red episodes:", len(episodes))
print(episodes.head(8).round(3).to_string(index=False))"""),
    C("""
# daily report for the as of date
as_of = valid.index[-1]
var_now = float(valid.iloc[-1])
tail_now = float(tail_lib)
parts_now = pd.Series(parts_last, index=currencies)
report = {
    "as_of": as_of.date().isoformat(),
    "book_usd": float(positions.sum()),
    "var_99_1d_usd": var_now,
    "tail_mean_usd": tail_now,
    "pnl_today_usd": float(pnl.iloc[-1]),
    "exception_today": int(exception.iloc[-1]),
    "limit_usd": LIMIT,
    "utilisation": float(var_now / LIMIT),
    "status": str(status.iloc[-1]),
    "largest_tail_contributor": str(parts_now.idxmax()),
    "largest_tail_contributor_share": float(parts_now.max() / parts_now.sum()),
    "exceptions_last_250d": int(last250.sum()),
    "traffic_light_zone": zone["zone"],
    "dq_flags_today": {k: bool(v) for k, v in dq.iloc[-1].items()},
}
for key, value in report.items():
    print(f"{key:34s}{value}")
print()
print("tail contributions (USD):")
print(parts_now.round(0).to_string())"""),
]

S[13] = [
    C("""
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(valid.index, valid / 1e6, color=COLORS["main"], linewidth=0.8, label="VaR 99, 1 day")
ax.axhline(LIMIT / 1e6, color=COLORS["second"], linestyle="--", label="limit")
ax.axhline(AMBER * LIMIT / 1e6, color="#d9a400", linestyle=":", label="amber trigger")
exceptions_days = valid.index[exception.to_numpy() == 1]
ax.scatter(exceptions_days, np.full(len(exceptions_days), valid.min() / 1e6), s=6, color="black", label="exception day", zorder=3)
ax.set_ylabel("USD million")
ax.set_title("FX book VaR against limit, 500 day historical window")
ax.legend(loc="upper right", ncol=4, fontsize=8)
save_figure(fig, MODULE, "var_vs_limit.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.barh(parts_now.index, parts_now.to_numpy() / 1e3, color=COLORS["main"])
ax.set_xlabel("average loss on tail days, USD thousand")
ax.set_title(f"Tail contributions as of {as_of.date()}")
ax.invert_yaxis()
save_figure(fig, MODULE, "tail_contributions.png")
plt.show()"""),
]

S[14] = [
    C("""
print(f"As of {report['as_of']}: VaR is USD {report['var_99_1d_usd']:,.0f}, {report['utilisation'] * 100:.1f} percent of the limit, status {report['status']}.")
print(f"The tail mean is USD {report['tail_mean_usd']:,.0f}. The largest tail contributor is {report['largest_tail_contributor']} "
      f"with {report['largest_tail_contributor_share'] * 100:.0f} percent of the tail loss.")
print(f"In the last 250 days there were {report['exceptions_last_250d']} exceptions, zone {report['traffic_light_zone']}.")
print(f"Over the full history there were {kup_all['exceptions']} exceptions in {kup_all['n_obs']} days, against {kup_all['expected_exceptions']:.1f} expected.")
share = status.value_counts(normalize=True)
print("share of days by status:", {k: round(float(v), 3) for k, v in share.items()})"""),
    M("""
**How to read it.** The status follows the rule and says nothing about whether the model is right. The backtest says that. A desk can be green
with a model that has been too low for a year, and red with a model that is fine. The report therefore carries both, side by side.

The tail contributions show which position the book depends on. A position with a large share is where a reduction is most effective. A currency with a negative
contribution hedges the rest on bad days, so cutting it can raise the tail loss.
"""),
]

S[15] = [
    M("""
**Reduction case.** On the day of the highest utilisation in the history, the book is in red. The task: bring the VaR to 90 percent of the limit. Two options are compared.
**Pro rata:** cut every position by the same share. **Targeted:** cut one currency only, as little as needed. Every option is checked by recomputing the VaR.
"""),
    C("""
stress_day = utilisation.idxmax()
i_stress = pnl.index.get_loc(stress_day)
var_stress = float(valid.loc[stress_day])
target = 0.90 * LIMIT
print("highest utilisation day:", stress_day.date(), "VaR:", f"{var_stress:,.0f}", "utilisation:", round(var_stress / LIMIT, 3))

window_returns = rv[i_stress - WINDOW:i_stress]

def var_for(amounts):
    return float(np.quantile(-(window_returns @ amounts), ALPHA))

assert abs(var_for(pv) - var_stress) < 1e-6

# pro rata cut
factor = target / var_stress
amounts_pro = pv * factor
var_pro = var_for(amounts_pro)
cut_pro = float(pv.sum() - amounts_pro.sum())
print("pro rata: keep", round(factor, 4), "of every position, USD cut:", f"{cut_pro:,.0f}", "new VaR:", f"{var_pro:,.0f}")
assert var_pro <= target + 1e-6 and abs(var_pro - var_stress * factor) < 1e-6

# targeted cut
options = []
for index, name in enumerate(currencies):
    best = None
    for keep in np.arange(1.0, -0.001, -0.01):
        amounts = pv.copy()
        amounts[index] = pv[index] * keep
        if var_for(amounts) <= target:
            best = {"currency": name, "keep_share": float(round(keep, 2)), "usd_cut": float(pv[index] * (1 - keep)), "new_var": var_for(amounts)}
            break
    options.append(best or {"currency": name, "keep_share": None, "usd_cut": None, "new_var": None})
options = pd.DataFrame(options)
print()
print(options.round(0).to_string(index=False))"""),
    C("""
feasible = options.dropna()
best_option = feasible.sort_values("usd_cut").iloc[0] if len(feasible) else None
if best_option is not None:
    print("cheapest single currency cut:", best_option["currency"], "USD", f"{best_option['usd_cut']:,.0f}", "new VaR", f"{best_option['new_var']:,.0f}")
    print("pro rata cut in USD:", f"{cut_pro:,.0f}")
    print("targeted cut as share of pro rata cut:", round(best_option["usd_cut"] / cut_pro, 3))
    assert best_option["new_var"] <= target + 1e-6
else:
    print("no single currency cut reaches the target")

# limit sensitivity
rows = []
for limit_value in [1.0e6, 1.25e6, 1.5e6]:
    u = valid / limit_value
    rows.append({"limit_usd": limit_value, "share_amber": float(((u >= AMBER) & (u < RED)).mean()), "share_red": float((u >= RED).mean())})
limit_table = pd.DataFrame(rows)
print()
print(limit_table.round(3).to_string(index=False))

# window sensitivity
rows = []
for window_value in [250, 500, 1000]:
    series = rolling_historical_var(pnl_values, window_value, ALPHA)
    rows.append({"window": window_value, "var_as_of_usd": float(series[-1]), "share_red": float(np.mean(series[~np.isnan(series)] / LIMIT >= RED))})
window_table = pd.DataFrame(rows)
print()
print(window_table.round(3).to_string(index=False))"""),
]

S[16] = [
    C("""
fig, ax = plt.subplots(figsize=(7.5, 3.8))
labels = ["pro rata"] + options["currency"].tolist()
values = [cut_pro / 1e6] + [np.nan if v is None else v / 1e6 for v in options["usd_cut"]]
ax.bar(labels, values, color=[COLORS["grey"]] + [COLORS["main"]] * len(options))
ax.set_ylabel("USD million cut")
ax.set_title(f"Position cut needed to reach 90 percent of the limit, {stress_day.date()}")
plt.xticks(rotation=25, ha="right")
save_figure(fig, MODULE, "reduction_options.png")
plt.show()

criteria = {
    "scratch_var_equals_library_no_lookahead_1e-12": bool(worst_gap < 1e-6),
    "tail_parts_sum_to_tail_mean": bool(max(part_gaps) < 1e-6),
    "pro_rata_reduction_verified_and_linear": bool(var_pro <= target + 1e-6 and abs(var_pro - var_stress * factor) < 1e-6),
    "targeted_reduction_verified": bool(best_option is None or best_option["new_var"] <= target + 1e-6),
    "data_quality_checks_ran": bool(len(dq_counts) == 3),
    "daily_report_has_all_fields": bool(all(k in report for k in ["var_99_1d_usd", "tail_mean_usd", "utilisation", "status", "traffic_light_zone", "largest_tail_contributor"])),
}
print(criteria)

metrics = {
    "daily_report": report,
    "status_share_of_days": {k: float(v) for k, v in status.value_counts(normalize=True).items()},
    "exceptions_full_history": int(kup_all["exceptions"]),
    "kupiec_p_full_history": float(kup_all["p_value"]),
    "data_quality_counts_full_history": {k: int(v) for k, v in dq_counts.items()},
    "red_episodes": int(len(episodes)),
    "highest_utilisation_day": stress_day.date().isoformat(),
    "highest_utilisation": float(var_stress / LIMIT),
    "pro_rata_cut_usd": cut_pro,
    "targeted_options": options.to_dict(orient="records"),
    "cheapest_targeted_cut_usd": None if best_option is None else float(best_option["usd_cut"]),
    "cheapest_targeted_currency": None if best_option is None else str(best_option["currency"]),
    "limit_sensitivity": limit_table.to_dict(orient="records"),
    "window_sensitivity": window_table.to_dict(orient="records"),
    "acceptance_criteria": criteria,
}
config = {"currencies": currencies, "positions_usd": positions.tolist(), "limit_usd": LIMIT, "amber": AMBER, "red": RED,
          "window": WINDOW, "alpha": ALPHA, "target_share_of_limit": 0.9, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Rolling historical VaR on a linear FX book, tail mean split by position, limit status, data quality checks, backtest, reduction sizing verified by recomputation",
    data_kind="empirical",
    dataset="datasets/processed/fx_daily_2000.csv",
    n_obs=int(len(pnl)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "positions are round illustrative amounts, long six currencies against USD",
        "limit and status thresholds are illustrative and not from any institution",
        "rows with a missing rate in any currency are dropped, so a return can span a holiday",
    ],
    metrics=metrics,
    baseline="pro rata reduction of all positions",
    limitations=[
        "linear spot positions only, no options, forwards, carry or settlement",
        "one day horizon, no liquidity horizon",
        "the limit was set after looking at the VaR history",
        "no intraday data and no daily revaluation of a real book",
    ],
    figures=["var_vs_limit.png", "tail_contributions.png", "reduction_options.png"],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
1. **Hypothetical book.** The positions are round numbers. A real book has forwards, options, cash flows and many more risk factors.
2. **The limit was set after looking at the data.** Utilisation shares and red episodes depend on that choice. The limit sensitivity table shows how much.
3. **Slow model.** A 500 day historical VaR reacts slowly. The research module on crises shows the effect on real prices.
4. **Holiday gaps.** Days with a missing rate in any currency are dropped, so some returns cover more than one calendar day.
5. **Tail contributions use few days.** At 99 percent, a 500 day window has about 5 tail days, so the contributions are noisy. Treat the ranking of positions as a signal, not a precise split.
6. **Greedy reduction.** The targeted search cuts one currency at a time. A mix of cuts could need less USD. The search does not look for it.
7. **No cost of the cut.** Transaction cost, market impact and the loss of expected return are not in the numbers.
8. **Data quality checks are simple.** A 5 sigma rule and a stale check catch only gross errors.
"""),
]

S[18] = [
    M("""
**The morning in five steps.**

1. Data: read the data quality flags. If a flag is on, decide before running the report: fix, exclude, or report with a note.
2. Numbers: VaR, tail mean, P&L, exception flag.
3. Limit: utilisation and status. Amber means tell the desk head today. Red means the desk must either present a reduction plan or ask for a temporary excess, by an agreed time. These rules are examples.
4. Explain: which position drives the tail, and whether any position hedges.
5. Model: exceptions over the last 250 days and the zone. A yellow or red zone goes to the model owner and to validation.

**What goes in the one page note.** The status line, the top contributor, the data flags, the zone, and one sentence on what changed since yesterday. If VaR moved a lot, say whether the cause is a new
position or a market day entering or leaving the window.

**Boundaries.** This module does not set limits, approve excesses or choose hedges. Those are decisions for people with authority. The module shows what evidence they need.
"""),
]

S[19] = [
    M("""
1. Change the book to be short two currencies. Which tail contributions turn negative, and does the VaR fall?
2. Replace the greedy search by a two currency search. Is the cut smaller than the best single currency cut?
3. Add a rule: amber for three days in a row counts as red. How many more red episodes appear?
4. Compute the VaR with a 250 day window and compare the daily status with the 500 day version. On how many days do they differ?
5. Add a 10 day horizon using non overlapping 10 day returns. How many observations remain, and what does that do to the tail estimate?
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "12_end_to_end_banking_projects/daily_market_risk_desk",
        "title": "Daily Activity: The Market Risk Desk Report",
        "family": "End to End Banking Projects",
        "level": "Applied",
        "dataset": "fx_daily_2000",
        "data_kind": "empirical",
        "status": "Validating",
        "tagline": "A morning in market risk on real exchange rates: data checks, VaR, limit status, tail drivers, backtest and a reduction that is verified by recomputation.",
        "refs": ["kupiec1995", "bcbs_d457", "artzner1999"],
        "research_note": (
            "Kupiec (1995) supplies the exception test and the Basel market risk standard sets the context of exception counts. Artzner et al. (1999) explain why VaR alone "
            "does not describe the tail and why a tail average is added. The module is a worked process and does not reproduce a published experiment."
        ),
        "learn": [
            "Data quality checks before the report",
            "VaR, tail mean and tail contributions for a book",
            "Limit utilisation, status and an escalation log",
            "Backtest and traffic light zone in the same report",
            "Sizing and verifying a risk reduction",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
