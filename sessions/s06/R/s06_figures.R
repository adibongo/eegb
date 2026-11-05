# =============================================================================
# EEGB · Session 6 · AD–AS in a Shock-Prone World
# Replication script — regenerates every chart in the Session 6 deck (R)
# Data: data/ng_macro_monthly.csv (stylised Nigerian macro series, 2015–2025)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
m <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
old <- m |> filter(date < as.Date("2025-01-01"))      # one CPI base only

# --- F01 · Demand shock vs supply shock -------------------------------------------------
q <- seq(0, 10, length.out = 100)
curves <- bind_rows(
  tibble(panel = "Demand shock: prices UP, output UP", q = q, AS = 2 + .6 * q, AD = 8 - .6 * q, new = 9.5 - .6 * q, newlab = "new AD"),
  tibble(panel = "Supply shock: prices UP, output DOWN", q = q, AS = 2 + .6 * q, AD = 8 - .6 * q, new = 3.5 + .6 * q, newlab = "new AS"))
pts <- tibble(panel = rep(unique(curves$panel), each = 2), q = c(5, 6.25, 5, 3.75), p = c(5, 5.75, 5, 5.75),
              when = rep(c("before", "after"), 2))
p1 <- ggplot(curves, aes(q)) +
  geom_line(aes(y = AS), colour = eegb[["slate"]], linewidth = 1.1) +
  geom_line(aes(y = AD), colour = eegb[["teal"]], linewidth = 1.1) +
  geom_line(aes(y = new), colour = eegb[["rust"]], linewidth = 1.1, linetype = "dashed") +
  geom_point(data = pts, aes(q, p, colour = when), size = 3.5) +
  scale_colour_manual(values = c(before = eegb[["navy"]], after = eegb[["gold"]]), name = NULL) +
  facet_wrap(~panel) + coord_cartesian(ylim = c(0, 10)) +
  labs(title = "Same rise in prices, opposite news for output", subtitle = "Solid: AS (grey) and AD (teal). Dashed: the curve after the shock.",
       x = "Real output (GDP)", y = "Price level") +
  theme_eegb() + theme(axis.text = element_blank(), panel.grid = element_blank())
save_fig(p1, "s06", "f01", width = 11, height = 4.8)

