# =============================================================================
# EEGB · Session 5 · Market Failures & Government Intervention
# Replication script — regenerates every chart in the Session 5 deck (R)
# Data: data/fuel_subsidy_incidence.csv (stylised household budgets by consumption decile)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
h <- read_csv("data/fuel_subsidy_incidence.csv", show_col_types = FALSE)
FARE_RISE <- 0.50; FOOD_RISE <- 0.10; TRANSFER <- 10000; TARGET <- 4     # stylised assumptions
h <- h |> mutate(D = factor(paste0("D", decile), levels = paste0("D", 1:10)),
                 subsidy = petrol_litres_month * subsidy_per_litre_pre,
                 subsidy_share = 100 * subsidy / sum(subsidy),
                 subsidy_pct_budget = 100 * subsidy / monthly_spend_naira,
                 direct_pct = 100 * petrol_litres_month * (pump_price_post - pump_price_pre) / monthly_spend_naira,
                 indirect_pct = 100 * (transport_share * FARE_RISE + food_share * FOOD_RISE),
                 total_pct = direct_pct + indirect_pct)
annual <- sum(h$subsidy * h$households_m * 1e6 * 12) / 1e12
tcost <- TARGET * h$households_m[1] * 1e6 * TRANSFER * 12 / 1e12
universal <- tcost * 1e12 / (sum(h$households_m) * 1e6 * 12)
xlab <- "D1 = poorest 10% … D10 = richest 10%"

# --- F01 · Negative externality ---------------------------------------------------------------------
q <- seq(0, 10, length.out = 200)
cur <- bind_rows(tibble(q, p = 9 - .7 * q, curve = "Demand (private benefit)"),
                 tibble(q, p = 1 + .5 * q, curve = "Private cost (fuel, maintenance)"),
                 tibble(q, p = 3 + .5 * q, curve = "Social cost (+ noise, fumes, health)"))
qm <- 8 / 1.2; qs <- 6 / 1.2; dw <- tibble(q = seq(qs, qm, length.out = 50)) |> mutate(top = 9 - .7 * q, bot = 3 + .5 * q)
p1 <- ggplot() + geom_ribbon(data = dw, aes(q, ymin = pmin(top, bot), ymax = pmax(top, bot)), fill = eegb[["rust"]], alpha = .3) +
  geom_line(data = cur, aes(q, p, colour = curve, linetype = curve), linewidth = 1.2) +
  annotate("point", x = c(qm, qs), y = 9 - .7 * c(qm, qs), size = 3.5, colour = c(eegb[["teal"]], eegb[["rust"]])) +
  annotate("text", x = c(qm + .2, qs - .2), y = 9 - .7 * c(qm, qs) + c(-1, .5), label = c("Market outcome", "Best for society"),
           hjust = c(0, 1), fontface = "bold", colour = c(eegb[["teal"]], eegb[["rust"]])) +
  scale_colour_manual(values = c(eegb[["navy"]], eegb[["teal"]], eegb[["rust"]]), name = NULL) +
  scale_linetype_manual(values = c("solid", "solid", "dashed"), name = NULL) + coord_cartesian(xlim = c(0, 10), ylim = c(0, 10)) +
  labs(title = "When users don't pay the full cost, the market produces too much of it",
       subtitle = "Shaded: deadweight loss from over-use. The gap between the cost lines is the right (Pigouvian) tax.",
       x = "Hours of generator use", y = "Naira per hour") + theme_eegb() + theme(axis.text = element_blank(), legend.direction = "vertical")
save_fig(p1, "s05", "f01")

