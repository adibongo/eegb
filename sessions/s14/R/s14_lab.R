# =============================================================================
# EEGB · Session 14 LAB · Rank eight markets, then stress-test the Nigeria plan (R)
# Data: data/country_risk_panel.csv (stylised indicators for eight African markets)
# =============================================================================
library(dplyr); library(readr)
cr <- read_csv("data/country_risk_panel.csv", show_col_types = FALSE)
cr

# ---- STEP 1 · z-scores, with high = risky -------------------------------------------------
sign <- c(inflation_pct = 1, public_debt_gdp_pct = 1, fx_depreciation_12m = 1, eurobond_spread_pct = 1,
          real_growth_pct = -1, reserves_months_imports = -1, current_account_gdp_pct = -1,
          political_stability_wgi = -1, regulatory_quality_wgi = -1)
z <- sapply(names(sign), function(k) sign[[k]] * as.numeric(scale(cr[[k]])))
rownames(z) <- cr$country
round(z, 2)

# ---- STEP 2 · Four pillars ------------------------------------------------------------------
pill <- cbind(macro = rowMeans(z[, c("inflation_pct", "real_growth_pct")]),
              external = rowMeans(z[, c("reserves_months_imports", "current_account_gdp_pct", "fx_depreciation_12m")]),
              fiscal_market = rowMeans(z[, c("public_debt_gdp_pct", "eurobond_spread_pct")]),
              political = rowMeans(z[, c("political_stability_wgi", "regulatory_quality_wgi")]))

# ---- STEP 3 · Weight and rank (8 = riskiest) ----------------------------------------------------
rank_with <- function(w) rank(as.numeric(pill %*% w))
data.frame(country = cr$country, equal = rank_with(c(1, 1, 1, 1)),
           lender = rank_with(c(.5, 2, 2, .5)), investor = rank_with(c(2, .5, .5, 2)))

# ---- STEP 4 · Scenarios for the Nigeria plan (EBITDA, ₦ bn) ------------------------------------
scen <- data.frame(scenario = c("Reform pays off", "Muddle through", "Relapse"), prob = c(.35, .45, .20), ebitda = c(18.39, 11.23, -5.93))
scen; sum(scen$prob * scen$ebitda)     # probability-weighted EBITDA vs ₦18bn today

# ---- YOUR TURN -------------------------------------------------------------------------------------
# (a) Choose weights for YOUR company. Where does Nigeria rank?
# (b) Set Relapse = 0.35 and Muddle through = 0.30. What happens to expected EBITDA?
# (c) Three signposts you would watch monthly, with trigger levels.
