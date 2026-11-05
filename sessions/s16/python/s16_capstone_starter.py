# =============================================================================
# EEGB · Session 16 · CAPSTONE STARTER — build the evidence pack for your board memo (Python)
# Data: data/ng_macro_monthly.csv and any industry file from the course (all stylised teaching data)
# Run from the project root. Change the settings in STEP 1, then run the whole file.
# Output: sessions/s16/figures/python/capstone_evidence_pack.png + a printed evidence table
# =============================================================================
import sys; sys.path.insert(0, "python")
import pandas as pd
import matplotlib.pyplot as plt
from eegb_style import *

set_style()

# ---- STEP 1 · Choose your industry and its macro drivers ----------------------------------------
INDUSTRY = "Cement"                      # e.g. "Flour milling", "Banking", "Consumer goods", "Telecoms"
DRIVERS = {                              # column in ng_macro_monthly.csv : why it matters to the industry
    "official_fx_ngn_usd": "imported energy, spare parts and kiln inputs",
    "headline_inflation": "construction costs and household purchasing power",
    "mpr": "mortgage and developer credit",
    "pmi": "early signal of construction activity",
}

# ---- STEP 2 · Load the data and compute the evidence ----------------------------------------------
m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
latest, year_ago = m.iloc[-1], m.iloc[-13]
ev = pd.DataFrame({"driver": list(DRIVERS), "why it matters": list(DRIVERS.values()),
                   "latest": [latest[c] for c in DRIVERS], "a year ago": [year_ago[c] for c in DRIVERS]})
ev["change"] = ev["latest"] - ev["a year ago"]
pd.set_option("display.width", 160)
print(f"\nEVIDENCE TABLE — {INDUSTRY}\n", ev.round(2).to_string(index=False))

# ---- STEP 3 · One page of charts (last five years) --------------------------------------------------
w = m[m.date >= m.date.max() - pd.DateOffset(years=5)]
fig, axes = plt.subplots(2, 2, figsize=(12, 6.5), sharex=True)
for ax, (col, why), c in zip(axes.flat, DRIVERS.items(), [RUST, NAVY, TEAL, GOLD]):
    ax.plot(w.date, w[col], color=c, lw=2.3)
    ax.set_title(f"{col}: {latest[col]:,.1f}\n({why})", fontsize=11.5, loc="left")
fig.suptitle(f"Macro evidence pack — {INDUSTRY}", x=0.01, ha="left", fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig)
save(fig, "s16", "capstone_evidence_pack")

# ---- STEP 4 · Draft your memo (fill in, then rewrite in your own words) -------------------------------
print(f"""
MEMO TO THE BOARD — {INDUSTRY}
1. Recommendation (one sentence): ...
2. What has changed in the economy (three numbers from the evidence table): ...
3. What it means for us (prices, volumes, costs, financing): ...
4. Scenarios for the next 12 months (upside / base / downside, with probabilities): ...
5. Signposts and triggers we will watch: ...
6. Actions and owners (pricing, hedging, capex, financing): ...
""")

# ---- YOUR TURN -------------------------------------------------------------------------------------------
# (a) Replace INDUSTRY and DRIVERS with your own industry and the four macro drivers that matter most to it.
# (b) Add one industry dataset from data/ (e.g. cement_demand_monthly.csv or miller_exposure_monthly.csv) to the pack.
# (c) Write the memo in no more than one page. Lead with the recommendation.
