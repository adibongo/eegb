# =============================================================================
# EEGB · Session 14 · Country Risk & Scenario Planning
# Replication script — regenerates every chart in the Session 14 deck (R)
# Data: data/country_risk_panel.csv (stylised indicators for eight African markets)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
cr <- read_csv("data/country_risk_panel.csv", show_col_types = FALSE)

sign <- c(inflation_pct = 1, real_growth_pct = -1, reserves_months_imports = -1, current_account_gdp_pct = -1,
          fx_depreciation_12m = 1, public_debt_gdp_pct = 1, eurobond_spread_pct = 1,
          political_stability_wgi = -1, regulatory_quality_wgi = -1)
pillars <- list(Macro = c("inflation_pct", "real_growth_pct"),
                External = c("reserves_months_imports", "current_account_gdp_pct", "fx_depreciation_12m"),
                `Fiscal & market` = c("public_debt_gdp_pct", "eurobond_spread_pct"),
                `Political & policy` = c("political_stability_wgi", "regulatory_quality_wgi"))
z <- as.data.frame(sapply(names(sign), function(k) sign[[k]] * as.numeric(scale(cr[[k]]))))
rownames(z) <- cr$country
pill <- sapply(pillars, function(cols) rowMeans(z[, cols]))
score <- function(w) { s <- as.numeric(pill %*% w) / sum(w); 100 * (s - min(s)) / (max(s) - min(s)) }
W <- list(`Base (equal)` = c(1, 1, 1, 1), `Lender (external & fiscal)` = c(.5, 2, 2, .5), `Investor (macro & policy)` = c(2, .5, .5, 2))
scores <- as.data.frame(lapply(W, score), check.names = FALSE); scores$country <- cr$country

# --- F01 · Heatmap -----------------------------------------------------------------------
lev <- scores$country[order(scores$`Base (equal)`)]
d1 <- z |> mutate(country = rownames(z)) |> pivot_longer(-country, names_to = "indicator", values_to = "z") |>
  left_join(cr |> pivot_longer(-country, names_to = "indicator", values_to = "raw"), by = c("country", "indicator")) |>
  mutate(country = factor(country, levels = lev), indicator = factor(indicator, levels = unlist(pillars)))
p1 <- ggplot(d1, aes(indicator, country, fill = z)) + geom_tile(colour = "white") + geom_text(aes(label = raw), size = 3.2) +
  scale_fill_gradient2(low = "#1A9850", mid = "#FFFFBF", high = "#D73027", limits = c(-2, 2), oob = scales::squish, name = "Risk z") +
  labs(title = "Eight markets, nine indicators: numbers shown, colour = risk relative to the group",
       x = NULL, y = NULL, caption = eegb_caption) + theme_eegb() + theme(axis.text.x = element_text(angle = 30, hjust = 1))
save_fig(p1, "s14", "f01")

# --- F02 · Composite score -----------------------------------------------------------------
p2 <- ggplot(scores, aes(`Base (equal)`, reorder(country, `Base (equal)`),
                         fill = cut(`Base (equal)`, c(-1, 33, 66, 101), labels = c("low", "mid", "high")))) +
  geom_col(show.legend = FALSE) + geom_text(aes(label = round(`Base (equal)`)), hjust = -.2, fontface = "bold") +
  scale_fill_manual(values = unname(eegb[c("teal", "gold", "rust")])) + xlim(0, 112) +
  labs(title = "Composite country-risk score with equal pillar weights (0 = safest, 100 = riskiest)",
       x = "Risk score", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p2, "s14", "f02")

# --- F03 · Rank sensitivity -------------------------------------------------------------------
d3 <- scores |> pivot_longer(-country, names_to = "weights", values_to = "s") |> group_by(weights) |>
  mutate(rank = rank(s), weights = factor(weights, levels = names(W)), ng = country == "Nigeria")
