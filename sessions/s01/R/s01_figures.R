# =============================================================================
# EEGB · Session 1 · Course Overview & Data Literacy for Managers
# Replication script — regenerates every chart in the Session 1 deck (R)
# Data: data/ng_macro_monthly.csv (stylised Nigerian macro series, 2015–2025)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
m <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
rebase <- as.Date("2025-01-01")

# --- F01 · Three ways to measure inflation ------------------------------------------
inf <- m |> select(date, Food = food_inflation, `Headline (all items)` = headline_inflation,
                   `Core (excl. farm produce & energy)` = core_inflation) |>
  pivot_longer(-date, names_to = "measure", values_to = "rate")
p1 <- ggplot(inf, aes(date, rate, colour = measure)) + geom_line(linewidth = 1.1) +
  geom_vline(xintercept = rebase, linetype = "dashed", colour = eegb[["slate"]]) +
  annotate("text", x = rebase, y = 43, label = " CPI rebased\n Jan 2025", hjust = 0, vjust = 1, colour = eegb[["slate"]]) +
  scale_colour_manual(values = c(Food = eegb[["gold"]], `Headline (all items)` = eegb[["navy"]],
                                 `Core (excl. farm produce & energy)` = eegb[["teal"]]), name = NULL) +
  scale_y_continuous(labels = pct, limits = c(0, 45)) +
  labs(title = "Inflation: food led, core followed — and the 2025 rebasing broke the series",
       x = NULL, y = "Year-on-year change", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s01", "f01")

# --- F02 · Official vs parallel exchange rate -----------------------------------------
p2 <- ggplot(m, aes(date)) +
  geom_ribbon(aes(ymin = official_fx_ngn_usd, ymax = parallel_fx_ngn_usd), fill = eegb[["gold"]], alpha = .25) +
  geom_line(aes(y = parallel_fx_ngn_usd, colour = "Parallel market"), linewidth = 1) +
  geom_line(aes(y = official_fx_ngn_usd, colour = "Official window"), linewidth = 1.3) +
  scale_colour_manual(values = c(`Parallel market` = eegb[["rust"]], `Official window` = eegb[["navy"]]), name = NULL) +
  scale_y_continuous(labels = function(v) paste0("₦", format(v, big.mark = ","))) +
  labs(title = "Two prices for one dollar: the gap closed only after the 2023–24 unification",
       x = NULL, y = "Naira per US dollar", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s01", "f02")

# --- F03 · Correlation is not causation -------------------------------------------------
r1 <- cor(m$private_credit_growth_yoy, m$headline_inflation)
p3 <- ggplot(m, aes(private_credit_growth_yoy, headline_inflation)) + geom_point(colour = eegb[["teal"]], alpha = .7, size = 2.5) +
  labs(title = sprintf("Credit growth vs inflation: r = %.2f — strong, but which causes which?", r1),
       subtitle = "Both rose after the 2023 devaluation: a third factor can drive two series at once",
       x = "Private credit growth (%)", y = "Headline inflation (%)", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s01", "f03")

# --- F04 · A six-number board dashboard (last 36 months) ---------------------------------
last <- m |> filter(date >= max(date) - 365 * 3 + 20) |>
  select(date, `Inflation (%)` = headline_inflation, `Policy rate (%)` = mpr, `₦ per US$` = official_fx_ngn_usd,
         `Brent (US$/bbl)` = brent_usd, `Reserves (US$ bn)` = fx_reserves_usd_bn, `PMI (50 = no change)` = pmi) |>
  pivot_longer(-date, names_to = "indicator", values_to = "value")
p4 <- ggplot(last, aes(date, value)) + geom_line(colour = eegb[["teal"]], linewidth = 1.1) +
  geom_point(data = last |> group_by(indicator) |> slice_max(date), colour = eegb[["navy"]], size = 2.5) +
  facet_wrap(~indicator, scales = "free_y", ncol = 3) +
  labs(title = "The board's monthly macro page: six numbers, latest value, trend",
       x = NULL, y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p4, "s01", "f04", width = 12, height = 6)

# --- F05 · Real interest rate ----------------------------------------------------------
m <- m |> mutate(real = mpr - headline_inflation)
p5 <- ggplot(m, aes(date, real)) +
  geom_area(aes(fill = real < 0), alpha = .35, show.legend = FALSE) +
  geom_line(colour = eegb[["navy"]], linewidth = 1.1) + geom_hline(yintercept = 0) +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]])) +
  scale_y_continuous(labels = pct) +
  labs(title = sprintf("Savers lost to inflation for most of the decade (latest real rate: %+.1f pts)", tail(m$real, 1)),
       x = NULL, y = "Policy rate minus headline inflation", caption = eegb_caption) + theme_eegb()
save_fig(p5, "s01", "f05")

# --- F06 · PMI as an early signal ---------------------------------------------------------
p6 <- ggplot(m, aes(date, pmi)) + geom_line(colour = eegb[["teal"]], linewidth = 1.1) +
  geom_hline(yintercept = 50, linetype = "dashed", colour = eegb[["rust"]]) +
  annotate("rect", xmin = as.Date(c("2016-01-01", "2020-04-01", "2023-11-01")),
           xmax = as.Date(c("2016-12-01", "2020-09-01", "2024-07-01")), ymin = -Inf, ymax = Inf,
           fill = eegb[["gold"]], alpha = .18) +
  labs(title = "The PMI arrives weeks before GDP — and dipped below 50 in every downturn",
       x = NULL, y = "Purchasing Managers' Index", caption = eegb_caption) + theme_eegb()
save_fig(p6, "s01", "f06")
