"""fetch_official_data.py — downloads REAL data to compare with the stylised course datasets.

Sources (free, no API key):
  * World Bank World Development Indicators — annual data for Nigeria and peers
  * FRED (Federal Reserve Bank of St. Louis) — US policy rate, US CPI, Brent oil price

Run from the project root:  python tools/fetch_official_data.py
Output: data/official/wdi_annual.csv and data/official/fred_monthly.csv
For Nigerian monthly data (CPI, MPR, exchange rates, reserves) use the CBN and NBS websites directly.
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
