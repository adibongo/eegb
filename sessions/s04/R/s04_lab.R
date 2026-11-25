# =============================================================================
# EEGB · Session 4 LAB · Is the market too concentrated? (R)
# Data (real): data/official/ng_mobile_market_shares.csv (NCC), platform_concentration.csv,
#              ng_nip_value.csv (NIBSS). Step 4 is an illustrative pricing model.
# Run from the project root (open eegb.Rproj), line by line with Ctrl/Cmd + Enter
# =============================================================================
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })

# ---- STEP 1 · Market shares and concentration, 2019–2025 ---------------------------------------
ms <- read_csv("data/official/ng_mobile_market_shares.csv", show_col_types = FALSE)
ms <- ms |> group_by(period) |>
  mutate(share = coalesce(share_pct, 100 * subscriptions_m / sum(subscriptions_m))) |> ungroup()   # 2021: counts only
conc <- ms |> group_by(period) |>
  summarise(CR2 = sum(sort(share, decreasing = TRUE)[1:2]), HHI = sum(share^2))
print(conc, n = Inf)

# ---- STEP 2 · Did MTN really grow from 39% to 51% in 2024? Look at the counts --------------------------
ms |> filter(period %in% c("2023-12", "2024-12")) |> select(period, operator, subscriptions_m) |>
  pivot_wider(names_from = period, values_from = subscriptions_m) |>
  mutate(change_m = `2024-12` - `2023-12`) |> print()

# ---- STEP 3 · Merger screen ------------------------------------------------------------------------------------
latest <- ms |> filter(period == "2025-09") |> select(operator, share) |> tibble::deframe()
merger_screen <- function(s, a, b) {
  post <- s; post[a] <- s[a] + s[b]; post <- post[names(post) != b]
  h0 <- sum(s^2); h1 <- sum(post^2); d <- h1 - h0
  tibble(merger = paste(a, "+", b), hhi_before = h0, hhi_after = h1, change = d, merged_share = post[[a]],
         presumed_harmful = (h1 > 1800 & d > 100) | (post[[a]] > 30 & d > 100))
}
bind_rows(merger_screen(latest, "Airtel", "Glo"), merger_screen(latest, "Glo", "9mobile"),
          merger_screen(latest, "MTN", "9mobile")) |> print()
# Note: change in HHI = 2 × share_a × share_b (check it!)

# ---- STEP 4 · Monopoly pricing (illustrative): fee = 100 − Q, marginal cost ₦20 -------------------------------------
a <- 100; b <- 1; mc <- 20
Qc <- (a - mc) / b; Qm <- (a - mc) / (2 * b); Pm <- a - b * Qm
dwl <- 0.5 * (Pm - mc) * (Qc - Qm); elast <- (1 / b) * Pm / Qm
cat(sprintf("Competition: Q=%.0fm, fee ₦%.0f | Monopoly: Q=%.0fm, fee ₦%.0f | DWL ₦%.0fm\n", Qc, mc, Qm, Pm, dwl))
cat(sprintf("Lerner index (P − MC)/P = %.2f vs 1/|elasticity| = %.2f\n", (Pm - mc) / Pm, 1 / elast))

# ---- STEP 5 · Platform markets: how concentrated? ------------------------------------------------------------------
read_csv("data/official/platform_concentration.csv", show_col_types = FALSE) |> group_by(market) |>
  summarise(hhi_low = sum(share_pct^2), hhi_high = hhi_low + pmax(0, 100 - sum(share_pct))^2) |> print()

# ---- STEP 6 · Instant payments: nominal vs real vs dollars -------------------------------------------------------------
infl <- read_csv("data/official/ng_official_monthly.csv", show_col_types = FALSE) |>
  mutate(year = as.integer(format(date, "%Y"))) |> group_by(year) |> summarise(infl = mean(cpi_headline_yoy, na.rm = TRUE))
fx <- read_csv("data/official/ng_worldbank_annual.csv", show_col_types = FALSE) |> select(year, ngn_usd_avg)
read_csv("data/official/ng_nip_value.csv", show_col_types = FALSE) |> left_join(infl, by = "year") |> left_join(fx, by = "year") |>
  mutate(price = cumprod(ifelse(year == 2018, 1, 1 + infl / 100)), real_2018_prices = nip_value_ntn / price,
         usd_bn = nip_value_ntn * 1e3 / ngn_usd_avg) |> select(year, nip_value_ntn, real_2018_prices, usd_bn) |> print()

# ---- YOUR TURN ------------------------------------------------------------------------------------------------------------
# (a) Recompute the HHI for Dec 2023 by hand from the four shares. Is the market 'highly concentrated'?
# (b) In Step 2, MTN LOST lines in 2024 yet its share rose 12 points. Explain in two sentences.
# (c) Which merger in Step 3 would a regulator block? Which might pass? Why might 'Glo + 9mobile' still be good for customers?
# (d) If demand became MORE elastic (fee = 60 − 0.5Q), how would the monopoly fee change? Re-run Step 4.
# (e) Kenya's M-Pesa holds ~90% of mobile-money accounts, yet Kenya has near-universal inclusion. Is that market 'too concentrated'?