# --- F02 · Food minus core inflation ----------------------------------------------------
old <- old |> mutate(gap = food_inflation - core_inflation)
p2 <- ggplot(old, aes(date, gap, fill = gap > 0)) + geom_col(show.legend = FALSE) + geom_hline(yintercept = 0) +
  scale_fill_manual(values = c(`TRUE` = eegb[["gold"]], `FALSE` = eegb[["teal"]])) +
  labs(title = sprintf("Food inflation ran ahead of core almost every month (average gap %+.1f pts)", mean(old$gap)),
       x = NULL, y = "Food minus core inflation (points)", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s06", "f02")

# --- F03 · Exchange-rate pass-through ---------------------------------------------------
m <- m |> mutate(dep = 100 * (official_fx_ngn_usd / lag(official_fx_ngn_usd, 12) - 1))
lags <- 0:12
rs <- sapply(lags, function(k) { x <- lag(m$dep, k); ok <- !is.na(x) & m$date < as.Date("2025-01-01")
                                  cor(x[ok], m$headline_inflation[ok]) })
best <- lags[which.max(rs)]
scale_k <- 0.15   # put depreciation (up to ~230%) on the inflation axis
p3 <- ggplot(m, aes(date)) +
  geom_line(aes(y = dep * scale_k, colour = "Naira depreciation vs a year ago (right axis)"), linewidth = 1) +
  geom_line(aes(y = headline_inflation, colour = "Headline inflation (left axis)"), linewidth = 1.3) +
  geom_vline(xintercept = as.Date("2025-01-01"), linetype = "dashed", colour = eegb[["slate"]]) +
  scale_y_continuous(name = "Inflation, % y/y", sec.axis = sec_axis(~ . / scale_k, name = "Depreciation, % y/y")) +
  scale_colour_manual(values = c(eegb[["navy"]], eegb[["rust"]]), name = NULL) +
  labs(title = sprintf("A weaker naira shows up in prices about %d months later (r = %.2f at that lag)", best, max(rs)),
       x = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p3, "s06", "f03")

# --- F04 · Stagflation scatter ------------------------------------------------------------
old <- old |> mutate(period = case_when(date < as.Date("2020-01-01") ~ "2015–19",
                                        date < as.Date("2023-01-01") ~ "2020–22", TRUE ~ "2023–24 reforms"))
p4 <- ggplot(old, aes(pmi, headline_inflation, colour = period)) + geom_point(size = 2.5, alpha = .75) +
  geom_vline(xintercept = 50, linetype = "dashed") +
  scale_colour_manual(values = c(`2015–19` = eegb[["slate"]], `2020–22` = eegb[["teal"]], `2023–24 reforms` = eegb[["rust"]]), name = NULL) +
  scale_y_continuous(labels = pct) +
  labs(title = "2023–24: inflation doubled while activity stalled near PMI 50 — a supply-shock signature",
       x = "Purchasing Managers' Index", y = "Headline inflation", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s06", "f04")

# --- F05 · Mean, median and trimmed mean (illustrative basket) ---------------------------------
basket <- tibble(item = c("Bread & cereals", "Yam & tubers", "Meat & fish", "Vegetables", "Rent", "Electricity",
                          "Petrol & transport", "Clothing", "Health", "Education", "Phone & data", "Restaurants"),
                 w = c(18, 9, 10, 8, 12, 5, 9, 7, 5, 6, 5, 6), chg = c(3.4, 4.8, 2.6, 6.2, 1.4, .6, 9.5, 1.1, 1.6, .9, .4, 2.2)) |>
  mutate(w = w / sum(w)) |> arrange(chg) |> mutate(cw = cumsum(w), keep = (cw - w >= .15) & (cw <= .85 + 1e-9))
wmean <- sum(basket$w * basket$chg)
tmean <- with(filter(basket, keep), sum(w * chg) / sum(w))
wmed <- basket$chg[which(basket$cw >= .5)[1]]
p5 <- ggplot(basket, aes(chg, reorder(item, chg), fill = keep)) + geom_col(show.legend = FALSE) +
  geom_vline(xintercept = c(wmean, tmean, wmed), colour = c(eegb[["navy"]], eegb[["teal"]], eegb[["rust"]]), linetype = "dashed", linewidth = 1) +
  annotate("text", x = 6, y = c(3, 2, 1), hjust = 0, fontface = "bold", colour = c(eegb[["navy"]], eegb[["teal"]], eegb[["rust"]]),
           label = c(sprintf("weighted mean %.1f%%", wmean), sprintf("trimmed mean %.1f%%", tmean), sprintf("weighted median %.1f%%", wmed))) +
  scale_fill_manual(values = c(`TRUE` = eegb[["gold"]], `FALSE` = "#C9D2DC")) +
  labs(title = "Trimmed mean: drop the most extreme price moves, average the middle 70%",
       x = "Price change this month (%) — grey items are trimmed", y = NULL,
       caption = "Illustrative basket; not NBS data.") + theme_eegb()
save_fig(p5, "s06", "f05")

# --- F06 · Persistence ----------------------------------------------------------------------
s <- old |> mutate(lag12 = lag(headline_inflation, 12)) |> filter(!is.na(lag12))
fit <- lm(headline_inflation ~ lag12, data = s)
p6 <- ggplot(s, aes(lag12, headline_inflation)) + geom_point(colour = eegb[["teal"]], alpha = .7, size = 2.3) +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed", colour = eegb[["slate"]]) +
  geom_smooth(method = "lm", se = FALSE, colour = eegb[["gold"]], linewidth = 1.4, formula = y ~ x) +
  labs(title = sprintf("Inflation is sticky: last year's rate is the best single guide to this year's (slope %.2f)", coef(fit)[2]),
       x = "Inflation 12 months earlier (%)", y = "Inflation now (%)", caption = eegb_caption) + theme_eegb()
save_fig(p6, "s06", "f06")

# --- F07 · Expectations-augmented Phillips curve ----------------------------------------------
u <- seq(2, 10, length.out = 100)
pc <- expand_grid(u = u, pe = c(10, 20, 30)) |> mutate(infl = pe + 2.2 * (6 - u), lab = paste0("Expected inflation ", pe, "%"))
p7 <- ggplot(pc, aes(u, infl, colour = lab)) + geom_line(linewidth = 1.3) + geom_vline(xintercept = 6, linetype = "dotted") +
  scale_colour_manual(values = c(eegb[["teal"]], eegb[["gold"]], eegb[["rust"]]), name = NULL) + coord_cartesian(ylim = c(0, 42)) +
  labs(title = "When expectations rise, the whole curve shifts up: same slack, higher inflation",
       x = "Slack in the economy (unemployment / spare capacity)", y = "Inflation (%)", caption = "Conceptual diagram.") + theme_eegb()
save_fig(p7, "s06", "f07")
