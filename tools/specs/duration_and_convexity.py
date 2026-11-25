"""Spec: bond pricing, duration and convexity."""

from nbgen import C, M

from specs._common import check_sections, setup_code

MODULE = "duration_and_convexity"

SETUP = setup_code(MODULE) + """
from risk_lab.finance.bonds import (
    bond_price, convexity, dv01, macaulay_duration, modified_duration, price_change_estimate,
    yield_to_maturity,
)"""

S = {}

S[1] = [
    M("""
A bank holds fixed coupon bonds in its liquidity buffer. Treasury must answer one question every day:
**if market yields move by a given amount, how much does the value of the bond portfolio change?**

The exact answer needs a full revaluation of every bond. That is slow for a large book and says nothing about
which position drives the loss. Duration and convexity give a fast, decomposable approximation.
This notebook builds both measures from first principles, tests how accurate they are, and shows
where the approximation stops being safe.

**Decision this supports:** size a yield sensitivity limit (DV01) and decide how much of a rate move
a hedge must absorb.
"""),
]

S[2] = [
    M("""
After this notebook you can:

1. Price a fixed coupon bond as a present value and reproduce a par price by hand.
2. Derive and compute Macaulay duration, modified duration, convexity and DV01.
3. Measure the error of the duration estimate and the duration plus convexity estimate against full revaluation.
4. Find the yield shock size at which an approximation exceeds a stated error tolerance.
5. Build a DV01 hedge and measure what is left after a yield move.
"""),
]

S[3] = [
    M("""
| Term | Meaning | Unit |
|---|---|---|
| Coupon rate | Yearly coupon as a share of face value | decimal per year |
| Yield to maturity (YTM) | Single discount rate that makes the present value of cash flows equal the price | decimal per year, compounded at the coupon frequency |
| Macaulay duration | Present value weighted average time to cash flows | years |
| Modified duration | Macaulay duration divided by (1 + y / f). Percentage price change per unit yield change | years |
| Convexity | Curvature of the price yield curve, relative to price | years squared |
| DV01 | Currency price change for a one basis point rise in yield | currency |

Price and yield move in opposite directions. The relationship is convex: a yield fall raises the price
by more than an equal yield rise lowers it.
"""),
]

S[4] = [
    M("""
**Why duration and convexity instead of only full revaluation?**

| Method | Strength | Weakness |
|---|---|---|
| Full revaluation | Exact for the chosen yield shock | Needs every cash flow and a pricing call per scenario. Gives no direct attribution |
| Duration (first order) | One number per bond, additive across a portfolio when yields move in parallel | Error grows with the square of the shock |
| Duration plus convexity (second order) | Captures the curvature that duration misses | Still a local approximation. Ignores embedded options |

Full revaluation is the benchmark in this notebook. The two approximations are accepted only if they stay within
a stated tolerance. Tolerance used here: **0.10 percent of price**. This is a learning choice, not a regulatory number.
"""),
]

S[6] = [
    M(r"""
Price with yearly yield $y$, frequency $f$ and $N$ periods:

$$P(y) = \sum_{k=1}^{N} \frac{CF_k}{(1 + y/f)^k}$$

Differentiate once with respect to $y$:

$$\frac{dP}{dy} = -\frac{1}{f}\sum_{k=1}^{N} \frac{k \, CF_k}{(1 + y/f)^{k+1}}$$

Macaulay duration uses time $t_k = k/f$ in years:

$$D_{Mac} = \frac{1}{P}\sum_{k=1}^{N} t_k \frac{CF_k}{(1 + y/f)^k}, \qquad D_{Mod} = \frac{D_{Mac}}{1 + y/f} = -\frac{1}{P}\frac{dP}{dy}$$

Differentiate twice and divide by the price to get convexity:

$$C = \frac{1}{P}\frac{d^2P}{dy^2} = \frac{1}{P}\sum_{k=1}^{N} \frac{k(k+1)}{f^2} \frac{CF_k}{(1 + y/f)^{k+2}}$$

The second order Taylor expansion of the price is

$$\frac{\Delta P}{P} \approx -D_{Mod}\,\Delta y + \frac{1}{2} C \,(\Delta y)^2$$

DV01 is $D_{Mod} \cdot P \cdot 0.0001$.

**Closed form check.** For a bond priced at par ($y$ equals the coupon rate) Macaulay duration is

$$D_{Mac} = \frac{1 + y/f}{y}\left[1 - (1 + y/f)^{-N}\right]$$

This gives an independent test of the code that does not use the sums above.
"""),
]

