# =============================================================================
# EEGB · Session 13 LAB · What would a carbon price do to our sector? (Python)
# Data: data/firm_carbon_exposure.csv — 40 fictional Nigerian listed companies (stylised)
# Run from the project root, line by line.
# =============================================================================
import pandas as pd

f = pd.read_csv("data/firm_carbon_exposure.csv")
FX = 1500                                  # assumed ₦ per US$ — change it and see what happens

# ---- STEP 1 · Look at the data --------------------------------------------------------
print(f.head()); print(f.sector.value_counts())
# scope 1 = direct emissions (kilns, generators, flaring); scope 2 = purchased electricity

# ---- STEP 2 · Total emissions and intensity ------------------------------------------------
f["emissions_t"] = (f.scope1_kt_co2e + f.scope2_kt_co2e) * 1000
f["intensity"] = f.emissions_t / (f.revenue_ngn_bn * 1000)        # tonnes per ₦1 million of revenue
print(f.groupby("sector").intensity.mean().sort_values().round(2))

# ---- STEP 3 · The carbon bill at three prices ------------------------------------------------
for p in (25, 50, 100):
    f[f"bill_{p}"] = f.emissions_t * p * FX / 1e9                   # ₦ bn
    f[f"pct_ebitda_{p}"] = 100 * f[f"bill_{p}"] / f.ebitda_ngn_bn
sec = f.groupby("sector")[["bill_50", "ebitda_ngn_bn"]].sum()
sec["pct_ebitda_50"] = 100 * sec.bill_50 / sec.ebitda_ngn_bn
print(sec.sort_values("pct_ebitda_50", ascending=False).round(1))

# ---- STEP 4 · Which firms are most exposed? ------------------------------------------------------
print(f.sort_values("pct_ebitda_50", ascending=False)[["firm_id", "sector", "pct_ebitda_50", "publishes_tcfd"]].head(10).round(1))

# ---- STEP 5 · Who discloses? --------------------------------------------------------------------
print(f.groupby("sector").publishes_tcfd.mean().round(2))

# ---- YOUR TURN -------------------------------------------------------------------------------------
# (a) Repeat Step 3 with FX = 1,000 and FX = 2,000. Why does the naira exchange rate change a carbon bill set in dollars?
# (b) A cement firm can cut 30% of its emissions at US$20/t. Recompute its bill at US$50/t. Is the investment worth it?
# (c) Write three sentences for a cement board: our exposure, what customers will bear, and our first two actions.
