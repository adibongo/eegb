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
print((c.groupby("m").vs_year_avg.mean() * 100).round(0))

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
    print(f"{name:25s} MAPE = {np.mean(np.abs(test.cement_mt - f) / test.cement_mt):.1%}")

# ---- STEP 5 · Forecast 2026 with the model fitted on all the data ------------------------------------------
b_all, *_ = np.linalg.lstsq(X(c), np.log(c.cement_mt), rcond=None)
fut = pd.DataFrame({"t": np.arange(len(c), len(c) + 12), "m": range(1, 13)})
f26 = np.exp(X(fut) @ b_all)
print(f"2026 forecast: {f26.sum():.1f} million tonnes")

# ---- STEP 6 · Size the market two ways -------------------------------------------------------------------------
print("Top-down: 230m people × 140 kg =", 230 * 140 / 1000, "million tonnes")
print("Bottom-up: homes 14.4 + repairs 6.5 + public works 6.0 + commercial 4.5 + precast 2.4 =",
      14.4 + 6.5 + 6.0 + 4.5 + 2.4, "million tonnes")

# ---- YOUR TURN -------------------------------------------------------------------------------------------------
# (a) Build a downside and upside scenario for 2026. What would have to happen for each?
# (b) Which assumption in the bottom-up sizing are you least sure of? How would you check it?
# (c) Recommend a 2026 capacity plan in two sentences: how many tonnes, and what flexibility you keep.