S[7] = [
    M("""
Bond: face 100, coupon 5 percent, 5 years, semiannual coupons, yield 5 percent. Because yield equals coupon,
the price must be exactly 100. The table below builds every step by hand.
"""),
    C("""
face, coupon_rate, years, freq, ytm = 100.0, 0.05, 5, 2, 0.05
periods = years * freq
table = pd.DataFrame({"period": np.arange(1, periods + 1)})
table["time_years"] = table["period"] / freq
table["cashflow"] = face * coupon_rate / freq
table.loc[periods - 1, "cashflow"] += face
table["discount_factor"] = (1 + ytm / freq) ** (-table["period"])
table["present_value"] = table["cashflow"] * table["discount_factor"]
table["time_x_pv"] = table["time_years"] * table["present_value"]
price = table["present_value"].sum()
mac = table["time_x_pv"].sum() / price
print(table.round(4).to_string(index=False))
print()
print("price:", round(price, 6))
print("macaulay duration:", round(mac, 6))"""),
    C("""
# closed form check
mac_closed = (1 + ytm / freq) / ytm * (1 - (1 + ytm / freq) ** (-periods))
print("closed form duration:", round(mac_closed, 6))
assert abs(price - 100.0) < 1e-9
assert abs(mac - mac_closed) < 1e-9
print("par price and closed form duration confirmed")"""),
]

S[8] = [
    M("""
This module has **no dataset file**. The bonds are defined in the notebook and are illustrative.
Nothing here describes a real security or a real bank. The synthetic datasets in `datasets/` are
used from the credit and market modules onward.
"""),
    C("""
bonds = pd.DataFrame(
    {
        "name": ["Short note", "Medium bond", "Long bond", "Zero coupon"],
        "face": [1_000_000, 1_000_000, 1_000_000, 1_000_000],
        "coupon_rate": [0.03, 0.04, 0.05, 0.0],
        "maturity_years": [2, 5, 10, 10],
        "ytm": [0.035, 0.04, 0.045, 0.045],
    }
)
bonds["price_per_100"] = [
    bond_price(r.ytm, 100, r.coupon_rate, r.maturity_years) for r in bonds.itertuples()
]
print(bonds.to_string(index=False))"""),
]

S[9] = [
    M("""
Preparation is limited to fixing the shock grid and the tolerance, so every later table uses the same inputs.
Shocks are parallel yield shifts from -300 to +300 basis points.
"""),
    C("""
# fixed inputs
face, coupon_rate, years, freq, ytm = 100.0, 0.05, 10, 2, 0.05
tolerance_pct = 0.10
shock_bp = np.arange(-300, 301, 25)
fine_bp = np.arange(0, 501, 1)
print("reference bond: face", face, "coupon", coupon_rate, "years", years, "yield", ytm)
print("tolerance in percent of price:", tolerance_pct)"""),
]

S[10] = [
    M("""
Plain loops, no helper from the library. Each function follows the formulas in section 6 term by term.
"""),
    C("""
def my_price(y, face, c, n_years, f):
    total = 0.0
    for k in range(1, n_years * f + 1):
        cash = face * c / f
        if k == n_years * f:
            cash += face
        total += cash / (1 + y / f) ** k
    return total


def my_mac(y, face, c, n_years, f):
    p = my_price(y, face, c, n_years, f)
    total = 0.0
    for k in range(1, n_years * f + 1):
        cash = face * c / f
        if k == n_years * f:
            cash += face
        total += (k / f) * cash / (1 + y / f) ** k
    return total / p


def my_convexity(y, face, c, n_years, f):
    p = my_price(y, face, c, n_years, f)
    total = 0.0
    for k in range(1, n_years * f + 1):
        cash = face * c / f
        if k == n_years * f:
            cash += face
        total += k * (k + 1) / f**2 * cash / (1 + y / f) ** (k + 2)
    return total / p


p0 = my_price(ytm, face, coupon_rate, years, freq)
mac0 = my_mac(ytm, face, coupon_rate, years, freq)
mod0 = mac0 / (1 + ytm / freq)
conv0 = my_convexity(ytm, face, coupon_rate, years, freq)
print("price", round(p0, 6), "mac", round(mac0, 6), "mod", round(mod0, 6), "convexity", round(conv0, 6))"""),
]

