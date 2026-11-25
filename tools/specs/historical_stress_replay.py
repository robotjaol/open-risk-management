"""Spec: stress testing by replaying history on today's portfolio, plus a reverse stress test."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "historical_stress_replay"

SETUP = setup_code(MODULE) + """
from risk_lab.finance.bonds import bond_price, convexity, modified_duration
from risk_lab.market.backtest import kupiec_pof
from risk_lab.market.var import rolling_historical_var

W_EQUITY = 0.6
W_BOND = 0.4
VALUE = 100e6
LOSS_APPETITE = 0.20
VAR_WINDOW = 240
ALPHA = 0.99"""

S = {}

S[1] = [
    M("""
A VaR number describes an ordinary bad day. A bank also has to answer a different question: **what happens in a month or a year that is not ordinary?**
That is **stress testing**. Two forms are used every day in risk teams:

* **Historical scenario replay.** Take the worst periods in recorded history and apply their market moves to the portfolio held today.
* **Reverse stress test.** Start from the loss the bank cannot accept and work backwards to the market moves that would cause it.

This notebook does both for a USD 100 million portfolio of 60 percent US equities and 40 percent 10 year government bonds, on **real monthly data from 1871**
(Shiller's S&P 500 series with dividends and the 10 year yield). It also checks something that is easy to forget: **how badly a VaR model, built on 20 years of history, understated the worst months it later met.**

**Decision this supports:** a stress loss table and a reverse stress frontier that a risk committee can compare with its stated loss appetite.

**Assumption to read first.** The loss appetite of 20 percent of portfolio value in a month is an illustrative number for this exercise, not a rule or an institution's limit.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Build monthly equity and bond returns from raw price, dividend and yield data, and check the bond approximation against full repricing.
2. Find the worst non overlapping periods in a long history by a stated rule.
3. Measure how many times a rolling 99 percent VaR was exceeded, and how large the worst month was relative to the VaR in force.
4. Apply historical equity and rate moves to today's bond (today's yield and duration) and report a stress loss in USD.
5. Solve a reverse stress test: which pairs of equity fall and rate rise cause a loss of 20 percent, and check the answer by recomputation.
6. Say what a history based stress test cannot tell you.
"""),
]

S[3] = [
    M("""
| Term | Meaning |
|---|---|
| Scenario replay | Applying the market moves of a past period to today's positions |
| Reverse stress test | Finding the scenarios that produce a given unacceptable loss |
| Loss appetite | The loss level management has said it cannot accept. Here 20 percent in a month, illustrative |
| Total return | Price change plus income. Equity income is the dividend, bond income is the coupon accrual |
| Constant maturity bond | A bond whose maturity is kept at 10 years each month, which is how a yield index is used as a price series |
| Frontier | The set of equity and rate moves that give exactly the loss appetite |
| Exception | A month where the loss was larger than the VaR forecast |
"""),
]

S[4] = [
    M("""
**Why replay history?** It is simple to explain, uses moves that actually happened, and needs no model of the joint distribution. Its limit is that history contains only what happened. The reverse test
supplies the other view: it asks what would have to happen.

**Method checks (acceptance criteria).** These check the method, not the market.

1. The monthly bond return approximation (duration and convexity) is within 0.1 percent of full repricing in the 99th percentile of months. The 0.1 percent tolerance is the one used in the duration module.
2. The equity total return for one month matches a hand calculation.
3. The rolling VaR for five random months, recomputed from scratch with earlier months only, equals the library to 1e-12.
4. Every point on the reverse stress frontier gives a portfolio loss of exactly the appetite when recomputed.
5. The selected worst 12 month windows start at least 12 months apart.
6. The rows excluded from the source file all lie after the last valid month, and the valid months are consecutive.
"""),
]

S[6] = [
    M(r"""
**Equity.** With index level $P_t$ and annual dividend rate $D_t$, the monthly total return is $r^E_{t+1} = (P_{t+1} + D_{t+1}/12)/P_t - 1$.

**Bond.** For a par 10 year bond at yield $y_t$ with modified duration $D_t$ and convexity $C_t$ (computed from the cash flows), a yield change $\Delta y$ gives

$$r^B_{t+1} \approx \frac{y_t}{12} - D_t\,\Delta y + \tfrac12 C_t\,\Delta y^2$$

The first term is one month of coupon income. Full repricing instead computes the price of the same coupon at the new yield: $r^B = \dfrac{P(y_t + \Delta y; c = y_t)}{P(y_t; c = y_t)} - 1 + \dfrac{y_t}{12}$.

