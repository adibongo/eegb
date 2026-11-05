# =============================================================================
# EEGB · Session 15 LAB · A hedging plan for a flour miller (R)
# Data: data/miller_exposure_monthly.csv — stylised miller, Jan 2019 – Dec 2025
#       data/ng_macro_monthly.csv and data/global_policy_rates.csv — for forward prices
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
mi  <- read_csv("data/miller_exposure_monthly.csv", show_col_types = FALSE) |> mutate(month = as.Date(month))
mac <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
pr  <- read_csv("data/global_policy_rates.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
OTHER <- 1.12   # other costs (energy, packaging, labour) as a multiple of the wheat bill

# ---- STEP 1 · Map the exposure -------------------------------------------------------
head(mi, 3); tail(mi, 3)
summary(select(mi, wheat_usd_per_tonne, fx_ngn_usd, gross_margin_pct))

# ---- STEP 2 · Which risk mattered more: wheat or the naira? -----------------------------
yr <- mi |> mutate(y = format(month, "%Y")) |> filter(y %in% c("2019", "2025")) |>
  group_by(y) |> summarise(w = mean(wheat_usd_per_tonne), f = mean(fx_ngn_usd))
lw <- log(yr$w[2] / yr$w[1]); lf <- log(yr$f[2] / yr$f[1])
cat(sprintf("Wheat: %+.0f log-points | Naira: %+.0f log-points | FX share = %.0f%%\n", 100 * lw, 100 * lf, 100 * lf / (lw + lf)))

# ---- STEP 3 · Build a 3-month forward price ---------------------------------------------
# Covered interest parity: forward = spot x (1 + (naira rate - US rate) x 3/12)
m <- mac |> select(date, official_fx_ngn_usd, mpr) |> left_join(select(pr, date, us_fed), by = "date") |>
  mutate(us_fed = coalesce(us_fed, 2.5),
         fwd_3m = official_fx_ngn_usd * (1 + (mpr - us_fed) / 100 * 3 / 12),
         fwd_premium_pct = 100 * (fwd_3m / official_fx_ngn_usd - 1),
         fwd_locked = lag(fwd_3m, 3))
tail(m, 3)

# ---- STEP 4 · Simulate hedge ratios ------------------------------------------------------
sim <- mi |> left_join(select(m, date, fwd_locked), by = c("month" = "date")) |> filter(!is.na(fwd_locked))
for (h in c(0, 0.25, 0.5, 0.75, 1)) {
  rate <- h * sim$fwd_locked + (1 - h) * sim$fx_ngn_usd
  margin <- 100 * (sim$revenue_ngn_bn - sim$imported_cost_usd_m * rate / 1e3 * OTHER) / sim$revenue_ngn_bn
  cat(sprintf("hedge %3.0f%%: mean %5.1f%%  sd %4.1f  worst %5.1f%%\n", 100 * h, mean(margin), sd(margin), min(margin)))
}

# ---- STEP 5 · Sensitivity: what does a 20% shock do to the margin? -----------------------------
b <- mi |> filter(format(month, "%Y") == "2025") |> summarise(across(where(is.numeric), mean))
marg <- function(fx = 1, wheat = 1, price = 1) {
  rev  <- b$flour_price_ngn_per_kg * price * b$flour_volume_kt * 1e6 / 1e9
  cost <- b$wheat_usd_per_tonne * wheat * 1.32 * b$flour_volume_kt * 1000 / 1e6 * b$fx_ngn_usd * fx / 1e3 * OTHER
  100 * (rev - cost) / rev
}
c(base = marg(), naira_minus20 = marg(fx = 1.2), wheat_plus20 = marg(wheat = 1.2),
  both = marg(fx = 1.2, wheat = 1.2), both_with_price_up10 = marg(fx = 1.2, wheat = 1.2, price = 1.1))

# ---- YOUR TURN ------------------------------------------------------------------------------------
# (a) Which hedge ratio would you recommend, and why is 100% NOT the safest here?
# (b) The forward premium is about (MPR − US rate) / 4 per quarter. What does a year of rolling 3-month
#     hedges cost at a 27% MPR? When would you accept that cost?
# (c) Score your own company's top 5 macro risks (likelihood 1–5, impact 1–5). Which are hedgeable with
#     contracts, which with operations (pricing, sourcing, stock), and which only with capital?
