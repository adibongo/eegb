# =============================================================================
# EEGB · Session 1 LAB · Build a simple macro dashboard (R)
# Data: data/ng_macro_monthly.csv — stylised Nigerian macro series, Jan 2015 – Dec 2025
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
m <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE)

# ---- STEP 1 · Look before you calculate ------------------------------------------
dim(m); names(m); tail(m, 3)

# ---- STEP 2 · The latest value and the change on a year ago --------------------------
cols <- c("headline_inflation", "mpr", "official_fx_ngn_usd", "brent_usd", "fx_reserves_usd_bn", "pmi")
n <- nrow(m)
board <- tibble(indicator = cols,
                latest = unlist(m[n, cols]),
                a_year_ago = unlist(m[n - 12, cols])) |>
  mutate(change = latest - a_year_ago)
board

# ---- STEP 3 · Two derived numbers managers actually use --------------------------------
m <- m |> mutate(real_policy_rate = mpr - headline_inflation,
                 fx_premium_pct = 100 * (parallel_fx_ngn_usd / official_fx_ngn_usd - 1))
tail(select(m, date, real_policy_rate, fx_premium_pct), 6)

# ---- STEP 4 · Beware breaks in a series ----------------------------------------------------
# The CPI was rebased in January 2025: year-on-year rates before and after are NOT like-for-like.
m |> group_by(cpi_base_note) |> summarise(min = min(headline_inflation), max = max(headline_inflation),
                                          mean = mean(headline_inflation))

# ---- STEP 5 · Correlation vs causation -----------------------------------------------------
round(cor(select(m, headline_inflation, private_credit_growth_yoy, m2_growth_yoy, brent_usd)), 2)

# ---- YOUR TURN ---------------------------------------------------------------------------------
# (a) Pick the five numbers YOUR board should watch. Which two above would you drop, and what would you add?
# (b) Inflation fell from about 34% to 16% in 2025. How much of that fall is real, and how much is the rebasing?
# (c) Credit growth and inflation are highly correlated. Why does that NOT prove lending caused inflation?
# (d) Optional: download the real series with tools/fetch_official_data.R and repeat Steps 2–3.