# --- F02 · Who received the subsidy? -----------------------------------------------------------------
p2 <- ggplot(h, aes(D, subsidy_share, fill = decile)) + geom_col(show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.0f%%", subsidy_share)), vjust = -0.4) +
  scale_fill_gradient(low = eegb[["teal"]], high = eegb[["rust"]]) + scale_y_continuous(labels = pct) +
  labs(title = sprintf("The richest 10%% received %.0f%% of the subsidy; the poorest 40%% just %.0f%%", h$subsidy_share[10], sum(h$subsidy_share[1:4])),
       x = xlab, y = "Share of total petrol subsidy", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s05", "f02")

# --- F03 · Naira vs % of budget ----------------------------------------------------------------------
sc <- 50 / 14
p3 <- ggplot(h, aes(D)) + geom_col(aes(y = subsidy / 1000), fill = eegb[["sky"]]) +
  geom_line(aes(y = subsidy_pct_budget * sc, group = 1), colour = eegb[["navy"]], linewidth = 1.3) +
  geom_point(aes(y = subsidy_pct_budget * sc), colour = eegb[["navy"]], size = 2.5) +
  scale_y_continuous(name = "₦'000 per household per month (bars)", sec.axis = sec_axis(~ . / sc, name = "% of household budget (line)")) +
  labs(title = sprintf("A rich household got ₦%s a month, a poor one ₦%s", format(h$subsidy[10], big.mark = ","), format(h$subsidy[1], big.mark = ",")),
       x = xlab, caption = eegb_caption) + theme_eegb()
save_fig(p3, "s05", "f03")

# --- F04 · Cost of removal ----------------------------------------------------------------------------
rm <- h |> select(D, `Direct: dearer petrol for cars & generators` = direct_pct, `Indirect: transport fares +50%, food +10%` = indirect_pct) |>
  pivot_longer(-D)
p4 <- ggplot(rm, aes(D, value, fill = name)) + geom_col() +
  geom_text(data = h, aes(D, total_pct, label = sprintf("%.0f%%", total_pct)), inherit.aes = FALSE, vjust = -0.4) +
  scale_fill_manual(values = c(eegb[["rust"]], eegb[["gold"]]), name = NULL) + scale_y_continuous(labels = pct) +
  labs(title = "Removal raised living costs for everyone — the poor mostly through fares and food",
       x = xlab, y = "Extra cost, % of monthly budget",
       caption = "Pump price ₦185 → ₦617 per litre; indirect effects are stylised assumptions. Source: EEGB stylised teaching data.") + theme_eegb()
save_fig(p4, "s05", "f04")

# --- F05 · Compensation options --------------------------------------------------------------------------
net <- h |> transmute(D, `No compensation` = -total_pct,
                      `Same budget, everyone` = -total_pct + 100 * universal / monthly_spend_naira,
                      `Targeted: ₦10,000/month to poorest 40%` = -total_pct + ifelse(decile <= TARGET, 100 * TRANSFER / monthly_spend_naira, 0)) |>
  pivot_longer(-D) |> mutate(name = factor(name, levels = c("No compensation", "Same budget, everyone", "Targeted: ₦10,000/month to poorest 40%")))
p5 <- ggplot(net, aes(D, value, fill = name)) + geom_col(position = "dodge") + geom_hline(yintercept = 0) +
  scale_fill_manual(values = unname(eegb[c("slate", "gold", "teal")]), name = NULL) + scale_y_continuous(labels = pct) +
  labs(title = "A targeted cash transfer can leave the poorest better off — for a fraction of the subsidy's cost",
       x = xlab, y = "Net change, % of monthly budget", caption = eegb_caption) + theme_eegb(12)
save_fig(p5, "s05", "f05")

# --- F06 · Fiscal arithmetic ------------------------------------------------------------------------------
fa <- tibble(item = factor(c("Household petrol subsidy (per year, before removal)", "Targeted transfer (₦10,000/month × poorest 40%)"),
                           levels = c("Targeted transfer (₦10,000/month × poorest 40%)", "Household petrol subsidy (per year, before removal)")),
             v = c(annual, tcost))
p6 <- ggplot(fa, aes(v, item, fill = item)) + geom_col(show.legend = FALSE, width = .6) +
  geom_text(aes(label = sprintf("₦%.1f trillion", v)), hjust = -0.1) + scale_fill_manual(values = unname(eegb[c("rust", "teal")])) +
  scale_x_continuous(expand = expansion(mult = c(0, .3))) +
  labs(title = sprintf("Compensating the poor costs about %.0f%% of what the subsidy cost", 100 * tcost / annual),
       x = "₦ trillion per year", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p6, "s05", "f06", height = 4.6)
