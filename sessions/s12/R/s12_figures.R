# =============================================================================
# EEGB · Session 12 · Trade, Supply Chains & Industrial Policy
# Replication script — regenerates every chart in the Session 12 deck (R)
# Data: data/ng_trade_partners.csv (stylised Nigerian trade with 30 partners, US$ m)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
t <- read_csv("data/ng_trade_partners.csv", show_col_types = FALSE)
usd_m <- function(v) ifelse(abs(v) >= 1000, paste0("$", round(v / 1000, 1), "bn"), paste0("$", round(v), "m"))

# --- F01 · Who Nigeria trades with -----------------------------------------------------
top <- t |> slice_max(total_trade_usd_m, n = 12) |> mutate(partner = reorder(partner, total_trade_usd_m))
top_long <- bind_rows(top |> transmute(partner, flow = "Nigeria's exports", value = exports_usd_m),
                      top |> transmute(partner, flow = "Nigeria's imports", value = -imports_usd_m))
p1 <- ggplot(top_long, aes(value, partner, fill = flow)) + geom_col() + geom_vline(xintercept = 0) +
  scale_fill_manual(values = c(`Nigeria's exports` = eegb[["teal"]], `Nigeria's imports` = eegb[["gold"]]), name = NULL) +
  scale_x_continuous(labels = function(v) paste0("$", abs(v) / 1000, "bn")) +
  labs(title = "Oil buyers in Europe, Asia and America; manufactured goods from China",
       x = "<- imports    |    exports ->  (US$, stylised year)", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p1, "s12", "f01", height = 6)

# --- F02 · Gravity in one picture --------------------------------------------------------
t <- t |> mutate(group = ifelse(region == "Africa", "Africa (AfCFTA)", "Rest of world"))
lab <- t |> filter(partner %in% c("China", "United States", "India", "Ghana", "Benin", "South Africa", "Kenya", "Chad"))
p2 <- ggplot(t, aes(distance_km, total_trade_usd_m, colour = group, size = partner_gdp_usd_bn)) +
  geom_point(alpha = .75) + geom_text(data = lab, aes(label = partner), size = 3.5, hjust = -0.15, colour = eegb[["ink"]]) +
  scale_x_log10(labels = function(v) paste0(format(v, big.mark = ","), " km")) + scale_y_log10(labels = usd_m) +
  scale_colour_manual(values = c(`Africa (AfCFTA)` = eegb[["gold"]], `Rest of world` = eegb[["navy"]]), name = NULL) +
  scale_size_area(max_size = 14, guide = "none") +
  labs(title = "Big economies trade more; distant ones trade less (bubble = partner GDP)",
       x = "Distance from Lagos (log scale)", y = "Total trade with Nigeria (log scale)", caption = eegb_caption) + theme_eegb()
save_fig(p2, "s12", "f02")

# --- F03 · The gravity regression -----------------------------------------------------------
grav <- lm(log(total_trade_usd_m) ~ log(partner_gdp_usd_bn) + log(distance_km) + common_language + landlocked, data = t)
cf <- coef(grav)
eff <- tibble(term = c("Partner GDP (+1%)", "Distance (+1%)", "Shared language (yes vs no)", "Landlocked (yes vs no)"),
              panel = c("Elasticities: % change in trade", "Elasticities: % change in trade",
                        "Shifts: % difference in trade", "Shifts: % difference in trade"),
              value = c(cf[2], cf[3], 100 * (exp(cf[4]) - 1), 100 * (exp(cf[5]) - 1)))
p3 <- ggplot(eff, aes(term, value, fill = value > 0)) + geom_col(show.legend = FALSE) + geom_hline(yintercept = 0) +
  geom_text(aes(y = value / 2, label = ifelse(abs(value) < 5, sprintf("%+.2f%%", value), sprintf("%+.0f%%", value))),
            colour = "white", fontface = "bold") +
  facet_wrap(~panel, scales = "free") +
  scale_fill_manual(values = c(`TRUE` = eegb[["teal"]], `FALSE` = eegb[["rust"]])) +
  labs(title = sprintf("Gravity model of Nigeria's trade (R² = %.2f): size pulls, distance pushes", summary(grav)$r.squared),
       x = NULL, y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p3, "s12", "f03")

