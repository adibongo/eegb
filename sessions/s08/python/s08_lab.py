# =============================================================================
# EEGB · Session 8 LAB · How fast does the policy rate reach your firm? (Python)
# Data: data/ng_macro_monthly.csv and data/global_policy_rates.csv (stylised)
# Run from the project root, line by line
# =============================================================================
import numpy as np, pandas as pd

m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
pr = pd.read_csv("data/global_policy_rates.csv", parse_dates=["date"])

# ---- STEP 1 · List every CBN policy-rate decision ------------------------------------
moves = m.loc[m.mpr.diff() != 0, ["date", "mpr"]].copy()
moves["change_pts"] = moves.mpr.diff()
print(moves.tail(12))

# ---- STEP 2 · Real policy rate: is policy tight or loose? ---------------------------------
m["real_mpr"] = m.mpr - m.headline_inflation
print(m.groupby(m.date.dt.year).real_mpr.mean().round(1))

# ---- STEP 3 · Liquidity: is the interbank rate following the MPR? ----------------------------
m["interbank_gap"] = m.interbank_rate - m.mpr
print(m.groupby(m.date.dt.year).interbank_gap.mean().round(1))

# ---- STEP 4 · Transmission lags: when does credit growth respond? -------------------------------
m["mpr_change_12m"] = m.mpr - m.mpr.shift(12)
for lag in [0, 3, 6, 9, 12, 18]:
    r = m.mpr_change_12m.corr(m.private_credit_growth_yoy.shift(-lag))
    print(f"MPR change vs credit growth {lag:>2} months later: r = {r:.2f}")

# ---- STEP 5 · Compare with peers ---------------------------------------------------------------
latest = pr.iloc[-1].drop("date")
print("latest policy rates:\n", latest.sort_values(ascending=False))

# ---- STEP 6 · An illustrative Taylor rule ---------------------------------------------------------
target, neutral_real = 9.0, 2.0
old = m[m.date < "2025-01-01"].copy()
old["taylor"] = neutral_real + old.headline_inflation + 0.5 * (old.headline_inflation - target) + 0.5 * (old.pmi - 50)
print(old[["date", "mpr", "headline_inflation", "taylor"]].tail(6).round(1))

# ---- YOUR TURN ---------------------------------------------------------------------------------------
# (a) Your firm has a ₦5bn overdraft priced at MPR + 6 points. How much did annual interest rise between
#     June 2023 and December 2024? (Hint: use Step 1.)
# (b) Step 4 gives correlations at different lags. Why can correlation alone not prove the lag? What else moved?
# (c) The Taylor rule in Step 6 says rates "should" have been far higher. Give two reasons a central bank facing
#     a SUPPLY shock might choose not to follow it.
