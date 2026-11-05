# =============================================================================
# EEGB · Session 4 LAB · Is the mobile-payments market competitive? (R)
# Data: data/payments_market_shares.csv — stylised; providers are fictional except the 'Banks' aggregate
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr); library(tidyr)
p <- read_csv("data/payments_market_shares.csv", show_col_types = FALSE)

# ---- STEP 1 · Shares over time ---------------------------------------------------------------
sh <- p |> select(year, provider, share_of_value_pct) |> pivot_wider(names_from = provider, values_from = share_of_value_pct)
sh

# ---- STEP 2 · Concentration: CR2 and the HHI ------------------------------------------------------
conc <- p |> group_by(year) |>
  summarise(CR2 = sum(sort(share_of_value_pct, decreasing = TRUE)[1:2]), HHI = sum(share_of_value_pct^2))
conc

# ---- STEP 3 · Market definition matters: split 'Banks' into 10 equal banks ---------------------------
split <- p |> group_by(year) |>
  summarise(HHI_banks_as_ten = sum(share_of_value_pct[provider != "Banks (app & USSD)"]^2) +
              10 * (share_of_value_pct[provider == "Banks (app & USSD)"] / 10)^2)
left_join(conc, split, by = "year")

# ---- STEP 4 · Two-sided network growth ------------------------------------------------------------
tot <- p |> group_by(year) |> summarise(users = sum(active_users_m), merchants = sum(merchants_m))
coef(lm(log(merchants) ~ log(users), data = tot))[2]     # % more merchants per 1% more users

# ---- STEP 5 · Does the leader's fee rise with its share? -------------------------------------------
k <- filter(p, provider == "KoboLink"); k |> select(year, share_of_value_pct, avg_fee_pct)
cor(k$share_of_value_pct, k$avg_fee_pct)

# ---- STEP 6 · Merger test: SwiftNaira + AgentPay in 2025 -------------------------------------------
s25 <- filter(p, year == 2025)
delta <- 2 * s25$share_of_value_pct[s25$provider == "SwiftNaira"] * s25$share_of_value_pct[s25$provider == "AgentPay"]
delta    # rise in HHI from the merger

# ---- YOUR TURN ------------------------------------------------------------------------------------------
# (a) Is this market 'concentrated'? Answer under BOTH market definitions, and say which you prefer.
# (b) KoboLink's fee rose after it became the largest network. Is that proof of abuse? What else could explain it?
# (c) Write a 3-sentence note to the competition regulator (FCCPC) on the merger in Step 6.
