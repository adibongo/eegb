# =============================================================================
# EEGB · Session 7 · National Accounts, Productivity & Welfare
# Replication script — regenerates every chart in the Session 7 deck (R)
# Data: data/ng_gdp_sectors.csv and data/peer_income.csv (stylised)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
g <- read_csv("data/ng_gdp_sectors.csv", show_col_types = FALSE)
peers <- read_csv("data/peer_income.csv", show_col_types = FALSE)
sectors <- c("agriculture", "oil_and_gas", "manufacturing", "construction", "trade", "ict_telecom",
             "finance_insurance", "real_estate", "public_admin", "other_services")
nice <- c(agriculture = "Agriculture", oil_and_gas = "Oil & gas", manufacturing = "Manufacturing", construction = "Construction",
          trade = "Trade", ict_telecom = "ICT & telecom", finance_insurance = "Finance & insurance", real_estate = "Real estate",
          public_admin = "Public admin", other_services = "Other services")
kfmt <- function(v) paste0("$", v / 1000, "k")

# --- F01 · Growth contributions: oil vs non-oil ---------------------------------------------
g <- g |> mutate(growth = 100 * (real_gdp_total / lag(real_gdp_total) - 1), non_oil = real_gdp_total - oil_and_gas,
                 `Oil & gas contribution` = 100 * (oil_and_gas - lag(oil_and_gas)) / lag(real_gdp_total),
                 `Non-oil contribution` = 100 * (non_oil - lag(non_oil)) / lag(real_gdp_total))
contrib <- g |> filter(!is.na(growth)) |> select(year, `Oil & gas contribution`, `Non-oil contribution`) |>
  pivot_longer(-year, names_to = "part", values_to = "pts")
