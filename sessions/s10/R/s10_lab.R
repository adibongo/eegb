# =============================================================================
# EEGB · Session 10 LAB · Could our bank become the next SVB? (R)
# Data: data/bank_balance_sheet.csv (fictional Nigerian bank, ₦ bn), data/ng_yield_curves.csv
# =============================================================================
library(dplyr); library(readr); library(tidyr)
bs <- read_csv("data/bank_balance_sheet.csv", show_col_types = FALSE)
yc <- read_csv("data/ng_yield_curves.csv", show_col_types = FALSE)

# ---- STEP 1 · Read the yield curves ---------------------------------------------------
yc |> pivot_wider(names_from = date, values_from = yield_pct)
# Which dates are upward-sloping (normal) and which are inverted?

# ---- STEP 2 · Price a bond and see what a rate rise does ----------------------------------
bond_price <- function(coupon, yld, years, freq = 2, face = 100) {
  n <- round(years * freq); c <- coupon / freq * face; y <- yld / freq; t <- seq_len(n)
  sum(c / (1 + y)^t) + face / (1 + y)^n
}
for (y in c(.13, .15, .18, .20)) cat(sprintf("10-year 13%% bond at a %.0f%% yield: price %.1f\n", 100 * y, bond_price(.13, y, 10)))

# ---- STEP 3 · Equity and leverage -------------------------------------------------------------
A <- filter(bs, side == "asset"); L <- filter(bs, side == "liability")
TA <- sum(A$amount_ngn_bn); TL <- sum(L$amount_ngn_bn); E <- TA - TL
cat(sprintf("Assets %.0f, liabilities %.0f, equity %.0f (₦ bn); leverage %.1fx\n", TA, TL, E, TA / E))

# ---- STEP 4 · The duration gap ------------------------------------------------------------------
DA <- sum(A$amount_ngn_bn * A$duration_years) / TA
DL <- sum(L$amount_ngn_bn * L$duration_years) / TL
gap <- DA - TL / TA * DL
cat(sprintf("Asset duration %.2fy, liability duration %.2fy, gap %.2fy\n", DA, DL, gap))

# ---- STEP 5 · Stress test ---------------------------------------------------------------------------
tibble(shock = c(1, 2, 3, 5)) |> mutate(change_in_equity = -gap * TA * (shock / 100) / 1.18,
                                        equity_left = E + change_in_equity)

# ---- YOUR TURN -----------------------------------------------------------------------------------------
# (a) Cut the FGN bond book from ₦1,850bn to ₦1,000bn and move the rest to T-bills. Recompute the gap.
# (b) Why do 'held to maturity' rules hide this risk until depositors start to leave?
# (c) Two sentences for the board: our interest-rate risk, and one action you would take.
