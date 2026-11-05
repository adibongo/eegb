# =============================================================================
# EEGB · Session 8 · Monetary Policy from QE to QT
# Replication script — regenerates every chart in the Session 8 deck (R)
# Data: data/ng_macro_monthly.csv and data/global_policy_rates.csv (stylised)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
m  <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
pr <- read_csv("data/global_policy_rates.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
names_cb <- c(us_fed = "US Fed", euro_area_ecb = "ECB", uk_boe = "Bank of England", nigeria_cbn = "CBN (Nigeria)",
              south_africa_sarb = "SARB (S. Africa)", ghana_bog = "Bank of Ghana", kenya_cbk = "CBK (Kenya)")
cols_cb <- c(`US Fed` = eegb[["navy"]], ECB = eegb[["sky"]], `Bank of England` = eegb[["slate"]], `CBN (Nigeria)` = eegb[["rust"]],
             `SARB (S. Africa)` = eegb[["olive"]], `Bank of Ghana` = eegb[["gold"]], `CBK (Kenya)` = eegb[["teal"]])
long <- pr |> pivot_longer(-date, names_to = "bank", values_to = "rate") |> mutate(bank = names_cb[bank])

# --- F01 · Global tightening ---------------------------------------------------------
p1 <- ggplot(long, aes(date, rate, colour = bank)) + geom_step(linewidth = 1) +
  scale_colour_manual(values = cols_cb, name = NULL) + scale_y_continuous(labels = pct) +
  labs(title = "From near-zero to the fastest hikes in decades: 2022–24 was a global tightening",
       x = NULL, y = "Policy rate", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s08", "f01")

# --- F02 · Size of each tightening -----------------------------------------------------
lo <- long |> filter(date >= as.Date("2020-01-01"), date <= as.Date("2022-06-01")) |> group_by(bank) |> summarise(low = min(rate))
hi <- long |> filter(date >= as.Date("2022-01-01")) |> group_by(bank) |> summarise(high = max(rate))
hk <- inner_join(lo, hi, by = "bank") |> mutate(hike = high - low)
p2 <- ggplot(hk, aes(hike, reorder(bank, hike), fill = bank)) + geom_col(show.legend = FALSE) +
  geom_text(aes(label = sprintf("+%.2f pts  (%.2f%% → %.2f%%)", hike, low, high)), hjust = -0.05, size = 3.8) +
  scale_fill_manual(values = cols_cb) + scale_x_continuous(limits = c(0, max(hk$hike) * 1.6)) +
  labs(title = "Size of the tightening: from each bank's post-COVID low to its peak",
       x = "Increase in policy rate (percentage points)", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p2, "s08", "f02")

# --- F03 · MPR, interbank and inflation ---------------------------------------------------
p3 <- ggplot(m, aes(date)) +
  geom_line(aes(y = headline_inflation, colour = "Headline inflation"), linewidth = 1.1) +
  geom_step(aes(y = mpr, colour = "Monetary policy rate (MPR)"), linewidth = 1.3) +
  geom_line(aes(y = interbank_rate, colour = "Interbank rate"), linewidth = .8) +
  geom_vline(xintercept = as.Date("2025-01-01"), linetype = "dashed", colour = eegb[["slate"]]) +
  scale_colour_manual(values = c(`Headline inflation` = eegb[["gold"]], `Monetary policy rate (MPR)` = eegb[["navy"]],
                                 `Interbank rate` = eegb[["teal"]]), name = NULL) +
  scale_y_continuous(labels = pct) +
  labs(title = "The CBN chased inflation from behind until 2024", x = NULL, y = "Percent", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s08", "f03")

# --- F04 · Interbank minus MPR --------------------------------------------------------------
m <- m |> mutate(spread = interbank_rate - mpr)
p4 <- ggplot(m, aes(date, spread)) + geom_col(aes(fill = spread >= 0), show.legend = FALSE, width = 25) +
  geom_hline(yintercept = 0) +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]])) +
  labs(title = "The rate banks actually pay each other often strays far from the policy rate",
       subtitle = "Teal: interbank below MPR (cash plentiful). Rust: above MPR (cash tight).",
       x = NULL, y = "Interbank rate minus MPR (points)", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s08", "f04")

# --- F05 · Money and credit growth ------------------------------------------------------------
mc <- m |> select(date, `Broad money (M2) growth` = m2_growth_yoy, `Private-sector credit growth` = private_credit_growth_yoy) |>
  pivot_longer(-date, names_to = "series", values_to = "g")
p5 <- ggplot(mc, aes(date, g, colour = series)) +
  annotate("rect", xmin = as.Date("2023-06-01"), xmax = as.Date("2024-06-01"), ymin = -Inf, ymax = Inf, fill = eegb[["gold"]], alpha = .12) +
  geom_line(linewidth = 1.2) +
  scale_colour_manual(values = c(eegb[["teal"]], eegb[["gold"]]), name = NULL) + scale_y_continuous(labels = pct) +
  labs(title = "Money and credit growth peaked in 2023–24, then slowed as tight policy bit",
       subtitle = "Shaded: Jun 2023–Jun 2024, when devaluation revalued FX balances",
       x = NULL, y = "Growth, % y/y", caption = eegb_caption) + theme_eegb()
save_fig(p5, "s08", "f05")

# --- F06 · Illustrative Taylor rule ---------------------------------------------------------------
target <- 9; neutral_real <- 2
old <- m |> filter(date < as.Date("2025-01-01")) |>
  mutate(taylor = neutral_real + headline_inflation + 0.5 * (headline_inflation - target) + 0.5 * (pmi - 50))
p6 <- ggplot(old, aes(date)) +
  geom_ribbon(aes(ymin = pmin(mpr, taylor), ymax = taylor), fill = eegb[["rust"]], alpha = .18) +
  geom_line(aes(y = taylor, colour = "Illustrative Taylor-rule rate"), linewidth = 1.2) +
  geom_step(aes(y = mpr, colour = "Actual MPR"), linewidth = 1.3) +
  scale_colour_manual(values = c(`Illustrative Taylor-rule rate` = eegb[["gold"]], `Actual MPR` = eegb[["navy"]]), name = NULL) +
  scale_y_continuous(labels = pct) +
  labs(title = sprintf("By the rule, policy was too loose for most of the decade (Dec 2024: rule %.0f%% vs MPR %.1f%%)",
                       last(old$taylor), last(old$mpr)),
       x = NULL, y = "Percent",
       caption = "Rule: rate = 2% + inflation + 0.5 × (inflation − 9%) + 0.5 × (PMI − 50). Illustrative; stylised data.") + theme_eegb()
save_fig(p6, "s08", "f06")

# --- F07 · Rate differential vs the US and later depreciation ---------------------------------------
j <- pr |> select(date, us_fed) |> inner_join(select(m, date, mpr, official_fx_ngn_usd), by = "date") |>
  mutate(`CBN rate minus US Fed rate` = mpr - us_fed,
         `Naira depreciation over the NEXT 12 months` = 100 * (lead(official_fx_ngn_usd, 12) / official_fx_ngn_usd - 1)) |>
  select(date, `CBN rate minus US Fed rate`, `Naira depreciation over the NEXT 12 months`) |>
  pivot_longer(-date, names_to = "series", values_to = "v")
p7 <- ggplot(j, aes(date, v, colour = series, linetype = series)) + geom_line(linewidth = 1.2, na.rm = TRUE) + geom_hline(yintercept = 0) +
  scale_colour_manual(values = c(eegb[["teal"]], eegb[["rust"]]), name = NULL) +
  scale_linetype_manual(values = c("solid", "dashed"), name = NULL) +
  labs(title = "A big rate gap attracts dollars — unless the naira falls by more",
       x = NULL, y = "Percentage points / percent", caption = eegb_caption) + theme_eegb()
save_fig(p7, "s08", "f07")
