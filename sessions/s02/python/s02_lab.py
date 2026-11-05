# =============================================================================
# EEGB · Session 2 LAB · How price-sensitive are our customers? (Python)
# Data: data/fmcg_price_volume.csv — stylised weekly noodles sales, 3 regions, 2022–2025
# Run from the project root, line by line (Ctrl/Cmd + Enter)
# =============================================================================
import numpy as np, pandas as pd

d = pd.read_csv("data/fmcg_price_volume.csv", parse_dates=["week"])

# ---- STEP 1 · Look at the data -------------------------------------------------------
print(d.head())
print(d.groupby("region")[["price_naira", "units"]].agg(["first", "last"]))

# ---- STEP 2 · The naive elasticity: units on price, nothing else -----------------------
# In a log-log line, the slope IS the elasticity: % change in units for a 1% change in price.
naive = np.polyfit(np.log(d.price_naira), np.log(d.units), 1)[0]
print(f"Naive elasticity: {naive:.2f}")   # close to zero — does price really not matter?

# ---- STEP 3 · Hold other things constant (multiple regression with numpy) ------------------
d["t"] = d.groupby("region").cumcount()          # time trend: soaks up general inflation
X = np.column_stack([np.ones(len(d)),
                     np.log(d.price_naira),            # own price
                     np.log(d.competitor_price_naira), # rival's price
                     np.log(d.income_index),           # customers' income
                     d.t,
                     (d.region == "North").astype(float), (d.region == "South-East").astype(float)])
b, *_ = np.linalg.lstsq(X, np.log(d.units), rcond=None)
print(f"Own-price elasticity:   {b[1]:.2f}")
print(f"Cross-price elasticity: {b[2]:.2f}")
print(f"Income elasticity:      {b[3]:.2f}")

# ---- STEP 4 · What a price rise does to revenue -----------------------------------------------
for rise in (0.05, 0.10, 0.20):
    q_change = (1 + rise) ** b[1] - 1
    r_change = (1 + rise) * (1 + q_change) - 1
    print(f"Price +{rise:.0%}: volume {q_change:+.1%}, revenue {r_change:+.1%}")

# ---- STEP 5 · Promotions -----------------------------------------------------------------------
lift = d.groupby(["region", "promo"]).units.mean().unstack()
print((lift[1] / lift[0] - 1).round(3))

# ---- STEP 6 · Cost pass-through: flour up 40% ----------------------------------------------------
P0, C0 = 500.0, 350.0
dc = C0 * 0.45 * 0.40                       # flour is 45% of unit cost
for share in (0, 0.5, 1.0):
    P = P0 + share * dc
    Q = (P / P0) ** b[1]                     # rivals hold their price
    print(f"Pass on {share:.0%}: price ₦{P:.0f}, volume {Q - 1:+.1%}, profit {(P - C0 - dc) * Q / (P0 - C0):.0%} of before")

# ---- YOUR TURN -----------------------------------------------------------------------------------
# (a) Why is the naive elasticity so close to zero? What changed at the same time as prices?
# (b) Re-run Step 6 assuming rivals follow you (use b[1] + b[2] as the elasticity). What changes?
# (c) Write a 3-sentence pricing recommendation to the MD: how much of the flour shock to pass on,
#     how fast, and what you would watch in the first four weeks.
