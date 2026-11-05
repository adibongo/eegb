# =============================================================================
# EEGB · Session 11 · Exchange Rates, Capital Flows & the Impossible Trinity
# Replication script — regenerates every chart in the Session 11 deck (R)
# Data: data/ng_macro_monthly.csv, data/ng_bop_quarterly.csv (stylised teaching data)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
m <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
b <- read_csv("data/ng_bop_quarterly.csv", show_col_types = FALSE) |>
  mutate(date = as.Date(paste0(substr(quarter, 1, 4), "-", (as.integer(substr(quarter, 6, 6)) - 1) * 3 + 1, "-01")))
ngn_lab <- function(v) paste0("₦", format(v, big.mark = ","))

# --- F01 · Three regimes ------------------------------------------------------------------
reg <- tibble(start = as.Date(c("2015-01-01", "2016-06-01", "2023-06-01")), end = as.Date(c("2016-06-01", "2023-06-01", "2025-12-31")),
              label = c("Hard peg", "Managed rate + multiple windows", "Unified, more market-determined"))
p1 <- ggplot(m) + geom_rect(data = reg, aes(xmin = start, xmax = end, ymin = -Inf, ymax = Inf, fill = label), alpha = .25) +
  geom_line(aes(date, parallel_fx_ngn_usd), colour = eegb[["rust"]], linewidth = .9) +
  geom_line(aes(date, official_fx_ngn_usd), colour = eegb[["navy"]], linewidth = 1.3) +
  scale_fill_manual(values = unname(eegb[c("slate", "gold", "sky")]), name = NULL) +
  scale_y_continuous(labels = ngn_lab) +
  labs(title = "Three regimes in a decade: peg, managed float with rationing, then unification",
       subtitle = "Navy = official rate, rust = parallel market", x = NULL, y = "Naira per US dollar", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s11", "f01")

# --- F02 · Premium vs reserves ----------------------------------------------------------------
m <- m |> mutate(premium = 100 * (parallel_fx_ngn_usd / official_fx_ngn_usd - 1))
k <- max(m$premium) / max(m$fx_reserves_usd_bn)
p2 <- ggplot(m, aes(date)) + geom_line(aes(y = premium, colour = "Parallel premium (%)"), linewidth = 1.2) +
  geom_line(aes(y = fx_reserves_usd_bn * k, colour = "Reserves (US$ bn, right axis)"), linewidth = 1) +
  scale_y_continuous(sec.axis = sec_axis(~ . / k, name = "Gross reserves (US$ bn)")) +
  scale_colour_manual(values = unname(eegb[c("rust", "teal")]), name = NULL) +
  labs(title = sprintf("Average premium: %.0f%% before unification, %.0f%% after mid-2024",
                       mean(m$premium[m$date < as.Date("2023-06-01")]), mean(m$premium[m$date >= as.Date("2024-06-01")])),
       x = NULL, y = "Parallel-market premium (%)", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s11", "f02")

# --- F03 · Balance of payments ------------------------------------------------------------------
d3 <- b |> select(date, `Goods trade balance` = trade_balance, Remittances = remittances,
                  `Services & income (net)` = services_income_net) |> pivot_longer(-date)
p3 <- ggplot() + geom_col(data = d3, aes(date, value, fill = name), width = 70) +
  geom_line(data = b, aes(date, current_account), colour = eegb[["navy"]], linewidth = 1.2) +
  geom_point(data = b, aes(date, current_account), colour = eegb[["navy"]], size = 1.5) +
  scale_fill_manual(values = unname(eegb[c("teal", "gold", "slate")]), name = NULL) + geom_hline(yintercept = 0) +
  labs(title = "Remittances keep the current account afloat when oil exports weaken",
       subtitle = "Line = current account", x = NULL, y = "US$ bn per quarter", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s11", "f03")

# --- F04 · Hot money vs the real policy rate -----------------------------------------------------
mq <- m |> mutate(date = as.Date(paste0(format(date, "%Y-"), sprintf("%02d", (as.integer(format(date, "%m")) - 1) %/% 3 * 3 + 1), "-01"))) |>
  group_by(date) |> summarise(real_rate = mean(mpr - headline_inflation))
bq <- inner_join(b, mq, by = "date")
r <- cor(bq$portfolio_inflows, bq$real_rate)
p4 <- ggplot(bq, aes(real_rate, portfolio_inflows)) + geom_point(colour = eegb[["teal2"]], size = 3) +
  geom_smooth(method = "lm", se = FALSE, colour = eegb[["rust"]], formula = y ~ x) +
  labs(title = sprintf("Hot money follows the real return: inflows vs real policy rate (r = %.2f)", r),
       x = "Real policy rate (points)", y = "Portfolio inflows, US$ bn per quarter", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s11", "f04")

# --- F05 · The impossible trinity (conceptual) -------------------------------------------------------
tri <- tibble(x = c(0, 10, 5), y = c(0, 0, 8.66), lab = c("Fixed exchange rate", "Free capital flows", "Independent monetary policy"))
sides <- tibble(x = c(5, 1.6, 8.4), y = c(-.8, 4.7, 4.7),
                lab = c("Currency board / euro area", "Capital controls (China; Nigeria's FX rationing)", "Floating rate (US, UK; Nigeria since 2023–24)"))
p5 <- ggplot() + geom_polygon(data = tri, aes(x, y), fill = NA, colour = eegb[["navy"]], linewidth = 1.3) +
  geom_point(data = tri, aes(x, y), colour = eegb[["gold"]], size = 9) +
  geom_text(data = tri, aes(x, y + ifelse(y > 0, .9, -1.2), label = lab), fontface = "bold", colour = eegb[["navy"]]) +
  geom_label(data = sides, aes(x, y, label = lab), colour = eegb[["teal"]], size = 3.5) +
  coord_equal(xlim = c(-2.5, 12.5), ylim = c(-3, 10.5)) +
  labs(title = "The impossible trinity: pick any two corners — each side is a policy choice") + theme_void(base_size = 13) +
  theme(plot.title = element_text(face = "bold", colour = eegb[["navy"]]))
save_fig(p5, "s11", "f05", width = 9, height = 7)

# --- F06 · Currency mismatch: a US$10m loan ------------------------------------------------------------
d6 <- m |> filter(date >= as.Date("2023-01-01"), date <= as.Date("2025-01-01")) |> mutate(debt = 10e6 * official_fx_ngn_usd / 1e9)
p6 <- ggplot(d6, aes(date, debt)) + geom_area(fill = eegb[["rust"]], alpha = .25) + geom_line(colour = eegb[["rust"]], linewidth = 1.3) +
  geom_hline(yintercept = d6$debt[1], linetype = "dashed", colour = eegb[["slate"]]) +
  labs(title = sprintf("A US$10m loan with naira revenues: the debt grew %.1f× without borrowing a kobo more", tail(d6$debt, 1) / d6$debt[1]),
       x = NULL, y = "Loan value in naira (₦ bn)", caption = eegb_caption) + theme_eegb()
save_fig(p6, "s11", "f06")

# --- F07 · Real exchange rate ---------------------------------------------------------------------------
m <- m |> mutate(p_ng = cumprod((1 + headline_inflation / 100)^(1 / 12)), p_us = (1.025^(1 / 12))^row_number(),
                 rer = official_fx_ngn_usd * p_us / p_ng, rer = 100 * rer / first(rer),
                 nom = 100 * official_fx_ngn_usd / first(official_fx_ngn_usd))
d7 <- m |> select(date, `Nominal: naira per dollar` = nom, `Real: adjusted for inflation` = rer) |> pivot_longer(-date)
p7 <- ggplot(d7, aes(date, value, colour = name)) + geom_line(linewidth = 1.2) + geom_hline(yintercept = 100) +
  scale_colour_manual(values = unname(eegb[c("slate", "teal")]), name = NULL) +
  labs(title = "In real terms the naira cheapened far less — and inflation is eroding the gain",
       x = NULL, y = "Index, Jan 2015 = 100 (higher = cheaper naira)",
       caption = "Real rate uses stylised CPI with US inflation assumed at 2.5% a year. EEGB stylised teaching data.") + theme_eegb()
save_fig(p7, "s11", "f07")
