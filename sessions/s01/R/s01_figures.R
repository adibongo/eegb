# =============================================================================
# EEGB · Session 1 · Course Overview & Data Literacy for Managers
# Replication script — regenerates every chart in the Session 1 deck (R)
# Data (official): data/official/ng_official_monthly.csv (CBN statistics + FRED Brent)
#                  data/official/ng_worldbank_annual.csv  (World Bank WDI)
# Refresh with:  python tools/fetch_official_data.py
# Run from the project root (open eegb.Rproj):  source("sessions/s01/R/s01_figures.R")
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr); library(patchwork) })

m <- read_csv("data/official/ng_official_monthly.csv", show_col_types = FALSE) |> filter(date >= as.Date("2015-01-01"))
a <- read_csv("data/official/ng_worldbank_annual.csv", show_col_types = FALSE)
cbn_src <- "Source: CBN statistics (cbn.gov.ng/rates), accessed Nov 2026."
newcpi <- as.Date("2025-01-01"); unif <- as.Date("2023-06-01")

# --- F01 · Headline, food and core inflation -------------------------------------------
p1 <- m |> select(date, Food = cpi_food_yoy, `Headline (all items)` = cpi_headline_yoy,
                  `Core (excl. farm produce & energy)` = cpi_core_yoy) |>
  pivot_longer(-date, names_to = "series", values_to = "v") |> filter(!is.na(v)) |>
  ggplot(aes(date, v, colour = series, linewidth = series)) + geom_line() +
  geom_vline(xintercept = c(unif, newcpi), linetype = "dashed", colour = eegb[c("rust", "slate")]) +
  annotate("text", x = unif, y = 44, label = "Subsidy removal & FX unification ", hjust = 1, size = 3.4, colour = eegb[["rust"]]) +
  annotate("text", x = newcpi, y = 44, label = " New CPI (2024 = 100)", hjust = 0, size = 3.4, colour = eegb[["slate"]]) +
  scale_colour_manual(values = c(Food = eegb[["gold"]], `Headline (all items)` = eegb[["navy"]], `Core (excl. farm produce & energy)` = eegb[["teal"]]), name = NULL) +
  scale_linewidth_manual(values = c(0.8, 1.3, 0.8), guide = "none") +
  scale_y_continuous(labels = pct, limits = c(0, 45)) +
  labs(title = "Inflation: food led, core followed — then the yardstick changed", x = NULL, y = "Year-on-year change",
       caption = paste(cbn_src, "2025 values: NBS revised series on the 2024 base.")) + theme_eegb()
save_fig(p1, "s01", "f01")

# --- F02 · Naira per US dollar: official and bureau de change ---------------------------
p2 <- ggplot(m, aes(date)) +
  geom_ribbon(data = filter(m, !is.na(usd_bdc_avg)), aes(ymin = usd_official_avg, ymax = usd_bdc_avg), fill = eegb[["gold"]], alpha = .25) +
  geom_line(aes(y = usd_official_avg, colour = "Official (CBN central rate)"), linewidth = 1.3) +
  geom_line(aes(y = usd_bdc_avg, colour = "Bureau de change (series ends Apr 2021)"), linewidth = 0.9, na.rm = TRUE) +
  geom_vline(xintercept = unif, linetype = "dashed", colour = eegb[["rust"]]) +
  scale_colour_manual(values = c(eegb[["rust"]], eegb[["navy"]]), name = NULL) +
  scale_y_continuous(labels = scales::label_comma(prefix = "₦")) +
  labs(title = "Naira per US dollar: rationing, then a reset", x = NULL, y = "₦ per US$", caption = cbn_src) + theme_eegb()
save_fig(p2, "s01", "f02")

# --- F03 · Real policy rate (exact Fisher) ----------------------------------------------
r <- m |> transmute(date, real = ((1 + policy_rate / 100) / (1 + cpi_headline_yoy / 100) - 1) * 100) |> filter(!is.na(real))
p3 <- ggplot(r, aes(date, real)) +
  geom_area(aes(y = pmin(real, 0)), fill = eegb[["rust"]], alpha = .35) +
  geom_area(aes(y = pmax(real, 0)), fill = eegb[["teal"]], alpha = .35) +
  geom_line(colour = eegb[["navy"]], linewidth = 1) + geom_hline(yintercept = 0, colour = eegb[["slate"]]) +
  geom_vline(xintercept = newcpi, linetype = "dashed", colour = eegb[["slate"]]) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  labs(title = sprintf("Savers lost to inflation for most of a decade (latest: %+.1f%%, %s)", tail(r$real, 1), format(tail(r$date, 1), "%b %Y")),
       x = NULL, y = "Policy rate in real terms", caption = paste(cbn_src, "Real rate = (1 + MPR) / (1 + inflation) − 1.")) + theme_eegb()
save_fig(p3, "s01", "f03")

