# =============================================================================
# EEGB · Session 13 · Climate & Energy-Transition Economics
# Replication script — regenerates every chart in the Session 13 deck (R)
# Data: data/firm_carbon_exposure.csv (40 fictional Nigerian listed companies, stylised)
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
f <- read_csv("data/firm_carbon_exposure.csv", show_col_types = FALSE)
FX <- 1500                                   # assumed ₦ per US$
f <- f |> mutate(emissions_t = (scope1_kt_co2e + scope2_kt_co2e) * 1000)
bill <- function(t, usd) t * usd * FX / 1e9  # ₦ bn

sec <- f |> group_by(sector) |>
  summarise(revenue = sum(revenue_ngn_bn), ebitda = sum(ebitda_ngn_bn), emissions_t = sum(emissions_t),
            tcfd = mean(publishes_tcfd), .groups = "drop") |>
  mutate(intensity = emissions_t / (revenue * 1000),
         c25 = 100 * bill(emissions_t, 25) / ebitda, c50 = 100 * bill(emissions_t, 50) / ebitda,
         c100 = 100 * bill(emissions_t, 100) / ebitda)

# --- F01 · Intensity by sector -----------------------------------------------------------
p1 <- ggplot(sec, aes(intensity, reorder(sector, intensity))) + geom_col(fill = eegb[["teal"]]) +
  geom_text(aes(label = sprintf("%.2f", intensity)), hjust = -.1) +
  labs(title = "Carbon intensity differs a hundred-fold across sectors", y = NULL,
       x = "Tonnes of CO₂e per ₦1 million of revenue (scope 1 + 2)", caption = eegb_caption) + theme_eegb()
save_fig(p1, "s13", "f01")

# --- F02 · Carbon bill as % of EBITDA at three prices --------------------------------------
d2 <- sec |> select(sector, `US$25` = c25, `US$50` = c50, `US$100` = c100) |>
  pivot_longer(-sector, names_to = "price", values_to = "pct") |>
  mutate(price = factor(price, levels = c("US$25", "US$50", "US$100")))
p2 <- ggplot(d2, aes(pct, reorder(sector, pct), fill = price)) + geom_col(position = "dodge") +
  scale_fill_manual(values = unname(eegb[c("sky", "gold", "rust")]), name = "Carbon price per tonne") +
  labs(title = "At US$100 a tonne, steel and power would lose half or more of EBITDA; cement a third",
       x = "Carbon bill as % of EBITDA (no pass-through, no abatement)", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p2, "s13", "f02")

# --- F03 · Firm by firm ------------------------------------------------------------------------
f <- f |> mutate(intensity = emissions_t / (revenue_ngn_bn * 1000), margin = 100 * ebitda_ngn_bn / revenue_ngn_bn,
                 cost50 = 100 * bill(emissions_t, 50) / ebitda_ngn_bn, hot = cost50 > 20)
p3 <- ggplot(f, aes(intensity, margin, colour = hot)) + geom_point(size = 3, alpha = .85) + scale_x_log10() +
  scale_colour_manual(values = c(`TRUE` = eegb[["rust"]], `FALSE` = eegb[["teal"]]),
                      labels = c(`TRUE` = "Loses >20% of EBITDA at US$50", `FALSE` = "Loses ≤20%"), name = NULL) +
  labs(title = sprintf("%d of 40 firms would lose more than a fifth of EBITDA at US$50 a tonne", sum(f$hot)),
       x = "Carbon intensity (t CO₂e per ₦m revenue, log scale)", y = "EBITDA margin (%)", caption = eegb_caption) + theme_eegb()
save_fig(p3, "s13", "f03")

# --- F04 · Cement vs solar as the price rises --------------------------------------------------
d4 <- expand_grid(price = seq(0, 150, 5), sector = c("Cement", "Solar & clean energy", "Power generation", "Banking")) |>
  left_join(sec, by = "sector") |> mutate(left = 100 - 100 * bill(emissions_t, price) / ebitda)