**Portfolio.** $r_t = 0.6\,r^E_t + 0.4\,r^B_t$, rebalanced monthly.

**Replay on today's portfolio.** For a historical equity return $R^E$ over a window and a yield change $\Delta y$ over the same window, the stress return of the portfolio held today is
$0.6\,R^E + 0.4\left[\frac{P(y_0 + \Delta y; c = y_0)}{P(y_0; c = y_0)} - 1 + y_0 \cdot h\right]$, with $h$ the window length in years and $y_0$ today's yield.

**Reverse stress.** For a rate shock $\Delta y$, the equity return $s$ that gives portfolio return $-L$ is
$s = \dfrac{-L - 0.4\,b(\Delta y)}{0.6}$ where $b(\Delta y)$ is the bond return for that shock.
"""),
]

S[7] = [
    M("""
A one month check by hand. Equity index 100 to 98, annual dividend 3.0. Yield 4.00 percent to 4.50 percent on a 10 year par bond. Weights 60 and 40.
"""),
    C("""
p0, p1, div = 100.0, 98.0, 3.0
equity_return = (p1 + div / 12) / p0 - 1
y0, y1 = 0.04, 0.045
dur = modified_duration(y0, 100, y0, 10, 2)
conv = convexity(y0, 100, y0, 10, 2)
approx = y0 / 12 - dur * (y1 - y0) + 0.5 * conv * (y1 - y0) ** 2
full = bond_price(y1, 100, y0, 10, 2) / bond_price(y0, 100, y0, 10, 2) - 1 + y0 / 12
portfolio = W_EQUITY * equity_return + W_BOND * full
print("equity return:", round(equity_return, 5))
print("bond return, approximation:", round(approx, 5), "full repricing:", round(full, 5))
print("portfolio return:", round(portfolio, 5), "loss on USD 100 million:", f"{-portfolio * VALUE:,.0f}")"""),
    M("""
The approximation and full repricing agree to about four decimals for a 50 basis point move. The portfolio loses about 2.5 percent in this month, USD 2.5 million on USD 100 million. The bond causes most of it, because a 50 basis point rise on a 10 year bond costs about 3.7 percent.
"""),
]

S[8] = [
    C("""
raw = pd.read_csv(ROOT / "datasets" / "raw" / "sp500_shiller_monthly.csv", parse_dates=["Date"]).set_index("Date")
print("rows:", len(raw), raw.index.min().date(), "to", raw.index.max().date())
usable = (raw["Dividend"] > 0) & (raw["Long Interest Rate"] > 0)
print("rows with a positive dividend and yield:", int(usable.sum()), "last:", raw.index[usable].max().date())
print("rows with zero dividend or zero yield:", int((~usable).sum()), "from", raw.index[~usable].min().date())
print()
print(raw.loc["2023-05-01":"2023-11-01", ["SP500", "Dividend", "Long Interest Rate"]].round(2).to_string())"""),
    M("""
The source file ends with months where the price is present and every other field is **zero**. Using those rows would give a zero dividend and a zero yield, which would
silently produce wrong returns. They are excluded and counted.
"""),
]

S[9] = [
    C("""
data = raw[usable].copy()
months_gap = data.index.to_series().diff().dt.days.dropna()
print("valid months:", len(data), "largest gap in days:", int(months_gap.max()))

price = data["SP500"].to_numpy()
dividend = data["Dividend"].to_numpy()
yield_rate = data["Long Interest Rate"].to_numpy() / 100
dates = data.index[1:]

equity = (price[1:] + dividend[1:] / 12) / price[:-1] - 1
delta_y = np.diff(yield_rate)
duration_t = np.array([modified_duration(y, 100, y, 10, 2) for y in yield_rate[:-1]])
convexity_t = np.array([convexity(y, 100, y, 10, 2) for y in yield_rate[:-1]])
bond_approx = yield_rate[:-1] / 12 - duration_t * delta_y + 0.5 * convexity_t * delta_y**2
bond_full = np.array([bond_price(yield_rate[i + 1], 100, yield_rate[i], 10, 2) / bond_price(yield_rate[i], 100, yield_rate[i], 10, 2) - 1
                      for i in range(len(delta_y))]) + yield_rate[:-1] / 12
approx_error = np.abs(bond_approx - bond_full)
print("bond approximation error, percentiles 50, 99, 100:", np.percentile(approx_error, [50, 99, 100]).round(6))

