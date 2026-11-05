# =============================================================================
# EEGB · Session 5 LAB · Who gained from the petrol subsidy, and who pays for its removal? (R)
# Data: data/fuel_subsidy_incidence.csv — stylised household budgets by consumption decile
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
h <- read_csv("data/fuel_subsidy_incidence.csv", show_col_types = FALSE)
h                                  # decile 1 = poorest 10% of households ... 10 = richest 10%

# ---- STEP 1 · The subsidy each household received ------------------------------------------
h <- h |> mutate(subsidy = petrol_litres_month * subsidy_per_litre_pre,
                 share_of_subsidy = 100 * subsidy / sum(subsidy),
                 subsidy_pct_budget = 100 * subsidy / monthly_spend_naira)
select(h, decile, subsidy, share_of_subsidy, subsidy_pct_budget)

# ---- STEP 2 · Who got most of it? -------------------------------------------------------------------
c(richest_10 = h$share_of_subsidy[10], poorest_40 = sum(h$share_of_subsidy[1:4]))

# ---- STEP 3 · The cost of removal: direct + indirect ------------------------------------------------
fare_rise <- 0.50; food_rise <- 0.10                       # your assumptions — change them!
h <- h |> mutate(direct_pct = 100 * petrol_litres_month * (pump_price_post - pump_price_pre) / monthly_spend_naira,
                 indirect_pct = 100 * (transport_share * fare_rise + food_share * food_rise),
                 total_pct = direct_pct + indirect_pct)
select(h, decile, direct_pct, indirect_pct, total_pct)

# ---- STEP 4 · The fiscal saving and a targeted cash transfer ---------------------------------------------
annual <- sum(h$subsidy * h$households_m * 1e6 * 12) / 1e12; annual      # ₦ trillion a year
transfer <- 10000
cost <- 4 * h$households_m[1] * 1e6 * transfer * 12 / 1e12; cost
h |> mutate(net_with_transfer = -total_pct + (decile <= 4) * 100 * transfer / monthly_spend_naira) |>
  select(decile, net_with_transfer)

# ---- YOUR TURN ------------------------------------------------------------------------------------------------
# (a) Change fare_rise and food_rise. How sensitive is the burden on deciles 1–4?
# (b) What transfer leaves deciles 3 and 4 no worse off? What does it cost?
# (c) Name two practical problems with targeting cash in Nigeria, and one way to solve each.
# (d) Should the savings go to transfers, transport (e.g. CNG buses), or reducing the deficit?
