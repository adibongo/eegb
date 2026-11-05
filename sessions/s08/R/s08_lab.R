# =============================================================================
# EEGB · Session 8 LAB · How fast does the policy rate reach your firm? (R)
# Data: data/ng_macro_monthly.csv and data/global_policy_rates.csv (stylised)
# Open eegb.Rproj first, then run line by line
# =============================================================================
library(dplyr); library(readr)
m  <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
pr <- read_csv("data/global_policy_rates.csv", show_col_types = FALSE)

# ---- STEP 1 · List every CBN policy-rate decision ------------------------------------
moves <- m |> mutate(change_pts = mpr - lag(mpr)) |> filter(is.na(change_pts) | change_pts != 0) |> select(date, mpr, change_pts)
tail(moves, 12)

# ---- STEP 2 · Real policy rate --------------------------------------------------------------
m <- m |> mutate(real_mpr = mpr - headline_inflation, year = format(date, "%Y"))
m |> group_by(year) |> summarise(real_mpr = round(mean(real_mpr), 1))

# ---- STEP 3 · Liquidity: interbank minus MPR ----------------------------------------------------
m |> mutate(interbank_gap = interbank_rate - mpr) |> group_by(year) |> summarise(gap = round(mean(interbank_gap), 1))

# ---- STEP 4 · Transmission lags ----------------------------------------------------------------
m <- m |> mutate(mpr_change_12m = mpr - lag(mpr, 12))
for (k in c(0, 3, 6, 9, 12, 18)) {
  r <- cor(m$mpr_change_12m, lead(m$private_credit_growth_yoy, k), use = "complete.obs")
  cat(sprintf("MPR change vs credit growth %2d months later: r = %.2f\n", k, r))
}

# ---- STEP 5 · Compare with peers ------------------------------------------------------------------
sort(unlist(pr[nrow(pr), -1]), decreasing = TRUE)

# ---- STEP 6 · An illustrative Taylor rule ----------------------------------------------------------
target <- 9; neutral_real <- 2
m |> filter(date < as.Date("2025-01-01")) |>
  mutate(taylor = neutral_real + headline_inflation + 0.5 * (headline_inflation - target) + 0.5 * (pmi - 50)) |>
  select(date, mpr, headline_inflation, taylor) |> tail(6)

# ---- YOUR TURN ---------------------------------------------------------------------------------------
# (a) A ₦5bn overdraft priced at MPR + 6 points: how much did annual interest rise between June 2023 and December 2024?
# (b) Why can correlation alone (Step 4) not prove the transmission lag? What else moved at the same time?
# (c) Give two reasons a central bank facing a SUPPLY shock might choose not to follow the Taylor rule.
