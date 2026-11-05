# =============================================================================
# EEGB · Session 16 · CAPSTONE STARTER — build the evidence pack for your board memo (R)
# Data: data/ng_macro_monthly.csv and any industry file from the course (all stylised teaching data)
# Change the settings in STEP 1, then run the whole file (Ctrl/Cmd + Shift + Enter).
# =============================================================================
source("R/theme_eegb.R")
suppressPackageStartupMessages({ library(dplyr); library(readr); library(tidyr) })

# ---- STEP 1 · Choose your industry and its macro drivers ----------------------------------------
INDUSTRY <- "Cement"
DRIVERS <- c(official_fx_ngn_usd = "imported energy, spare parts and kiln inputs",
             headline_inflation  = "construction costs and household purchasing power",
             mpr                 = "mortgage and developer credit",
             pmi                 = "early signal of construction activity")

# ---- STEP 2 · Evidence table -----------------------------------------------------------------------
m <- read_csv("data/ng_macro_monthly.csv", show_col_types = FALSE) |> mutate(date = as.Date(date))
n <- nrow(m)
ev <- tibble(driver = names(DRIVERS), why = unname(DRIVERS),
             latest = unlist(m[n, names(DRIVERS)]), a_year_ago = unlist(m[n - 12, names(DRIVERS)])) |>
  mutate(change = latest - a_year_ago)
print(ev)

# ---- STEP 3 · One page of charts (last five years) ----------------------------------------------------
w <- m |> filter(date >= max(date) - 365 * 5) |> select(date, all_of(names(DRIVERS))) |> pivot_longer(-date)
p <- ggplot(w, aes(date, value)) + geom_line(colour = eegb[["teal"]], linewidth = 1) +
  facet_wrap(~name, scales = "free_y") +
  labs(title = paste("Macro evidence pack —", INDUSTRY), x = NULL, y = NULL, caption = eegb_caption) + theme_eegb()
save_fig(p, "s16", "capstone_evidence_pack", width = 12, height = 6.5)

# ---- STEP 4 · Memo template -------------------------------------------------------------------------
cat("\nMEMO TO THE BOARD —", INDUSTRY, "\n",
    "1. Recommendation (one sentence): ...\n",
    "2. What has changed in the economy (three numbers): ...\n",
    "3. What it means for us (prices, volumes, costs, financing): ...\n",
    "4. Scenarios for the next 12 months (with probabilities): ...\n",
    "5. Signposts and triggers: ...\n",
    "6. Actions and owners: ...\n")

# ---- YOUR TURN -------------------------------------------------------------------------------------------
# (a) Replace INDUSTRY and DRIVERS with your own. (b) Add one industry dataset. (c) Write the memo in one page.
