# =============================================================================
# EEGB · Session 15 · Corporate Macro Strategy: Hedging & Resilience
# Replication script — regenerates every chart in the Session 15 deck (R)
# Data: data/miller_exposure_monthly.csv, data/ng_macro_monthly.csv, data/global_policy_rates.csv
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
mi  <- read_csv("data/miller_exposure_monthly.csv", show_col_types = FALSE) |> mutate(month = as.Date(month))
mac <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
pr  <- read_csv("data/global_policy_rates.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
OTHER <- 1.12   # other costs as a multiple of the imported wheat bill

# --- F01 · Two sources of risk ------------------------------------------------------------
b19 <- mi |> filter(format(month, "%Y") == "2019") |> summarise(w = mean(wheat_usd_per_tonne), f = mean(fx_ngn_usd))
idx <- mi |> transmute(month,
  `Wheat price (US$)` = 100 * wheat_usd_per_tonne / b19$w,
  `Exchange rate (₦ per US$)` = 100 * fx_ngn_usd / b19$f,
  `Wheat cost in naira (₦ per tonne)` = 100 * wheat_usd_per_tonne * fx_ngn_usd / (b19$w * b19$f)) |>
  pivot_longer(-month, names_to = "series", values_to = "index")
p1 <- ggplot(idx, aes(month, index, colour = series)) + geom_line(linewidth = 1.1) +
  geom_hline(yintercept = 100, linetype = "dashed", colour = eegb[["slate"]]) +
  scale_colour_manual(values = c(`Wheat price (US$)` = eegb[["gold"]], `Exchange rate (₦ per US$)` = eegb[["rust"]],
                                 `Wheat cost in naira (₦ per tonne)` = eegb[["navy"]]), name = NULL) +
  labs(title = "Wheat cost in naira rose about five-fold — the exchange rate did most of the work",
       x = NULL, y = "Index, 2019 average = 100", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s15", "f01")

# --- F02 · Decompose the rise --------------------------------------------------------------
yr <- mi |> mutate(y = format(month, "%Y")) |> filter(y %in% c("2019", "2025")) |>
  group_by(y) |> summarise(w = mean(wheat_usd_per_tonne), f = mean(fx_ngn_usd))
lw <- log(yr$w[2] / yr$w[1]); lf <- log(yr$f[2] / yr$f[1])
dec <- tibble(part = factor(c("Wheat price in US$", "Naira per US$", "Total (₦ per tonne)"),
                            levels = rev(c("Wheat price in US$", "Naira per US$", "Total (₦ per tonne)"))),
              v = 100 * c(lw, lf, lw + lf))
p2 <- ggplot(dec, aes(v, part, fill = part)) + geom_col(show.legend = FALSE) +
  geom_text(aes(label = sprintf("%+.0f log-points", v)), hjust = -0.1) +
  scale_fill_manual(values = c(`Wheat price in US$` = eegb[["gold"]], `Naira per US$` = eegb[["rust"]],
                               `Total (₦ per tonne)` = eegb[["navy"]])) + xlim(0, 100 * (lw + lf) + 50) +
  labs(title = sprintf("2019 → 2025: the exchange rate explains %.0f%% of the rise in naira wheat cost", 100 * lf / (lw + lf)),
       x = "Change in log points (they add up)", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p2, "s15", "f02", height = 4.8)

# --- F03 · Margin squeeze ------------------------------------------------------------------
p3 <- ggplot(mi, aes(month, gross_margin_pct)) + geom_line(colour = eegb[["teal"]], linewidth = 1.2) +
  geom_hline(yintercept = mean(mi$gross_margin_pct), linetype = "dashed", colour = eegb[["slate"]]) +
  geom_point(data = slice_min(mi, gross_margin_pct, n = 3), colour = eegb[["rust"]], size = 3) +
  scale_y_continuous(labels = pct) +
  labs(title = "Each devaluation hit margins first; flour prices caught up only months later",
       x = NULL, y = "Gross margin", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s15", "f03")

# --- F04/F05 · Hedge simulation -------------------------------------------------------------
m2 <- mac |> select(date, official_fx_ngn_usd, mpr) |> left_join(select(pr, date, us_fed), by = "date") |>
  mutate(us_fed = coalesce(us_fed, 2.5),
         fwd = official_fx_ngn_usd * (1 + (mpr - us_fed) / 100 * 3 / 12),
         fwd_locked = lag(fwd, 3))
sim <- mi |> left_join(select(m2, date, fwd_locked), by = c("month" = "date")) |> filter(!is.na(fwd_locked))
hedged <- bind_rows(lapply(c(0, 0.5, 1), function(h) {
  sim |> mutate(hedge = paste0(100 * h, "% hedged"),
                rate = h * fwd_locked + (1 - h) * fx_ngn_usd,
                margin = 100 * (revenue_ngn_bn - imported_cost_usd_m * rate / 1e3 * OTHER) / revenue_ngn_bn)
}))
p4 <- ggplot(hedged, aes(month, margin, colour = hedge)) + geom_line(linewidth = 1) +
  scale_colour_manual(values = c(`0% hedged` = eegb[["rust"]], `50% hedged` = eegb[["gold"]], `100% hedged` = eegb[["teal"]]), name = NULL) +
  scale_y_continuous(labels = pct) +
  labs(title = "Hedging FX three months ahead smooths the margin — at a price in calm times",
       x = NULL, y = "Gross margin", caption = "Forward = spot × (1 + (MPR − US policy rate) × 3/12). Illustrative.") + theme_eegb()
save_fig(p4, "s15", "f04")
summ <- hedged |> group_by(hedge) |> summarise(`Average margin` = mean(margin), `Volatility (sd)` = sd(margin),
                                               `Worst month` = min(margin)) |>
  pivot_longer(-hedge, names_to = "measure", values_to = "value") |>
  mutate(hedge = factor(hedge, levels = c("0% hedged", "50% hedged", "100% hedged")))
p5 <- ggplot(summ, aes(hedge, value, fill = measure)) + geom_col(show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.1f", value)), vjust = -0.3) + facet_wrap(~measure, scales = "free_y") +
  scale_fill_manual(values = unname(eegb[c("teal", "rust", "gold")])) +
  labs(title = "A 50% hedge gave the steadiest margin; 100% over-hedged",
       x = "Share of FX hedged", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p5, "s15", "f05", width = 12, height = 4.6)

# --- F06 · Tornado -------------------------------------------------------------------------------
b <- mi |> filter(format(month, "%Y") == "2025") |> summarise(across(where(is.numeric), mean))
marg <- function(fx = 1, wheat = 1, price = 1, other = 1) {
  rev  <- b$flour_price_ngn_per_kg * price * b$flour_volume_kt * 1e6 / 1e9
  cost <- b$wheat_usd_per_tonne * wheat * 1.32 * b$flour_volume_kt * 1000 / 1e6 * b$fx_ngn_usd * fx / 1e3
  100 * (rev - cost * (1 + (OTHER - 1) * other)) / rev
}
m0 <- marg()
tor <- tibble(shock = c("Naira 20% weaker / stronger", "Wheat 20% dearer / cheaper", "Flour price 10% lower / higher",
                        "Other costs 25% higher / lower", "Naira AND wheat 20% worse / better"),
              bad  = c(marg(fx = 1.2), marg(wheat = 1.2), marg(price = 0.9), marg(other = 1.25), marg(fx = 1.2, wheat = 1.2)) - m0,
              good = c(marg(fx = 0.8), marg(wheat = 0.8), marg(price = 1.1), marg(other = 0.75), marg(fx = 0.8, wheat = 0.8)) - m0) |>
  mutate(shock = reorder(shock, good - bad))
p6 <- ggplot(tor) + geom_col(aes(bad, shock), fill = eegb[["rust"]]) + geom_col(aes(good, shock), fill = eegb[["teal"]]) +
  geom_vline(xintercept = 0) +
  labs(title = sprintf("From a %.1f%% base margin, the exchange rate and wheat dominate", m0),
       x = "Change in gross margin (percentage points)", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p6, "s15", "f06")

# --- F07 · Risk heatmap ---------------------------------------------------------------------------
risks <- tibble(risk = c("Naira devaluation", "Wheat price spike", "Policy rate hike", "Port & shipping delays",
                         "Consumer demand slump", "Import levy / FX restriction", "Diesel & power costs", "Bank credit tightening"),
                likelihood = c(4, 3, 3, 3, 3, 2, 4, 2), impact = c(5, 4, 2, 3, 3, 4, 2, 3)) |>
  mutate(n = row_number()) |> group_by(likelihood, impact) |> mutate(x = likelihood - 0.22 + 0.44 * (row_number() - 1)) |> ungroup()
grid <- expand.grid(likelihood = 1:5, impact = 1:5) |> mutate(score = likelihood * impact)
p7 <- ggplot() + geom_tile(data = grid, aes(likelihood, impact, fill = score), alpha = .6) +
  scale_fill_gradient(low = "#FFF7D6", high = "#C0392B", guide = "none") +
  geom_point(data = risks, aes(x, impact), colour = eegb[["navy"]], size = 9) +
  geom_text(data = risks, aes(x, impact, label = n), colour = "white", fontface = "bold") +
  scale_x_continuous(breaks = 1:5, labels = c("Rare", "Unlikely", "Possible", "Likely", "Almost certain")) +
  scale_y_continuous(breaks = 1:5, labels = c("Minor", "Moderate", "Serious", "Major", "Severe")) +
  labs(title = "The miller's macro-risk heatmap: act first on the top-right corner",
       subtitle = paste(paste0(risks$n, " ", risks$risk), collapse = " · "),
       x = "Likelihood over the next 12 months", y = "Impact on gross margin",
       caption = "Scores are management judgements. Illustrative.") + theme_eegb()
save_fig(p7, "s15", "f07", height = 6)

# --- F08 · Leading indicator ------------------------------------------------------------------------
li <- mac |> mutate(premium = 100 * (parallel_fx_ngn_usd / official_fx_ngn_usd - 1),
                    dep_next6 = 100 * (lead(official_fx_ngn_usd, 6) / official_fx_ngn_usd - 1)) |> filter(!is.na(dep_next6))
p8 <- ggplot(li, aes(premium, dep_next6, colour = premium > 30)) + geom_point(alpha = .75, size = 2.5) +
  geom_vline(xintercept = 30, linetype = "dashed", colour = eegb[["rust"]]) +
  scale_colour_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]]), labels = c("Premium ≤ 30%", "Premium > 30%"), name = NULL) +
  scale_x_continuous(labels = pct) + scale_y_continuous(labels = pct) +
  labs(title = sprintf("A wide parallel-market premium often came before a devaluation (r = %.2f)", cor(li$premium, li$dep_next6)),
       x = "Parallel-market premium today", y = "Official naira depreciation over next 6 months", caption = eegb_caption) + theme_eegb()
save_fig(p8, "s15", "f08")
