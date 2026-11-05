# =============================================================================
# EEGB · Session 1 LAB · Build the board's macro page (Python)
# Data: data/official/ng_official_monthly.csv — OFFICIAL CBN series (CPI, MPR, T-bill, N/$, reserves)
#       plus FRED Brent. Refresh with:  python tools/fetch_official_data.py
# Run from the project root, line by line (Ctrl/Cmd + Enter in RStudio or VS Code)
# =============================================================================
import pandas as pd

m = pd.read_csv("data/official/ng_official_monthly.csv", parse_dates=["date"]).set_index("date")

# ---- STEP 1 · Look before you calculate --------------------------------------------------
print(m.columns.tolist())                       # what is measured?
print(m.tail(3))                                # the latest rows — note the gaps (NaN)
print(m.apply(lambda s: s.last_valid_index()))  # each series has its OWN latest date

# ---- STEP 2 · Latest value, value a year ago, change ---------------------------------------
cols = {"cpi_headline_yoy": "pp", "cpi_core_yoy": "pp", "policy_rate": "pp",
        "usd_official_avg": "₦", "reserves_gross_usdbn": "$bn", "brent": "$"}
rows = []
for c, unit in cols.items():
    s = m[c].dropna()
    last = s.index[-1]; ago = s.loc[: last - pd.DateOffset(months=12)]
    rows.append({"indicator": c, "date": f"{last:%b %Y}", "latest": s.iloc[-1],
                 "a_year_ago": ago.iloc[-1], "change": s.iloc[-1] - ago.iloc[-1], "unit_of_change": unit})
board = pd.DataFrame(rows).set_index("indicator").round(2)
print(board)

# ---- STEP 3 · Two derived numbers ---------------------------------------------------------------
# (a) Real policy rate — EXACT Fisher formula, not the "minus" shortcut
m["real_policy_rate"] = ((1 + m.policy_rate / 100) / (1 + m.cpi_headline_yoy / 100) - 1) * 100
print(m["real_policy_rate"].dropna().tail(6).round(1))
# (b) Your firm's real revenue growth — replace with your own numbers
nominal_growth, inflation = 0.30, 0.3324          # FY2024: naira sales +30%; 2024 average CPI inflation
print(f"Real revenue growth: {(1 + nominal_growth) / (1 + inflation) - 1:.1%}")

# ---- STEP 4 · Beware breaks in a series -------------------------------------------------------------
# NBS moved to a new CPI (2024 = 100) in January 2025 and revised the 2025 figures in December 2025.
# Year-on-year rates either side of January 2025 are NOT like-for-like.
seg = m["cpi_headline_yoy"].dropna()
print(pd.DataFrame({"old CPI (to Dec 2024)": seg[:"2024-12"].tail(3), "new CPI (from Jan 2025)": seg["2025-01":].head(3)}))

# ---- STEP 5 · Correlation is not causation ------------------------------------------------------------
d = m[["brent", "reserves_gross_usdbn"]].loc["2015":].dropna()
print("Oil vs reserves, same month:", round(d.brent.corr(d.reserves_gross_usdbn), 2))
print("Oil vs reserves 12 months later:", round(d.brent.corr(d.reserves_gross_usdbn.shift(-12)), 2))

# ---- YOUR TURN ------------------------------------------------------------------------------------------
# (a) Which six numbers should YOUR board watch? Drop two of the above if needed and say what you would add.
# (b) Under each number write one 'so what' line, using the macro-to-P&L map from the slides.
# (c) Oil earns most of Nigeria's dollars, yet the correlation with reserves is modest. Give two reasons.
# (d) Redo Step 3(b) with your own company's revenue — in naira, in real terms and in dollars.