# --- F04 · Oil and reserves ---------------------------------------------------------------
d <- m |> select(date, brent, reserves_gross_usdbn) |> filter(!is.na(brent), !is.na(reserves_gross_usdbn))
same <- cor(d$brent, d$reserves_gross_usdbn)
lag12 <- cor(d$brent, dplyr::lead(d$reserves_gross_usdbn, 12), use = "complete.obs")
k <- max(d$brent) / max(d$reserves_gross_usdbn)
p4 <- ggplot(d, aes(date)) +
  geom_line(aes(y = brent, colour = "Brent crude (US$/bbl, left)"), linewidth = 1) +
  geom_line(aes(y = reserves_gross_usdbn * k, colour = "Gross reserves (US$ bn, right)"), linewidth = 1.3) +
  scale_y_continuous(name = "US$ per barrel", sec.axis = sec_axis(~ . / k, name = "US$ billion")) +
  scale_colour_manual(values = c(eegb[["gold"]], eegb[["navy"]]), name = NULL) +
  labs(title = sprintf("Oil and reserves: r = %.2f in the same month, %.2f twelve months later", same, lag12), x = NULL,
       caption = "Sources: CBN gross reserves (month-end); FRED MCOILBRENTEU.") + theme_eegb()
save_fig(p4, "s01", "f04")
message(sprintf("F04 correlations: same month %.3f; 12 months later %.3f", same, lag12))

# --- F05 · GDP per person: constant vs current dollars -----------------------------------
p5 <- a |> filter(year >= 2000) |> select(year, `Constant 2015 US$ (real output per person)` = gdp_pc_const2015_usd,
                                          `Current US$ (prices and the exchange rate move it)` = gdp_pc_current_usd) |>
  pivot_longer(-year) |> ggplot(aes(year, value, colour = name)) + geom_line(linewidth = 1.2) +
  scale_colour_manual(values = c(eegb[["navy"]], eegb[["rust"]]), name = NULL) +
  scale_y_continuous(labels = scales::label_dollar(), limits = c(0, 3800)) +
  labs(title = "GDP per person: the dollar collapse is mostly the naira; real output fell ~10%", x = NULL, y = NULL,
       caption = "Source: World Bank WDI (NY.GDP.PCAP.KD, NY.GDP.PCAP.CD), Oct 2026.") + theme_eegb()
save_fig(p5, "s01", "f05")

# --- F06 · The board's macro page -----------------------------------------------------------
panel <- function(col, lab, colour) {
  s <- m |> filter(date >= as.Date("2023-10-01"), !is.na(.data[[col]])) |> select(date, v = all_of(col))
  last <- tail(s, 1); ago <- tail(filter(s, date <= seq(last$date, by = "-12 months", length.out = 2)[2]), 1)
  ggplot(s, aes(date, v)) + geom_line(colour = colour, linewidth = 1.1) + geom_point(data = last, colour = colour, size = 2) +
    labs(title = sprintf("%s\n%.1f (%+.1f vs a year ago, %s)", lab, last$v, last$v - ago$v, format(last$date, "%b %y")), x = NULL, y = NULL) +
    theme_eegb(10) + theme(plot.title = element_text(size = 10))
}
p6 <- (panel("cpi_headline_yoy", "Headline inflation (%)", eegb[["navy"]]) | panel("cpi_core_yoy", "Core inflation (%)", eegb[["teal"]]) |
       panel("policy_rate", "Monetary policy rate (%)", eegb[["teal2"]])) /
      (panel("usd_official_avg", "₦ per US$ (official)", eegb[["rust"]]) | panel("reserves_gross_usdbn", "Gross reserves (US$ bn)", eegb[["navy"]]) |
       panel("brent", "Brent crude (US$/bbl)", eegb[["gold"]])) +
  plot_annotation(title = "The board's macro page — latest value, three-year trend, change on a year ago",
                  caption = "Sources: CBN statistics; FRED (Brent).", theme = theme_eegb())
save_fig(p6, "s01", "f06", width = 13, height = 6.4)

# --- F07 · The 30% question (illustrative firm) ----------------------------------------------
fx23 <- a$ngn_usd_avg[a$year == 2023]; fx24 <- a$ngn_usd_avg[a$year == 2024]; infl <- 0.3324
vals <- c(52 / 40 - 1, (52 / 40) / (1 + infl) - 1, (52e9 / fx24) / (40e9 / fx23) - 1) * 100
p7 <- tibble(what = factor(c("Naira revenue\n(nominal)", "Real revenue\n(deflated by CPI)", "Revenue in\nUS dollars"), levels = c("Naira revenue\n(nominal)", "Real revenue\n(deflated by CPI)", "Revenue in\nUS dollars")), v = vals) |>
  ggplot(aes(what, v, fill = what)) + geom_col(width = .55, show.legend = FALSE) + geom_hline(yintercept = 0, colour = eegb[["slate"]]) +
  geom_text(aes(label = sprintf("%+.1f%%", v), vjust = ifelse(v > 0, -0.5, 1.5)), size = 5, fontface = "bold") +
  scale_fill_manual(values = unname(eegb[c("teal", "gold", "rust")])) + scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(-55, 40)) +
  labs(title = "FY2024 vs FY2023: 'sales up 30%' — or down 2%, or down 43%?", x = NULL, y = NULL,
       caption = sprintf("Illustrative firm: ₦40bn → ₦52bn. 2024 average inflation 33.2%%; ₦/$ averages %.0f (2023), %.0f (2024), World Bank.", fx23, fx24)) + theme_eegb()
save_fig(p7, "s01", "f07")
