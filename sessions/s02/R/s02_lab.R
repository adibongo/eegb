# =============================================================================
# EEGB · Session 2 LAB · How price-sensitive are our customers? (R)
# Data: data/fmcg_price_volume.csv — stylised weekly noodles sales, 3 regions, 2022–2025
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
d <- read_csv("data/fmcg_price_volume.csv", show_col_types = FALSE)

# ---- STEP 1 · Look at the data -------------------------------------------------------
head(d)
d |> group_by(region) |> summarise(first_price = first(price_naira), last_price = last(price_naira),
                                   first_units = first(units), last_units = last(units))

# ---- STEP 2 · The naive elasticity -------------------------------------------------------
naive <- lm(log(units) ~ log(price_naira), data = d)
coef(naive)        # slope close to zero — does price really not matter?

# ---- STEP 3 · Hold other things constant ------------------------------------------------------
d <- d |> group_by(region) |> mutate(t = row_number() - 1) |> ungroup()
fit <- lm(log(units) ~ log(price_naira) + log(competitor_price_naira) + log(income_index) + t + region, data = d)
summary(fit)
own <- coef(fit)[["log(price_naira)"]]; cross <- coef(fit)[["log(competitor_price_naira)"]]

# ---- STEP 4 · What a price rise does to revenue -----------------------------------------------
for (rise in c(.05, .10, .20)) {
  q_change <- (1 + rise)^own - 1
  cat(sprintf("Price +%.0f%%: volume %+.1f%%, revenue %+.1f%%\n", 100 * rise, 100 * q_change, 100 * ((1 + rise) * (1 + q_change) - 1)))
}

# ---- STEP 5 · Promotions -----------------------------------------------------------------------
d |> group_by(region, promo) |> summarise(units = mean(units), .groups = "drop") |>
  tidyr::pivot_wider(names_from = promo, values_from = units) |> mutate(lift = `1` / `0` - 1)

# ---- STEP 6 · Cost pass-through: flour up 40% ----------------------------------------------------
P0 <- 500; C0 <- 350; dc <- C0 * 0.45 * 0.40
for (share in c(0, .5, 1)) {
  P <- P0 + share * dc; Q <- (P / P0)^own
  cat(sprintf("Pass on %.0f%%: price N%.0f, volume %+.1f%%, profit %.0f%% of before\n",
              100 * share, P, 100 * (Q - 1), 100 * (P - C0 - dc) * Q / (P0 - C0)))
}

# ---- YOUR TURN -----------------------------------------------------------------------------------
# (a) Why is the naive elasticity so close to zero? What changed at the same time as prices?
# (b) Re-run Step 6 assuming rivals follow you (use own + cross as the elasticity). What changes?
# (c) Write a 3-sentence pricing recommendation to the MD: how much to pass on, how fast, and what to watch.