S[11] = [
    M("""
Two independent checks. First the library functions must match the loops above. Second, a central finite
difference of the price must match the analytical duration and convexity. The finite difference does not use
the derivative formulas, so it can catch an algebra error that both implementations share.
"""),
    C("""
p_lib = bond_price(ytm, face, coupon_rate, years, freq)
mac_lib = macaulay_duration(ytm, face, coupon_rate, years, freq)
mod_lib = modified_duration(ytm, face, coupon_rate, years, freq)
conv_lib = convexity(ytm, face, coupon_rate, years, freq)
dv01_lib = dv01(ytm, face, coupon_rate, years, freq)

assert abs(p_lib - p0) < 1e-9
assert abs(mac_lib - mac0) < 1e-9
assert abs(conv_lib - conv0) < 1e-9

h = 1e-4
up = bond_price(ytm + h, face, coupon_rate, years, freq)
down = bond_price(ytm - h, face, coupon_rate, years, freq)
mod_fd = -(up - down) / (2 * h) / p_lib
conv_fd = (up + down - 2 * p_lib) / h**2 / p_lib
check = pd.DataFrame(
    {
        "analytical": [mod_lib, conv_lib],
        "finite_difference": [mod_fd, conv_fd],
    },
    index=["modified duration", "convexity"],
)
check["abs_gap"] = (check["analytical"] - check["finite_difference"]).abs()
print(check.round(8))
assert check["abs_gap"].max() < 1e-4
print("DV01 per 100 face:", round(dv01_lib, 6))"""),
    C("""
# yield from price
implied = yield_to_maturity(p_lib, face, coupon_rate, years, freq)
print("yield recovered from price:", round(implied, 10))
assert abs(implied - ytm) < 1e-9"""),
]

S[12] = [
    M("""
Each shock is evaluated three ways: full revaluation, duration only, and duration plus convexity.
Error is measured as the estimate minus the full revaluation price, as a percent of the starting price.
"""),
    C("""
rows = []
for bp in shock_bp:
    dy = bp / 10000
    true_price = bond_price(ytm + dy, face, coupon_rate, years, freq)
    est1 = price_change_estimate(p_lib, mod_lib, conv_lib, dy, use_convexity=False)
    est2 = price_change_estimate(p_lib, mod_lib, conv_lib, dy, use_convexity=True)
    rows.append(
        {
            "shock_bp": bp,
            "full_price": true_price,
            "duration_price": est1,
            "dur_conv_price": est2,
            "err_duration_pct": 100 * (est1 - true_price) / p_lib,
            "err_dur_conv_pct": 100 * (est2 - true_price) / p_lib,
        }
    )
errors = pd.DataFrame(rows)
show = errors[errors["shock_bp"].isin([-300, -100, -25, 25, 100, 300])]
print(show.round(4).to_string(index=False))"""),
    C("""
# largest safe shock
def safe_shock(method):
    for bp in fine_bp:
        dy = bp / 10000
        for sign in (1, -1):
            true_price = bond_price(ytm + sign * dy, face, coupon_rate, years, freq)
            est = price_change_estimate(
                p_lib, mod_lib, conv_lib, sign * dy, use_convexity=(method == "dur_conv")
            )
            if abs(est - true_price) / p_lib * 100 > tolerance_pct:
                return int(bp)
    return int(fine_bp[-1])


safe_duration = safe_shock("duration")
safe_dur_conv = safe_shock("dur_conv")
print("first shock above tolerance, duration only (bp):", safe_duration)
print("first shock above tolerance, duration plus convexity (bp):", safe_dur_conv)
assert safe_dur_conv > safe_duration"""),
]

