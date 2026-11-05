# =============================================================================
# EEGB · Session 15 LAB · A hedging plan for a flour miller (Python)
# Data: data/miller_exposure_monthly.csv — stylised miller, Jan 2019 – Dec 2025
#       data/ng_macro_monthly.csv and data/global_policy_rates.csv — for forward prices
# Run from the project root, line by line
# =============================================================================
import numpy as np, pandas as pd

mi = pd.read_csv("data/miller_exposure_monthly.csv", parse_dates=["month"])
mac = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
pr = pd.read_csv("data/global_policy_rates.csv", parse_dates=["date"])
OTHER = 1.12   # other costs (energy, packaging, labour) as a multiple of the wheat bill

# ---- STEP 1 · Map the exposure -------------------------------------------------------
# Costs: wheat priced in US$, paid in naira. Revenue: flour sold in naira.
print(mi.head(3)); print(mi.tail(3))
print(mi[["wheat_usd_per_tonne", "fx_ngn_usd", "gross_margin_pct"]].describe().round(1))

# ---- STEP 2 · Which risk mattered more: wheat or the naira? -----------------------------
y19 = mi[mi.month.dt.year == 2019].mean(numeric_only=True)
y25 = mi[mi.month.dt.year == 2025].mean(numeric_only=True)
log_wheat = np.log(y25.wheat_usd_per_tonne / y19.wheat_usd_per_tonne)
log_fx = np.log(y25.fx_ngn_usd / y19.fx_ngn_usd)
print(f"Wheat (US$): {log_wheat*100:+.0f} log-points | Naira: {log_fx*100:+.0f} log-points | FX share = {log_fx/(log_wheat+log_fx):.0%}")

# ---- STEP 3 · Build a 3-month forward price ---------------------------------------------
# Covered interest parity: forward = spot x (1 + (naira rate - US rate) x 3/12)
m = mac.set_index("date")[["official_fx_ngn_usd", "mpr"]].join(pr.set_index("date")[["us_fed"]])
m["us_fed"] = m.us_fed.fillna(2.5)
m["fwd_3m"] = m.official_fx_ngn_usd * (1 + (m.mpr - m.us_fed) / 100 * 3 / 12)
m["fwd_premium_pct"] = 100 * (m.fwd_3m / m.official_fx_ngn_usd - 1)
print(m.tail(3).round(1))

# ---- STEP 4 · Simulate hedge ratios ------------------------------------------------------
sim = mi.set_index("month").join(m.fwd_3m.shift(3).rename("fwd_locked"), how="left").dropna()
for h in (0, 0.25, 0.5, 0.75, 1.0):
    rate = h * sim.fwd_locked + (1 - h) * sim.fx_ngn_usd
    margin = 100 * (sim.revenue_ngn_bn - sim.imported_cost_usd_m * rate / 1e3 * OTHER) / sim.revenue_ngn_bn
    print(f"hedge {h:>4.0%}: mean {margin.mean():5.1f}%  sd {margin.std():4.1f}  worst {margin.min():5.1f}%")

# ---- STEP 5 · Sensitivity: what does a 20% shock do to the margin? -----------------------------
b = y25
def margin(fx=1, wheat=1, price=1):
    rev = b.flour_price_ngn_per_kg * price * b.flour_volume_kt * 1e6 / 1e9
    cost = b.wheat_usd_per_tonne * wheat * 1.32 * b.flour_volume_kt * 1000 / 1e6 * b.fx_ngn_usd * fx / 1e3 * OTHER
    return 100 * (rev - cost) / rev
print("base", round(margin(), 1), "| naira -20%:", round(margin(fx=1.2), 1), "| wheat +20%:", round(margin(wheat=1.2), 1),
      "| both:", round(margin(fx=1.2, wheat=1.2), 1), "| price +10% too:", round(margin(fx=1.2, wheat=1.2, price=1.1), 1))

# ---- YOUR TURN ------------------------------------------------------------------------------------
# (a) Which hedge ratio would you recommend, and why is 100% NOT the safest here? (Hint: flour prices
#     already follow the naira with a lag — a "natural hedge".)
# (b) The forward premium is about (MPR − US rate) / 4 per quarter. At a 27% MPR, what does a year of
#     rolling 3-month hedges cost? When would you accept that cost?
# (c) Score your own company's top 5 macro risks for likelihood (1–5) and impact (1–5). Which are hedgeable
#     with contracts, which with operations (pricing, sourcing, stock), and which only with capital?
