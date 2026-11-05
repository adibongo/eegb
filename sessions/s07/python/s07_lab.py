# =============================================================================
# EEGB · Session 7 LAB · Is Nigeria getting richer? Reading the national accounts (Python)
# Data: data/ng_gdp_sectors.csv — stylised real GDP by sector (₦ tn, 2010 prices), 2010–2025
#       data/peer_income.csv   — stylised cross-country snapshot
# Run from the project root, line by line
# =============================================================================
import numpy as np, pandas as pd

g = pd.read_csv("data/ng_gdp_sectors.csv")
peers = pd.read_csv("data/peer_income.csv")

# ---- STEP 1 · Real growth, year by year -------------------------------------------
g["real_growth_pct"] = 100 * g.real_gdp_total.pct_change()
print(g[["year", "real_gdp_total", "real_growth_pct"]].round(2))

# ---- STEP 2 · Oil vs non-oil ----------------------------------------------------------
g["non_oil"] = g.real_gdp_total - g.oil_and_gas
g["oil_growth_pct"] = 100 * g.oil_and_gas.pct_change()
g["non_oil_growth_pct"] = 100 * g.non_oil.pct_change()
print(g[["year", "oil_growth_pct", "non_oil_growth_pct"]].round(1).tail(6))

# ---- STEP 3 · Which sectors grew fastest? (average annual growth 2010–2025) -----------------
sectors = ["agriculture", "oil_and_gas", "manufacturing", "construction", "trade", "ict_telecom",
           "finance_insurance", "real_estate", "public_admin", "other_services"]
years = g.year.iloc[-1] - g.year.iloc[0]
cagr = 100 * ((g[sectors].iloc[-1] / g[sectors].iloc[0]) ** (1 / years) - 1)
print(cagr.sort_values(ascending=False).round(1))

# ---- STEP 4 · Per person: is the average Nigerian better off? ----------------------------------
g["gdp_per_person_naira"] = g.real_gdp_total * 1e12 / (g.population_m * 1e6)
pc_growth = 100 * ((g.gdp_per_person_naira.iloc[-1] / g.gdp_per_person_naira.iloc[0]) ** (1 / years) - 1)
print(f"real GDP per person grew {pc_growth:.2f}% a year; years to double at that rate: {np.log(2)/np.log(1+pc_growth/100):.0f}")

# ---- STEP 5 · Nominal vs real, and the GDP deflator ---------------------------------------------
g["deflator"] = 100 * g.nominal_gdp_old_base / g.real_gdp_total
g["deflator_inflation_pct"] = 100 * g.deflator.pct_change()
print(g[["year", "nominal_gdp_old_base", "real_gdp_total", "deflator", "deflator_inflation_pct"]].round(1).tail(5))

# ---- STEP 6 · Market rates vs PPP across peers ------------------------------------------------------
peers["ppp_ratio"] = peers.gdp_per_capita_ppp / peers.gdp_per_capita_usd
print(peers.sort_values("ppp_ratio", ascending=False)[["country", "gdp_per_capita_usd", "gdp_per_capita_ppp", "ppp_ratio"]])

# ---- YOUR TURN ---------------------------------------------------------------------------------------
# (a) Your board says "Nigeria's GDP grew 50% since 2010, so our market grew 50%". Using Steps 1 and 4, reply in two sentences.
# (b) Which two sectors would you bet on for a B2B business, and why? Use Step 3.
# (c) A foreign investor compares Nigeria and Ghana at market exchange rates. Why might PPP give a different picture
#     of the size of the consumer market — and which measure should they use to price a product?
