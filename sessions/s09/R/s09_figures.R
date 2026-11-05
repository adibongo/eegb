# =============================================================================
# EEGB · Session 9 · Fiscal Policy, Debt & Sovereign Risk
# Replication script — regenerates every chart in the Session 9 deck (R)
# Data: data/fgn_fiscal_annual.csv (stylised Federal Government finances, 2010–2025, ₦ trillion)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
f <- read_csv("data/fgn_fiscal_annual.csv", show_col_types = FALSE) |>
  mutate(d = total_public_debt_ntn / nominal_gdp_ntn,
         g = nominal_gdp_ntn / lag(nominal_gdp_ntn) - 1,
         r = interest_payments_ntn / lag(total_public_debt_ntn),
         pb_gdp = primary_balance_ntn / nominal_gdp_ntn,
         debt_to_rev = total_public_debt_ntn / fgn_revenue_ntn)

# --- F01 · Debt vs revenue as shares of GDP ------------------------------------------
f1 <- f |> select(year, `Public debt (% of GDP)` = debt_to_gdp_pct, `FGN revenue (% of GDP)` = revenue_to_gdp_pct) |>
  pivot_longer(-year, names_to = "series", values_to = "value")
p1 <- ggplot(f1, aes(year, value, colour = series)) + geom_line(linewidth = 1.3) + geom_point(size = 2) +
  scale_colour_manual(values = c(`Public debt (% of GDP)` = eegb[["navy"]], `FGN revenue (% of GDP)` = eegb[["gold"]]), name = NULL) +
  scale_y_continuous(labels = pct) +
  labs(title = "Debt looks moderate next to GDP — the problem is how little revenue the state collects",
       x = NULL, y = "Share of nominal GDP", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s09", "f01")

# --- F02 · Interest as a share of revenue ----------------------------------------------
p2 <- ggplot(f, aes(year, interest_to_revenue_pct, fill = interest_to_revenue_pct >= 60)) + geom_col() +
  geom_text(aes(label = round(interest_to_revenue_pct)), vjust = -0.4, size = 3.4) +
  geom_hline(yintercept = 100, linetype = "dashed") +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]]), guide = "none") +
  scale_y_continuous(labels = pct, limits = c(0, 112)) +
  labs(title = "From 16 kobo to over 90 kobo of every revenue naira spent on interest",
       x = NULL, y = "Interest payments as % of FGN revenue", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s09", "f02")

# --- F03 · Debt measured against revenue ----------------------------------------------------
p3 <- ggplot(f, aes(year, debt_to_rev)) + geom_area(fill = eegb[["rust"]], alpha = .12) +
  geom_line(colour = eegb[["rust"]], linewidth = 1.3) + geom_point(colour = eegb[["rust"]], size = 2) +
  labs(title = "How many years of revenue would it take to repay the debt?",
       x = NULL, y = "Public debt ÷ FGN revenue (years)", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s09", "f03")

# --- F04 · r versus g -------------------------------------------------------------------------
f4 <- f |> filter(!is.na(r)) |> select(year, `r: effective interest rate on debt` = r, `g: nominal GDP growth` = g) |>
  pivot_longer(-year, names_to = "series", values_to = "value")
p4 <- ggplot(f4, aes(year, 100 * value, colour = series)) + geom_line(linewidth = 1.3) + geom_point(size = 2) +
  scale_colour_manual(values = c(`r: effective interest rate on debt` = eegb[["rust"]], `g: nominal GDP growth` = eegb[["teal"]]), name = NULL) + scale_y_continuous(labels = pct) +
  labs(title = "Inflation has kept nominal growth above the interest rate — the debt ratio's friend",
       x = NULL, y = "Per cent per year", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s09", "f04")

# --- F05 · Debt dynamics decomposition --------------------------------------------------------
dd <- f |> mutate(d_prev = lag(d), delta = d - d_prev,
                  `Interest–growth effect (r − g)` = (r - g) / (1 + g) * d_prev,
                  `Primary deficit` = -pb_gdp) |>
  mutate(`Other: FX revaluation, CBN overdraft securitisation, sub-national debt` =
           delta - `Interest–growth effect (r − g)` - `Primary deficit`) |>
  filter(!is.na(r))
dl <- dd |> select(year, `Interest–growth effect (r − g)`, `Primary deficit`,
                     `Other: FX revaluation, CBN overdraft securitisation, sub-national debt`) |>
  pivot_longer(-year, names_to = "component", values_to = "value")
p5 <- ggplot(dl, aes(year, 100 * value, fill = component)) + geom_col(width = .7) +
  geom_point(data = dd, aes(year, 100 * delta), inherit.aes = FALSE, colour = eegb[["navy"]], size = 2.5) +
  geom_hline(yintercept = 0) +
  scale_fill_manual(values = c(`Interest–growth effect (r − g)` = eegb[["teal"]], `Primary deficit` = eegb[["gold"]],
    `Other: FX revaluation, CBN overdraft securitisation, sub-national debt` = eegb[["slate"]]), name = NULL) +
  labs(title = "Why debt/GDP moved: not the deficit, but revaluations and one-off transfers",
       x = NULL, y = "Change in debt/GDP (percentage points)", caption = eegb_caption) +
  theme_eegb() + theme(legend.direction = "vertical")
save_fig(p5, "s09", "f05")

# --- F06 · Three scenarios ---------------------------------------------------------------------
simulate <- function(d0, r, g, pb, years = 10, shock_year = NA, shock = 0) {
  d <- numeric(years + 1); d[1] <- d0
  for (t in 1:years) {
    d[t + 1] <- (1 + r) / (1 + g) * d[t] - pb
    if (!is.na(shock_year) && t == shock_year) d[t + 1] <- d[t + 1] + shock
  }
  d
}
d0 <- tail(f$d, 1)
sc <- bind_rows(
  tibble(year = 2025:2035, d = simulate(d0, .13, .20, .005), scenario = "Reform: g 20%, r 13%, primary surplus 0.5% of GDP"),
  tibble(year = 2025:2035, d = simulate(d0, .15, .17, -.01), scenario = "Baseline: g 17%, r 15%, primary deficit 1% of GDP"),
  tibble(year = 2025:2035, d = simulate(d0, .17, .14, -.02, 2, .08), scenario = "Adverse: g 14%, r 17%, deficit 2% + 2027 FX shock"))
p6 <- ggplot(sc, aes(year, 100 * d, colour = scenario)) + geom_line(linewidth = 1.4) +
  geom_text(data = filter(sc, year == 2035), aes(label = paste0(round(100 * d), "%")), hjust = -0.2, show.legend = FALSE) +
  scale_colour_manual(values = unname(eegb[c("rust", "navy", "teal")]), name = NULL) +
  scale_y_continuous(labels = pct) + xlim(2025, 2036.5) +
  labs(title = "Same starting debt, three futures: r, g and the primary balance decide the path",
       x = NULL, y = "Public debt (% of GDP)", caption = eegb_caption) + theme_eegb() + theme(legend.direction = "vertical")
save_fig(p6, "s09", "f06")

# --- F07 · Oil and non-oil revenue -------------------------------------------------------------
f7 <- f |> mutate(`Oil revenue` = fgn_revenue_ntn * oil_share_of_revenue,
                  `Non-oil revenue (taxes, fees, other)` = fgn_revenue_ntn - `Oil revenue`) |>
  select(year, `Oil revenue`, `Non-oil revenue (taxes, fees, other)`) |>
  pivot_longer(-year, names_to = "source", values_to = "ntn")
p7 <- ggplot(f7, aes(year, ntn, fill = source)) + geom_col() +
  scale_fill_manual(values = c(`Oil revenue` = eegb[["gold"]], `Non-oil revenue (taxes, fees, other)` = eegb[["teal"]]), name = NULL) +
  scale_y_continuous(labels = function(v) paste0("₦", v, "tn")) +
  labs(title = "Revenue grew in naira after 2022 — but oil still supplies over a third",
       x = NULL, y = "FGN revenue (₦ trillion)", caption = eegb_caption) + theme_eegb()
save_fig(p7, "s09", "f07")
