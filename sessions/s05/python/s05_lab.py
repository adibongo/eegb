# =============================================================================
# EEGB · Session 5 LAB · Who gained from the petrol subsidy, and who pays for its removal? (Python)
# Data: data/fuel_subsidy_incidence.csv — stylised household budgets by consumption decile
# Run from the project root, line by line (Ctrl/Cmd + Enter)
# =============================================================================
import pandas as pd

h = pd.read_csv("data/fuel_subsidy_incidence.csv")
print(h)                      # D1 = poorest 10% of households ... D10 = richest 10%

# ---- STEP 1 · The subsidy each household received ------------------------------------------
h["subsidy"] = h.petrol_litres_month * h.subsidy_per_litre_pre          # ₦ per household per month
h["share_of_subsidy"] = 100 * h.subsidy / h.subsidy.sum()
h["subsidy_pct_budget"] = 100 * h.subsidy / h.monthly_spend_naira
print(h[["decile", "subsidy", "share_of_subsidy", "subsidy_pct_budget"]].round(1))

# ---- STEP 2 · Who got most of it? -------------------------------------------------------------------
print(f"Richest 10% got {h.share_of_subsidy.iloc[-1]:.0f}% ; poorest 40% got {h.share_of_subsidy.iloc[:4].sum():.0f}%")

# ---- STEP 3 · The cost of removal: direct + indirect ------------------------------------------------
fare_rise, food_rise = 0.50, 0.10                                         # your assumptions — change them!
h["direct_pct"] = 100 * h.petrol_litres_month * (h.pump_price_post - h.pump_price_pre) / h.monthly_spend_naira
h["indirect_pct"] = 100 * (h.transport_share * fare_rise + h.food_share * food_rise)
h["total_pct"] = h.direct_pct + h.indirect_pct
print(h[["decile", "direct_pct", "indirect_pct", "total_pct"]].round(1))

# ---- STEP 4 · The fiscal saving and a targeted cash transfer ---------------------------------------------
annual = (h.subsidy * h.households_m * 1e6 * 12).sum() / 1e12
transfer = 10_000
cost = 4 * h.households_m.iloc[0] * 1e6 * transfer * 12 / 1e12
print(f"Subsidy cost ₦{annual:.1f}tn a year; transfer to poorest 40% costs ₦{cost:.2f}tn")
h["net_with_transfer"] = -h.total_pct + (h.decile <= 4) * 100 * transfer / h.monthly_spend_naira
print(h[["decile", "net_with_transfer"]].round(1))

# ---- YOUR TURN ------------------------------------------------------------------------------------------------
# (a) Change fare_rise and food_rise. How sensitive is the burden on D1–D4 to these assumptions?
# (b) What transfer (₦ per month) leaves D3 and D4 no worse off? What does it cost?
# (c) Name two practical problems with targeting cash to the poorest 40% in Nigeria, and one way to solve each.
# (d) In two sentences: should the savings go to transfers, transport (e.g. CNG buses), or reducing the deficit?
