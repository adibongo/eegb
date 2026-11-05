# =============================================================================
# EEGB · Session 3 · Demand Forecasting & Market Sizing
# Replication script — regenerates every chart in the Session 3 deck (R)
# Data: data/cement_demand_monthly.csv (stylised Nigerian cement consumption, 2012–2025)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
c <- read_csv("data/cement_demand_monthly.csv", show_col_types = FALSE) |>
  mutate(month = as.Date(month), t = row_number() - 1, m = as.integer(format(month, "%m")),
         year = as.integer(format(month, "%Y")))
mape <- function(a, f) 100 * mean(abs(a - f) / a)
fit_ts <- function(df, deg = 1) lm(log(cement_mt) ~ poly(I(t / 100), deg, raw = TRUE) + factor(m), data = df)

# --- F01 · Raw series and trend ------------------------------------------------------------
c$ma12 <- as.numeric(stats::filter(c$cement_mt, rep(1 / 12, 12), sides = 2))
shocks <- tibble(s = as.Date(c("2016-01-01", "2020-04-01", "2024-01-01")), e = as.Date(c("2016-12-01", "2020-08-01", "2024-12-01")),
                 lab = c("2016 recession", "COVID lockdown", "2024 price spike"))
p1 <- ggplot(c, aes(month)) +
  geom_rect(data = shocks, aes(xmin = s, xmax = e, ymin = -Inf, ymax = Inf), inherit.aes = FALSE, fill = eegb[["gold"]], alpha = .18) +
  geom_text(data = shocks, aes(x = s, y = 3.1, label = lab), inherit.aes = FALSE, hjust = 0, size = 3.3, colour = eegb[["navy"]]) +
  geom_line(aes(y = cement_mt, colour = "Monthly consumption"), linewidth = .7) +
  geom_line(aes(y = ma12, colour = "12-month moving average (trend)"), linewidth = 1.4, na.rm = TRUE) +
  scale_colour_manual(values = c(`Monthly consumption` = eegb[["sky"]], `12-month moving average (trend)` = eegb[["navy"]]), name = NULL) +
  labs(title = "Cement demand: a steady upward trend, a strong yearly rhythm, and occasional shocks",
       x = NULL, y = "Million tonnes per month", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s03", "f01")

# --- F02 · Seasonal index ------------------------------------------------------------------------
fa <- fit_ts(c); b <- coef(fa)
seas <- exp(c(0, b[grep("factor", names(b))])); seas <- 100 * seas / mean(seas)
si <- tibble(m = factor(month.abb, levels = month.abb), idx = seas, rainy = 1:12 %in% 6:9)
p2 <- ggplot(si, aes(m, idx, fill = rainy)) + geom_col(show.legend = FALSE) + geom_hline(yintercept = 100) +
  geom_text(aes(label = round(idx)), vjust = -0.4) + coord_cartesian(ylim = c(60, 125)) +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]])) +
  labs(title = sprintf("The rainy season (red) cuts demand: August is %.0f%% below an average month", 100 - seas[8]),
       x = NULL, y = "Seasonal index (average month = 100)", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s03", "f02", height = 4.8)

# --- F03 & F04 · Backtest -------------------------------------------------------------------------
train <- filter(c, year <= 2023); test <- filter(c, year >= 2024)
f_reg <- exp(predict(fit_ts(train), newdata = test))
last12 <- tail(train$cement_mt, 12)
f_sn <- c(last12, last12); f_avg <- rep(mean(last12), 24); f_j <- c(last12 * 1.05, last12 * 1.05^2)
bt <- bind_rows(tibble(month = test$month, value = f_sn, series = "Same month last year"),
                tibble(month = test$month, value = f_reg, series = "Trend + seasonal model"),
                filter(c, year >= 2021) |> transmute(month, value = cement_mt, series = "Actual"))
p3 <- ggplot(bt, aes(month, value, colour = series, linetype = series)) + geom_line(linewidth = 1.1) +
  geom_vline(xintercept = as.Date("2024-01-01"), linetype = "dotted") +
  scale_colour_manual(values = c(Actual = eegb[["ink"]], `Same month last year` = eegb[["gold"]], `Trend + seasonal model` = eegb[["teal"]]), name = NULL) +
  scale_linetype_manual(values = c(Actual = "solid", `Same month last year` = "dashed", `Trend + seasonal model` = "solid"), name = NULL) +
  labs(title = "Backtest: models built on 2012–2023 data, tested on 2024–2025", x = NULL, y = "Million tonnes per month",
       caption = eegb_caption) + theme_eegb()
save_fig(p3, "s03", "f03")
sc <- tibble(method = c("Flat average of last year", "Same month last year", "Budget rule: last year + 5%", "Trend + seasonal model"),
             mape = c(mape(test$cement_mt, f_avg), mape(test$cement_mt, f_sn), mape(test$cement_mt, f_j), mape(test$cement_mt, f_reg))) |>
  mutate(method = factor(method, levels = rev(method)))
p4 <- ggplot(sc, aes(mape, method)) + geom_col(fill = rev(unname(eegb[c("slate", "gold", "olive", "teal")]))) +
  geom_text(aes(label = sprintf("%.1f%%", mape)), hjust = -0.2) + scale_x_continuous(labels = pct, expand = expansion(mult = c(0, .15))) +
  labs(title = "Average forecast error (MAPE) on 2024–2025: simple, honest models win",
       x = "Mean absolute percentage error (lower is better)", y = NULL) + theme_eegb()
save_fig(p4, "s03", "f04", height = 4.6)

# --- F05 · 2026 forecast with an uncertainty band ---------------------------------------------------
fut <- tibble(month = seq(as.Date("2026-01-01"), by = "month", length.out = 12), t = nrow(c) + 0:11, m = 1:12)
fut$f <- exp(predict(fa, newdata = fut)); rsd <- summary(fa)$sigma
fut <- fut |> mutate(lo = f * exp(-1.645 * rsd), hi = f * exp(1.645 * rsd))
ann_dev <- c |> mutate(fit = exp(fitted(fa))) |> group_by(year) |> summarise(d = log(sum(cement_mt) / sum(fit)))
sd_a <- sd(ann_dev$d); tot <- sum(fut$f)
p5 <- ggplot() + geom_line(data = filter(c, year >= 2022), aes(month, cement_mt), colour = eegb[["ink"]], linewidth = 1) +
  geom_ribbon(data = fut, aes(month, ymin = lo, ymax = hi), fill = eegb[["teal"]], alpha = .25) +
  geom_line(data = fut, aes(month, f), colour = eegb[["teal"]], linewidth = 1.4) +
  labs(title = sprintf("2026 forecast: about %.1f million tonnes (range roughly %.1f–%.1f)", tot, tot * exp(-1.645 * sd_a), tot * exp(1.645 * sd_a)),
       x = NULL, y = "Million tonnes per month", caption = eegb_caption) + theme_eegb()
save_fig(p5, "s03", "f05")

# --- F06 · Scenarios -----------------------------------------------------------------------------------
scen <- tibble(s = factor(c("Downside: price spike + weak incomes (−8%)", "Base: trend + season", "Upside: housing & road programme (+6%)"),
                          levels = c("Downside: price spike + weak incomes (−8%)", "Base: trend + season", "Upside: housing & road programme (+6%)")),
               v = tot * c(.92, 1, 1.06))
p6 <- ggplot(scen, aes(s, v, fill = s)) + geom_col(width = .55, show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.1f mt", v)), vjust = -0.4) +
  scale_fill_manual(values = unname(eegb[c("rust", "teal", "gold")])) + scale_x_discrete(labels = function(x) gsub(": ", ":\n", x)) +
  labs(title = "Plan capacity for a range, not a point: three 2026 scenarios", x = NULL, y = "Million tonnes in 2026") + theme_eegb()
save_fig(p6, "s03", "f06", height = 4.8)

# --- F07 · Market sizing ----------------------------------------------------------------------------------
parts <- tibble(route = "Bottom-up", part = c("New homes", "Repairs & extensions", "Roads, bridges & public works", "Commercial & industrial", "Blocks, pipes & precast"),
                v = c(0.45 * 32, 6.5, 6.0, 4.5, 2.4))
td <- tibble(route = "Top-down", part = "230m people × 140 kg", v = 230 * 140 / 1000)
p7 <- ggplot(bind_rows(parts, td), aes(v, route, fill = part)) + geom_col(width = .6) +
  geom_text(aes(label = sprintf("%.1f", v)), position = position_stack(vjust = .5), colour = "white", fontface = "bold") +
  scale_fill_manual(values = c(`New homes` = eegb[["teal"]], `Repairs & extensions` = eegb[["teal2"]], `Roads, bridges & public works` = eegb[["gold"]],
                               `Commercial & industrial` = eegb[["olive"]], `Blocks, pipes & precast` = eegb[["sky"]], `230m people × 140 kg` = eegb[["navy"]]), name = NULL) +
  labs(title = sprintf("Two routes to market size: top-down %.1f mt vs bottom-up %.1f mt", td$v, sum(parts$v)),
       x = "Million tonnes per year", y = NULL) + theme_eegb()
save_fig(p7, "s03", "f07")

# --- F08 · Overfitting --------------------------------------------------------------------------------------
of <- bind_rows(lapply(1:8, function(k) { f <- fit_ts(train, k)
  tibble(deg = k, `Error on the data used to fit (2012–2023)` = mape(train$cement_mt, exp(fitted(f))),
         `Error on new data (2024–2025)` = mape(test$cement_mt, exp(predict(f, newdata = test)))) })) |>
  pivot_longer(-deg)
p8 <- ggplot(of, aes(deg, value, colour = name)) + geom_line(linewidth = 1.2) + geom_point(size = 2.5) +
  scale_y_log10(labels = function(v) paste0(v, "%")) + scale_colour_manual(values = unname(eegb[c("rust", "teal")]), name = NULL) +
  labs(title = "Extra flexibility barely improves the fit — but wrecks the forecast",
       x = "Model complexity (degree of the trend curve)", y = "MAPE (log scale)") + theme_eegb()
save_fig(p8, "s03", "f08")
