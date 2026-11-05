# =============================================================================
# EEGB · Session 1 LAB · Build the board's macro page (R)
# Data: data/official/ng_official_monthly.csv — OFFICIAL CBN series (CPI, MPR, T-bill, N/$, reserves)
#       plus FRED Brent. Refresh with:  python tools/fetch_official_data.py
# Run from the project root, line by line (Ctrl/Cmd + Enter in RStudio)
# =============================================================================
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })
m <- read_csv("data/official/ng_official_monthly.csv", show_col_types = FALSE)

# ---- STEP 1 · Look before you calculate --------------------------------------------------
names(m)                                    # what is measured?
tail(m, 3)                                  # the latest rows — note the gaps (NA)
sapply(m[-1], function(s) format(max(m$date[!is.na(s)])))   # each series has its OWN latest date

# ---- STEP 2 · Latest value, value a year ago, change ---------------------------------------
cols <- c(cpi_headline_yoy = "pp", cpi_core_yoy = "pp", policy_rate = "pp",
          usd_official_avg = "₦", reserves_gross_usdbn = "$bn", brent = "$")
board <- bind_rows(lapply(names(cols), function(c) {
  s <- m |> filter(!is.na(.data[[c]])) |> select(date, v = all_of(c))
  last <- tail(s, 1); ago <- tail(filter(s, date <= seq(last$date, by = "-12 months", length.out = 2)[2]), 1)
  tibble(indicator = c, date = format(last$date, "%b %Y"), latest = last$v, a_year_ago = ago$v,
         change = last$v - ago$v, unit_of_change = cols[[c]])
}))
print(board, width = Inf)

# ---- STEP 3 · Two derived numbers ---------------------------------------------------------------
# (a) Real policy rate — EXACT Fisher formula, not the "minus" shortcut
m <- m |> mutate(real_policy_rate = ((1 + policy_rate / 100) / (1 + cpi_headline_yoy / 100) - 1) * 100)
m |> filter(!is.na(real_policy_rate)) |> select(date, real_policy_rate) |> tail(6)
# (b) Your firm's real revenue growth — replace with your own numbers
nominal_growth <- 0.30; inflation <- 0.3324     # FY2024: naira sales +30%; 2024 average CPI inflation
sprintf("Real revenue growth: %.1f%%", ((1 + nominal_growth) / (1 + inflation) - 1) * 100)

# ---- STEP 4 · Beware breaks in a series -------------------------------------------------------------
# NBS moved to a new CPI (2024 = 100) in January 2025 and revised the 2025 figures in December 2025.
# Year-on-year rates either side of January 2025 are NOT like-for-like.
m |> filter(date >= as.Date("2024-10-01"), date <= as.Date("2025-03-01")) |>
  mutate(basis = ifelse(date < as.Date("2025-01-01"), "old CPI (2009 base)", "new CPI (2024 = 100)")) |>
  select(date, basis, cpi_headline_yoy)

# ---- STEP 5 · Correlation is not causation ------------------------------------------------------------
d <- m |> filter(date >= as.Date("2015-01-01"), !is.na(brent), !is.na(reserves_gross_usdbn))
cat("Oil vs reserves, same month:", round(cor(d$brent, d$reserves_gross_usdbn), 2), "\n")
cat("Oil vs reserves 12 months later:", round(cor(d$brent, lead(d$reserves_gross_usdbn, 12), use = "complete.obs"), 2), "\n")

# ---- YOUR TURN ------------------------------------------------------------------------------------------
# (a) Which six numbers should YOUR board watch? Drop two of the above if needed and say what you would add.
# (b) Under each number write one 'so what' line, using the macro-to-P&L map from the slides.
# (c) Oil earns most of Nigeria's dollars, yet the correlation with reserves is modest. Give two reasons.
# (d) Redo Step 3(b) with your own company's revenue — in naira, in real terms and in dollars.
