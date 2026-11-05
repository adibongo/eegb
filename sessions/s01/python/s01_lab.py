# =============================================================================
# EEGB · Session 1 LAB · Build a simple macro dashboard (Python)
# Data: data/ng_macro_monthly.csv — stylised Nigerian macro series, Jan 2015 – Dec 2025
# Run from the project root, line by line (Ctrl/Cmd + Enter in RStudio or VS Code)
# =============================================================================
import pandas as pd

m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])

# ---- STEP 1 · Look before you calculate ------------------------------------------
print(m.shape)            # how many months and columns?
print(m.columns.tolist()) # what is measured?
print(m.tail(3))          # the latest readings

# ---- STEP 2 · The latest value and the change on a year ago --------------------------
cols = ["headline_inflation", "mpr", "official_fx_ngn_usd", "brent_usd", "fx_reserves_usd_bn", "pmi"]
latest, year_ago = m.iloc[-1], m.iloc[-13]
board = pd.DataFrame({"latest": latest[cols], "a_year_ago": year_ago[cols]})
board["change"] = board.latest - board.a_year_ago
print(board)

# ---- STEP 3 · Two derived numbers managers actually use --------------------------------
m["real_policy_rate"] = m.mpr - m.headline_inflation                       # positive = savers beat inflation
m["fx_premium_pct"] = 100 * (m.parallel_fx_ngn_usd / m.official_fx_ngn_usd - 1)
print(m[["date", "real_policy_rate", "fx_premium_pct"]].tail(6))

# ---- STEP 4 · Beware breaks in a series ----------------------------------------------------
# The CPI was rebased in January 2025. Year-on-year rates before and after are NOT like-for-like.
print(m.groupby("cpi_base_note").headline_inflation.agg(["min", "max", "mean"]))

# ---- STEP 5 · Correlation vs causation -----------------------------------------------------
print(m[["headline_inflation", "private_credit_growth_yoy", "m2_growth_yoy", "brent_usd"]].corr().round(2))

# ---- YOUR TURN ---------------------------------------------------------------------------------
# (a) Pick the five numbers YOUR board should watch. Which two above would you drop, and what would you add?
# (b) Inflation fell from about 34% to 16% in 2025. How much of that fall is real, and how much is the rebasing?
# (c) Credit growth and inflation are highly correlated. Write one sentence on why that does NOT prove
#     that bank lending caused the inflation. Name one third factor that could drive both.
# (d) Optional: download the real series with tools/fetch_official_data.py and repeat Steps 2–3.