p1 <- ggplot(contrib, aes(year, pts, fill = part)) + geom_col() +
  geom_line(data = filter(g, !is.na(growth)), aes(year, growth), inherit.aes = FALSE, colour = eegb[["navy"]], linewidth = 1.1) +
  geom_point(data = filter(g, !is.na(growth)), aes(year, growth), inherit.aes = FALSE, colour = eegb[["navy"]], size = 2.5) +
  geom_hline(yintercept = 0) +
  scale_fill_manual(values = c(`Oil & gas contribution` = eegb[["gold"]], `Non-oil contribution` = eegb[["teal"]]), name = NULL) +
  labs(title = "Non-oil activity drives growth; oil mostly subtracts or adds a little",
       subtitle = "Bars: contributions in percentage points. Line: real GDP growth.",
       x = NULL, y = "Percentage points of real GDP growth", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s07", "f01")

# --- F02 · Sector shares 2010 vs 2025 ---------------------------------------------------------
sh <- g |> filter(year %in% c(2010, 2025)) |> select(year, real_gdp_total, all_of(sectors)) |>
  pivot_longer(all_of(sectors), names_to = "sector", values_to = "v") |> mutate(share = 100 * v / real_gdp_total,
  sector = nice[sector], year = factor(year))
ord <- sh |> filter(year == "2025") |> arrange(share) |> pull(sector)
p2 <- ggplot(sh, aes(share, factor(sector, levels = ord), fill = year)) + geom_col(position = position_dodge(width = .8), width = .75) +
  scale_fill_manual(values = c(`2010` = "#C9D2DC", `2025` = eegb[["teal"]]), name = NULL) +
  scale_x_continuous(labels = function(v) paste0(v, "%")) +
  labs(title = "ICT and services grew their share; oil's share of real GDP fell sharply",
       x = "Share of real GDP (constant prices)", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p2, "s07", "f02")

# --- F03 · GDP, population and GDP per person (index) ------------------------------------------
idx <- g |> transmute(year, `Real GDP` = 100 * real_gdp_total / first(real_gdp_total),
                      Population = 100 * population_m / first(population_m),
                      `Real GDP per person` = 100 * (real_gdp_total / population_m) / first(real_gdp_total / population_m)) |>
  pivot_longer(-year, names_to = "series", values_to = "index")
p3 <- ggplot(idx, aes(year, index, colour = series)) + geom_line(linewidth = 1.3) + geom_hline(yintercept = 100, linetype = "dotted") +
  scale_colour_manual(values = c(`Real GDP` = eegb[["teal"]], Population = eegb[["slate"]], `Real GDP per person` = eegb[["rust"]]), name = NULL) +
  labs(title = "The economy grew; the average Nigerian's real income barely moved", x = NULL, y = "Index, 2010 = 100",
       caption = eegb_caption) + theme_eegb()
save_fig(p3, "s07", "f03")

# --- F04 · Nominal vs real GDP ---------------------------------------------------------------
p4 <- ggplot(g, aes(year)) +
  geom_ribbon(aes(ymin = real_gdp_total, ymax = nominal_gdp_old_base), fill = eegb[["gold"]], alpha = .15) +
  geom_line(aes(y = nominal_gdp_old_base, colour = "Nominal GDP (current prices)"), linewidth = 1.4) +
  geom_line(aes(y = real_gdp_total, colour = "Real GDP (2010 prices)"), linewidth = 1.4) +
  scale_colour_manual(values = c(eegb[["gold"]], eegb[["navy"]]), name = NULL) +
  scale_y_continuous(labels = function(v) paste0("₦", v, "tn")) +
  labs(title = sprintf("Nominal GDP rose %.1f×; real GDP only %.2f×", last(g$nominal_gdp_old_base) / first(g$nominal_gdp_old_base),
                       last(g$real_gdp_total) / first(g$real_gdp_total)), x = NULL, y = "₦ trillion", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s07", "f04")

# --- F05 · Rebasing ---------------------------------------------------------------------------
rb <- g |> filter(year >= 2019) |> select(year, `Old base` = nominal_gdp_old_base, `New (rebased) series` = nominal_gdp_new_base) |>
  pivot_longer(-year, names_to = "series", values_to = "v")
p5 <- ggplot(rb, aes(factor(year), v, fill = series)) + geom_col(position = "dodge") +
  scale_fill_manual(values = c(`Old base` = "#C9D2DC", `New (rebased) series` = eegb[["teal"]]), name = NULL) +
  scale_y_continuous(labels = function(v) paste0("₦", v, "tn")) +
  labs(title = "Rebasing captured activity the old survey missed — the economy did not grow overnight",
       x = NULL, y = "Nominal GDP, ₦ trillion",
       caption = "Stylised teaching data. The size of the uplift is illustrative, not the official NBS revision.") + theme_eegb()
save_fig(p5, "s07", "f05")

# --- F06 · Market exchange rates vs PPP -------------------------------------------------------
p6 <- ggplot(peers, aes(y = reorder(country, gdp_per_capita_ppp))) +
  geom_segment(aes(x = gdp_per_capita_usd, xend = gdp_per_capita_ppp, yend = reorder(country, gdp_per_capita_ppp)), colour = "#C9D2DC", linewidth = 2) +
  geom_point(aes(x = gdp_per_capita_usd, colour = "At market exchange rates"), size = 3.5) +
  geom_point(aes(x = gdp_per_capita_ppp, colour = "At purchasing power parity (PPP)"), size = 3.5) +
  scale_colour_manual(values = c(eegb[["rust"]], eegb[["teal"]]), name = NULL) + scale_x_continuous(labels = kfmt) +
  labs(title = "A dollar buys far more in Lagos than in New York: PPP corrects for that",
       x = "GDP per person, US$", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p6, "s07", "f06")

# --- F07 · Informality vs income --------------------------------------------------------------
fit <- lm(I(100 * informal_share_gdp) ~ I(gdp_per_capita_ppp / 1000), data = peers)
p7 <- ggplot(peers, aes(gdp_per_capita_ppp, 100 * informal_share_gdp)) +
  geom_smooth(method = "lm", se = FALSE, linetype = "dashed", colour = eegb[["gold"]], formula = y ~ x) +
  geom_point(aes(size = pmin(population_m, 400)), colour = eegb[["navy"]], fill = eegb[["teal"]], shape = 21, alpha = .7, show.legend = FALSE) +
  geom_text(aes(label = country), nudge_x = 300, nudge_y = 1, hjust = 0, size = 3.6) +
  scale_x_continuous(labels = kfmt) + scale_y_continuous(labels = function(v) paste0(v, "%")) +
  labs(title = sprintf("Poorer economies are more informal — about %.1f pts less informality per $1k of PPP income", abs(coef(fit)[2])),
       x = "GDP per person, PPP US$ (bubble size = population)", y = "Informal share of GDP", caption = eegb_caption) + theme_eegb()
save_fig(p7, "s07", "f07")

# --- F08 · Rule of 70 ---------------------------------------------------------------------------
pc <- g$real_gdp_total / g$population_m
pc_growth <- 100 * ((last(pc) / first(pc))^(1 / (nrow(g) - 1)) - 1)
r70 <- tibble(rate = c(0.5, 1, 2, 3, 4, 5, 7)) |> mutate(years = log(2) / log(1 + rate / 100), lab = paste0(rate, "%"))
p8 <- ggplot(r70, aes(factor(lab, levels = lab), years, fill = rate < 1.5)) + geom_col(show.legend = FALSE) +
  geom_text(aes(label = paste0(round(years), " yrs")), vjust = -.4) +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]])) +
  labs(title = sprintf("At this data's %.1f%% a year per person, living standards double in about %.0f years",
                       pc_growth, log(2) / log(1 + pc_growth / 100)),
       x = "Growth in real income per person, per year", y = "Years to double", caption = "Years to double = ln 2 ÷ ln(1 + g) ≈ 70 ÷ g.") + theme_eegb()
save_fig(p8, "s07", "f08")