monthly = pd.DataFrame({"equity": equity, "bond": bond_full, "delta_y": delta_y, "yield": yield_rate[:-1]}, index=dates)
monthly["portfolio"] = W_EQUITY * monthly["equity"] + W_BOND * monthly["bond"]
print(monthly[["equity", "bond", "portfolio"]].describe().loc[["count", "mean", "std", "min", "max"]].round(4).to_string())"""),
    M("""
Full repricing is used for the series because it is exact for a constant maturity par bond. The approximation is kept only to show how good it is. The roll down effect (the bond getting one month shorter) is ignored, which is a standard simplification for a yield index.
"""),
]

S[10] = [
    C("""
# hand check one month
i = 100
by_hand = (price[i + 1] + dividend[i + 1] / 12) / price[i] - 1
print("equity return by hand:", round(by_hand, 8), "in series:", round(float(equity[i]), 8))
assert abs(by_hand - equity[i]) < 1e-15


def var_scratch(x, i, window, alpha):
    # sort past losses
    past = np.sort(-x[i - window:i])
    position = (window - 1) * alpha
    low = int(np.floor(position))
    return past[low] + (position - low) * (past[low + 1] - past[low])


port = monthly["portfolio"].to_numpy()
library_var = rolling_historical_var(port, VAR_WINDOW, ALPHA)
rng = np.random.default_rng(SEED)
check = rng.integers(VAR_WINDOW, len(port), size=5)
worst_gap = max(abs(var_scratch(port, k, VAR_WINDOW, ALPHA) - library_var[k]) for k in check)
print("scratch VaR against library, largest gap:", f"{worst_gap:.2e}")
assert worst_gap < 1e-12"""),
]

S[11] = [
    C("""
var_series = pd.Series(library_var, index=monthly.index)
valid_var = var_series.dropna()
loss = -monthly["portfolio"].loc[valid_var.index]
exceptions = (loss > valid_var).astype(int)
kup = kupiec_pof(exceptions.to_numpy(), 1 - ALPHA)
print("months evaluated:", kup["n_obs"], "from", valid_var.index.min().date(), "to", valid_var.index.max().date())
print("exceptions:", kup["exceptions"], "expected:", round(kup["expected_exceptions"], 1), "Kupiec p:", round(kup["p_value"], 4))
print("mean 99 percent VaR in force (percent of value):", round(float(valid_var.mean()) * 100, 2))
print("largest realised monthly loss (percent):", round(float(loss.max()) * 100, 2), "in", loss.idxmax().date())
print("VaR in force that month (percent):", round(float(valid_var.loc[loss.idxmax()]) * 100, 2))"""),
]

S[12] = [
    C("""
# worst 12 month windows
cum12 = (1 + monthly["portfolio"]).rolling(12).apply(np.prod, raw=True) - 1
order = cum12.dropna().sort_values()
chosen = []
for end_date, value in order.items():
    start = end_date - pd.DateOffset(months=11)
    if all(abs((start.year - s.year) * 12 + start.month - s.month) >= 12 for s, _ in chosen):
        chosen.append((start, end_date))
    if len(chosen) == 5:
        break
starts_ok = all(abs((chosen[i][0].year - chosen[j][0].year) * 12 + chosen[i][0].month - chosen[j][0].month) >= 12
                for i in range(len(chosen)) for j in range(i))
print("worst non overlapping 12 month windows (historical portfolio):")
for start, end in chosen:
    print(" ", start.date(), "to", end.date(), "return", round(float(cum12.loc[end]) * 100, 1), "percent")"""),
    C("""
# replay on today's portfolio
y_today = float(yield_rate[-1])
print("today's yield (last valid month):", round(y_today * 100, 2), "percent at", data.index[-1].date())


def bond_return_shock(dy, years):
    reprice = bond_price(y_today + dy, 100, y_today, 10, 2) / bond_price(y_today, 100, y_today, 10, 2) - 1
    return reprice + y_today * years


def replay_return(equity_total, dy, years):
    return W_EQUITY * equity_total + W_BOND * bond_return_shock(dy, years)


replay_rows = []
for start, end in chosen:
    window = monthly.loc[start:end]
    equity_cum = float((1 + window["equity"]).prod() - 1)
    dy_window = float(window["delta_y"].sum())
    r = replay_return(equity_cum, dy_window, 1.0)
    replay_rows.append({"window": f"{start.date()} to {end.date()}", "equity_return": equity_cum, "yield_change_bp": dy_window * 1e4,
                        "portfolio_return": r, "loss_usd": -r * VALUE})
