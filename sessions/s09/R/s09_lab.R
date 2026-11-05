# =============================================================================
# EEGB · Session 9 LAB · Is the debt the problem — or the revenue? (R)
# Data: data/fgn_fiscal_annual.csv — stylised Federal Government finances, 2010–2025 (₦ trillion)
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
f <- read_csv("data/fgn_fiscal_annual.csv", show_col_types = FALSE)

# ---- STEP 1 · Look before you calculate ------------------------------------------
names(f)
tail(select(f, year, nominal_gdp_ntn, fgn_revenue_ntn, interest_payments_ntn, total_public_debt_ntn), 5)

# ---- STEP 2 · Three ways to measure the debt burden ----------------------------------
f <- f |> mutate(debt_to_gdp = total_public_debt_ntn / nominal_gdp_ntn,          # the headline ratio
                 debt_to_revenue = total_public_debt_ntn / fgn_revenue_ntn,      # years of revenue to repay
                 interest_to_revenue = interest_payments_ntn / fgn_revenue_ntn)  # share of revenue on interest
tail(select(f, year, debt_to_gdp, debt_to_revenue, interest_to_revenue), 8)

# ---- STEP 3 · r and g ---------------------------------------------------------------------
f <- f |> mutate(g = nominal_gdp_ntn / lag(nominal_gdp_ntn) - 1,                 # nominal GDP growth
                 r = interest_payments_ntn / lag(total_public_debt_ntn))         # effective interest rate
tail(select(f, year, r, g), 8)
f$year[which(f$g > f$r)]                                                         # years in which g > r

# ---- STEP 4 · The debt-dynamics equation ------------------------------------------------------
# change in d = (r − g) / (1 + g) × d(last year)  −  primary balance / GDP  +  other ("stock-flow") items
f <- f |> mutate(d_prev = lag(debt_to_gdp),
                 interest_growth = (r - g) / (1 + g) * d_prev,
                 primary = -primary_balance_ntn / nominal_gdp_ntn,
                 other = (debt_to_gdp - d_prev) - interest_growth - primary)
f |> select(year, interest_growth, primary, other) |> mutate(across(-year, ~ round(100 * .x, 1))) |> tail(6)

# ---- STEP 5 · Project the next ten years -------------------------------------------------------
project <- function(d0, r, g, pb, years = 10) {
  d <- d0
  for (i in 1:years) d <- (1 + r) / (1 + g) * d - pb
  d
}
d0 <- tail(f$debt_to_gdp, 1)
round(100 * project(d0, .15, .17, -.01), 1)    # baseline, % of GDP in 2035
round(100 * project(d0, .13, .20, .005), 1)    # reform

# ---- STEP 6 · What primary balance keeps debt/GDP stable? ----------------------------------------
# Set change in d = 0:  pb* = (r − g) / (1 + g) × d
stab <- tibble(r = c(.15, .17, .20), g = c(.17, .14, .12)) |>
  mutate(pb_star_pct_gdp = round(100 * (r - g) / (1 + g) * d0, 1))
stab

# ---- YOUR TURN ------------------------------------------------------------------------------------
# (a) In which year was 'other' biggest? Name two things (outside the budget) that can push debt up.
# (b) Inflation falls to 10% and nominal growth drops to 13%, but r stays at 15%. What primary balance
#     now stabilises debt? Is that realistic for Nigeria?
# (c) Revenue is about 5% of GDP. If it rose to 10% with spending unchanged, what happens to the
#     interest-to-revenue ratio? Write a two-sentence note to a bank CEO on what that means for FGN bonds.
