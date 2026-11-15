# =============================================================================
# EEGB · Session 3 LAB · How much cement will Nigeria buy in 2026? (R)
# Data: data/cement_demand_monthly.csv — stylised monthly cement consumption, 2012–2025
# Open eegb.Rproj first, then run line by line (Ctrl/Cmd + Enter)
# =============================================================================
library(dplyr); library(readr)
c <- read_csv("data/cement_demand_monthly.csv", show_col_types = FALSE) |>
  mutate(t = row_number() - 1, m = as.integer(format(month, "%m")), year = as.integer(format(month, "%Y")))

# ---- STEP 1 · Trend: annual totals and the average growth rate ----------------------------
annual <- c |> group_by(year) |> summarise(mt = sum(cement_mt)); annual
cagr <- (last(annual$mt) / first(annual$mt))^(1 / (nrow(annual) - 1)) - 1; cagr

# ---- STEP 2 · Seasonality ---------------------------------------------------------------------
idx <- c |> group_by(year) |> mutate(vs_year_avg = cement_mt / mean(cement_mt)) |>
  group_by(m) |> summarise(index = mean(vs_year_avg))
idx |> mutate(index = round(100 * index))
# Seasonally adjust the latest month and read it as an annual rate
last <- tail(c, 1)
cat(sprintf("Latest month seasonally adjusted x12 = %.1f Mt a year\n", last$cement_mt / idx$index[idx$m == last$m] * 12))

# ---- STEP 3 · A trend + seasonal model --------------------------------------------------------------
train <- filter(c, year <= 2023); test <- filter(c, year >= 2024)
fit <- lm(log(cement_mt) ~ t + factor(m), data = train)
f_model <- exp(predict(fit, newdata = test))

# ---- STEP 4 · Backtest against simple rules -----------------------------------------------------------
last12 <- tail(train$cement_mt, 12)
rules <- list(`same month last year` = c(last12, last12), `last year + 5%` = c(last12 * 1.05, last12 * 1.05^2),
              `trend + seasonal model` = f_model)
sapply(rules, function(f) c(MAPE = round(100 * mean(abs(test$cement_mt - f) / test$cement_mt), 1),
                             bias = round(100 * mean((f - test$cement_mt) / test$cement_mt), 1)))

# ---- STEP 5 · Forecast 2026 -----------------------------------------------------------------------------
fit_all <- lm(log(cement_mt) ~ t + factor(m), data = c)
fut <- tibble(t = nrow(c) + 0:11, m = 1:12)
f26 <- sum(exp(predict(fit_all, newdata = fut)))   # million tonnes in 2026
ann <- c |> mutate(fit = exp(fitted(fit_all))) |> group_by(year) |> summarise(a = sum(cement_mt), f = sum(fit))
annual_sd <- sd(log(ann$a / ann$f))                 # typical annual miss
c(base = f26, low90 = f26 * exp(-1.645 * annual_sd), high90 = f26 * exp(1.645 * annual_sd))

# ---- STEP 5b · The capacity decision: critical ratio --------------------------------------------------------
cost_short <- 20; cost_idle <- 8                    # ₦ thousand per tonne (illustrative)
cr <- cost_short / (cost_short + cost_idle)
c(critical_ratio = cr, plan_capacity_Mt = f26 * exp(qnorm(cr) * annual_sd))

# ---- STEP 6 · Size the market two ways ---------------------------------------------------------------------
237.5 * 0.129                        # top-down: World Bank population 2025 × CemNet kg per person
33.9e9 / 237.5e6                     # kg per person implied by the 33.9 Mt industry figure — why the gap?
14.4 + 6.5 + 6.0 + 4.5 + 2.4         # bottom-up

# ---- YOUR TURN -------------------------------------------------------------------------------------------------
# (a) Build a downside and upside scenario for 2026. What would have to happen for each?
# (b) Which assumption in the bottom-up sizing are you least sure of? How would you check it?
# (c) Recommend a 2026 capacity plan in two sentences.
