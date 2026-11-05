# fetch_official_data.R — downloads REAL data to compare with the stylised course datasets.
# Sources (free, no API key): World Bank WDI (annual, Nigeria and peers) and FRED (US rates, CPI, Brent).
# Run from the project root:  source("tools/fetch_official_data.R")
# Output: data/official/wdi_annual.csv and data/official/fred_monthly.csv
library(jsonlite); library(dplyr); library(readr); library(tidyr)
out <- "data/official"; dir.create(out, recursive = TRUE, showWarnings = FALSE)
countries <- "NGA;GHA;KEN;ZAF;EGY;CIV;MAR;ETH"
wdi <- c(NY.GDP.MKTP.KD.ZG = "real_gdp_growth_pct", FP.CPI.TOTL.ZG = "inflation_pct",
         NY.GDP.PCAP.CD = "gdp_per_capita_usd", PA.NUS.FCRF = "official_fx_lcu_per_usd",
         BN.CAB.XOKA.GD.ZS = "current_account_gdp_pct", FI.RES.TOTL.MO = "reserves_months_imports",
         BX.TRF.PWKR.CD.DT = "remittances_usd", SP.POP.TOTL = "population")

get_wdi <- function(code, name) {
  url <- sprintf("https://api.worldbank.org/v2/country/%s/indicator/%s?format=json&per_page=2000&date=2000:2025", countries, code)
  js <- fromJSON(url)[[2]]
  tibble(country = js$country$value, iso3 = js$countryiso3code, year = as.integer(js$date), indicator = name, value = js$value)
}
wdi_df <- bind_rows(Map(get_wdi, names(wdi), wdi)) |> filter(!is.na(value)) |>
  pivot_wider(names_from = indicator, values_from = value) |> arrange(iso3, year)
write_csv(wdi_df, file.path(out, "wdi_annual.csv")); message("saved ", file.path(out, "wdi_annual.csv"))

fred <- c(FEDFUNDS = "us_fed_funds_rate", CPIAUCSL = "us_cpi_index", DCOILBRENTEU = "brent_usd")
fr <- lapply(names(fred), function(code) {
  d <- read_csv(paste0("https://fred.stlouisfed.org/graph/fredgraph.csv?id=", code), show_col_types = FALSE, na = c("", "."))
  names(d) <- c("date", fred[[code]])
  d |> mutate(date = as.Date(format(as.Date(date), "%Y-%m-01"))) |> group_by(date) |> summarise(across(everything(), ~ mean(.x, na.rm = TRUE)))
})
fred_df <- Reduce(function(a, b) full_join(a, b, by = "date"), fr) |> filter(date >= as.Date("2000-01-01")) |> arrange(date)
write_csv(fred_df, file.path(out, "fred_monthly.csv")); message("saved ", file.path(out, "fred_monthly.csv"))
