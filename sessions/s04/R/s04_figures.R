# =============================================================================
# EEGB · Session 4 · Market Structure, Platforms & Competition Policy
# Replication script — regenerates every chart in the Session 4 deck (R)
# Data: data/payments_market_shares.csv (stylised; fictional providers except the 'Banks' aggregate)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
p <- read_csv("data/payments_market_shares.csv", show_col_types = FALSE)
ORDER <- c("Banks (app & USSD)", "KoboLink", "SwiftNaira", "AgentPay", "PayFast", "Others")
COL <- setNames(c(eegb[["slate"]], eegb[["teal"]], eegb[["gold"]], eegb[["olive"]], eegb[["sky"]], "#C9D1DA"), ORDER)
p <- p |> mutate(provider = factor(provider, levels = ORDER))

# --- F01 · Shares over time --------------------------------------------------------------------
p1 <- ggplot(p, aes(year, share_of_value_pct, fill = provider)) + geom_area(alpha = .95) +
  scale_fill_manual(values = COL, name = NULL) + scale_y_continuous(labels = pct) +
  labs(title = "Banks' share of mobile-payment value fell from 78% to 28% as fintech platforms grew",
       x = NULL, y = "Share of payment value", caption = eegb_caption) + theme_eegb() + theme(legend.position = "bottom")
save_fig(p1, "s04", "f01")

# --- F02 · HHI under two market definitions -------------------------------------------------------
h <- p |> group_by(year) |>
  summarise(`Banks counted as one block` = sum(share_of_value_pct^2),
            `Banks counted as ~10 separate firms` = sum(share_of_value_pct[provider != "Banks (app & USSD)"]^2) +
              10 * (share_of_value_pct[provider == "Banks (app & USSD)"] / 10)^2) |>
  pivot_longer(-year)
p2 <- ggplot(h, aes(year, value, colour = name)) +
  annotate("rect", xmin = -Inf, xmax = Inf, ymin = 2500, ymax = 7000, fill = eegb[["rust"]], alpha = .08) +
  annotate("rect", xmin = -Inf, xmax = Inf, ymin = 1500, ymax = 2500, fill = eegb[["gold"]], alpha = .10) +
  annotate("text", x = 2016.1, y = 2650, label = "highly concentrated (> 2,500)", hjust = 0, colour = eegb[["rust"]]) +
  annotate("text", x = 2016.1, y = 1650, label = "moderately concentrated (1,500–2,500)", hjust = 0, colour = eegb[["gold"]]) +
  geom_line(linewidth = 1.3) + geom_point(size = 2.5) +
  scale_colour_manual(values = c(eegb[["navy"]], eegb[["teal"]]), name = NULL) +
  labs(title = "Concentration depends on how you define the market", x = NULL, y = "Herfindahl–Hirschman Index (HHI)",
       caption = "Thresholds: US 2010 merger guidelines (the 2023 guidelines use lower cut-offs). Source: EEGB stylised teaching data.") + theme_eegb()
save_fig(p2, "s04", "f02")

# --- F03 · Users and merchants ------------------------------------------------------------------------
tot <- p |> group_by(year) |> summarise(users = sum(active_users_m), merchants = sum(merchants_m))
sl <- coef(lm(log(merchants) ~ log(users), data = tot))[2]
p3 <- ggplot(tot, aes(users, merchants)) + geom_path(colour = eegb[["teal"]], linewidth = 1.3) + geom_point(colour = eegb[["teal"]], size = 3) +
  geom_text(data = filter(tot, year %in% c(2016, 2019, 2022, 2025)), aes(label = year), vjust = -1, colour = eegb[["navy"]]) +
  labs(title = sprintf("Each 1%% more users came with about %.1f%% more merchants: the two sides feed each other", sl),
       x = "Active users (million)", y = "Merchants accepting mobile payments (million)", caption = eegb_caption) + theme_eegb(12)
save_fig(p3, "s04", "f03")