replay = pd.DataFrame(replay_rows)

# worst single months, replayed
month_rows = []
worst_months = monthly["portfolio"].nsmallest(5).index
for date in worst_months:
    row = monthly.loc[date]
    r = replay_return(row["equity"], row["delta_y"], 1 / 12)
    month_rows.append({"month": date.date().isoformat(), "equity_return": float(row["equity"]), "yield_change_bp": float(row["delta_y"] * 1e4),
                       "portfolio_return": float(r), "loss_usd": float(-r * VALUE)})
month_replay = pd.DataFrame(month_rows)
print()
print(replay.round(3).to_string(index=False))
print()
print(month_replay.round(3).to_string(index=False))"""),
    C("""
# reverse stress
shocks_bp = [-100, 0, 100, 200, 300, 400]
frontier_rows = []
for bp in shocks_bp:
    dy = bp / 1e4
    b = bond_return_shock(dy, 1 / 12)
    s = (-LOSS_APPETITE - W_BOND * b) / W_EQUITY
    check_return = W_EQUITY * s + W_BOND * b
    frontier_rows.append({"rate_shock_bp": bp, "bond_return": float(b), "equity_return_needed": float(s), "portfolio_return": float(check_return)})
frontier = pd.DataFrame(frontier_rows)
print(frontier.round(4).to_string(index=False))

# history against frontier
worst_month_loss = float(-month_replay["portfolio_return"].min())
print()
print("worst replayed month loss (percent):", round(worst_month_loss * 100, 2), "against appetite", LOSS_APPETITE * 100)
equity_min = float(monthly["equity"].min())
print("worst historical monthly equity return (percent):", round(equity_min * 100, 2), "needed with no rate move:", round(float(frontier.loc[frontier['rate_shock_bp'] == 0, 'equity_return_needed'].iloc[0]) * 100, 2))"""),
]

S[13] = [
    C("""
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.plot(frontier["rate_shock_bp"], frontier["equity_return_needed"] * 100, color=COLORS["main"], marker="o", label="loss of 20 percent")
ax.scatter(monthly["delta_y"] * 1e4, monthly["equity"] * 100, s=4, color=COLORS["grey"], alpha=0.4, label="historical months")
ax.set_xlabel("10 year yield change in a month (basis points)")
ax.set_ylabel("equity return in a month (percent)")
ax.set_xlim(-250, 450)
ax.set_title("Reverse stress frontier and 150 years of monthly moves")
ax.legend()
save_figure(fig, MODULE, "reverse_stress_frontier.png")
plt.show()"""),
    C("""
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(valid_var.index, valid_var * 100, color=COLORS["main"], linewidth=0.9, label="99 percent VaR, 240 month window")
ax.plot(loss.index, loss * 100, color=COLORS["grey"], linewidth=0.5, label="monthly loss")
ex_dates = exceptions.index[exceptions == 1]
ax.scatter(ex_dates, loss.loc[ex_dates] * 100, s=10, color=COLORS["second"], label="exception", zorder=3)
ax.set_ylabel("percent of value")
ax.set_title("Monthly VaR for a 60/40 portfolio and the months that exceeded it")
ax.legend(loc="upper left", fontsize=8)
save_figure(fig, MODULE, "monthly_var_exceptions.png")
plt.show()"""),
]

S[14] = [
    C("""
print(f"Over {kup['n_obs']} months the rolling 99 percent VaR was exceeded {kup['exceptions']} times, against {kup['expected_exceptions']:.1f} expected (Kupiec p {kup['p_value']:.3f}).")
print(f"The worst 12 month window replayed on today's portfolio loses {-replay['portfolio_return'].min() * 100:.1f} percent, USD {replay['loss_usd'].max():,.0f}.")
print(f"The worst single month replayed loses {worst_month_loss * 100:.1f} percent, against a loss appetite of {LOSS_APPETITE * 100:.0f} percent.")
no_move = float(frontier.loc[frontier['rate_shock_bp'] == 0, 'equity_return_needed'].iloc[0])
print(f"With no rate move, an equity fall of {-no_move * 100:.1f} percent in one month would reach the appetite. The worst historical month was {monthly['equity'].min() * 100:.1f} percent.")"""),
    M("""
**How to read it.** Replay answers "has this happened before and what would it cost today". The reverse test answers "how far are we from the edge". If the worst historical month sits well inside the frontier, the portfolio has
history based room, and the remaining risk is a month **unlike** any in the file. That gap is why risk committees add hypothetical scenarios written by experts, which this notebook does not do.

