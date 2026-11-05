"""fetch_official_data.py — downloads REAL data to compare with the stylised course datasets.

Sources (free, no API key):
  * World Bank World Development Indicators — annual data for Nigeria and peers
  * FRED (Federal Reserve Bank of St. Louis) — US policy rate, US CPI, Brent oil price

Run from the project root:  python tools/fetch_official_data.py
Output: data/official/wdi_annual.csv and data/official/fred_monthly.csv
Nigeria monthly (CPI, MPR, T-bill, N/$, reserves) comes from the CBN statistics API -> data/official/ng_official_monthly.csv
"""
import io, os
import pandas as pd
import requests

OUT = "data/official"; os.makedirs(OUT, exist_ok=True)
COUNTRIES = "NGA;GHA;KEN;ZAF;EGY;CIV;MAR;ETH"
WDI = {"NY.GDP.MKTP.KD.ZG": "real_gdp_growth_pct", "FP.CPI.TOTL.ZG": "inflation_pct",
       "NY.GDP.PCAP.CD": "gdp_per_capita_usd", "PA.NUS.FCRF": "official_fx_lcu_per_usd",
       "BN.CAB.XOKA.GD.ZS": "current_account_gdp_pct", "FI.RES.TOTL.MO": "reserves_months_imports",
       "BX.TRF.PWKR.CD.DT": "remittances_usd", "SP.POP.TOTL": "population"}


def wdi(code, name):
    url = f"https://api.worldbank.org/v2/country/{COUNTRIES}/indicator/{code}?format=json&per_page=2000&date=2000:2025"
    js = requests.get(url, timeout=60).json()
    rows = [{"country": r["country"]["value"], "iso3": r["countryiso3code"], "year": int(r["date"]), name: r["value"]}
            for r in js[1] if r["value"] is not None]
    return pd.DataFrame(rows)


frames = []
for code, name in WDI.items():
    print("World Bank:", name)
    frames.append(wdi(code, name).set_index(["country", "iso3", "year"]))
wdi_df = pd.concat(frames, axis=1).reset_index().sort_values(["iso3", "year"])
wdi_df.to_csv(f"{OUT}/wdi_annual.csv", index=False)
print("saved", f"{OUT}/wdi_annual.csv", wdi_df.shape)

FRED = {"FEDFUNDS": "us_fed_funds_rate", "CPIAUCSL": "us_cpi_index", "DCOILBRENTEU": "brent_usd"}
fr = []
for code, name in FRED.items():
    print("FRED:", name)
    txt = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}", timeout=60).text
    d = pd.read_csv(io.StringIO(txt))
    d.columns = ["date", name]
    d["date"] = pd.to_datetime(d["date"])
    d[name] = pd.to_numeric(d[name], errors="coerce")
    fr.append(d.set_index("date").resample("MS").mean())
fred = pd.concat(fr, axis=1).loc["2000":].reset_index()
fred.to_csv(f"{OUT}/fred_monthly.csv", index=False)
print("saved", f"{OUT}/fred_monthly.csv", fred.shape)


# =============================================================================
# Nigeria: official monthly series from the CBN statistics API (used by the Session 1 deck)
#   https://www.cbn.gov.ng/rates/  — the same data behind the CBN's own tables and charts
# Output: data/official/ng_official_monthly.csv and data/official/ng_worldbank_annual.csv
# =============================================================================
def cbn(endpoint):
    return pd.DataFrame(requests.get(f"https://www.cbn.gov.ng/api/{endpoint}", timeout=180).json())

def ym(df):
    return pd.to_datetime(dict(year=df.tyear, month=df.tmonth, day=1))

print("CBN: inflation, money-market rates, exchange rates, reserves")
inf = cbn("GetAllInflationRates"); inf.index = ym(inf)
I = pd.DataFrame({"cpi_headline_yoy": pd.to_numeric(inf.allItemsYearOn, errors="coerce"),
                  "cpi_food_yoy": pd.to_numeric(inf.foodYearOn, errors="coerce"),
                  "cpi_core_yoy": pd.to_numeric(inf.allItemsLessFrmProdAndEnergyYearOn, errors="coerce")}).sort_index()
mm = cbn("GetAllMoneyMarketIndicators"); mm.index = ym(mm)
num = lambda s: pd.to_numeric(s, errors="coerce")
M = pd.DataFrame({"mpr": num(mm.mpr).replace(0, pd.NA), "mrr": num(mm.mrr), "tbill": num(mm.treasuryBill),
                  "prime_lending": num(mm.primeLending), "max_lending": num(mm.maxLending),
                  "savings_dep": num(mm.savingsDeposit)}).sort_index()
M["policy_rate"] = M.mpr.fillna(M.mrr)                      # MRR before the MPR was introduced
# Documented correction: the CBN monthly table shows 27.0% for Aug 2025, but the cut to 27% was decided at the
# MPC of 22–23 Sep 2025 (Nairametrics, 23 Sep 2025). Use 27.5% for Aug 2025.
M.loc["2025-08-01", ["mpr", "policy_rate"]] = 27.5
ex = cbn("GetAllExchangeRates"); ex = ex[ex.currency.str.strip() == "US DOLLAR"].copy()
ex["d"] = pd.to_datetime(ex.ratedate); ex["c"] = num(ex.centralrate)
ex = ex.sort_values("d").drop_duplicates("d").set_index("d").c
E = pd.DataFrame({"usd_official_avg": ex.resample("MS").mean(), "usd_official_eom": ex.resample("MS").last()})
ma = cbn("GetAllMonthlyAvgExchRates"); ma.index = ym(ma)
E["usd_bdc_avg"] = num(ma.bdcDollar).sort_index()           # CBN's BDC series ends in April 2021
rs = cbn("GetAllReserves"); rs["d"] = pd.to_datetime(rs.moveDate, format="%d/%m/%Y")
R = (num(rs.set_index("d").sort_index().gross) / 1e9).resample("MS").last().rename("reserves_gross_usdbn").to_frame()
br = pd.read_csv(io.StringIO(requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=MCOILBRENTEU", timeout=60).text))
br.columns = ["date", "brent"]; br["date"] = pd.to_datetime(br.date); br = br.set_index("date")
ng = I.join(M, how="outer").join(E, how="outer").join(R, how="outer").join(br, how="left").loc["2006":]
ng.index.name = "date"
ng.to_csv(f"{OUT}/ng_official_monthly.csv", float_format="%.2f")
print("saved", f"{OUT}/ng_official_monthly.csv", ng.shape)

print("World Bank: Nigeria annual")
WB = {"NY.GDP.PCAP.KD": "gdp_pc_const2015_usd", "NY.GDP.PCAP.CD": "gdp_pc_current_usd",
      "NY.GDP.MKTP.KD.ZG": "gdp_growth", "SP.POP.GROW": "pop_growth", "PA.NUS.FCRF": "ngn_usd_avg"}
rows = {}
for code, name in WB.items():
    js = requests.get(f"https://api.worldbank.org/v2/country/NGA/indicator/{code}?format=json&per_page=100", timeout=60).json()
    for r in js[1]:
        rows.setdefault(int(r["date"]), {})[name] = r["value"]
wb = pd.DataFrame(rows).T.sort_index(); wb.index.name = "year"
wb.to_csv(f"{OUT}/ng_worldbank_annual.csv", float_format="%.3f")
print("saved", f"{OUT}/ng_worldbank_annual.csv", wb.shape)