# --- F04 · Actual vs predicted for African partners ----------------------------------------------
t <- t |> mutate(predicted = exp(fitted(grav)), ratio = total_trade_usd_m / predicted)
a <- t |> filter(region == "Africa") |> mutate(partner = reorder(partner, ratio))
p4 <- ggplot(a, aes(ratio, partner, fill = ratio < 1)) + geom_col(show.legend = FALSE) +
  geom_vline(xintercept = 1, linetype = "dashed") + geom_text(aes(label = sprintf("%.2f×", ratio)), hjust = -0.15, size = 3.6) +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]])) +
  labs(title = "African partners: actual trade vs what gravity predicts",
       x = "Actual ÷ predicted trade (below 1 = trading less than size and distance suggest)", y = NULL,
       caption = eegb_caption) + theme_eegb()
save_fig(p4, "s12", "f04")

# --- F05 · Non-oil exports by region ------------------------------------------------------------
reg <- t |> mutate(nonoil = exports_usd_m * (1 - oil_share_of_exports)) |> group_by(region) |>
  summarise(nonoil = sum(nonoil)) |> mutate(region = reorder(region, nonoil))
oil_share <- with(t, sum(exports_usd_m * oil_share_of_exports) / sum(exports_usd_m))
p5 <- ggplot(reg, aes(nonoil, region)) + geom_col(fill = eegb[["teal"]]) +
  geom_text(aes(label = paste0("$", round(nonoil), "m")), hjust = -0.1) + scale_x_continuous(labels = usd_m) +
  labs(title = sprintf("Oil & gas is %.0f%% of exports — Africa is already the No. 2 non-oil market", 100 * oil_share),
       x = "Non-oil exports", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p5, "s12", "f05")

# --- F06 · Import concentration ------------------------------------------------------------------
imp <- t |> mutate(share = 100 * imports_usd_m / sum(imports_usd_m)) |> arrange(desc(share))
hhi <- sum(imp$share^2)
p6 <- ggplot(head(imp, 8) |> mutate(partner = reorder(partner, share)), aes(share, partner, fill = partner == "China")) +
  geom_col(show.legend = FALSE) + geom_text(aes(label = paste0(round(share), "%")), hjust = -0.2) +
  scale_fill_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["slate"]])) + scale_x_continuous(labels = pct) +
  labs(title = sprintf("One country supplies %.0f%% of imports (HHI = %s: highly concentrated)", imp$share[1],
                       format(round(hhi), big.mark = ",")), x = "Share of Nigeria's imports", y = NULL,
       caption = eegb_caption) + theme_eegb()
save_fig(p6, "s12", "f06")

# --- F07 · AfCFTA tariff scenario -------------------------------------------------------------------
af_trade <- sum(t$total_trade_usd_m[t$region == "Africa"])
sc <- tibble(tariff = seq(0, 9, by = 0.5), trade = af_trade * (1.09 / (1 + tariff / 100))^4)
p7 <- ggplot(sc, aes(tariff, trade)) + geom_line(colour = eegb[["teal"]], linewidth = 1.5) +
  geom_point(data = sc |> filter(tariff %in% c(0, 9)), colour = eegb[["gold"]], size = 4) +
  scale_x_reverse() + scale_y_continuous(labels = usd_m) +
  labs(title = "Cutting tariffs helps — but roads, borders and payments matter as much",
       x = "Average tariff on intra-African trade (%)", y = "Nigeria's trade with African partners",
       caption = "Illustrative: trade proportional to (1 + tariff)^-4. EEGB stylised teaching data.") + theme_eegb()
save_fig(p7, "s12", "f07")