A detail worth seeing: the stress loss of the replay depends on **today's yield**. A bond bought at a low yield has a longer duration and loses more per basis point than one bought at a high yield.
"""),
]

S[15] = [
    C("""
# sensitivity to weights and appetite
rows = []
for w_e in [0.4, 0.6, 0.8]:
    for appetite in [0.10, 0.20, 0.30]:
        b0 = bond_return_shock(0.0, 1 / 12)
        need = (-appetite - (1 - w_e) * b0) / w_e
        rows.append({"equity_weight": w_e, "loss_appetite": appetite, "equity_fall_needed_no_rate_move": float(need)})
sens = pd.DataFrame(rows)
print(sens.pivot(index="equity_weight", columns="loss_appetite", values="equity_fall_needed_no_rate_move").round(3).to_string())

# var window sensitivity
rows = []
for window in [120, 240, 480]:
    series = pd.Series(rolling_historical_var(port, window, ALPHA), index=monthly.index).dropna()
    losses = -monthly["portfolio"].loc[series.index]
    k = kupiec_pof((losses > series).astype(int).to_numpy(), 1 - ALPHA)
    rows.append({"window_months": window, "months": k["n_obs"], "exceptions": k["exceptions"], "expected": round(k["expected_exceptions"], 1), "kupiec_p": round(k["p_value"], 4)})
window_table = pd.DataFrame(rows)
print()
print(window_table.to_string(index=False))"""),
    M("""
The first table shows how the frontier moves with the equity weight and the appetite. The second shows how the exception count depends on the VaR window. With only 2 to 5 tail months in a window, the VaR is a rough number at monthly frequency.
"""),
]

S[16] = [
    C("""
excluded_rows = raw.index[~usable]
criteria = {
    "bond_approximation_p99_below_0.1_percent": bool(np.percentile(approx_error, 99) < 0.001),
    "equity_hand_check_matches": bool(abs(by_hand - equity[i]) < 1e-15),
    "scratch_var_equals_library_no_lookahead_1e-12": bool(worst_gap < 1e-12),
    "reverse_stress_frontier_gives_exact_appetite": bool(np.all(np.abs(frontier["portfolio_return"] + LOSS_APPETITE) < 1e-9)),
    "worst_windows_start_12_months_apart": bool(starts_ok and len(chosen) == 5),
    "excluded_rows_are_trailing_and_valid_months_consecutive": bool(excluded_rows.min() > data.index.max() and months_gap.max() <= 31),
}
print(criteria)

metrics = {
    "valid_months": int(len(data)),
    "excluded_trailing_rows": int(len(excluded_rows)),
    "last_valid_month": data.index.max().date().isoformat(),
    "todays_yield": y_today,
    "bond_approx_error_p50_p99_max": np.percentile(approx_error, [50, 99, 100]).tolist(),
    "var_exceptions": int(kup["exceptions"]),
    "var_expected_exceptions": float(kup["expected_exceptions"]),
    "var_months_evaluated": int(kup["n_obs"]),
    "kupiec_p": float(kup["p_value"]),
    "worst_monthly_loss_historical_portfolio": float(loss.max()),
    "worst_monthly_loss_date": loss.idxmax().date().isoformat(),
    "var_in_force_at_worst_month": float(valid_var.loc[loss.idxmax()]),
    "replay_12_month_windows": replay.to_dict(orient="records"),
    "replay_worst_months": month_replay.to_dict(orient="records"),
    "worst_replayed_month_loss": worst_month_loss,
    "loss_appetite": LOSS_APPETITE,
    "reverse_stress_frontier": frontier.to_dict(orient="records"),
    "weight_appetite_sensitivity": sens.to_dict(orient="records"),
    "var_window_sensitivity": window_table.to_dict(orient="records"),
    "acceptance_criteria": criteria,
}
config = {"weights": {"equity": W_EQUITY, "bond": W_BOND}, "value_usd": VALUE, "loss_appetite": LOSS_APPETITE,
          "var_window_months": VAR_WINDOW, "alpha": ALPHA, "bond": {"maturity_years": 10, "freq": 2, "par": True}, "seed": SEED}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Historical scenario replay on today's portfolio, reverse stress frontier, rolling monthly VaR with Kupiec test",
    data_kind="empirical",
    dataset="datasets/raw/sp500_shiller_monthly.csv",
    n_obs=int(len(monthly)),
    seed=SEED,
    parameters=config,
    assumptions=[
        "loss appetite of 20 percent in a month is illustrative",
        "10 year bond is a constant maturity par bond, roll down ignored",
        "equity dividend is the annual rate in the file divided by 12",
        "rows with zero dividend or zero yield at the end of the file are excluded",
    ],
    metrics=metrics,
    baseline="rolling 99 percent historical VaR with a 240 month window",
    limitations=[
        "US equity and US rates only, one portfolio",
        "monthly data hides intra month moves, so the worst day is not seen",
        "price definition (monthly average or month end) is not verified, an average would understate tail months",
        "history based replay cannot show a month unlike any in the file",
        "no credit spread, inflation or liquidity effect, and no correlation break scenario",
        "the yield series of the 19th century is a reconstruction by the data author",
    ],
    figures=["reverse_stress_frontier.png", "monthly_var_exceptions.png"],
)
print("saved", path.name)"""),
]

S[17] = [
    M("""
