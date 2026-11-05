# =============================================================================
# EEGB · Session 10 LAB · Could our bank become the next SVB? (Python)
# Data: data/bank_balance_sheet.csv (fictional Nigerian bank, ₦ bn)
#       data/ng_yield_curves.csv (stylised FGN yield curves)
# Run from the project root, line by line.
# =============================================================================
import numpy as np, pandas as pd

bs = pd.read_csv("data/bank_balance_sheet.csv")
yc = pd.read_csv("data/ng_yield_curves.csv")

# ---- STEP 1 · Read the yield curves ---------------------------------------------------
print(yc.pivot(index="tenor_years", columns="date", values="yield_pct"))
# Which dates are upward-sloping (normal) and which are inverted (short rates above long)?

# ---- STEP 2 · Price a bond and see what a rate rise does ----------------------------------
def bond_price(coupon, yld, years, freq=2, face=100):
    n = int(round(years * freq)); c = coupon / freq * face; y = yld / freq
    t = np.arange(1, n + 1)
    return np.sum(c / (1 + y) ** t) + face / (1 + y) ** n

for y in (0.13, 0.15, 0.18, 0.20):
    print(f"10-year 13% bond at a {y:.0%} yield: price {bond_price(0.13, y, 10):.1f}")

# ---- STEP 3 · Equity and leverage -------------------------------------------------------------
A = bs[bs.side == "asset"]; L = bs[bs.side == "liability"]
TA, TL = A.amount_ngn_bn.sum(), L.amount_ngn_bn.sum(); E = TA - TL
print(f"Assets ₦{TA:,.0f}bn, liabilities ₦{TL:,.0f}bn, equity ₦{E:,.0f}bn, leverage {TA / E:.1f}x")

# ---- STEP 4 · The duration gap ------------------------------------------------------------------
DA = (A.amount_ngn_bn * A.duration_years).sum() / TA      # average life of assets (years)
DL = (L.amount_ngn_bn * L.duration_years).sum() / TL      # average life of liabilities
gap = DA - TL / TA * DL
print(f"Asset duration {DA:.2f}y, liability duration {DL:.2f}y, duration gap {gap:.2f}y")

# ---- STEP 5 · Stress test: what happens to equity if rates jump? -----------------------------------
for shock in (1, 2, 3, 5):
    dE = -gap * TA * (shock / 100) / 1.18
    print(f"+{shock} points: equity changes by ₦{dE:,.0f}bn → ₦{E + dE:,.0f}bn left")

# ---- YOUR TURN -----------------------------------------------------------------------------------------
# (a) The treasurer proposes cutting the FGN bond book from ₦1,850bn to ₦1,000bn and moving the rest to T-bills.
#     Edit the data frame and recompute the duration gap. How big a rate shock can the bank now survive?
# (b) Why do 'held to maturity' accounting rules hide this risk until depositors start to leave?
# (c) Write two sentences for the board: what is our interest-rate risk, and what one action would you take?