S[13] = [
    C("""
grid = np.linspace(-0.03, 0.03, 121)
full = np.array([bond_price(ytm + d, face, coupon_rate, years, freq) for d in grid])
line1 = np.array([price_change_estimate(p_lib, mod_lib, conv_lib, d, False) for d in grid])
line2 = np.array([price_change_estimate(p_lib, mod_lib, conv_lib, d, True) for d in grid])

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].plot(grid * 1e4, full, color=COLORS["main"], label="full revaluation")
axes[0].plot(grid * 1e4, line1, color=COLORS["second"], linestyle="--", label="duration only")
axes[0].plot(grid * 1e4, line2, color=COLORS["third"], linestyle=":", label="duration plus convexity")
axes[0].set_xlabel("parallel yield shock (bp)")
axes[0].set_ylabel("price per 100 face")
axes[0].set_title("Price yield curve and approximations")
axes[0].legend()

axes[1].plot(errors["shock_bp"], errors["err_duration_pct"], color=COLORS["second"], label="duration only")
axes[1].plot(errors["shock_bp"], errors["err_dur_conv_pct"], color=COLORS["third"], label="duration plus convexity")
axes[1].axhline(tolerance_pct, color=COLORS["grey"], linewidth=0.8)
axes[1].axhline(-tolerance_pct, color=COLORS["grey"], linewidth=0.8)
axes[1].set_xlabel("parallel yield shock (bp)")
axes[1].set_ylabel("error, percent of price")
axes[1].set_title("Approximation error against full revaluation")
axes[1].legend()
save_figure(fig, MODULE, "price_yield_and_errors.png")
plt.show()"""),
]

S[14] = [
    M("""
Read the output below as facts computed from this notebook. The general pattern: for a plain bond the true
price curve lies **above** its tangent line, so the duration only estimate is **too low for a yield rise and
too low for a yield fall**. After a rise it predicts a loss that is too large. After a fall it predicts a gain
that is too small. Convexity adds the missing curvature and removes most of the gap.
"""),
    C("""
row_up = errors[errors["shock_bp"] == 100].iloc[0]
row_down = errors[errors["shock_bp"] == -100].iloc[0]
print("At +100 bp, duration only error (pct of price):", round(row_up["err_duration_pct"], 4))
print("At -100 bp, duration only error (pct of price):", round(row_down["err_duration_pct"], 4))
print("At +100 bp, with convexity (pct of price):", round(row_up["err_dur_conv_pct"], 4))
print("At -100 bp, with convexity (pct of price):", round(row_down["err_dur_conv_pct"], 4))
print("Duration only below true price at +100 bp:", row_up["duration_price"] < row_up["full_price"])
print("Duration only below true price at -100 bp:", row_down["duration_price"] < row_down["full_price"])
assert row_up["duration_price"] < row_up["full_price"]
assert row_down["duration_price"] < row_down["full_price"]"""),
]

S[15] = [
    M("""
**Experiment A.** How does duration change with maturity and coupon at a fixed yield of 5 percent?

**Experiment B.** How does the safe shock size change with maturity? Longer bonds have higher duration and
convexity, so the approximation should break sooner.
"""),
    C("""
maturities = np.arange(1, 31)
coupons = [0.0, 0.05, 0.10]
dur_table = pd.DataFrame(
    {
        f"coupon {c:.0%}": [macaulay_duration(0.05, 100, c, int(m), 2) for m in maturities]
        for c in coupons
    },
    index=maturities,
)
dur_table.index.name = "maturity_years"
print(dur_table.loc[[1, 2, 5, 10, 20, 30]].round(3))

fig, ax = plt.subplots()
for column, color in zip(dur_table.columns, [COLORS["second"], COLORS["main"], COLORS["third"]]):
    ax.plot(dur_table.index, dur_table[column], color=color, label=column)
ax.plot(dur_table.index, dur_table.index, color=COLORS["grey"], linestyle=":", label="maturity")
ax.set_xlabel("maturity (years)")
ax.set_ylabel("Macaulay duration (years)")
ax.set_title("Duration by maturity and coupon, yield 5 percent")
ax.legend()
save_figure(fig, MODULE, "duration_by_maturity.png")
plt.show()"""),
    C("""
# safe shock by maturity
safe_rows = []
for m in [2, 5, 10, 20, 30]:
    p = bond_price(0.05, 100, 0.05, m, 2)
    md = modified_duration(0.05, 100, 0.05, m, 2)
    cv = convexity(0.05, 100, 0.05, m, 2)
    found = {}
    for label, use_conv in [("duration", False), ("dur_conv", True)]:
        limit = 500
        for bp in range(0, 501):
            dy = bp / 10000
            bad = False
            for sign in (1, -1):
                true_price = bond_price(0.05 + sign * dy, 100, 0.05, m, 2)
                est = price_change_estimate(p, md, cv, sign * dy, use_conv)
                if abs(est - true_price) / p * 100 > tolerance_pct:
                    bad = True
            if bad:
                limit = bp
                break
        found[label] = limit
    safe_rows.append({"maturity_years": m, "first_bad_shock_duration_bp": found["duration"], "first_bad_shock_dur_conv_bp": found["dur_conv"]})
safe_table = pd.DataFrame(safe_rows)
print(safe_table.to_string(index=False))
print("500 means the tolerance was never exceeded up to 500 bp")"""),
]

