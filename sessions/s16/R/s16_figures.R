# =============================================================================
# EEGB · Session 16 · Capstone & Integrative Review
# Replication script — regenerates every chart in the Session 16 deck (R)
# Data: data/ng_macro_monthly.csv, data/miller_exposure_monthly.csv, data/cement_demand_monthly.csv,
#       data/global_policy_rates.csv (all stylised teaching data)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
m  <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
mi <- read_csv("data/miller_exposure_monthly.csv", show_col_types = FALSE) |> mutate(month = as.Date(month))
ce <- read_csv("data/cement_demand_monthly.csv", show_col_types = FALSE) |> mutate(month = as.Date(month))
pr <- read_csv("data/global_policy_rates.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
reform <- as.Date("2023-06-01")

# --- F01 · Policy to profits: one shock, four panels --------------------------------------
d1 <- bind_rows(
  m |> filter(date >= as.Date("2022-01-01")) |> transmute(date, panel = "1 · Exchange rate (₦ per US$)", value = official_fx_ngn_usd),
  m |> filter(date >= as.Date("2022-01-01")) |> transmute(date, panel = "2 · Headline inflation (%)", value = headline_inflation),
  m |> filter(date >= as.Date("2022-01-01")) |> transmute(date, panel = "3 · CBN policy rate (%)", value = mpr),
  mi |> filter(month >= as.Date("2022-01-01")) |> transmute(date = month, panel = "4 · A flour miller's gross margin (%)", value = gross_margin_pct))
p1 <- ggplot(d1, aes(date, value, colour = panel)) + geom_line(linewidth = 1.1, show.legend = FALSE) +
  geom_vline(xintercept = reform, linetype = "dashed", colour = eegb[["slate"]]) +
  facet_wrap(~panel, ncol = 1, scales = "free_y") + scale_colour_manual(values = unname(eegb[c("rust", "navy", "teal", "gold")])) +
  labs(title = "Policy to profits: one reform, four panels (dashed line = June 2023)", x = NULL, y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p1, "s16", "f01", height = 8)

# --- F02 · The course on one page ---------------------------------------------------------
map <- tibble(part = rep(c("PART I · Micro & markets", "PART II · Macro, policy & risk", "PART III · Open economy", "PART IV · Strategy"), c(5, 5, 2, 4)),
              session = c("1 Data literacy", "2 Demand & elasticity", "3 Forecasting & sizing", "4 Platforms & competition", "5 Market failures",
                          "6 AD–AS & inflation", "7 National accounts", "8 Monetary policy", "9 Fiscal policy & debt", "10 Financial stability",
                          "11 FX & capital flows", "12 Trade & industrial policy",
                          "13 Climate & transition", "14 Country risk & scenarios", "15 Hedging & resilience", "16 Board memo")) |>
  group_by(part) |> mutate(row = row_number()) |> ungroup() |> mutate(part = factor(part, levels = unique(part)))
p2 <- ggplot(map, aes(part, -row)) + geom_tile(aes(fill = part), width = .92, height = .8, alpha = .2, colour = "white") +
  geom_text(aes(label = session), size = 3.6) +
  scale_fill_manual(values = unname(eegb[c("teal", "navy", "rust", "gold")]), guide = "none") +
  labs(title = "The course on one page: micro → macro → global → strategy", x = NULL, y = NULL) +
  theme_eegb() + theme(axis.text.y = element_blank(), panel.grid = element_blank())
save_fig(p2, "s16", "f02", width = 12, height = 6)

# --- F03 · Three scenarios for 2026 -------------------------------------------------------------
last <- tail(m, 1); months <- seq(as.Date("2026-01-01"), by = "month", length.out = 12)
scen <- tibble(scenario = c("Upside: reforms stick, oil firm", "Base: gradual disinflation", "Downside: oil slump, renewed FX pressure"),
               g = c(-.004, .008, .03), infl_end = c(13, 15, 24))
d3 <- scen |> rowwise() |> reframe(scenario, date = months, fx = last$official_fx_ngn_usd * (1 + g)^(1:12),
                                   inflation = seq(last$headline_inflation, infl_end, length.out = 13)[-1])
p3 <- ggplot() + geom_line(data = filter(m, date >= as.Date("2024-01-01")), aes(date, official_fx_ngn_usd), colour = eegb[["ink"]], linewidth = 1.1) +
  geom_line(data = d3, aes(date, fx, colour = scenario), linetype = "dashed", linewidth = 1.1) +
  scale_colour_manual(values = c("#2E7D5B", eegb[["teal"]], eegb[["rust"]]), name = NULL) +
  labs(title = "Three teaching scenarios for the naira in 2026", x = NULL, y = "Naira per US$", caption = eegb_caption) + theme_eegb() +
  theme(legend.direction = "vertical")
save_fig(p3, "s16", "f03")

# --- F04 · Cement evidence pack -------------------------------------------------------------------
ce <- ce |> mutate(r12 = as.numeric(stats::filter(cement_mt, rep(1, 12), sides = 1)), yoy = 100 * (r12 / lag(r12, 12) - 1))
d4 <- bind_rows(ce |> transmute(date = month, panel = "Cement volumes, 12-month growth (%)", value = yoy),
                ce |> transmute(date = month, panel = "Price per bag (₦)", value = price_per_bag_naira),
                m |> transmute(date, panel = "Real policy rate (pts)", value = mpr - headline_inflation),
                m |> transmute(date, panel = "PMI (50 = no change)", value = pmi))
p4 <- ggplot(filter(d4, !is.na(value)), aes(date, value)) + geom_line(colour = eegb[["teal"]], linewidth = 1) +
  facet_wrap(~panel, scales = "free_y") +
  labs(title = "A memo evidence pack: the cement industry", x = NULL, y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p4, "s16", "f04", width = 12, height = 6.5)

# --- F05 · Nominal vs real price of a bag of cement ---------------------------------------------------
cpi <- m |> transmute(month = date, cpi = cumprod((1 + headline_inflation / 100)^(1 / 12)))
d5 <- inner_join(ce, cpi, by = "month") |> mutate(nominal = 100 * price_per_bag_naira / first(price_per_bag_naira),
                                                  real = 100 * (price_per_bag_naira / cpi) / first(price_per_bag_naira / cpi))
p5 <- ggplot(pivot_longer(select(d5, month, nominal, real), -month), aes(month, value, colour = name)) + geom_line(linewidth = 1.2) +
  scale_colour_manual(values = unname(eegb[c("rust", "teal")]), labels = c("Nominal (naira)", "Real (after inflation)"), name = NULL) +
  geom_hline(yintercept = 100) +
  labs(title = sprintf("A bag of cement: %+.0f%% in naira since 2015, but %+.0f%% after inflation",
                       tail(d5$nominal, 1) - 100, tail(d5$real, 1) - 100),
       x = NULL, y = "Index, Jan 2015 = 100", caption = eegb_caption) + theme_eegb()
save_fig(p5, "s16", "f05")

# --- F06 · Policy rates compared ----------------------------------------------------------------------
d6 <- pr |> select(date, `US Fed` = us_fed, `Nigeria CBN` = nigeria_cbn, `South Africa` = south_africa_sarb, Kenya = kenya_cbk, Ghana = ghana_bog) |>
  pivot_longer(-date)
gap <- tail(pr$nigeria_cbn, 1) - tail(pr$us_fed, 1)
p6 <- ggplot(d6, aes(date, value, colour = name)) + geom_step(linewidth = 1.1) +
  scale_colour_manual(values = c(Ghana = eegb[["gold"]], Kenya = eegb[["olive"]], `Nigeria CBN` = eegb[["navy"]], `South Africa` = eegb[["teal"]], `US Fed` = eegb[["rust"]]), name = NULL) +
  labs(title = sprintf("The Fed sets the global tide: the CBN–Fed gap is %.1f points (late 2025)", gap),
       x = NULL, y = "Policy rate (%)", caption = eegb_caption) + theme_eegb()
save_fig(p6, "s16", "f06")
