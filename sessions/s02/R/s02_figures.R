# =============================================================================
# EEGB · Session 2 · Demand, Supply & Elasticity with Behavioural Insights
# Replication script — regenerates every chart in the Session 2 deck (R)
# Data: data/fmcg_price_volume.csv (stylised weekly noodles sales, 3 regions, 2022–2025)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
d <- read_csv("data/fmcg_price_volume.csv", show_col_types = FALSE) |>
  group_by(region) |> mutate(t = row_number() - 1) |> ungroup()
reg_cols <- c(Lagos = eegb[["teal"]], North = eegb[["gold"]], `South-East` = eegb[["rust"]])

fit <- lm(log(units) ~ log(price_naira) + log(competitor_price_naira) + log(income_index) + t + region, data = d)
own <- coef(fit)[["log(price_naira)"]]; cross <- coef(fit)[["log(competitor_price_naira)"]]
inc <- coef(fit)[["log(income_index)"]]
naive <- coef(lm(log(units) ~ log(price_naira), data = d))[[2]]

# --- F01 · A cost shock shifts supply ---------------------------------------------------
q <- seq(0, 10, length.out = 200)
cur <- bind_rows(tibble(q, p = 900 - 50 * q, curve = "Demand"),
                 tibble(q, p = 200 + 40 * q, curve = "Supply before the flour shock"),
                 tibble(q, p = 290 + 40 * q, curve = "Supply after: costs up"))
eq <- tibble(q = c(700, 610) / 90) |> mutate(p = 900 - 50 * q)
p1 <- ggplot(cur, aes(q, p, colour = curve, linetype = curve)) + geom_line(linewidth = 1.3) +
  geom_point(data = eq, aes(q, p), inherit.aes = FALSE, size = 3.5, colour = c(eegb[["teal"]], eegb[["rust"]])) +
  scale_colour_manual(values = c(Demand = eegb[["navy"]], `Supply before the flour shock` = eegb[["teal"]],
                                 `Supply after: costs up` = eegb[["rust"]]), name = NULL) +
  scale_linetype_manual(values = c(Demand = "solid", `Supply before the flour shock` = "solid", `Supply after: costs up` = "dashed"), name = NULL) +
  coord_cartesian(ylim = c(0, 950)) +
  labs(title = "A cost shock shifts supply up: the price rises by less than the cost, and volume falls",
       x = "Quantity of noodles", y = "Price") + theme_eegb() + theme(axis.text = element_blank())
save_fig(p1, "s02", "f01")

# --- F02 · Prices and volumes ----------------------------------------------------------------
long <- d |> group_by(region) |> mutate(units_k = as.numeric(stats::filter(units, rep(1 / 4, 4), sides = 1)) / 1000) |> ungroup() |>
  select(week, region, `Shelf price per pack (₦)` = price_naira, `Packs sold ('000, 4-week avg)` = units_k) |>
  pivot_longer(-c(week, region))
p2 <- ggplot(long, aes(week, value, colour = region)) + geom_line(linewidth = 1) +
  facet_wrap(~name, ncol = 1, scales = "free_y") + scale_colour_manual(values = reg_cols, name = NULL) +
  labs(title = "Prices more than tripled — yet volumes held up in two of three regions", x = NULL, y = NULL) + theme_eegb()
save_fig(p2, "s02", "f02", height = 6.4)

# --- F03 · The naive picture ------------------------------------------------------------------
p3 <- ggplot(d, aes(price_naira, units / 1000)) + geom_point(aes(colour = region), alpha = .55) +
  geom_smooth(method = "lm", formula = y ~ log(x), se = FALSE, colour = eegb[["navy"]]) +
  scale_colour_manual(values = reg_cols, name = NULL) +
  labs(title = sprintf("Naive view: price 'barely matters' (elasticity %.2f) — because everything else inflated too", naive),
       x = "Shelf price per pack (₦)", y = "Packs sold per week ('000)") + theme_eegb(12)
save_fig(p3, "s02", "f03")

# --- F04 · Controlled estimates -----------------------------------------------------------------
est <- tibble(term = factor(c("Own-price elasticity", "Cross-price elasticity", "Income elasticity", "Naive own-price (no controls)"),
                            levels = rev(c("Own-price elasticity", "Cross-price elasticity", "Income elasticity", "Naive own-price (no controls)"))),
              value = c(own, cross, inc, naive))
p4 <- ggplot(est, aes(value, term)) + geom_col(fill = c(eegb[["rust"]], eegb[["teal"]], eegb[["gold"]], "#B8C2CE")) +
  geom_text(aes(label = sprintf("%+.2f", value), hjust = ifelse(value >= 0, -0.2, 1.2))) + geom_vline(xintercept = 0) +
  xlim(-2, 1.6) + labs(title = "Once inflation, rivals and income are held constant, customers are price-sensitive",
                       x = "% change in packs sold for a 1% change", y = NULL) + theme_eegb()
