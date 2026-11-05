# =============================================================================
# EEGB · Session 6 LAB · Demand shock or supply shock? Diagnosing Nigeria's inflation (Python)
# Data: data/ng_macro_monthly.csv — stylised Nigerian macro series, Jan 2015 – Dec 2025
# Run from the project root, line by line (Ctrl/Cmd + Enter in RStudio or VS Code)
# =============================================================================
import numpy as np, pandas as pd

m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
old = m[m.date < "2025-01-01"].copy()     # one CPI base only: the 2025 rebasing breaks the series

# ---- STEP 1 · Describe the inflation episode -----------------------------------------
before = old[(old.date >= "2022-01-01") & (old.date <= "2023-05-01")]
after = old[(old.date >= "2023-06-01") & (old.date <= "2024-12-01")]
for name, s in [("Jan 2022 – May 2023", before), ("Jun 2023 – Dec 2024", after)]:
    print(f"{name}: headline {s.headline_inflation.mean():.1f}%, food {s.food_inflation.mean():.1f}%, "
          f"core {s.core_inflation.mean():.1f}%, PMI {s.pmi.mean():.1f}")

# ---- STEP 2 · Food minus core: is the pressure coming from food and energy? -------------
old["food_core_gap"] = old.food_inflation - old.core_inflation
print(old.groupby(old.date.dt.year).food_core_gap.mean().round(1))

# ---- STEP 3 · Exchange-rate pass-through ----------------------------------------------
old["depreciation_yoy"] = 100 * (old.official_fx_ngn_usd / old.official_fx_ngn_usd.shift(12) - 1)
for lag in [0, 2, 4, 6, 9, 12]:
    r = old.depreciation_yoy.shift(lag).corr(old.headline_inflation)
    print(f"correlation of inflation with depreciation {lag:>2} months earlier: {r:.2f}")

# ---- STEP 4 · Persistence: how much of last year's inflation carries over? -----------------
old["lag12"] = old.headline_inflation.shift(12)
s = old.dropna(subset=["lag12"])
X = np.column_stack([np.ones(len(s)), s.lag12])
intercept, slope = np.linalg.lstsq(X, s.headline_inflation, rcond=None)[0]
print(f"inflation now = {intercept:.2f} + {slope:.2f} x inflation a year ago")

# ---- STEP 5 · A real interest rate check ----------------------------------------------------
old["real_rate"] = old.mpr - old.headline_inflation
print(old[["date", "mpr", "headline_inflation", "real_rate"]].tail(6))

# ---- YOUR TURN ---------------------------------------------------------------------------------
# (a) Using Steps 1–3, write three sentences: was the 2023–24 surge mainly a demand shock, a supply shock, or both?
#     Cite at least two numbers.
# (b) If it was mostly a supply shock, what does raising the policy rate achieve — and what does it cost?
# (c) Your company sets prices once a quarter. Using the slope in Step 4, what inflation would you plan for
#     next year if this year's is 30%? Why might that be too high or too low?