p3 <- ggplot(d3, aes(weights, rank, group = country, colour = ng)) + geom_line(aes(linewidth = ng)) + geom_point(size = 3) +
  geom_text(data = filter(d3, weights == names(W)[3]), aes(label = country), hjust = -.15) +
  scale_colour_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["slate"]]), guide = "none") +
  scale_linewidth_manual(values = c(`TRUE` = 1.8, `FALSE` = .7), guide = "none") +
  labs(title = "Change the weights and the ranking moves — the middle of the table is fragile",
       x = NULL, y = "Rank (8 = riskiest)", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s14", "f03")

# --- F04 · Opportunity vs risk ------------------------------------------------------------------
d4 <- cr |> mutate(opp = population_m * (1 + real_growth_pct / 100)^5) |> left_join(scores, by = "country")
p4 <- ggplot(d4, aes(`Base (equal)`, opp, size = population_m)) + geom_point(colour = eegb[["teal"]], alpha = .6) +
  geom_text(aes(label = country), size = 3.5, hjust = -.25) + scale_y_log10() + scale_size(range = c(3, 15), guide = "none") +
  geom_vline(xintercept = 50, linetype = "dashed", colour = eegb[["slate"]]) +
  labs(title = "Big markets are not always safe markets: opportunity vs risk",
       x = "Risk score (base weights)", y = "Market size in 5 years (log scale)", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s14", "f04")

# --- Plan model ----------------------------------------------------------------------------------
REV <- 120; IMP <- .45; MARGIN <- .15
plan_ebitda <- function(fx_change, demand_growth, price_pass, rate_rise) {
  cost <- REV * (1 - MARGIN); new_cost <- cost * IMP * (1 + fx_change) + cost * (1 - IMP) * 1.15
  price <- 1 + price_pass * (new_cost / cost - 1); vol <- (1 + demand_growth) * price^-0.8
  REV * price * vol - new_cost * vol - (4 * (1 + rate_rise / 25) - 4)
}
scen <- tibble(scenario = c("Reform pays off", "Muddle through", "Relapse"), prob = c(.35, .45, .20),
               fx = c(.05, .25, .80), dem = c(.10, .01, -.04), pass = c(.8, .6, .4), rate = c(-3, 0, 6)) |>
  rowwise() |> mutate(ebitda = plan_ebitda(fx, dem, pass, rate)) |> ungroup()
ev <- sum(scen$prob * scen$ebitda)

# --- F05 · Scenario outcomes ----------------------------------------------------------------------
p5 <- ggplot(scen, aes(factor(scenario, levels = scenario), ebitda, fill = scenario)) + geom_col(width = .55, show.legend = FALSE) +
  geom_text(aes(label = sprintf("₦%.1fbn\np = %.0f%%", ebitda, 100 * prob)), vjust = ifelse(scen$ebitda >= 0, -.3, 1.3)) +
  geom_hline(yintercept = c(18, ev), linetype = c("dashed", "dotted"), colour = eegb[["navy"]]) +
  scale_fill_manual(values = c(`Reform pays off` = eegb[["teal"]], `Muddle through` = eegb[["gold"]], Relapse = eegb[["rust"]])) +
  labs(title = "Next-year EBITDA of the Nigeria plan under three scenarios",
       subtitle = sprintf("Dashed: today ₦18bn · dotted: probability-weighted ₦%.1fbn", ev),
       x = NULL, y = "EBITDA (₦ bn)", caption = "Illustrative plan model; scenario values are teaching assumptions.") + theme_eegb()
save_fig(p5, "s14", "f05")

# --- F06 · Tornado ---------------------------------------------------------------------------------
b0 <- plan_ebitda(.25, .01, .6, 0)
d6 <- tibble(shock = c("Naira 30% weaker", "Demand 5 pts lower", "Pass-through 30 pts lower", "Rates +5 points"),
             change = c(plan_ebitda(.55, .01, .6, 0), plan_ebitda(.25, -.04, .6, 0), plan_ebitda(.25, .01, .3, 0), plan_ebitda(.25, .01, .6, 5)) - b0)
p6 <- ggplot(d6, aes(change, reorder(shock, -change))) + geom_col(fill = eegb[["rust"]]) +
  geom_text(aes(label = sprintf("₦%.1fbn", change)), hjust = 1.1) + geom_vline(xintercept = 0) +
  labs(title = sprintf("Stress test from the 'muddle through' case (₦%.1fbn): pricing power matters most", b0),
       x = "Change in EBITDA (₦ bn)", y = NULL, caption = "Illustrative plan model. EEGB teaching assumptions.") + theme_eegb()
save_fig(p6, "s14", "f06", height = 4.8)

# --- F07 · Signpost board ----------------------------------------------------------------------------
ng <- filter(cr, country == "Nigeria")
sig <- tibble(indicator = c("Reserves (months of imports)", "Inflation (%)", "Eurobond spread (%)", "12-month FX depreciation (%)", "Public debt (% GDP)"),
              value = c(ng$reserves_months_imports, ng$inflation_pct, ng$eurobond_spread_pct, 100 * ng$fx_depreciation_12m, ng$public_debt_gdp_pct),
              amber = c(5, 15, 5, 15, 50), red = c(3, 25, 8, 30, 70), worse_high = c(FALSE, TRUE, TRUE, TRUE, TRUE)) |>
  mutate(status = ifelse(worse_high, ifelse(value >= red, "red", ifelse(value >= amber, "amber", "green")),
                         ifelse(value <= red, "red", ifelse(value <= amber, "amber", "green"))))
p7 <- ggplot(sig, aes(1, factor(indicator, levels = rev(indicator)), fill = status)) + geom_tile(width = 1, height = .8) +
  geom_text(aes(label = paste0(indicator, ":  now ", value)), colour = "white", fontface = "bold") +
  scale_fill_manual(values = c(green = eegb[["teal"]], amber = eegb[["gold"]], red = eegb[["rust"]]), name = NULL) +
  labs(title = "Nigeria signpost board: agree the triggers before the crisis, not during it", x = NULL, y = NULL,
       caption = "Trigger levels are illustrative. EEGB stylised teaching data.") + theme_void(base_size = 13) +
  theme(plot.title = element_text(face = "bold", colour = eegb[["navy"]]))
save_fig(p7, "s14", "f07", height = 4.8)
