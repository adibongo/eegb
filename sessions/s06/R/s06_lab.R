# =============================================================================
# EEGB · Session 6 LAB · Demand shock or supply shock? Diagnosing Nigeria's inflation (R)
# Data: data/ng_macro_monthly.csv — stylised Nigerian macro series, Jan 2015 – Dec 2025
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
m <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
old <- m |> filter(date < as.Date("2025-01-01"))   # one CPI base only: the 2025 rebasing breaks the series

# ---- STEP 1 · Describe the inflation episode -----------------------------------------
old |> mutate(episode = case_when(date >= as.Date("2022-01-01") & date <= as.Date("2023-05-01") ~ "Jan 2022 – May 2023",
                                  date >= as.Date("2023-06-01") ~ "Jun 2023 – Dec 2024")) |>
  filter(!is.na(episode)) |> group_by(episode) |>
  summarise(headline = mean(headline_inflation), food = mean(food_inflation), core = mean(core_inflation), pmi = mean(pmi))

# ---- STEP 2 · Food minus core -------------------------------------------------------------
old <- old |> mutate(food_core_gap = food_inflation - core_inflation)
old |> group_by(year = format(date, "%Y")) |> summarise(gap = round(mean(food_core_gap), 1))

# ---- STEP 3 · Exchange-rate pass-through ----------------------------------------------
old <- old |> mutate(depreciation_yoy = 100 * (official_fx_ngn_usd / lag(official_fx_ngn_usd, 12) - 1))
for (k in c(0, 2, 4, 6, 9, 12)) {
  r <- cor(lag(old$depreciation_yoy, k), old$headline_inflation, use = "complete.obs")
  cat(sprintf("correlation of inflation with depreciation %2d months earlier: %.2f\n", k, r))
}

# ---- STEP 4 · Persistence ------------------------------------------------------------------
old <- old |> mutate(lag12 = lag(headline_inflation, 12))
fit <- lm(headline_inflation ~ lag12, data = old)
coef(fit)          # inflation now = intercept + slope x inflation a year ago

# ---- STEP 5 · A real interest rate check ----------------------------------------------------
old |> mutate(real_rate = mpr - headline_inflation) |> select(date, mpr, headline_inflation, real_rate) |> tail(6)

# ---- YOUR TURN ---------------------------------------------------------------------------------
# (a) Was the 2023–24 surge mainly a demand shock, a supply shock, or both? Cite at least two numbers.
# (b) If it was mostly a supply shock, what does raising the policy rate achieve — and what does it cost?
# (c) Using the slope in Step 4, what inflation would you plan for next year if this year's is 30%?
