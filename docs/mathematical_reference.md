# Mathematical Reference

Audience: readers who want the formulas used by the code in `src/risk_lab`. This is a reference document. Each formula names the function that implements it. Derivations and worked numbers are in the module notebooks.

Notation: L is loss (negative return), alpha is the confidence level, N is the number of days, x is the exception count, p is the expected exception rate.

## Bonds (`finance/bonds.py`)

Let m be the coupon frequency, k = 1, ..., mn the period index, t_k = k/m, and PV_k = CF_k / (1 + y/m)^k. Price P = sum of PV_k. Macaulay duration D = (1/P) sum of t_k PV_k, in years. Modified duration D_mod = D / (1 + y/m). Convexity C = (1/P) sum of k (k + 1) PV_k / (m^2 (1 + y/m)^2), in years squared.

Price change for a yield shift dy: dP/P is approximately -D_mod dy + 0.5 C dy squared. DV01 is D_mod times P times 0.0001.

Closed form check: for a bond with coupon rate equal to yield, the price is the face value and D = (1 + y/m)/y times (1 - (1 + y/m)^(-mn)). The module tests this.

## Value at Risk (`market/var.py`)

Historical VaR at level alpha is the empirical alpha quantile of L. Normal VaR is mu_L + sigma z_alpha, with z_alpha the standard normal quantile. Student t VaR with nu degrees of freedom and standard deviation sigma is mu_L + sigma sqrt((nu - 2)/nu) t_alpha(nu). Variance covariance VaR for weights w is w' mu plus z_alpha sqrt(w' S w) in loss terms. EWMA variance: s2_t = lambda s2_(t-1) + (1 - lambda) r2_(t-1), with lambda 0.94 as the default. Component VaR of asset i is w_i times (S w)_i divided by sqrt(w' S w), times z_alpha, and the components sum to the total.

Square root of time scaling VaR_h = sqrt(h) VaR_1 assumes independent returns. The notebook compares it with overlapping 10 day returns, so the gap is a measured quantity.

## Expected Shortfall (`market/es.py`)

ES_alpha = (1/(1 - alpha)) times the integral of VaR_u for u from alpha to 1, in loss terms. The historical estimator uses the Acerbi and Tasche fractional weight on the boundary observation, so it is a proper tail average even when N(1 - alpha) is not an integer. Rockafellar and Uryasev: ES = min over v of v + E[(L - v)+]/(1 - alpha), and the minimiser is VaR. Normal: ES = mu + sigma phi(z_alpha)/(1 - alpha). Student t with standard deviation sigma: ES = mu + sigma sqrt((nu - 2)/nu) times f_nu(t_alpha) (nu + t_alpha squared)/((nu - 1)(1 - alpha)). The notebook checks both closed forms against numerical integration.

## Backtesting (`market/backtest.py`)

Kupiec proportion of failures: LR_pof = -2 ln[(1 - p)^(N - x) p^x] + 2 ln[(1 - x/N)^(N - x) (x/N)^x], chi squared with 1 degree of freedom under the null. Christoffersen independence uses the 2 by 2 transition counts n_ij of the exception indicator: LR_ind = -2 ln[L(pi; n) / L(pi_0, pi_1; n)], chi squared with 1 degree of freedom. Conditional coverage is LR_pof + LR_ind with 2 degrees of freedom. Traffic light zones for 250 days at 99 percent: the notebook derives the zone limits from the binomial cumulative probability P(X <= x) and compares them with the limits coded in `basel_traffic_light`.

## Credit metrics (`credit/metrics.py`, `credit/logistic.py`, `credit/woe.py`)

Logistic model: P(bad) = 1/(1 + exp(-(b0 + b'x))). Newton Raphson update: b_new = b + (X' W X)^(-1) X'(y - p), W = diag(p(1 - p)). Standard errors are the square roots of the diagonal of (X' W X)^(-1).

AUC through the rank sum formula, Gini = 2 AUC - 1, KS is the largest gap between cumulative bad and good distributions, Brier = mean of (p - y) squared.

Weight of evidence per bin: WoE = ln(share of goods / share of bads), with smoothing 0.5 on counts. Information value: IV = sum of (share goods - share bads) WoE. Population stability index: PSI = sum of (a_i - e_i) ln(a_i / e_i) over bins.

Score scaling: score = offset + factor ln(good odds), factor = PDO / ln 2, offset = base score - factor ln(base odds). With base 600, odds 50 to 1 and PDO 20, factor is 28.8539 and offset is 487.1229. These numbers are stored in the results file and tested.

## Expected credit loss (`credit/ecl.py`)

One period expected loss: EL = PD x LGD x EAD. Constant annual hazard: cumulative PD(t) = 1 - (1 - PD_12m)^t. Marginal PD in year t is PD(t) - PD(t - 1). Stage 1 uses year 1 only. Stage 2 sums years 1 to remaining term. Stage 3 uses LGD x EAD. Stage 1 and 2 loss: ECL = sum over t of marginal PD_t x LGD x B_t x (1 + EIR)^(-(t - 0.5)), where B_t is the balance at the start of year t and defaults fall in the middle of the year. Probability weighted ECL = sum over scenarios of weight_s x ECL_s, weights sum to 1.

## Assumptions

* Formulas are textbook forms. The sources are listed in each module `references.md`, and the book sources are not verified in version 0.2.0.
* Fact: each formula above is implemented in the code and checked by a second method. Judgment: the choice of lambda 0.94 and the 0.5 year default timing are conventions, not requirements.

## Check before use

* The Basel zone limits and add on values in `basel_traffic_light` come from the published framework as remembered by the author. Compare them with the current Basel text before any regulatory use.
