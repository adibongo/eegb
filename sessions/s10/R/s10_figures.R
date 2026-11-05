# =============================================================================
# EEGB · Session 10 · Financial Stability & Corporate Finance Conditions
# Replication script — regenerates every chart in the Session 10 deck (R)
# Data: data/ng_yield_curves.csv, data/bank_balance_sheet.csv, data/ng_macro_monthly.csv
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
yc <- read_csv("data/ng_yield_curves.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
bs <- read_csv("data/bank_balance_sheet.csv", show_col_types = FALSE)
m  <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))

bond_price <- function(coupon, yld, years, freq = 2, face = 100) {
  n <- round(years * freq); c <- coupon / freq * face; y <- yld / freq; t <- seq_len(n)
  sum(c / (1 + y)^t) + face / (1 + y)^n
}

# --- F01 · Five yield curves -------------------------------------------------------------
p1 <- ggplot(yc, aes(tenor_years, yield_pct, colour = format(date, "%b %Y"))) +
  geom_line(linewidth = 1.1) + geom_point(size = 2) +
  scale_x_log10(breaks = c(.25, .5, 1, 2, 5, 10, 20, 30), labels = c("3m", "6m", "1y", "2y", "5y", "10y", "20y", "30y")) +
  scale_colour_manual(values = unname(eegb[c("sky", "teal2", "rust", "gold", "navy")]), name = NULL) +
  scale_y_continuous(labels = pct) +
  labs(title = "The FGN yield curve: steep and low in 2021, high and inverted in 2024",
       x = "Time to maturity (log scale)", y = "Yield", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s10", "f01")

# --- F02 · Price–yield seesaw by maturity ------------------------------------------------
grid <- expand_grid(y = seq(.08, .24, length.out = 80), yrs = c(1, 5, 10, 20)) |>
  rowwise() |> mutate(price = bond_price(.13, y, yrs)) |> ungroup()
p2 <- ggplot(grid, aes(100 * y, price, colour = paste0(yrs, "-year bond"))) + geom_line(linewidth = 1.2) +
  geom_vline(xintercept = 13, linetype = "dashed", colour = eegb[["slate"]]) +
  geom_vline(xintercept = 18.8, linetype = "dotted", colour = eegb[["rust"]]) +
  scale_colour_manual(values = unname(eegb[c("sky", "teal", "navy", "rust")]), name = NULL) +
  scale_x_continuous(labels = pct) +
  labs(title = "Same 13% coupon, different maturities: the longer the bond, the bigger the fall",
       x = "Market yield", y = "Bond price (per ₦100 face value)", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s10", "f02")

# --- F03 · Mark-to-market loss, Jan 2023 → Jun 2024 ----------------------------------------
c23 <- filter(yc, date == as.Date("2023-01-31")); c24 <- filter(yc, date == as.Date("2024-06-28"))
ten <- c(2, 3, 5, 7, 10, 15, 20)
loss <- sapply(ten, function(t) bond_price(c23$yield_pct[c23$tenor_years == t] / 100,
                                           c24$yield_pct[c24$tenor_years == t] / 100, max(t - 1.4, .25)) - 100)
d3 <- tibble(tenor = factor(paste0(ten, "y"), levels = paste0(ten, "y")), loss = loss)
p3 <- ggplot(d3, aes(tenor, loss, fill = loss > -5)) + geom_col(show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.0f%%", loss)), vjust = 1.5) +
  scale_fill_manual(values = c(`TRUE` = eegb[["teal"]], `FALSE` = eegb[["rust"]])) +
  labs(title = "A par bond bought in January 2023 had lost up to a fifth of its value by mid-2024",
       x = "Original maturity of the FGN bond", y = "Change in market price (%)", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s10", "f03")

# --- F04 · The bank's balance sheet ----------------------------------------------------------
A <- filter(bs, side == "asset"); L <- filter(bs, side == "liability")
TA <- sum(A$amount_ngn_bn); TL <- sum(L$amount_ngn_bn); E <- TA - TL
d4 <- bind_rows(mutate(A, col = "Assets"), mutate(L, col = "Liabilities + equity"),
                tibble(col = "Liabilities + equity", item = "Equity", amount_ngn_bn = E, duration_years = 0))
p4 <- ggplot(d4, aes(col, amount_ngn_bn, fill = item)) + geom_col(colour = "white", width = .9) +
  geom_text(aes(label = paste0(item, " ₦", format(amount_ngn_bn, big.mark = ","), "bn")),
            position = position_stack(vjust = .5), size = 3, colour = "white") +
  scale_fill_manual(values = rep(unname(eegb_palette), 2), guide = "none") +
  labs(title = "A Nigerian bank: long FGN bonds funded by short deposits", x = NULL, y = "₦ bn", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s10", "f04", height = 6)

# --- F05 · Duration gap stress test ------------------------------------------------------------
DA <- sum(A$amount_ngn_bn * A$duration_years) / TA
DL <- sum(L$amount_ngn_bn * L$duration_years) / TL
gap <- DA - TL / TA * DL; y0 <- .18
d5 <- tibble(shock = seq(0, 7, .5), equity = E - gap * TA * (shock / 100) / (1 + y0))
be <- E * (1 + y0) / (gap * TA) * 100
p5 <- ggplot(d5, aes(shock, equity)) + geom_line(colour = eegb[["navy"]], linewidth = 1.3) + geom_point(colour = eegb[["navy"]]) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = eegb[["rust"]]) +
  geom_vline(xintercept = be, linetype = "dotted", colour = eegb[["gold"]]) +
  labs(title = sprintf("Duration gap of %.2f years: a %.1f-point rise in yields erases the bank's equity", gap, be),
       x = "Parallel rise in interest rates (percentage points)", y = "Economic value of equity (₦ bn)", caption = eegb_caption) + theme_eegb()
save_fig(p5, "s10", "f05")

# --- F06 · Unrealised loss on the bond book vs equity --------------------------------------------
bonds <- filter(A, grepl("FGN bonds", item))
dy <- c24$yield_pct[c24$tenor_years == 10] - bonds$rate_pct
htm <- bonds$duration_years / (1 + bonds$rate_pct / 100) * dy / 100 * bonds$amount_ngn_bn
d6 <- tibble(what = c("Equity (assets − liabilities)", "Unrealised loss on FGN bonds"), v = c(E, htm))
p6 <- ggplot(d6, aes(v, what, fill = what)) + geom_col(width = .5, show.legend = FALSE) +
  geom_text(aes(label = paste0("₦", round(v), "bn")), hjust = -.1) +
  scale_fill_manual(values = unname(eegb[c("gold", "rust")])) + xlim(0, max(d6$v) * 1.25) +
  labs(title = sprintf("If yields rise %.1f points, the hidden bond loss is bigger than the bank's equity", dy),
       x = NULL, y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p6, "s10", "f06", height = 4.8)

# --- F07 · Real 10-year yield -----------------------------------------------------------------------
ry <- yc |> filter(tenor_years == 10) |> rowwise() |>
  mutate(infl = tail(m$headline_inflation[m$date <= date], 1), real = yield_pct - infl) |> ungroup()
p7 <- ggplot(ry, aes(format(date, "%b %Y"), real, fill = real < 0)) + geom_col(width = .6, show.legend = FALSE) +
  geom_text(aes(label = sprintf("%+.1f", real)), vjust = ifelse(ry$real < 0, 1.4, -.4)) +
  scale_x_discrete(limits = format(ry$date, "%b %Y")) +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]])) + geom_hline(yintercept = 0) +
  labs(title = "Real 10-year yield (yield minus inflation): negative throughout, near zero only by end-2025",
       x = NULL, y = "Percentage points", caption = eegb_caption) + theme_eegb()
save_fig(p7, "s10", "f07")