S[16] = [
    C("""
metrics = {
    "reference_bond": {"face": face, "coupon_rate": coupon_rate, "maturity_years": years, "ytm": ytm, "freq": freq},
    "price": p_lib,
    "macaulay_duration": mac_lib,
    "modified_duration": mod_lib,
    "convexity": conv_lib,
    "dv01_per_100_face": dv01_lib,
    "error_pct_plus_100bp": {
        "duration_only": float(row_up["err_duration_pct"]),
        "duration_plus_convexity": float(row_up["err_dur_conv_pct"]),
    },
    "error_pct_plus_300bp": {
        "duration_only": float(errors[errors["shock_bp"] == 300].iloc[0]["err_duration_pct"]),
        "duration_plus_convexity": float(errors[errors["shock_bp"] == 300].iloc[0]["err_dur_conv_pct"]),
    },
    "first_shock_above_tolerance_bp": {"duration_only": safe_duration, "duration_plus_convexity": safe_dur_conv},
    "tolerance_pct_of_price": tolerance_pct,
    "par_bond_closed_form_check": "passed",
    "finite_difference_check_max_gap": float(check["abs_gap"].max()),
    "acceptance_criteria": {
        "par_bond_price_equals_100": bool(abs(price - 100.0) < 1e-9),
        "par_bond_duration_matches_closed_form": bool(abs(mac - mac_closed) < 1e-9),
        "loops_match_library": bool(abs(p_lib - p0) < 1e-9 and abs(mac_lib - mac0) < 1e-9 and abs(conv_lib - conv0) < 1e-9),
        "finite_difference_gap_below_1e-4": bool(check["abs_gap"].max() < 1e-4),
        "convexity_widens_safe_shock": bool(safe_dur_conv > safe_duration),
    },
}
print(pd.Series({k: v for k, v in metrics.items() if not isinstance(v, dict)}))"""),
]

S[17] = [
    M("""
**Limitations**

1. Parallel shifts only. Real curves twist and steepen, so one duration number cannot describe the risk. Key rate durations are the usual next step.
2. Fixed cash flows. A callable bond, a mortgage with prepayment or a deposit with behavioural maturity has cash flows that depend on the yield. Plain duration is wrong for those.
3. Credit spread is inside the yield here. A change in spread and a change in the risk free rate are not separated.
4. The tolerance of 0.10 percent of price is a teaching choice.
5. One flat yield per bond. No curve fitting, no day count conventions, no accrued interest.

**Model risk.** The pricing function is simple and verified by a closed form and a finite difference check.
The main risk is use, not code: applying a first order measure outside its range, or to instruments with optionality.
"""),
]

