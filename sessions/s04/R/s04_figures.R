# =============================================================================
# EEGB · Session 4 · Market Structure, Platforms & Competition Policy
# Replication script — regenerates every chart in the Session 4 deck (R)
# Data (real, with the source on every row): data/official/ng_mobile_market_shares.csv (NCC),
#   ng_nip_value.csv (NIBSS), platform_concentration.csv, findex_accounts.csv (World Bank Findex),
#   ng_official_monthly.csv and ng_worldbank_annual.csv (CPI and ₦/$).
# F03 and F04 are ILLUSTRATIVE models, not data.   Run from the project root (open eegb.Rproj).
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
ops <- c("MTN", "Airtel", "Glo", "9mobile/T2")
opcol <- c(MTN = eegb[["gold"]], Airtel = eegb[["rust"]], Glo = eegb[["teal"]], `9mobile/T2` = eegb[["olive"]])

# ---- NCC shares: published shares, or computed from counts where only counts are published -------
ms <- read_csv("data/official/ng_mobile_market_shares.csv", show_col_types = FALSE) |>
  group_by(period) |> mutate(share = coalesce(share_pct, 100 * subscriptions_m / sum(subscriptions_m))) |> ungroup() |>
  mutate(operator = factor(operator, levels = ops),
         lab = ifelse(period == "2025-09", "Sep 2025", paste("Dec", substr(period, 1, 4))))
lv <- unique(ms$lab); ms$lab <- factor(ms$lab, levels = lv); ms$x <- as.integer(ms$lab)
hhi <- ms |> group_by(lab) |> summarise(hhi = sum(share^2))
print(hhi)

# --- F01 · Nigeria's mobile market: shares (and the HHI in the title) -------------------------------
p1 <- ggplot(ms, aes(x, share, colour = operator, group = operator)) +
  annotate("rect", xmin = 5.5, xmax = 6.5, ymin = -Inf, ymax = Inf, fill = eegb[["slate"]], alpha = .12) +
  annotate("text", x = 6, y = 23, label = "NIN-SIM barring\nand a reporting\ncorrection", size = 3.2) +
  geom_line(linewidth = 1.3) + geom_point(size = 2.6) +
  geom_text(data = filter(ms, period == "2025-09"), aes(label = sprintf("%.0f%%", share)), hjust = -0.4, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = opcol, name = NULL) + scale_y_continuous(labels = \(x) paste0(x, "%"), limits = c(0, 62)) +
  scale_x_continuous(breaks = seq_along(lv), labels = lv, expand = expansion(add = c(0.3, 0.6))) +
  labs(title = "Nigeria's mobile market: MTN and Airtel now hold 86% of active lines",
       subtitle = paste0("HHI: ", paste(sprintf("%s %s", sub("Dec ", "", hhi$lab), format(round(hhi$hhi), big.mark = ",")), collapse = " · ")),
       x = NULL, y = "% of active mobile lines",
       caption = "Source: NCC year-end subscriber reports (2019–2024); NCC via ThisDay (Sep 2025). 2021 shares computed from operator counts.") +
  theme_eegb()
save_fig(p1, "s04", "f01")

# --- F02 · HHI in platform markets ----------------------------------------------------------------
pc <- read_csv("data/official/platform_concentration.csv", show_col_types = FALSE)
h2 <- pc |> group_by(market, period) |> summarise(lo = sum(share_pct^2), rest = pmax(0, 100 - sum(share_pct)), .groups = "drop") |>
  mutate(hi = lo + rest^2, market = paste0(market, "\n(", period, ")")) |>
  bind_rows(tibble(market = c("Nigeria mobile telephony (lines)\n(2023-12, before the break)", "Benchmark: 10 equal firms", "Benchmark: 5 equal firms"),
                   lo = c(hhi$hhi[hhi$lab == "Dec 2023"], 1000, 2000), hi = c(hhi$hhi[hhi$lab == "Dec 2023"], 1000, 2000))) |>
  mutate(kind = ifelse(grepl("Benchmark", market), "b", ifelse(grepl("Nigeria", market), "n", "p")),
         market = reorder(market, lo), lab = ifelse(hi - lo > 5, sprintf("%s–%s", format(round(lo), big.mark = ","), format(round(hi), big.mark = ",")), format(round(lo), big.mark = ",")))