p4 <- ggplot(d4, aes(price, left, colour = sector)) + geom_line(linewidth = 1.3) +
  scale_colour_manual(values = unname(eegb[c("slate", "rust", "gold", "teal")]), name = NULL) +
  labs(title = "Same carbon price, very different fates: EBITDA left after paying the carbon bill",
       x = "Carbon price (US$ per tonne CO₂e)", y = "EBITDA remaining (% of today)", caption = eegb_caption) + theme_eegb()
save_fig(p4, "s13", "f04")

# --- F05 · CBAM on EU exports of cement and steel --------------------------------------------------
EU_PRICE <- 80
cb <- f |> filter(sector %in% c("Cement", "Steel & metals")) |>
  mutate(cbam_bn = bill(scope1_kt_co2e * 1000 * eu_export_share, EU_PRICE),
         pct_eu_sales = 100 * cbam_bn / (revenue_ngn_bn * eu_export_share))
p5 <- ggplot(cb, aes(pct_eu_sales, reorder(firm_id, pct_eu_sales), fill = sector)) + geom_col() +
  scale_fill_manual(values = unname(eegb[c("rust", "gold")]), name = NULL) +
  labs(title = "CBAM would eat a large slice of EU export revenue — a small slice of total profit",
       x = "Border charge as % of EU export revenue (EU price US$80/t)", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p5, "s13", "f05")

# --- F06 · Who discloses? -------------------------------------------------------------------------------
p6 <- ggplot(sec, aes(tcfd, reorder(sector, tcfd))) + geom_col(fill = eegb[["teal2"]]) +
  scale_x_continuous(labels = scales::percent, limits = c(0, 1)) +
  labs(title = sprintf("Only %.0f%% of firms publish TCFD-style climate disclosures", 100 * mean(f$publishes_tcfd)),
       x = "Share of firms publishing TCFD-aligned climate reports", y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p6, "s13", "f06")

# --- F07 · Can cement pass the cost on? -------------------------------------------------------------
cem <- filter(sec, sector == "Cement"); cost <- bill(cem$emissions_t, 50)
d7 <- expand_grid(pt = seq(0, 1, .05), eps = c(.3, .8, 1.5)) |>
  mutate(hit = (1 - pt) * cost + eps * pt * cost / cem$revenue * .5 * cem$revenue, pct = 100 * hit / cem$ebitda)
p7 <- ggplot(d7, aes(100 * pt, pct, colour = factor(eps))) + geom_line(linewidth = 1.3) +
  scale_colour_manual(values = unname(eegb[c("teal", "gold", "rust")]), name = "Demand elasticity (−)") +
  labs(title = "Passing the carbon cost on helps — unless customers can switch",
       x = "Share of the US$50/t carbon bill passed on in prices (%)", y = "Fall in cement EBITDA (%)", caption = eegb_caption) + theme_eegb()
save_fig(p7, "s13", "f07")

# --- F08 · Marginal abatement cost curve (illustrative) -------------------------------------------------
opts <- tibble(option = c("Waste-heat recovery", "Clinker substitution", "Captive solar power", "Alternative fuels",
                          "Kiln efficiency upgrade", "Carbon capture (CCS)"),
               cost = c(-25, -10, 5, 20, 35, 110), kt = c(40, 110, 30, 70, 45, 200)) |>
  mutate(xmax = cumsum(kt), xmin = xmax - kt)
p8 <- ggplot(opts) + geom_rect(aes(xmin = xmin, xmax = xmax, ymin = 0, ymax = cost, fill = cost < 50), colour = "white") +
  geom_text(aes(x = (xmin + xmax) / 2, y = pmax(cost, 0) + 6, label = option), size = 3, angle = 90, hjust = 0) +
  geom_hline(yintercept = 50, linetype = "dashed", colour = eegb[["navy"]]) +
  scale_fill_manual(values = c(`TRUE` = eegb[["teal"]], `FALSE` = eegb[["rust"]]), guide = "none") +
  labs(title = "Cut the cheap tonnes first: below the carbon price, abatement pays",
       x = "Cumulative tonnes abated (thousand t CO₂e a year)", y = "Cost per tonne abated (US$)",
       caption = "Illustrative options for one cement plant; costs are teaching assumptions.") + theme_eegb()
save_fig(p8, "s13", "f08")
