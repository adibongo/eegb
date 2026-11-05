# =============================================================================
# EEGB · Session 12 LAB · Where should we export first under AfCFTA? (Python)
# Data: data/ng_trade_partners.csv — stylised Nigerian trade with 30 partners (US$ m)
# Run from the project root, line by line (Ctrl/Cmd + Enter in RStudio or VS Code)
# =============================================================================
import numpy as np, pandas as pd

t = pd.read_csv("data/ng_trade_partners.csv")

# ---- STEP 1 · Look before you calculate ------------------------------------------
print(t.shape)
print(t[["partner", "region", "partner_gdp_usd_bn", "distance_km", "exports_usd_m", "imports_usd_m"]].head(10))

# ---- STEP 2 · Who matters most? --------------------------------------------------------
print(t.sort_values("total_trade_usd_m", ascending=False)[["partner", "total_trade_usd_m"]].head(10))
print("Africa's share of Nigeria's trade:",
      round(t.loc[t.region == "Africa", "total_trade_usd_m"].sum() / t.total_trade_usd_m.sum() * 100, 1), "%")

# ---- STEP 3 · Fit the gravity model: log(trade) = a + b1 log(GDP) + b2 log(distance) + ... -----
X = np.column_stack([np.ones(len(t)), np.log(t.partner_gdp_usd_bn), np.log(t.distance_km),
                     t.common_language, t.landlocked])
y = np.log(t.total_trade_usd_m)
b, *_ = np.linalg.lstsq(X, y, rcond=None)
names = ["constant", "log GDP", "log distance", "common language", "landlocked"]
print(pd.Series(b, index=names).round(2))
#   Read: b(log GDP) ~ 1 means 1% bigger partner -> ~1% more trade.
#         b(log distance) ~ -1 means 1% further away -> ~1% less trade.

# ---- STEP 4 · How well does it fit? ----------------------------------------------------------
pred = X @ b
r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
print("R-squared:", round(r2, 2))

# ---- STEP 5 · Where is trade 'missing'? Actual vs predicted ------------------------------------
t["predicted_usd_m"] = np.exp(pred).round(0)
t["actual_vs_predicted"] = (t.total_trade_usd_m / t.predicted_usd_m).round(2)
print(t.loc[t.region == "Africa", ["partner", "total_trade_usd_m", "predicted_usd_m", "actual_vs_predicted"]]
        .sort_values("actual_vs_predicted"))

# ---- STEP 6 · A simple AfCFTA tariff scenario ----------------------------------------------------
sigma = 4                          # assumed trade elasticity (estimates are often 3–6)
uplift = (1.09 / 1.00) ** sigma - 1  # from 9% average tariff to zero
print(f"Trade with African partners could rise by about {uplift:.0%} if tariffs fell from 9% to 0")

# ---- STEP 7 · Supply-chain concentration on the import side ----------------------------------------
share = t.set_index("partner").imports_usd_m / t.imports_usd_m.sum() * 100
print(share.sort_values(ascending=False).head(5).round(1))
print("HHI of import sources:", round((share ** 2).sum()))   # above 2,500 = highly concentrated

# ---- YOUR TURN ---------------------------------------------------------------------------------
# (a) Rank African partners on market size (GDP), distance and the 'missing trade' ratio. Pick your top three
#     export markets for a Nigerian packaged-food firm, and justify each in one line.
# (b) Re-run STEP 6 with sigma = 3 and sigma = 6. How sensitive is the AfCFTA gain to this assumption?
# (c) Why might tariffs NOT be the binding constraint? List three non-tariff barriers you know from experience.
# (d) If 64% of your imported inputs come from one country, what two actions would reduce the risk?
