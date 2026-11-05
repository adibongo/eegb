# =============================================================================
# EEGB · Session 14 LAB · Rank eight markets, then stress-test the Nigeria plan (Python)
# Data: data/country_risk_panel.csv (stylised indicators for eight African markets)
# Run from the project root, line by line.
# =============================================================================
import pandas as pd

cr = pd.read_csv("data/country_risk_panel.csv").set_index("country")
print(cr)

# ---- STEP 1 · Put every indicator on the same scale (z-scores) -----------------------------
# A z-score says how many standard deviations a country is above or below the group average.
# We flip the sign where a HIGH value is GOOD (growth, reserves, current account, governance) so that high = risky.
sign = {"inflation_pct": 1, "public_debt_gdp_pct": 1, "fx_depreciation_12m": 1, "eurobond_spread_pct": 1,
        "real_growth_pct": -1, "reserves_months_imports": -1, "current_account_gdp_pct": -1,
        "political_stability_wgi": -1, "regulatory_quality_wgi": -1}
z = pd.DataFrame({k: s * (cr[k] - cr[k].mean()) / cr[k].std() for k, s in sign.items()})
print(z.round(2))

# ---- STEP 2 · Group indicators into four pillars ---------------------------------------------
pillars = {"macro": ["inflation_pct", "real_growth_pct"],
           "external": ["reserves_months_imports", "current_account_gdp_pct", "fx_depreciation_12m"],
           "fiscal_market": ["public_debt_gdp_pct", "eurobond_spread_pct"],
           "political": ["political_stability_wgi", "regulatory_quality_wgi"]}
pill = pd.DataFrame({p: z[c].mean(axis=1) for p, c in pillars.items()})

# ---- STEP 3 · Weight the pillars and rank ------------------------------------------------------
def rank_with(w):
    s = sum(pill[p] * wt for p, wt in w.items()) / sum(w.values())
    return s.rank().astype(int)          # 8 = riskiest
print(pd.DataFrame({"equal": rank_with({"macro": 1, "external": 1, "fiscal_market": 1, "political": 1}),
                    "lender": rank_with({"macro": .5, "external": 2, "fiscal_market": 2, "political": .5}),
                    "investor": rank_with({"macro": 2, "external": .5, "fiscal_market": .5, "political": 2})}))

# ---- STEP 4 · Scenarios for the Nigeria plan ------------------------------------------------------
# Next-year EBITDA (₦ bn) under three scenarios — from the session's plan model (see s14_figures.py)
scen = pd.DataFrame({"prob": [0.35, 0.45, 0.20], "ebitda": [18.39, 11.23, -5.93]},
                    index=["Reform pays off", "Muddle through", "Relapse"])
print(scen); print("probability-weighted EBITDA: ₦", round((scen.prob * scen.ebitda).sum(), 2), "bn  (today: ₦18bn)")

# ---- YOUR TURN -------------------------------------------------------------------------------------
# (a) Choose your own pillar weights for YOUR company (an importer? an exporter? a bank?). Where does Nigeria rank?
# (b) Change the 'Relapse' probability to 0.35 (and 'Muddle through' to 0.30). What happens to expected EBITDA?
# (c) Name three signposts you would watch monthly, with the trigger level that would make you switch scenario.