p2 <- ggplot(h2, aes(y = market)) + geom_col(aes(x = hi, fill = kind), alpha = .35) + geom_col(aes(x = lo, fill = kind)) +
  geom_text(aes(x = hi, label = lab), hjust = -0.1, size = 3.8) + geom_vline(xintercept = 1800, colour = eegb[["rust"]], linetype = 2) +
  scale_fill_manual(values = c(b = eegb[["slate"]], n = eegb[["gold"]], p = eegb[["teal"]]), guide = "none") +
  scale_x_continuous(limits = c(0, 10400), labels = comma) +
  labs(title = "Four platform markets, all far above the merger-screen line", x = "Herfindahl–Hirschman Index (sum of squared % shares)", y = NULL,
       caption = "Sources: NCC; CA Kenya; iResearch; US v. Google (Aug 2024). Dashed line = 1,800.\nPale bar = range when some shares are unpublished.") +
  theme_eegb()
save_fig(p2, "s04", "f02")

# --- F03 · Monopoly vs competition (ILLUSTRATIVE) ----------------------------------------------------
a <- 100; mc <- 20; Qc <- a - mc; Qm <- (a - mc) / 2; Pm <- a - Qm
p3 <- ggplot() +
  annotate("rect", xmin = 0, xmax = Qm, ymin = mc, ymax = Pm, fill = eegb[["gold"]], alpha = .35) +
  annotate("polygon", x = c(Qm, Qc, Qm), y = c(Pm, mc, mc), fill = eegb[["rust"]], alpha = .4) +
  geom_abline(intercept = a, slope = -1, colour = eegb[["navy"]], linewidth = 1.4) +
  annotate("segment", x = 0, xend = 50, y = 100, yend = 0, colour = eegb[["teal2"]], linetype = 2, linewidth = 1) +
  geom_hline(yintercept = mc, colour = eegb[["slate"]], linewidth = 1) +
  annotate("point", x = c(Qm, Qc), y = c(Pm, mc), size = 3) +
  annotate("text", x = c(Qm + 3, Qc - 2), y = c(Pm + 7, mc + 9), hjust = c(0, 0),
           label = c(sprintf("Monopoly: %.0fm at ₦%.0f", Qm, Pm), sprintf("Competition: %.0fm at ₦%.0f", Qc, mc))) +
  annotate("text", x = 20, y = 40, label = sprintf("Profit\n₦%sm", format((Pm - mc) * Qm, big.mark = ","))) +
  annotate("text", x = 52, y = 32, label = sprintf("Deadweight\nloss ₦%sm", 0.5 * (Pm - mc) * (Qc - Qm))) +
  coord_cartesian(xlim = c(0, 100), ylim = c(0, 105)) +
  labs(title = "A monopolist sells less, charges more — and some trades never happen", x = "Transactions per month (millions)", y = "Fee per transaction (₦)",
       caption = "Illustrative. Demand: fee = 100 − Q (navy); marginal revenue dashed; marginal cost ₦20. Monopoly sets MR = MC (Mankiw, ch. 15).") + theme_eegb()
save_fig(p3, "s04", "f03")

# --- F04 · Network effects and tipping (ILLUSTRATIVE) ------------------------------------------------
simulate <- function(beta, qb = 0.15, s0 = 0.55, T = 36, churn = 0.15) {
  s <- s0; for (t in 1:T) { pa <- 1 / (1 + exp(-(beta * (2 * s[t] - 1) - qb))); s <- c(s, (1 - churn) * s[t] + churn * pa) }; 100 * s }
sims <- bind_rows(lapply(list(c(0, "No network effect"), c(1.5, "Moderate network effect"), c(4, "Strong network effect")),
  \(z) tibble(month = 0:36, share = simulate(as.numeric(z[1])), case = z[2])))
p4 <- ggplot(sims, aes(month, share, colour = case)) + geom_hline(yintercept = 50, colour = eegb[["grid"]]) + geom_line(linewidth = 1.4) +
  geom_text(data = filter(sims, month == 36), aes(label = sprintf("%.0f%%", share)), hjust = -0.2, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = c(`No network effect` = eegb[["slate"]], `Moderate network effect` = eegb[["teal"]], `Strong network effect` = eegb[["rust"]]), name = NULL) +
  scale_y_continuous(labels = \(x) paste0(x, "%"), limits = c(0, 100)) +
  labs(title = "With strong network effects the early leader takes the market — even against a better rival",
       x = "Months", y = "Platform A's share of users",
       caption = "Illustrative simulation: A starts with 55%; B is slightly better; 15% of users choose again each month.") + theme_eegb()