S[18] = [
    M("""
A treasury desk wants the four bonds above to be insensitive to a small parallel yield move.
Step 1: compute each bond's DV01 in currency. Step 2: add them. Step 3: size a short position in a 10 year
4 percent bond whose DV01 offsets the total. Step 4: test the hedge by full revaluation after a +50 bp shock.
This is illustrative: yields, sizes and the hedge instrument are assumed.
"""),
    C("""
bonds["price_per_100"] = [bond_price(r.ytm, 100, r.coupon_rate, r.maturity_years) for r in bonds.itertuples()]
bonds["market_value"] = bonds["price_per_100"] / 100 * bonds["face"]
bonds["dv01_per_100"] = [dv01(r.ytm, 100, r.coupon_rate, r.maturity_years) for r in bonds.itertuples()]
bonds["dv01_currency"] = bonds["dv01_per_100"] / 100 * bonds["face"]
print(bonds[["name", "market_value", "dv01_currency"]].round(2).to_string(index=False))

portfolio_dv01 = bonds["dv01_currency"].sum()
hedge_yield = 0.04
hedge_dv01_per_100 = dv01(hedge_yield, 100, 0.04, 10)
hedge_face = portfolio_dv01 / hedge_dv01_per_100 * 100
print("portfolio DV01:", round(portfolio_dv01, 2))
print("short hedge face value:", round(hedge_face, 0))"""),
    C("""
# test the hedge
shock = 0.005
value_before = bonds["market_value"].sum() - hedge_face * bond_price(hedge_yield, 100, 0.04, 10) / 100
value_after = 0.0
for r in bonds.itertuples():
    value_after += bond_price(r.ytm + shock, 100, r.coupon_rate, r.maturity_years) / 100 * r.face
value_after -= hedge_face * bond_price(hedge_yield + shock, 100, 0.04, 10) / 100
unhedged_change = sum(
    (bond_price(r.ytm + shock, 100, r.coupon_rate, r.maturity_years) - r.price_per_100) / 100 * r.face
    for r in bonds.itertuples()
)
print("unhedged change:", round(unhedged_change, 0))
print("hedged change:", round(value_after - value_before, 0))
print("share of move left after hedge (percent):", round(100 * abs((value_after - value_before) / unhedged_change), 2))
hedge_left_pct = 100 * abs((value_after - value_before) / unhedged_change)"""),
    M("""
Results are written to `experiments/results/` here, after the hedge test, because the hedge numbers belong in the saved file.
"""),
    C("""
metrics["hedge_residual_pct_after_plus_50bp"] = hedge_left_pct
metrics["portfolio_dv01_currency"] = portfolio_dv01
config = {
    "bond": {"face": face, "coupon_rate": coupon_rate, "years": years, "freq": freq, "ytm": ytm},
    "shock_grid_bp": [int(shock_bp.min()), int(shock_bp.max()), 25],
    "tolerance_pct_of_price": tolerance_pct,
}
save_config(MODULE, config)
path = save_result(
    MODULE,
    methodology="Present value pricing, analytical duration and convexity, checked by closed form and finite difference",
    data_kind="illustrative",
    dataset="none, bonds defined in the notebook",
    n_obs=int(len(shock_bp)),
    seed=None,
    parameters=config,
    assumptions=[
        "flat yield per bond",
        "parallel yield shifts only",
        "fixed cash flows, no options",
        "tolerance of 0.10 percent of price is a teaching choice",
    ],
    metrics=metrics,
    baseline={"name": "full revaluation", "note": "duration estimates are compared with exact repricing"},
    limitations=["no curve shape changes", "no embedded options", "illustrative bonds only"],
)
print("saved", path.name)"""),
]

S[19] = [
    M("""
1. Change the yield to 8 percent and rerun sections 7 to 12. Predict first whether duration goes up or down, then check.
2. Price a 10 year zero coupon bond. Show that its Macaulay duration equals its maturity. Explain why no other 10 year bond can match it.
3. A bond has modified duration 7.2 and convexity 70. Estimate the price change for a +150 bp shock by hand, with and without convexity. State which sign the convexity term has.
4. Add a +/- 100 bp curve twist (short yields up, long yields down) to the four bond portfolio. Does the DV01 hedge still work? Measure the residual.
5. Write down one instrument for which the tolerance test in section 12 would be meaningless, and say why.
"""),
]

SPEC = check_sections(
    {
        "module": MODULE,
        "path": "03_market_risk/duration_and_convexity",
        "title": "Duration and Convexity",
        "family": "Fundamentals",
        "level": "Beginner",
        "dataset": "none (illustrative bonds defined in the notebook)",
        "data_kind": "illustrative",
        "status": "Validating",
        "tagline": "Price a fixed coupon bond, measure its rate sensitivity, and test when the approximation fails.",
        "refs": ["hull_rmfi", "bcbs_d457"],
        "research_note": (
            "The formulas are standard fixed income mathematics. The notebook verifies them with a par bond closed form "
            "and a finite difference, so its correctness does not depend on the textbook. The textbook entry is not "
            "verified in this build, which is why the module status is Validating."
        ),
        "learn": [
            "Bond price as a present value, and yield to maturity from a price",
            "Macaulay and modified duration, convexity and DV01",
            "Error of first and second order price estimates, with a stated tolerance",
            "Building and testing a DV01 hedge",
        ],
        "setup": SETUP,
        "sections": S,
    }
)
