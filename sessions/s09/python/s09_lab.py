# =============================================================================
# EEGB · Session 9 LAB · Is the debt the problem — or the revenue? (Python)
# Data: data/fgn_fiscal_annual.csv — stylised Federal Government finances, 2010–2025 (₦ trillion)
# Run from the project root, line by line (Ctrl/Cmd + Enter in RStudio or VS Code)
# =============================================================================
import pandas as pd

f = pd.read_csv("data/fgn_fiscal_annual.csv")

# ---- STEP 1 · Look before you calculate ------------------------------------------
print(f.columns.tolist())
print(f[["year", "nominal_gdp_ntn", "fgn_revenue_ntn", "interest_payments_ntn", "total_public_debt_ntn"]].tail(5))

# ---- STEP 2 · Three ways to measure the debt burden ----------------------------------
f["debt_to_gdp"] = f.total_public_debt_ntn / f.nominal_gdp_ntn            # the headline ratio
f["debt_to_revenue"] = f.total_public_debt_ntn / f.fgn_revenue_ntn        # years of revenue to repay
f["interest_to_revenue"] = f.interest_payments_ntn / f.fgn_revenue_ntn    # how much revenue goes on interest
print(f[["year", "debt_to_gdp", "debt_to_revenue", "interest_to_revenue"]].round(2).tail(8))

# ---- STEP 3 · r and g ---------------------------------------------------------------------
f["g"] = f.nominal_gdp_ntn.pct_change()                                   # nominal GDP growth
f["r"] = f.interest_payments_ntn / f.total_public_debt_ntn.shift(1)       # effective interest rate
print(f[["year", "r", "g"]].round(3).tail(8))
print("Years in which g > r:", f.loc[f.g > f.r, "year"].tolist())

# ---- STEP 4 · The debt-dynamics equation ------------------------------------------------------
# change in d = (r − g) / (1 + g) × d(last year)  −  primary balance / GDP  +  other ("stock-flow") items
f["d_prev"] = f.debt_to_gdp.shift(1)
f["interest_growth"] = (f.r - f.g) / (1 + f.g) * f.d_prev
f["primary"] = -f.primary_balance_ntn / f.nominal_gdp_ntn
f["other"] = (f.debt_to_gdp - f.d_prev) - f.interest_growth - f.primary
print((100 * f.set_index("year")[["interest_growth", "primary", "other"]]).round(1).tail(6))

# ---- STEP 5 · Project the next ten years -------------------------------------------------------
def project(d0, r, g, pb, years=10):
    d = d0
    for _ in range(years):
        d = (1 + r) / (1 + g) * d - pb
    return d

d0 = f.debt_to_gdp.iloc[-1]
print("Baseline (r 15%, g 17%, pb −1%):", round(100 * project(d0, .15, .17, -.01), 1), "% of GDP in 2035")
print("Reform   (r 13%, g 20%, pb +0.5%):", round(100 * project(d0, .13, .20, .005), 1), "% of GDP in 2035")

# ---- STEP 6 · What primary balance keeps debt/GDP stable? ----------------------------------------
# Set change in d = 0:  pb* = (r − g) / (1 + g) × d
for r, g in [(.15, .17), (.17, .14), (.20, .12)]:
    print(f"r = {r:.0%}, g = {g:.0%} → debt-stabilising primary balance = {100 * (r - g) / (1 + g) * d0:+.1f}% of GDP")

# ---- YOUR TURN ------------------------------------------------------------------------------------
# (a) In which year was 'other' biggest? Name two things (outside the budget) that can push debt up.
# (b) Inflation falls to 10% and nominal growth drops to 13%, but r stays at 15%. What primary balance
#     now stabilises debt? Is that realistic for Nigeria?
# (c) Revenue is about 5% of GDP. If it rose to 10% with spending unchanged, what happens to the
#     interest-to-revenue ratio? Write a two-sentence note to a bank CEO on what that means for FGN bonds.
