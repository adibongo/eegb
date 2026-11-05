# =============================================================================
# EEGB · Session 13 LAB · What would a carbon price do to our sector? (R)
# Data: data/firm_carbon_exposure.csv — 40 fictional Nigerian listed companies (stylised)
# =============================================================================
library(dplyr); library(readr)
f <- read_csv("data/firm_carbon_exposure.csv", show_col_types = FALSE)
FX <- 1500                                   # assumed ₦ per US$ — change it and see

# ---- STEP 1 · Look at the data --------------------------------------------------------
head(f); count(f, sector)

# ---- STEP 2 · Total emissions and intensity ------------------------------------------------
f <- f |> mutate(emissions_t = (scope1_kt_co2e + scope2_kt_co2e) * 1000,
                 intensity = emissions_t / (revenue_ngn_bn * 1000))
f |> group_by(sector) |> summarise(intensity = mean(intensity)) |> arrange(intensity)

# ---- STEP 3 · The carbon bill at three prices ------------------------------------------------
f <- f |> mutate(bill_25 = emissions_t * 25 * FX / 1e9, bill_50 = emissions_t * 50 * FX / 1e9,
                 bill_100 = emissions_t * 100 * FX / 1e9, pct_ebitda_50 = 100 * bill_50 / ebitda_ngn_bn)
f |> group_by(sector) |> summarise(bill_50 = sum(bill_50), ebitda = sum(ebitda_ngn_bn)) |>
  mutate(pct_ebitda_50 = 100 * bill_50 / ebitda) |> arrange(desc(pct_ebitda_50))

# ---- STEP 4 · Most exposed firms ---------------------------------------------------------------
f |> arrange(desc(pct_ebitda_50)) |> select(firm_id, sector, pct_ebitda_50, publishes_tcfd) |> head(10)

# ---- STEP 5 · Who discloses? --------------------------------------------------------------------
f |> group_by(sector) |> summarise(share_tcfd = mean(publishes_tcfd))

# ---- YOUR TURN -------------------------------------------------------------------------------------
# (a) Repeat Step 3 with FX = 1000 and FX = 2000. Why does the naira change a carbon bill set in dollars?
# (b) A cement firm cuts 30% of its emissions at US$20/t. Recompute its bill at US$50/t. Worth it?
# (c) Three sentences for a cement board: our exposure, what customers will bear, our first two actions.
