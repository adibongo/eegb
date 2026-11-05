# =============================================================================
# EEGB · Session 11 LAB · Reading the naira: premium, BoP and currency mismatch (Python)
# Data: data/ng_macro_monthly.csv, data/ng_bop_quarterly.csv (stylised teaching data)
# Run from the project root, line by line.
# =============================================================================
import pandas as pd

m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
b = pd.read_csv("data/ng_bop_quarterly.csv")

# ---- STEP 1 · The parallel-market premium ------------------------------------------------
m["premium"] = 100 * (m.parallel_fx_ngn_usd / m.official_fx_ngn_usd - 1)
m["year"] = m.date.dt.year
print(m.groupby("year")[["official_fx_ngn_usd", "parallel_fx_ngn_usd", "premium", "fx_reserves_usd_bn"]].mean().round(1))
# When was the premium highest? What happened to reserves in those years?

# ---- STEP 2 · Build the current account ------------------------------------------------------
print(b[["quarter", "trade_balance", "remittances", "services_income_net", "current_account"]].tail(8))
b["year"] = b.quarter.str[:4].astype(int)
print(b.groupby("year")[["trade_balance", "remittances", "current_account", "portfolio_inflows", "fdi_inflows"]].sum().round(1))

# ---- STEP 3 · Hot money and the real interest rate -----------------------------------------------
m["real_rate"] = m.mpr - m.headline_inflation
q = m.set_index("date").resample("QS").real_rate.mean().reset_index()
b["date"] = pd.PeriodIndex(b.quarter, freq="Q").to_timestamp()
bq = b.merge(q, on="date")
print("correlation, portfolio inflows vs real rate:", round(bq.portfolio_inflows.corr(bq.real_rate), 2))

# ---- STEP 4 · Currency mismatch: a US$10m loan, naira revenues ----------------------------------
fx = m.set_index("date").official_fx_ngn_usd
for d in ["2023-01-01", "2023-07-01", "2024-01-01", "2024-07-01", "2025-01-01"]:
    print(d, f"debt in naira: ₦{10e6 * fx[d] / 1e9:.1f}bn")

# ---- YOUR TURN -------------------------------------------------------------------------------------
# (a) Name the three corners of the impossible trinity. Which corner did Nigeria give up before 2023, and which after?
# (b) A firm borrowed US$10m in January 2023 at 8% instead of ₦4.5bn at 18%. Was the dollar loan cheaper in the end?
#     (Hint: compare the naira cost of interest + principal two years later.)
# (c) Write one paragraph for your CFO: three signals that the naira is under pressure, and where to find them.