save_fig(p4, "s02", "f04", height = 4.6)

# --- F05 · Revenue response by elasticity --------------------------------------------------------
rev <- expand_grid(rise = seq(0, 40, by = .5), e = c(-0.5, -1, round(own, 1), -2.5)) |>
  mutate(revenue = ((1 + rise / 100)^(1 + e) - 1) * 100, e = factor(paste("elasticity", e)))
p5 <- ggplot(rev, aes(rise, revenue, colour = e)) + geom_line(linewidth = 1.2) + geom_hline(yintercept = 0) +
  scale_colour_manual(values = unname(eegb[c("teal", "slate", "rust", "navy")]), name = NULL) +
  scale_x_continuous(labels = pct) + scale_y_continuous(labels = pct) +
  labs(title = "Raise price on an elastic product and revenue falls; on an inelastic one it rises",
       x = "Price increase (other prices unchanged)", y = "Change in revenue") + theme_eegb()
save_fig(p5, "s02", "f05")

# --- F06 · Reference prices ------------------------------------------------------------------------
d$res <- residuals(fit)
d <- d |> group_by(region) |>
  mutate(ref = { r <- numeric(n()); r[1] <- NA; m <- price_naira[1]
                 for (i in seq_len(n())[-1]) { r[i] <- m; m <- 0.8 * m + 0.2 * price_naira[i] }; r }) |> ungroup() |>
  mutate(gap = log(price_naira / ref),
         bin = cut(gap, c(-1, 0, .05, .10, 1), labels = c("Below usual (promotions)", "0–5% above usual", "5–10% above usual", "More than 10% above usual")))
rb <- d |> filter(!is.na(bin)) |> group_by(bin) |> summarise(res = 100 * mean(res))
p6 <- ggplot(rb, aes(bin, res, fill = bin)) + geom_col(show.legend = FALSE) + geom_hline(yintercept = 0) +
  geom_text(aes(label = sprintf("%+.1f%%", res), vjust = ifelse(res >= 0, -0.4, 1.4))) +
  scale_fill_manual(values = unname(eegb[c("teal", "slate", "gold", "rust")])) + scale_y_continuous(labels = pct) +
  labs(title = "Shoppers punish prices well above what they are used to", x = NULL, y = "Extra sales vs model prediction") + theme_eegb()
save_fig(p6, "s02", "f06", height = 4.8)

# --- F07 · Promotion lift ----------------------------------------------------------------------------
lift <- d |> group_by(region, promo) |> summarise(u = mean(units), .groups = "drop") |>
  pivot_wider(names_from = promo, values_from = u) |> mutate(lift = 100 * (`1` / `0` - 1))
p7 <- ggplot(lift, aes(region, lift, fill = region)) + geom_col(show.legend = FALSE) +
  geom_text(aes(label = sprintf("+%.0f%%", lift)), vjust = -0.4) + scale_fill_manual(values = reg_cols) +
  scale_y_continuous(labels = pct) +
  labs(title = "A 15% promotional discount lifts weekly volume by roughly a third", x = NULL, y = "Volume in promo weeks vs normal weeks") + theme_eegb()
save_fig(p7, "s02", "f07", height = 4.6)

# --- F08 · Cost pass-through ---------------------------------------------------------------------------
P0 <- 500; C0 <- 350; dc <- C0 * 0.45 * 0.40
pt <- expand_grid(share = seq(0, 1, by = .02), scen = c("Rivals hold their price (own elasticity)", "Rivals raise prices too (own + cross)")) |>
  mutate(e = ifelse(grepl("hold", scen), own, own + cross), P = P0 + share * dc, Q = (P / P0)^e,
         profit = 100 * (P - C0 - dc) * Q / (P0 - C0))
p8 <- ggplot(pt, aes(100 * share, profit, colour = scen)) + geom_line(linewidth = 1.3) +
  geom_hline(yintercept = 100, linetype = "dashed", colour = eegb[["slate"]]) +
  scale_colour_manual(values = unname(eegb[c("rust", "teal")]), name = NULL) +
  scale_x_continuous(labels = pct) + scale_y_continuous(labels = pct, limits = c(50, 105)) +
  labs(title = sprintf("Flour up 40%% adds ₦%.0f a pack: absorbing it is the costliest choice", dc),
       x = "Share of the cost increase passed into price", y = "Profit, % of pre-shock level") + theme_eegb()
save_fig(p8, "s02", "f08")