1. **Monthly data.** The worst month in this file is not the worst day in history. Intra month swings are invisible. The data card does not say whether the price is a month average or a month end value. If it is an average, month to month changes are smoothed and the tail months are understated. This must be checked against the original source before the numbers are used.
2. **One country, two assets.** US equities and a 10 year government bond. No credit, no inflation linked assets, no foreign exchange.
3. **Reconstructed early data.** The yield and dividend series before the modern period were built by the data author from historical sources. Their quality is not checked here.
4. **Constant maturity bond.** Real bonds roll down the curve and have different durations. The yield index is a proxy.
5. **Correlation.** The replay uses the joint moves that happened. It cannot show what happens if stocks and bonds fall together by more than they ever did.
6. **Appetite is illustrative.** The 20 percent loss figure is not tied to a capital or limit framework.
7. **Rolling VaR with 240 months.** At 99 percent that is 2 or 3 tail months, a very rough estimate. The notebook shows the sensitivity to the window.
8. **No supervisory scenario.** Official stress tests use scenarios designed by authorities, which are not reproduced here.
"""),
]

S[18] = [
    M("""
**Where this sits in the job.** Stress testing is run on a calendar (monthly or quarterly) and on request when markets move. The pack for the committee has four parts.

1. The scenario list with its source: historical windows with dates, and hypothetical scenarios written by the risk team and the economists.
2. The loss table in USD and as a share of capital or of the appetite, for today's portfolio.
3. The reverse stress frontier: how far the portfolio is from the unacceptable loss.
4. The actions: which scenarios exceed the appetite, which position or hedge would reduce the loss, and who decides.

**Limits of authority.** The analyst proposes the scenarios and the numbers. The committee sets the appetite and chooses the response. An analyst who changes the appetite to make a table pass has failed the control.
"""),
]

S[19] = [
    M("""
1. Add a third asset, a constant 2 year bond, using the same method. How does the frontier change?
2. Replace the 10 year bond by a bond with a different duration. How much does the worst replayed month change?
3. Add a hypothetical scenario: equity down 25 percent and the yield up 250 basis points in one month. What is the loss in USD?
4. Change the appetite to a loss of USD 15 million. What equity fall is needed with no rate move?
5. Run the same exercise on the 1970 to 1982 period only. Which replay windows change?
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "12_end_to_end_banking_projects/historical_stress_replay",
        "title": "Stress Testing: Replaying History on Today's Portfolio",
        "family": "End to End Banking Projects",
        "level": "Applied",
        "dataset": "sp500_shiller_monthly",
        "data_kind": "empirical",
        "status": "Validating",
        "tagline": "Real monthly history from 1871 replayed on a 60/40 portfolio, a reverse stress frontier, and a test of how much a 20 year VaR understated the worst months.",
        "refs": ["bcbs_d457", "kupiec1995", "artzner1999"],
        "research_note": (
            "The registry holds no paper on stress testing itself, which is a gap listed in research gaps. The Basel market risk standard gives the supervisory setting for VaR and its limits, "
            "Kupiec (1995) supplies the exception test, and Artzner et al. (1999) explain why a single quantile does not describe the tail. The method of scenario replay and reverse stress testing is standard risk practice and is implemented here from first principles."
        ),
        "learn": [
            "Build total returns from raw price, dividend and yield data",
            "Replay worst historical windows on today's portfolio",
            "Solve and verify a reverse stress frontier",
            "Measure how far a rolling VaR fell short of the worst months",
            "Say what a history based stress test cannot show",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
