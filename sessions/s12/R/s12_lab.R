# =============================================================================
# EEGB · Session 12 LAB · Where should we export first under AfCFTA? (R)
# Data: data/ng_trade_partners.csv — stylised Nigerian trade with 30 partners (US$ m)
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
t <- read_csv("data/ng_trade_partners.csv", show_col_types = FALSE)

# ---- STEP 1 · Look before you calculate ------------------------------------------
dim(t)
head(select(t, partner, region, partner_gdp_usd_bn, distance_km, exports_usd_m, imports_usd_m), 10)

# ---- STEP 2 · Who matters most? --------------------------------------------------------
t |> arrange(desc(total_trade_usd_m)) |> select(partner, total_trade_usd_m) |> head(10)
t |> summarise(africa_share_pct = 100 * sum(total_trade_usd_m[region == "Africa"]) / sum(total_trade_usd_m))

# ---- STEP 3 · Fit the gravity model -------------------------------------------------------
grav <- lm(log(total_trade_usd_m) ~ log(partner_gdp_usd_bn) + log(distance_km) + common_language + landlocked, data = t)
summary(grav)
#   Read: the log(GDP) coefficient ~ 1 means a 1% bigger partner -> ~1% more trade;
#         the log(distance) coefficient ~ -1 means 1% further away -> ~1% less trade.
(exp(coef(grav)[c("common_language", "landlocked")]) - 1) * 100   # % shifts for the yes/no variables

# ---- STEP 4 · How well does it fit? -------------------------------------------------------
summary(grav)$r.squared

# ---- STEP 5 · Where is trade 'missing'? -----------------------------------------------------
t <- t |> mutate(predicted_usd_m = round(exp(fitted(grav))),
                 actual_vs_predicted = round(total_trade_usd_m / predicted_usd_m, 2))
t |> filter(region == "Africa") |> select(partner, total_trade_usd_m, predicted_usd_m, actual_vs_predicted) |>
  arrange(actual_vs_predicted)

# ---- STEP 6 · A simple AfCFTA tariff scenario -----------------------------------------------
sigma <- 4                                  # assumed trade elasticity (estimates are often 3–6)
uplift <- (1.09 / 1.00)^sigma - 1           # from a 9% average tariff to zero
sprintf("Trade with African partners could rise by about %.0f%%", 100 * uplift)

# ---- STEP 7 · Supply-chain concentration on the import side -------------------------------------
imp <- t |> mutate(share = 100 * imports_usd_m / sum(imports_usd_m)) |> arrange(desc(share))
head(select(imp, partner, share), 5)
sum(imp$share^2)                            # HHI: above 2,500 = highly concentrated

# ---- YOUR TURN ---------------------------------------------------------------------------------
# (a) Pick your top three African export markets for a Nigerian packaged-food firm, using GDP, distance and
#     the 'missing trade' ratio. Justify each in one line.
# (b) Re-run STEP 6 with sigma = 3 and sigma = 6. How sensitive is the AfCFTA gain to this assumption?
# (c) List three non-tariff barriers that could matter more than tariffs.
# (d) If 64% of your imported inputs come from one country, what two actions would reduce the risk?
