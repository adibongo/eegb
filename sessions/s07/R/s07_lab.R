# =============================================================================
# EEGB · Session 7 LAB · Is Nigeria getting richer? Reading the national accounts (R)
# Data: data/ng_gdp_sectors.csv — stylised real GDP by sector (₦ tn, 2010 prices), 2010–2025
#       data/peer_income.csv   — stylised cross-country snapshot
# Open eegb.Rproj first, then run line by line
# =============================================================================
library(dplyr); library(readr)
g <- read_csv("data/ng_gdp_sectors.csv", show_col_types = FALSE)
peers <- read_csv("data/peer_income.csv", show_col_types = FALSE)

# ---- STEP 1 · Real growth, year by year -------------------------------------------
g <- g |> mutate(real_growth_pct = 100 * (real_gdp_total / lag(real_gdp_total) - 1))
select(g, year, real_gdp_total, real_growth_pct)

# ---- STEP 2 · Oil vs non-oil ----------------------------------------------------------
g <- g |> mutate(non_oil = real_gdp_total - oil_and_gas,
                 oil_growth_pct = 100 * (oil_and_gas / lag(oil_and_gas) - 1),
                 non_oil_growth_pct = 100 * (non_oil / lag(non_oil) - 1))
tail(select(g, year, oil_growth_pct, non_oil_growth_pct), 6)

# ---- STEP 3 · Which sectors grew fastest? ---------------------------------------------------
sectors <- c("agriculture", "oil_and_gas", "manufacturing", "construction", "trade", "ict_telecom",
             "finance_insurance", "real_estate", "public_admin", "other_services")
n_years <- last(g$year) - first(g$year)
cagr <- sapply(sectors, function(s) 100 * ((last(g[[s]]) / first(g[[s]]))^(1 / n_years) - 1))
sort(round(cagr, 1), decreasing = TRUE)

# ---- STEP 4 · Per person ----------------------------------------------------------------------
g <- g |> mutate(gdp_per_person_naira = real_gdp_total * 1e12 / (population_m * 1e6))
pc_growth <- 100 * ((last(g$gdp_per_person_naira) / first(g$gdp_per_person_naira))^(1 / n_years) - 1)
cat(sprintf("real GDP per person grew %.2f%% a year; years to double: %.0f\n", pc_growth, log(2) / log(1 + pc_growth / 100)))

# ---- STEP 5 · Nominal vs real, and the GDP deflator ---------------------------------------------
g <- g |> mutate(deflator = 100 * nominal_gdp_old_base / real_gdp_total,
                 deflator_inflation_pct = 100 * (deflator / lag(deflator) - 1))
tail(select(g, year, nominal_gdp_old_base, real_gdp_total, deflator, deflator_inflation_pct), 5)

# ---- STEP 6 · Market rates vs PPP ----------------------------------------------------------------
peers |> mutate(ppp_ratio = gdp_per_capita_ppp / gdp_per_capita_usd) |> arrange(desc(ppp_ratio)) |>
  select(country, gdp_per_capita_usd, gdp_per_capita_ppp, ppp_ratio)

# ---- YOUR TURN ---------------------------------------------------------------------------------------
# (a) "Nigeria's GDP grew 50% since 2010, so our market grew 50%." Reply in two sentences using Steps 1 and 4.
# (b) Which two sectors would you bet on for a B2B business, and why? Use Step 3.
# (c) Why might PPP give a different picture of a consumer market than market exchange rates —
#     and which measure should you use to price a product?