# --- F04 · Shares inside the fintech segment ------------------------------------------------------------
FIN <- c("KoboLink", "SwiftNaira", "AgentPay", "PayFast")
fin <- p |> filter(provider %in% FIN) |> group_by(year) |> mutate(s = 100 * share_of_value_pct / sum(share_of_value_pct)) |> ungroup()
p4 <- ggplot(fin, aes(year, s, colour = provider)) + geom_line(linewidth = 1.2) + geom_point(size = 2.3) +
  geom_text(data = filter(fin, year == 2025), aes(label = sprintf("%.0f%%", s)), hjust = -0.3, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = COL[FIN], name = NULL) + scale_y_continuous(labels = pct) + xlim(2016, 2025.8) +
  labs(title = "Among the fintechs, the fastest grower pulled away: a 'winner-takes-most' pattern",
       x = NULL, y = "Share of fintech payment value", caption = eegb_caption) + theme_eegb() + theme(legend.position = "bottom")
save_fig(p4, "s04", "f04")

# --- F05 · The leader's share and its fees --------------------------------------------------------------
k <- filter(p, provider == "KoboLink")
oth <- p |> filter(provider != "KoboLink") |> group_by(year) |> summarise(fee = mean(avg_fee_pct))
sc <- 0.8 / 30    # map fees (0–0.8%) onto the share axis (0–30%) for a two-axis chart
p5 <- ggplot() + geom_col(data = k, aes(year, share_of_value_pct), fill = eegb[["teal"]], alpha = .35) +
  geom_line(data = k, aes(year, avg_fee_pct / sc, colour = "KoboLink average fee"), linewidth = 1.3) +
  geom_point(data = k, aes(year, avg_fee_pct / sc, colour = "KoboLink average fee"), size = 2.5) +
  geom_line(data = oth, aes(year, fee / sc, colour = "Others' average fee"), linetype = "dashed", linewidth = 1) +
  scale_colour_manual(values = c(`KoboLink average fee` = eegb[["rust"]], `Others' average fee` = eegb[["slate"]]), name = NULL) +
  scale_y_continuous(name = "KoboLink market share (bars, %)", sec.axis = sec_axis(~ . * sc, name = "Average fee, % of value")) +
  labs(title = "The leader entered cheap — then nudged fees up once it was the biggest network", x = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p5, "s04", "f05")

# --- F06 · Monopoly vs competition ----------------------------------------------------------------------
q <- seq(0, 10, length.out = 300)
cur <- bind_rows(tibble(q, p = 10 - q, curve = "Demand"), tibble(q = q[q <= 5], p = 10 - 2 * q[q <= 5], curve = "Marginal revenue"),
                 tibble(q, p = 2, curve = "Marginal cost"))
dwl <- tibble(q = seq(4, 8, length.out = 50)) |> mutate(top = 10 - q)
p6 <- ggplot() +
  annotate("rect", xmin = 0, xmax = 4, ymin = 2, ymax = 6, fill = eegb[["gold"]], alpha = .35) +
  geom_ribbon(data = dwl, aes(q, ymin = 2, ymax = top), fill = eegb[["rust"]], alpha = .45) +
  geom_line(data = cur, aes(q, p, colour = curve), linewidth = 1.2) +
  annotate("point", x = c(8, 4), y = c(2, 6), size = 3.5, colour = c(eegb[["teal"]], eegb[["rust"]])) +
  annotate("text", x = c(8.2, 4.2), y = c(2.4, 6.4), label = c("Competition", "Monopoly"), hjust = 0, fontface = "bold",
           colour = c(eegb[["teal"]], eegb[["rust"]])) +
  scale_colour_manual(values = c(Demand = eegb[["navy"]], `Marginal revenue` = eegb[["slate"]], `Marginal cost` = eegb[["teal"]]), name = NULL) +
  coord_cartesian(xlim = c(0, 10.5), ylim = c(0, 10.5)) +
  labs(title = "A monopolist sells less at a higher price — and some value is simply lost",
       subtitle = "Gold: transferred from customers to the monopolist · Red: deadweight loss", x = "Quantity", y = "Price") +
  theme_eegb() + theme(axis.text = element_blank())
save_fig(p6, "s04", "f06")