save_fig(p4, "s04", "f04")

# --- F05 · Instant payments: nominal, real, dollars -------------------------------------------------------
nip <- read_csv("data/official/ng_nip_value.csv", show_col_types = FALSE)
infl <- read_csv("data/official/ng_official_monthly.csv", show_col_types = FALSE) |> mutate(year = as.integer(format(date, "%Y"))) |>
  group_by(year) |> summarise(infl = mean(cpi_headline_yoy, na.rm = TRUE))
fx <- read_csv("data/official/ng_worldbank_annual.csv", show_col_types = FALSE) |> select(year, ngn_usd_avg)
nip <- nip |> left_join(infl, by = "year") |> left_join(fx, by = "year") |>
  mutate(price = cumprod(ifelse(year == 2018, 1, 1 + infl / 100)), real = nip_value_ntn / price, usd_bn = nip_value_ntn * 1e3 / ngn_usd_avg)
g <- with(nip, c(nom = nip_value_ntn[7] / nip_value_ntn[1], real = real[7] / real[1], usd = usd_bn[7] / usd_bn[1])); print(round(g, 2))
long <- nip |> select(year, `Nominal ₦ trillion` = nip_value_ntn, `Real ₦ trillion (2018 prices)` = real) |> pivot_longer(-year)
p5 <- ggplot() + geom_col(data = long, aes(factor(year), value, fill = name), position = "dodge") +
  geom_line(data = nip, aes(factor(year), usd_bn, group = 1, colour = "US$ billion"), linewidth = 1.4) +
  geom_point(data = nip, aes(factor(year), usd_bn, colour = "US$ billion"), size = 2.5) +
  scale_fill_manual(values = c(eegb[["teal"]], eegb[["navy"]]), name = NULL) + scale_colour_manual(values = eegb[["gold"]], name = NULL) +
  labs(title = sprintf("Instant transfers, 2018→2024: ×%.0f in naira, ×%.1f in real terms, ×%.1f in dollars", g[1], g[2], g[3]),
       x = NULL, y = "₦ trillion (bars) · US$ billion (line)",
       caption = "Sources: NIBSS annual NIP values (via Techpoint, ThisDay, TheCable, Nairametrics); CBN CPI; World Bank ₦/$ annual average.") + theme_eegb()
save_fig(p5, "s04", "f05")

# --- F06 · Mobile-money accounts (Findex) ---------------------------------------------------------------------
fxd <- read_csv("data/official/findex_accounts.csv", show_col_types = FALSE) |> filter(!is.na(mobile_money_pct), country != "China") |>
  mutate(country = sub(", Arab Rep.", "", country))
p6 <- ggplot(fxd, aes(year, mobile_money_pct, colour = country)) + geom_line(aes(linewidth = country == "Nigeria")) + geom_point(size = 2.5) +
  geom_text(data = filter(fxd, year == 2024), aes(label = sprintf("%.0f%%", mobile_money_pct)), hjust = -0.3, fontface = "bold",
            nudge_y = c(Egypt = 0, Ghana = 0, Kenya = 0, Nigeria = 2, `South Africa` = -2)[filter(fxd, year == 2024)$country], show.legend = FALSE) +
  scale_linewidth_manual(values = c(`TRUE` = 1.8, `FALSE` = 1.1), guide = "none") +
  scale_colour_manual(values = c(Kenya = eegb[["rust"]], Ghana = eegb[["gold"]], Nigeria = eegb[["navy"]], `South Africa` = eegb[["teal"]], Egypt = eegb[["slate"]]), name = NULL) +
  scale_x_continuous(breaks = c(2014, 2017, 2021, 2024), limits = c(2014, 2025)) + scale_y_continuous(labels = \(x) paste0(x, "%"), limits = c(0, 100)) +
  labs(title = "Adults with a mobile-money account: Nigeria went from 9% to 33% in three years", x = NULL, y = "% of adults (15+)",
       caption = "Source: World Bank Global Findex Database 2025, indicator mobileaccount.t.d.") + theme_eegb()
save_fig(p6, "s04", "f06")
