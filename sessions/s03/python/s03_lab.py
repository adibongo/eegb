# =============================================================================
# EEGB · Session 3 LAB · How much cement will Nigeria buy in 2026? (Python)
# Data: data/cement_demand_monthly.csv — stylised monthly cement consumption, 2012–2025
# Run from the project root, line by line (Ctrl/Cmd + Enter)
# =============================================================================
import numpy as np, pandas as pd

c = pd.read_csv("data/cement_demand_monthly.csv", parse_dates=["month"])
c["t"] = np.arange(len(c)); c["m"] = c.month.dt.month; c["year"] = c.month.dt.year

# ---- STEP 1 · Trend: annual totals and the average growth rate ----------------------------
annual = c.groupby("year").cement_mt.sum()
print(annual.round(1))
cagr = (annual.iloc[-1] / annual.iloc[0]) ** (1 / (len(annual) - 1)) - 1
print(f"Average growth per year (CAGR): {cagr:.1%}")

# ---- STEP 2 · Seasonality: how each month compares with the year's average ---------------------
c["vs_year_avg"] = c.cement_mt / c.groupby("year").cement_mt.transform("mean")
idx = c.groupby("m").vs_year_avg.mean()
print((idx * 100).round(0))
# Seasonally adjust the latest month and read it as an annual rate
last = c.iloc[-1]
print(f"{last.month:%b %Y}: actual {last.cement_mt:.2f} Mt; seasonally adjusted x12 = {last.cement_mt / idx[last.m] * 12:.1f} Mt a year")

# ---- STEP 3 · A trend + seasonal model (one regression) --------------------------------------------
def X(df):
    return np.column_stack([np.ones(len(df)), df.t] + [(df.m == k).astype(float) for k in range(2, 13)])

train, test = c[c.year <= 2023], c[c.year >= 2024]
b, *_ = np.linalg.lstsq(X(train), np.log(train.cement_mt), rcond=None)
f_model = np.exp(X(test) @ b)
print(f"Model growth per month: {np.exp(b[1]) - 1:.2%}  (≈ {np.exp(12 * b[1]) - 1:.1%} a year)")

# ---- STEP 4 · Backtest against simple rules ------------------------------------------------------------
last12 = train.cement_mt.values[-12:]
rules = {"same month last year": np.r_[last12, last12],
         "last year + 5%": np.r_[last12 * 1.05, last12 * 1.05 ** 2],
         "trend + seasonal model": f_model}
for name, f in rules.items():
    err = f - test.cement_mt.values
    print(f"{name:25s} MAPE = {np.mean(np.abs(err) / test.cement_mt):.1%}   bias = {np.mean(err / test.cement_mt):+.1%}")

# ---- STEP 5 · Forecast 2026 with the model fitted on all the data ------------------------------------------
b_all, *_ = np.linalg.lstsq(X(c), np.log(c.cement_mt), rcond=None)
fut = pd.DataFrame({"t": np.arange(len(c), len(c) + 12), "m": range(1, 13)})
f26 = np.exp(X(fut) @ b_all)
print(f"2026 forecast: {f26.sum():.1f} million tonnes")
# 90% range from the spread of past annual misses: how far each year's total sat from the model's fitted total
fit_all = np.exp(X(c) @ b_all)
ann = c.assign(fit=fit_all).groupby("year")[["cement_mt", "fit"]].sum()
annual_sd = np.log(ann.cement_mt / ann.fit).std(ddof=1)
print(f"Typical annual miss: {annual_sd:.1%}")
print(f"90% range: {f26.sum() * np.exp(-1.645 * annual_sd):.1f} - {f26.sum() * np.exp(1.645 * annual_sd):.1f} Mt")

# ---- STEP 5b · The capacity decision: critical ratio -----------------------------------------------------------
from statistics import NormalDist
cost_short, cost_idle = 20, 8                       # ₦ thousand per tonne (illustrative)
cr = cost_short / (cost_short + cost_idle)
z = NormalDist().inv_cdf(cr)
print(f"Critical ratio {cr:.2f} -> plan capacity for {f26.sum() * np.exp(z * annual_sd):.1f} Mt")

# ---- STEP 6 · Size the market two ways -------------------------------------------------------------------------
print("Top-down: 237.5m people (World Bank 2025) × 129 kg =", round(237.5 * 0.129, 1), "Mt; industry report: 33.9 Mt")
print("Implied kg per person in the industry figure:", round(33.9e9 / 237.5e6), "kg — the source's own numbers disagree. Why might that be?")
print("Bottom-up: homes 14.4 + repairs 6.5 + public works 6.0 + commercial 4.5 + precast 2.4 =",
      14.4 + 6.5 + 6.0 + 4.5 + 2.4, "million tonnes")

# ---- YOUR TURN -------------------------------------------------------------------------------------------------
# (a) Build a downside and upside scenario for 2026. What would have to happen for each?
# (b) Which assumption in the bottom-up sizing are you least sure of? How would you check it?
# (c) Recommend a 2026 capacity plan in two sentences: how many tonnes, and what flexibility you keep.
