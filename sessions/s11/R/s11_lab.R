# =============================================================================
# EEGB · Session 11 LAB · Reading the naira: premium, BoP and currency mismatch (R)
# Data: data/ng_macro_monthly.csv, data/ng_bop_quarterly.csv (stylised teaching data)
# =============================================================================
library(dplyr); library(readr)
m <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE)
b <- read_csv("data/ng_bop_quarterly.csv", show_col_types = FALSE)

# ---- STEP 1 · The parallel-market premium by year --------------------------------------------
m <- m |> mutate(premium = 100 * (parallel_fx_ngn_usd / official_fx_ngn_usd - 1), year = as.integer(substr(date, 1, 4)))
m |> group_by(year) |> summarise(official = mean(official_fx_ngn_usd), parallel = mean(parallel_fx_ngn_usd),
                                 premium = mean(premium), reserves = mean(fx_reserves_usd_bn))

# ---- STEP 2 · The current account by year ------------------------------------------------------
b |> mutate(year = as.integer(substr(quarter, 1, 4))) |> group_by(year) |>
  summarise(across(c(trade_balance, remittances, current_account, portfolio_inflows, fdi_inflows), sum))

# ---- STEP 3 · Hot money and the real interest rate ------------------------------------------------
q <- m |> mutate(quarter = paste0(year, "Q", (as.integer(substr(date, 6, 7)) - 1) %/% 3 + 1)) |>
  group_by(quarter) |> summarise(real_rate = mean(mpr - headline_inflation))
bq <- inner_join(b, q, by = "quarter")
cor(bq$portfolio_inflows, bq$real_rate)

# ---- STEP 4 · Currency mismatch: a US$10m loan ------------------------------------------------------
m |> filter(date %in% c("2023-01-01", "2023-07-01", "2024-01-01", "2024-07-01", "2025-01-01")) |>
  transmute(date, debt_ngn_bn = 10e6 * official_fx_ngn_usd / 1e9)

# ---- YOUR TURN -------------------------------------------------------------------------------------
# (a) Which corner of the impossible trinity did Nigeria give up before 2023, and which after?
# (b) US$10m at 8% vs ₦4.5bn at 18% in January 2023: which was cheaper two years later, in naira?
# (c) One paragraph for your CFO: three signals that the naira is under pressure, and where to find them.
