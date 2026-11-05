"""make_data.py — generates every EEGB teaching dataset in data/ with fixed random seeds.

IMPORTANT: these are STYLISED TEACHING DATA. The macro series are calibrated to follow the broad,
published path of the Nigerian and global economy (levels, turning points, reform dates), but every
value is generated, smoothed and rounded for teaching. Do not quote them as official statistics.
For real numbers use tools/fetch_official_data.py (World Bank / FRED) or the CBN and NBS websites.

Run from the project root:  python tools/make_data.py
"""
import numpy as np, pandas as pd, os

os.makedirs("data", exist_ok=True)


def save(df, name):
    df.to_csv(f"data/{name}", index=False)
    print(f"data/{name:32s} {len(df):>6,} rows x {df.shape[1]} cols")


def path(anchors, index, rng=None, noise=0.0, smooth=True):
    """Interpolate a monthly series through (YYYY-MM, value) anchor points, plus optional noise."""
    a = pd.Series({pd.Timestamp(k + "-01"): v for k, v in anchors}).sort_index()
    s = a.reindex(a.index.union(index)).interpolate("time").reindex(index)
    s = s.ffill().bfill()
    if rng is not None and noise:
        e = rng.normal(0, noise, len(s))
        if smooth: e = pd.Series(e).rolling(3, min_periods=1).mean().values
        s = s + e
    return s.values


# =================================================================================================
# 1. ng_macro_monthly.csv — Nigeria monthly macro, Jan 2015 – Dec 2025 (Sessions 1, 6, 8, 11)
# =================================================================================================
rng = np.random.default_rng(101)
idx = pd.date_range("2015-01-01", "2025-12-01", freq="MS")
infl = path([("2015-01", 8.2), ("2015-12", 9.6), ("2016-06", 16.5), ("2017-01", 18.7), ("2017-12", 15.4),
             ("2018-12", 11.4), ("2019-12", 12.0), ("2020-06", 12.6), ("2021-03", 18.2), ("2021-12", 15.6),
             ("2022-06", 18.6), ("2022-12", 21.3), ("2023-06", 22.8), ("2023-12", 28.9), ("2024-06", 34.2),
             ("2024-12", 34.8), ("2025-01", 24.5), ("2025-06", 22.2), ("2025-12", 16.5)], idx, rng, 0.25)
food = path([("2015-01", 9.0), ("2015-12", 10.6), ("2016-06", 15.8), ("2017-01", 17.8), ("2017-08", 20.3),
             ("2018-12", 13.6), ("2019-12", 14.7), ("2020-12", 19.6), ("2021-03", 22.9), ("2021-12", 17.4),
             ("2022-12", 23.8), ("2023-06", 25.3), ("2023-12", 33.9), ("2024-06", 40.9), ("2024-12", 39.8),
             ("2025-01", 26.1), ("2025-06", 21.9), ("2025-12", 14.5)], idx, rng, 0.35)
core = path([("2015-01", 8.0), ("2015-12", 8.7), ("2016-06", 16.2), ("2017-01", 17.9), ("2017-12", 12.1),
             ("2018-12", 9.8), ("2019-12", 9.3), ("2020-12", 11.4), ("2021-12", 13.9), ("2022-12", 18.5),
             ("2023-06", 20.3), ("2023-12", 23.1), ("2024-06", 27.4), ("2024-12", 29.3), ("2025-01", 22.6),
             ("2025-06", 22.8), ("2025-12", 18.9)], idx, rng, 0.2)
mpr_steps = [("2015-01", 13.0), ("2015-11", 11.0), ("2016-07", 14.0), ("2019-03", 13.5), ("2020-05", 12.5),
             ("2020-09", 11.5), ("2022-05", 13.0), ("2022-07", 14.0), ("2022-09", 15.5), ("2022-11", 16.5),
             ("2023-01", 17.5), ("2023-03", 18.0), ("2023-05", 18.5), ("2023-07", 18.75), ("2024-02", 22.75),
             ("2024-03", 24.75), ("2024-05", 26.25), ("2024-07", 26.75), ("2024-09", 27.25), ("2024-11", 27.5),
             ("2025-09", 27.0)]
mpr = pd.Series({pd.Timestamp(k + "-01"): v for k, v in mpr_steps}).reindex(idx).ffill().values
interbank = np.clip(mpr + path([("2015-01", -1), ("2017-01", 2), ("2019-06", -2), ("2020-10", -9), ("2021-06", -4),
                                ("2022-06", -3), ("2023-06", -5), ("2024-03", 3), ("2024-12", 4), ("2025-12", -0.5)],
                               idx, rng, 1.2, smooth=False), 0.5, None)
off_fx = path([("2015-01", 169), ("2015-03", 197), ("2016-05", 199), ("2016-07", 290), ("2016-12", 305),
               ("2020-02", 307), ("2020-04", 361), ("2020-09", 380), ("2021-05", 410), ("2021-12", 415),
               ("2022-06", 420), ("2022-12", 446), ("2023-05", 462), ("2023-06", 640), ("2023-07", 760),
               ("2023-12", 900), ("2024-01", 1100), ("2024-02", 1500), ("2024-03", 1350), ("2024-04", 1200),
               ("2024-05", 1450), ("2024-07", 1590), ("2024-10", 1660), ("2024-12", 1540), ("2025-03", 1530),
               ("2025-06", 1540), ("2025-09", 1490), ("2025-12", 1460)], idx, rng, 4)
par_fx = path([("2015-01", 190), ("2015-12", 270), ("2016-02", 390), ("2016-09", 470), ("2017-02", 500),
               ("2017-06", 366), ("2019-12", 362), ("2020-06", 455), ("2020-12", 470), ("2021-06", 500),
               ("2021-11", 570), ("2022-06", 610), ("2022-10", 790), ("2023-01", 750), ("2023-06", 770),
               ("2023-09", 1000), ("2023-12", 1220), ("2024-02", 1560), ("2024-03", 1400), ("2024-04", 1220),
               ("2024-07", 1620), ("2024-10", 1710), ("2024-12", 1660), ("2025-06", 1555), ("2025-12", 1475)],
              idx, rng, 6)
brent = path([("2015-01", 48), ("2015-06", 62), ("2015-12", 38), ("2016-01", 31), ("2016-12", 54), ("2017-12", 64),
              ("2018-09", 79), ("2018-12", 57), ("2019-12", 66), ("2020-04", 23), ("2020-12", 50), ("2021-10", 84),
              ("2022-03", 112), ("2022-06", 117), ("2022-12", 81), ("2023-09", 94), ("2023-12", 77), ("2024-04", 90),
              ("2024-12", 74), ("2025-04", 66), ("2025-12", 63)], idx, rng, 2.0)
reserves = path([("2015-01", 34.5), ("2015-12", 28.3), ("2016-10", 24.3), ("2017-12", 38.8), ("2018-06", 47.8),
                 ("2019-12", 38.6), ("2020-12", 36.5), ("2021-10", 41.8), ("2022-12", 37.1), ("2023-12", 33.2),
                 ("2024-06", 34.2), ("2024-12", 40.9), ("2025-06", 37.3), ("2025-12", 44.5)], idx, rng, 0.3)
m2 = path([("2015-01", 10), ("2016-12", 17.8), ("2018-12", 12.1), ("2020-12", 13.0), ("2022-12", 18.0),
           ("2023-12", 51.9), ("2024-06", 64.0), ("2024-12", 45.0), ("2025-12", 18.0)], idx, rng, 1.0)
credit = path([("2015-01", 10), ("2016-12", 21), ("2018-12", 1.5), ("2019-12", 11), ("2020-12", 15),
               ("2022-12", 22), ("2023-12", 62), ("2024-06", 55), ("2024-12", 23), ("2025-12", 9)], idx, rng, 1.2)
pmi = np.clip(path([("2015-01", 52), ("2016-01", 45), ("2016-08", 43), ("2017-06", 52), ("2019-06", 57),
                    ("2020-05", 39), ("2020-12", 50), ("2022-06", 53), ("2023-06", 52), ("2023-12", 49),
                    ("2024-03", 47), ("2024-12", 49.5), ("2025-06", 51.5), ("2025-12", 53)], idx, rng, 1.0, smooth=False), 35, 62)
macro = pd.DataFrame({
    "date": idx.strftime("%Y-%m-%d"), "headline_inflation": infl.round(2), "food_inflation": food.round(2),
    "core_inflation": core.round(2), "mpr": mpr, "interbank_rate": interbank.round(2),
    "official_fx_ngn_usd": off_fx.round(1), "parallel_fx_ngn_usd": np.maximum(par_fx, off_fx).round(1),
    "brent_usd": brent.round(1), "fx_reserves_usd_bn": reserves.round(2), "m2_growth_yoy": m2.round(1),
    "private_credit_growth_yoy": credit.round(1), "pmi": pmi.round(1),
    "cpi_base_note": np.where(idx >= "2025-01-01", "rebased CPI (2024=100)", "old CPI (2009=100)")})
save(macro, "ng_macro_monthly.csv")

# =================================================================================================
# 2. fmcg_price_volume.csv — weekly noodles pricing in three regions (Session 2)
# =================================================================================================
rng = np.random.default_rng(202)
rows = []
weeks = pd.date_range("2022-01-03", "2025-12-29", freq="W-MON")
for region, base_units, inc0 in [("Lagos", 52000, 100), ("North", 61000, 82), ("South-East", 34000, 94)]:
    price, comp = 160.0, 155.0
    ref = price
    for t, w in enumerate(weeks):
        cost_push = 1 + 0.0042 + (0.012 if w.year == 2024 else 0) * (w.month <= 6)
        price = price * cost_push * rng.normal(1, 0.006)
        comp = comp * cost_push * rng.normal(1, 0.007)
        promo = int(rng.random() < 0.12)
        shelf = price * (0.85 if promo else 1.0)
        income = inc0 * (1 + 0.003 * t) * (0.92 if w >= pd.Timestamp("2023-07-01") else 1)
        real_p = shelf / (1 + 0.0042) ** t
        real_c = comp / (1 + 0.0042) ** t
        # demand: own -1.4, cross +0.6, income +0.8; loss aversion vs reference price
        gap = np.log(shelf / ref)
        la = -0.9 * gap if gap > 0 else -0.3 * gap
        units = (base_units * (real_p / 160) ** -1.4 * (real_c / 155) ** 0.6 * (income / inc0) ** 0.8
                 * np.exp(la) * (1 + 0.08 * np.sin(2 * np.pi * (w.dayofyear / 365 - 0.2))) * rng.lognormal(0, 0.05))
        rows.append([w.strftime("%Y-%m-%d"), region, round(shelf, 1), round(comp, 1), promo, round(income, 1),
                     int(units), round(shelf * units / 1e6, 2)])
        ref = 0.8 * ref + 0.2 * shelf
save(pd.DataFrame(rows, columns=["week", "region", "price_naira", "competitor_price_naira", "promo",
                                 "income_index", "units", "revenue_naira_m"]), "fmcg_price_volume.csv")

# =================================================================================================
# 3. cement_demand_monthly.csv — Nigerian cement consumption, 2012–2025 (Session 3)
# =================================================================================================
rng = np.random.default_rng(303)
idx3 = pd.date_range("2012-01-01", "2025-12-01", freq="MS")
t = np.arange(len(idx3))
season = {1: 1.10, 2: 1.12, 3: 1.10, 4: 1.04, 5: 0.98, 6: 0.90, 7: 0.84, 8: 0.82, 9: 0.88, 10: 1.02, 11: 1.08, 12: 1.06}
shock = np.ones(len(idx3))
for i, d in enumerate(idx3):
    if d.year == 2016: shock[i] = 0.91
    if pd.Timestamp("2020-04-01") <= d <= pd.Timestamp("2020-08-01"): shock[i] = 0.80
    if d.year == 2024: shock[i] = 0.93
level = 1.55 * (1.042 ** (t / 12)) * shock * np.array([season[d.month] for d in idx3]) * rng.lognormal(0, 0.035, len(idx3))
price = path([("2012-01", 1650), ("2016-06", 2300), ("2019-12", 2650), ("2021-12", 4100), ("2023-06", 5200),
              ("2024-03", 9500), ("2024-12", 8200), ("2025-12", 9000)], idx3, rng, 60)
save(pd.DataFrame({"month": idx3.strftime("%Y-%m-%d"), "cement_mt": level.round(3),
                   "price_per_bag_naira": price.round(0), "rainy_season": [int(d.month in (6, 7, 8, 9)) for d in idx3],
                   "building_permits_index": (100 * 1.03 ** (t / 12) * shock * rng.lognormal(0, .05, len(idx3))).round(1)}),
     "cement_demand_monthly.csv")

# =================================================================================================
# 4. payments_market_shares.csv — fictional mobile-payment providers, 2016–2025 (Session 4)
# =================================================================================================
rng = np.random.default_rng(404)
years = list(range(2016, 2026))
provs = {"Banks (app & USSD)": [78, 74, 69, 63, 55, 47, 40, 34, 30, 28],
         "KoboLink": [2, 4, 7, 10, 15, 19, 23, 27, 29, 30],
         "SwiftNaira": [1, 2, 3, 5, 8, 11, 14, 16, 18, 19],
         "AgentPay": [4, 5, 6, 7, 8, 9, 10, 11, 11, 11],
         "PayFast": [6, 7, 8, 8, 8, 7, 6, 6, 6, 6],
         "Others": [9, 8, 7, 7, 6, 7, 7, 6, 6, 6]}
rows = []
for j, y in enumerate(years):
    total = sum(v[j] for v in provs.values())
    for p, v in provs.items():
        share = v[j] / total * 100
        users = share / 100 * (12 + 9.5 * j) * rng.normal(1, .03)
        merch = share / 100 * (0.3 + 0.42 * j ** 1.3) * rng.normal(1, .05)
        fee = {"Banks (app & USSD)": 0.65, "KoboLink": 0.50, "SwiftNaira": 0.55, "AgentPay": 0.80,
               "PayFast": 0.70, "Others": 0.75}[p] + (0.12 * (share / 100) if p in ("KoboLink",) and y >= 2023 else 0)
        rows.append([y, p, round(share, 2), round(users, 2), round(merch, 3), round(fee * rng.normal(1, .02), 3)])
save(pd.DataFrame(rows, columns=["year", "provider", "share_of_value_pct", "active_users_m", "merchants_m",
                                 "avg_fee_pct"]), "payments_market_shares.csv")

# =================================================================================================
# 5. fuel_subsidy_incidence.csv — household budget by consumption decile (Session 5)
# =================================================================================================
rng = np.random.default_rng(505)
dec = np.arange(1, 11)
spend = np.array([38, 55, 70, 84, 99, 117, 140, 172, 226, 410]) * 1000          # monthly household spend, NGN (pre-reform)
pms_litres = np.array([4, 7, 11, 15, 21, 28, 38, 52, 78, 150])                  # direct petrol + generator use per month
transport_share = np.array([6, 7, 8, 8, 9, 9, 10, 10, 10, 9]) / 100
food_share = np.array([64, 61, 58, 55, 52, 49, 45, 41, 36, 27]) / 100
hh = pd.DataFrame({"decile": dec, "monthly_spend_naira": spend, "petrol_litres_month": pms_litres,
                   "transport_share": transport_share, "food_share": food_share,
                   "owns_vehicle_pct": [1, 2, 3, 5, 8, 12, 18, 27, 41, 68],
                   "uses_generator_pct": [9, 14, 20, 27, 34, 42, 51, 60, 70, 84],
                   "households_m": [4.4] * 10})
hh["subsidy_per_litre_pre"] = 315.0      # stylised gap between landing cost and pump price, mid-2023
hh["pump_price_pre"] = 185.0
hh["pump_price_post"] = 617.0
save(hh, "fuel_subsidy_incidence.csv")

# =================================================================================================
# 6. ng_gdp_sectors.csv — annual real GDP by sector (₦ tn, constant prices), 2010–2025 (Session 7)
# =================================================================================================
rng = np.random.default_rng(606)
yrs = np.arange(2010, 2026)
growth = {2010: 8.0, 2011: 5.3, 2012: 4.2, 2013: 5.5, 2014: 6.2, 2015: 2.7, 2016: -1.6, 2017: 0.8, 2018: 1.9,
          2019: 2.2, 2020: -1.8, 2021: 3.6, 2022: 3.1, 2023: 2.7, 2024: 3.4, 2025: 3.9}
oil_g = {2010: 5, 2011: 1, 2012: -5, 2013: -13, 2014: -1, 2015: -5.5, 2016: -14.5, 2017: 4.7, 2018: 1.0, 2019: 4.6,
         2020: -8.9, 2021: -8.3, 2022: -19.2, 2023: -2.2, 2024: 5.5, 2025: 6.0}
shares0 = {"agriculture": 23.9, "oil_and_gas": 15.8, "manufacturing": 6.6, "construction": 3.3,
           "trade": 16.4, "ict_telecom": 7.5, "finance_insurance": 3.0, "real_estate": 7.9, "public_admin": 3.9,
           "other_services": 11.7}
total0 = 54.6
rows = []; level = {k: total0 * v / 100 for k, v in shares0.items()}
for y in yrs:
    if y > 2010:
        g = growth[y] / 100
        level["oil_and_gas"] *= 1 + oil_g[y] / 100
        non_oil_now = sum(v for k, v in level.items() if k != "oil_and_gas")
        target_total = prev_total * (1 + g)
        need = target_total - level["oil_and_gas"]
        tilt = {"ict_telecom": 2.4, "finance_insurance": 1.3, "agriculture": .95, "manufacturing": .85,
                "construction": 1.0, "trade": .9, "real_estate": .8, "public_admin": .8, "other_services": 1.05}
        raw = {k: level[k] * (1 + (need / non_oil_now - 1) * tilt[k]) for k in tilt}
        scale = need / sum(raw.values())
        for k in tilt: level[k] = raw[k] * scale * rng.normal(1, .002)
    total = sum(level.values()); prev_total = total
    deflator = 100 * np.prod([1 + (x / 100) for x in [12, 9, 6, 7, 2, 2, 10, 11, 8, 6, 8, 10, 13, 18, 30, 22][: y - 2009]]) / 1.12
    row = {"year": y, **{k: round(v, 3) for k, v in level.items()}}
    row["real_gdp_total"] = round(total, 3)
    row["nominal_gdp_old_base"] = round(total * deflator / 100, 2)
    row["nominal_gdp_new_base"] = round(total * deflator / 100 * (1.36 if y >= 2019 else np.nan), 2) if y >= 2019 else np.nan
    row["population_m"] = round(160 * 1.026 ** (y - 2010), 1)
    rows.append(row)
save(pd.DataFrame(rows), "ng_gdp_sectors.csv")

# peer_income.csv — stylised cross-country snapshot (Session 7)
peers = pd.DataFrame([
    ["Nigeria", 1100, 6300, 230, 0.57, 2.9, 0.55],
    ["Ghana", 2300, 7300, 34, 0.38, 3.1, 0.60],
    ["Kenya", 2100, 6100, 56, 0.33, 4.6, 0.60],
    ["South Africa", 6200, 15800, 63, 0.18, 0.8, 0.72],
    ["Egypt", 3400, 16800, 114, 0.30, 3.8, 0.73],
    ["Côte d'Ivoire", 2700, 6900, 30, 0.40, 6.0, 0.55],
    ["India", 2600, 10200, 1440, 0.45, 6.8, 0.65],
    ["Indonesia", 5000, 15500, 280, 0.23, 5.0, 0.71],
    ["Vietnam", 4400, 14300, 100, 0.25, 6.0, 0.73],
    ["Brazil", 10300, 21000, 212, 0.29, 3.0, 0.76]],
    columns=["country", "gdp_per_capita_usd", "gdp_per_capita_ppp", "population_m", "informal_share_gdp",
             "real_growth_5y_avg", "hdi"])
save(peers, "peer_income.csv")

# =================================================================================================
# 7. global_policy_rates.csv — monthly policy rates, 2019–2025 (Session 8)
# =================================================================================================
rng = np.random.default_rng(707)
idx7 = pd.date_range("2019-01-01", "2025-12-01", freq="MS")
def steps(pairs): return pd.Series({pd.Timestamp(k + "-01"): v for k, v in pairs}).reindex(idx7).ffill().values
pr = pd.DataFrame({"date": idx7.strftime("%Y-%m-%d"),
    "us_fed": steps([("2019-01", 2.5), ("2019-08", 2.25), ("2019-10", 1.75), ("2020-03", 0.25), ("2022-03", 0.5),
                     ("2022-05", 1.0), ("2022-06", 1.75), ("2022-07", 2.5), ("2022-09", 3.25), ("2022-11", 4.0),
                     ("2022-12", 4.5), ("2023-02", 4.75), ("2023-03", 5.0), ("2023-05", 5.25), ("2023-07", 5.5),
                     ("2024-09", 5.0), ("2024-11", 4.75), ("2024-12", 4.5), ("2025-09", 4.25), ("2025-10", 4.0), ("2025-12", 3.75)]),
    "euro_area_ecb": steps([("2019-01", 0.0), ("2022-07", 0.5), ("2022-09", 1.25), ("2022-11", 2.0), ("2022-12", 2.5),
                            ("2023-02", 3.0), ("2023-03", 3.5), ("2023-05", 3.75), ("2023-06", 4.0), ("2023-08", 4.25),
                            ("2024-06", 4.0), ("2024-09", 3.65), ("2024-10", 3.4), ("2024-12", 3.15), ("2025-02", 2.9),
                            ("2025-03", 2.65), ("2025-04", 2.4), ("2025-06", 2.15)]),
    "uk_boe": steps([("2019-01", 0.75), ("2020-03", 0.1), ("2021-12", 0.25), ("2022-02", 0.5), ("2022-05", 1.0),
                     ("2022-08", 1.75), ("2022-11", 3.0), ("2023-02", 4.0), ("2023-05", 4.5), ("2023-08", 5.25),
                     ("2024-08", 5.0), ("2024-11", 4.75), ("2025-02", 4.5), ("2025-05", 4.25), ("2025-08", 4.0)]),
    "nigeria_cbn": steps([("2019-01", 14.0), ("2019-03", 13.5), ("2020-05", 12.5), ("2020-09", 11.5), ("2022-05", 13.0),
                          ("2022-07", 14.0), ("2022-09", 15.5), ("2022-11", 16.5), ("2023-01", 17.5), ("2023-03", 18.0),
                          ("2023-05", 18.5), ("2023-07", 18.75), ("2024-02", 22.75), ("2024-03", 24.75), ("2024-05", 26.25),
                          ("2024-07", 26.75), ("2024-09", 27.25), ("2024-11", 27.5), ("2025-09", 27.0)]),
    "south_africa_sarb": steps([("2019-01", 6.75), ("2019-07", 6.5), ("2020-01", 6.25), ("2020-03", 5.25), ("2020-04", 4.25),
                                ("2020-05", 3.75), ("2020-07", 3.5), ("2021-11", 3.75), ("2022-01", 4.0), ("2022-03", 4.25),
                                ("2022-05", 4.75), ("2022-07", 5.5), ("2022-09", 6.25), ("2022-11", 7.0), ("2023-01", 7.25),
                                ("2023-03", 7.75), ("2023-05", 8.25), ("2024-09", 8.0), ("2024-11", 7.75), ("2025-01", 7.5),
                                ("2025-05", 7.25), ("2025-07", 7.0)]),
    "ghana_bog": steps([("2019-01", 16.0), ("2020-03", 14.5), ("2021-05", 13.5), ("2022-03", 17.0), ("2022-05", 19.0),
                        ("2022-08", 22.0), ("2022-10", 24.5), ("2022-11", 27.0), ("2023-01", 28.0), ("2023-03", 29.5),
                        ("2023-07", 30.0), ("2024-03", 29.0), ("2024-07", 29.0), ("2024-09", 27.0), ("2025-03", 28.0),
                        ("2025-07", 25.0), ("2025-09", 21.5)]),
    "kenya_cbk": steps([("2019-01", 9.0), ("2019-11", 8.5), ("2020-01", 8.25), ("2020-03", 7.25), ("2020-04", 7.0),
                        ("2022-05", 7.5), ("2022-09", 8.25), ("2022-11", 8.75), ("2023-06", 10.5), ("2023-12", 12.5),
                        ("2024-02", 13.0), ("2024-08", 12.75), ("2024-10", 12.0), ("2024-12", 11.25), ("2025-02", 10.75),
                        ("2025-04", 10.0), ("2025-06", 9.75), ("2025-08", 9.5)])})
save(pr, "global_policy_rates.csv")

# =================================================================================================
# 8. fgn_fiscal_annual.csv — Federal Government finances, 2010–2025 (₦ tn) (Session 9)
# =================================================================================================
rng = np.random.default_rng(808)
fy = np.arange(2010, 2026)
ngdp = np.array([55, 63, 72, 81, 90, 95, 102, 114, 129, 145, 154, 176, 202, 234, 300, 370.0])
rev = np.array([3.1, 3.6, 3.6, 3.8, 3.7, 3.4, 2.7, 2.6, 3.9, 4.1, 3.9, 4.5, 6.4, 9.6, 13.7, 18.0])
oil_share = np.array([.70, .72, .70, .68, .66, .50, .38, .40, .50, .46, .37, .33, .30, .35, .40, .38])
spend = np.array([4.2, 4.7, 4.6, 5.2, 4.9, 4.6, 5.0, 6.5, 7.4, 8.2, 10.2, 11.4, 14.6, 18.6, 24.6, 30.0])
debt_service = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.1, 1.4, 1.8, 2.2, 2.5, 3.3, 4.2, 5.2, 7.8, 9.0, 12.0])
debt = np.array([7.6, 8.5, 9.6, 10.0, 11.2, 12.6, 17.4, 21.7, 24.4, 27.4, 32.9, 39.6, 46.3, 97.3, 144.7, 155.0])
fiscal = pd.DataFrame({"year": fy, "nominal_gdp_ntn": ngdp, "fgn_revenue_ntn": rev, "oil_share_of_revenue": oil_share,
                       "fgn_expenditure_ntn": spend, "interest_payments_ntn": debt_service,
                       "total_public_debt_ntn": debt})
fiscal["debt_to_gdp_pct"] = (100 * fiscal.total_public_debt_ntn / fiscal.nominal_gdp_ntn).round(1)
fiscal["revenue_to_gdp_pct"] = (100 * fiscal.fgn_revenue_ntn / fiscal.nominal_gdp_ntn).round(1)
fiscal["interest_to_revenue_pct"] = (100 * fiscal.interest_payments_ntn / fiscal.fgn_revenue_ntn).round(1)
fiscal["primary_balance_ntn"] = (fiscal.fgn_revenue_ntn - (fiscal.fgn_expenditure_ntn - fiscal.interest_payments_ntn)).round(2)
fiscal["nominal_gdp_growth_pct"] = (100 * fiscal.nominal_gdp_ntn.pct_change()).round(1)
fiscal["avg_interest_rate_pct"] = (100 * fiscal.interest_payments_ntn / fiscal.total_public_debt_ntn.shift(1)).round(1)
save(fiscal, "fgn_fiscal_annual.csv")

# =================================================================================================
# 9. ng_yield_curves.csv and bank_balance_sheet.csv (Session 10)
# =================================================================================================
ten = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30]
curves = {"2021-06-30": [2.5, 4.0, 7.5, 9.5, 10.5, 11.6, 12.2, 12.8, 13.1, 13.3, 13.4],
          "2023-01-31": [4.0, 5.5, 8.0, 10.0, 11.0, 12.8, 13.5, 14.0, 14.4, 14.7, 14.9],
          "2024-06-28": [17.5, 19.0, 21.0, 20.5, 19.8, 19.2, 18.9, 18.8, 18.6, 18.5, 18.3],
          "2025-06-30": [19.5, 20.5, 22.0, 20.0, 19.0, 18.2, 17.8, 17.5, 17.2, 17.0, 16.9],
          "2025-12-31": [16.0, 17.0, 17.8, 17.0, 16.6, 16.2, 16.0, 15.9, 15.8, 15.7, 15.6]}
save(pd.DataFrame([{"date": d, "tenor_years": t, "yield_pct": y} for d, ys in curves.items() for t, y in zip(ten, ys)]),
     "ng_yield_curves.csv")
bs = pd.DataFrame([
    ["asset", "Cash & CBN reserves", 1450, 0.0, 0.0, 0],
    ["asset", "Treasury bills", 620, 0.4, 17.0, 0],
    ["asset", "FGN bonds (held to maturity)", 1850, 7.5, 13.0, 1],
    ["asset", "Loans to corporates", 2300, 1.2, 24.0, 0],
    ["asset", "Loans to retail & SMEs", 950, 1.0, 29.0, 0],
    ["asset", "Fixed assets & other", 330, 0.0, 0.0, 0],
    ["liability", "Current & savings deposits", 4600, 0.3, 4.0, 0],
    ["liability", "Term deposits", 1650, 0.5, 18.0, 0],
    ["liability", "Interbank & CBN borrowing", 450, 0.1, 26.0, 0],
    ["liability", "Long-term borrowing", 300, 3.0, 12.0, 0],
    ["equity", "Shareholders' funds", 750, 0.0, 0.0, 0]],
    columns=["side", "item", "amount_ngn_bn", "duration_years", "rate_pct", "fixed_rate_long"])
save(bs, "bank_balance_sheet.csv")

# =================================================================================================
# 10. ng_bop_quarterly.csv — balance of payments, 2015Q1–2025Q2 (US$ bn) (Session 11)
# =================================================================================================
rng = np.random.default_rng(1010)
q = pd.period_range("2015Q1", "2025Q2", freq="Q")
qi = pd.to_datetime(q.to_timestamp())
def qpath(pairs, noise): return path(pairs, pd.DatetimeIndex(qi), rng, noise, smooth=False)
bop = pd.DataFrame({"quarter": q.astype(str),
    "trade_balance": qpath([("2015-01", -1.5), ("2016-01", -1.0), ("2017-01", 2.5), ("2018-01", 5.0), ("2019-01", 1.5),
                            ("2020-04", -5.0), ("2021-01", -2.5), ("2022-01", 3.0), ("2023-01", 2.0), ("2024-01", 5.5),
                            ("2025-04", 3.5)], 0.9),
    "remittances": qpath([("2015-01", 5.1), ("2018-01", 6.0), ("2020-04", 4.0), ("2022-01", 5.0), ("2024-01", 5.0),
                          ("2025-04", 5.4)], 0.3),
    "services_income_net": qpath([("2015-01", -6.5), ("2019-01", -8.0), ("2020-04", -4.5), ("2023-01", -6.0),
                                  ("2025-04", -5.5)], 0.6),
    "fdi_inflows": qpath([("2015-01", 0.8), ("2018-01", 0.5), ("2021-01", 0.25), ("2024-01", 0.3), ("2025-04", 0.35)], 0.08),
    "portfolio_inflows": qpath([("2015-01", 2.5), ("2016-04", 0.3), ("2017-07", 4.0), ("2018-01", 5.5), ("2019-01", 3.0),
                                ("2019-07", 6.0), ("2020-04", 0.6), ("2021-07", 1.0), ("2022-07", 0.4), ("2023-07", 0.6),
                                ("2024-04", 2.5), ("2024-10", 4.5), ("2025-04", 5.0)], 0.5)})
bop["current_account"] = (bop.trade_balance + bop.remittances + bop.services_income_net).round(2)
for c in bop.columns[1:]: bop[c] = bop[c].astype(float).round(2)
save(bop, "ng_bop_quarterly.csv")

# =================================================================================================
# 11. ng_trade_partners.csv — exports/imports by partner (US$ m, stylised 2024) (Session 12)
# =================================================================================================
rng = np.random.default_rng(1111)
P = [  # country, region, gdp_usd_bn, distance_km, english, afcfta, landlocked
    ["India", "Asia", 3900, 7800, 1, 0, 0], ["Spain", "Europe", 1700, 4300, 0, 0, 0], ["Netherlands", "Europe", 1150, 5000, 0, 0, 0],
    ["France", "Europe", 3100, 4700, 0, 0, 0], ["United States", "Americas", 28000, 9500, 1, 0, 0], ["China", "Asia", 18500, 11300, 0, 0, 0],
    ["Belgium", "Europe", 650, 4900, 0, 0, 0], ["Italy", "Europe", 2300, 4100, 0, 0, 0], ["United Kingdom", "Europe", 3300, 5000, 1, 0, 0],
    ["Germany", "Europe", 4500, 4900, 0, 0, 0], ["Brazil", "Americas", 2200, 6000, 0, 0, 0], ["Canada", "Americas", 2200, 9100, 1, 0, 0],
    ["Indonesia", "Asia", 1400, 11800, 0, 0, 0], ["Japan", "Asia", 4100, 13300, 0, 0, 0], ["UAE", "Middle East", 540, 5900, 0, 0, 0],
    ["Saudi Arabia", "Middle East", 1100, 4600, 0, 0, 0], ["Turkey", "Europe", 1300, 4300, 0, 0, 0], ["South Korea", "Asia", 1700, 12600, 0, 0, 0],
    ["Ghana", "Africa", 76, 400, 1, 1, 0], ["Côte d'Ivoire", "Africa", 80, 800, 0, 1, 0], ["Togo", "Africa", 9, 250, 0, 1, 0],
    ["Benin", "Africa", 20, 120, 0, 1, 0], ["Cameroon", "Africa", 50, 900, 1, 1, 0], ["Senegal", "Africa", 31, 2400, 0, 1, 0],
    ["South Africa", "Africa", 380, 4500, 1, 1, 0], ["Kenya", "Africa", 105, 3800, 1, 1, 0], ["Egypt", "Africa", 390, 3700, 0, 1, 0],
    ["Niger", "Africa", 18, 900, 0, 1, 1], ["Chad", "Africa", 13, 1100, 0, 1, 1], ["Morocco", "Africa", 150, 3300, 0, 1, 0]]
tp = pd.DataFrame(P, columns=["partner", "region", "partner_gdp_usd_bn", "distance_km", "common_language", "afcfta_member", "landlocked"])
lg = (-1.2 + 0.85 * np.log(tp.partner_gdp_usd_bn) - 0.95 * np.log(tp.distance_km) + 0.45 * tp.common_language
      - 0.6 * tp.landlocked + rng.normal(0, 0.45, len(tp)))
tp["total_trade_usd_m"] = (np.exp(lg) * 9000).round(0)
oil_buyer = tp.partner.isin(["India", "Spain", "Netherlands", "France", "United States", "Italy", "Canada", "Indonesia"])
tp["exports_usd_m"] = (tp.total_trade_usd_m * np.where(oil_buyer, 0.82, np.where(tp.region == "Africa", 0.55, 0.30))).round(0)
tp["imports_usd_m"] = (tp.total_trade_usd_m - tp.exports_usd_m).round(0)
tp.loc[tp.partner == "China", ["exports_usd_m", "imports_usd_m"]] = [2100, 11200]
tp["total_trade_usd_m"] = tp.exports_usd_m + tp.imports_usd_m
tp["oil_share_of_exports"] = np.where(oil_buyer, 0.88, np.where(tp.region == "Africa", 0.35, 0.55))
tp["avg_tariff_pct"] = np.where(tp.afcfta_member == 1, 9.0, 12.0).round(1)
save(tp, "ng_trade_partners.csv")

# =================================================================================================
# 12. firm_carbon_exposure.csv — fictional listed-company panel (Session 13)
# =================================================================================================
rng = np.random.default_rng(1313)
sect = [("Cement", 6, 900, 0.85, 0.10), ("Oil & gas upstream", 5, 1400, 0.55, 0.05), ("Power generation", 4, 380, 0.95, 0.0),
        ("Breweries & beverages", 5, 650, 0.06, 0.02), ("Banking", 6, 1200, 0.002, 0.0), ("Telecoms", 3, 2800, 0.03, 0.0),
        ("Agribusiness", 5, 300, 0.20, 0.15), ("Steel & metals", 3, 260, 0.75, 0.25), ("Solar & clean energy", 3, 90, 0.01, 0.0)]
rows = []
for s, n, rev0, inten, eu in sect:
    for i in range(n):
        rev = rev0 * rng.lognormal(0, .45)
        ebitda_m = {"Cement": .38, "Oil & gas upstream": .45, "Power generation": .30, "Banking": .40, "Telecoms": .42,
                    "Solar & clean energy": .22}.get(s, .18) * rng.normal(1, .12)
        scope1 = rev * inten * rng.lognormal(0, .25) * 1.0        # thousand tonnes CO2e (rev in ₦bn)
        scope2 = rev * {"Telecoms": .05, "Banking": .01, "Breweries & beverages": .03}.get(s, .04) * rng.lognormal(0, .3)
        rows.append([f"{s.split()[0][:4].upper()}{i + 1:02d}", s, round(rev, 1), round(rev * ebitda_m, 1),
                     round(scope1, 1), round(scope2, 1), round(max(0, eu * rng.normal(1, .3)), 3),
                     int(rng.random() < (0.6 if s in ("Banking", "Telecoms", "Cement") else 0.3))])
save(pd.DataFrame(rows, columns=["firm_id", "sector", "revenue_ngn_bn", "ebitda_ngn_bn", "scope1_kt_co2e",
                                 "scope2_kt_co2e", "eu_export_share", "publishes_tcfd"]), "firm_carbon_exposure.csv")

# =================================================================================================
# 13. country_risk_panel.csv — stylised indicators for eight African markets (Session 14)
# =================================================================================================
cr = pd.DataFrame([
    ["Nigeria", 230, 3.4, 24.0, 52, 7.0, 1.0, -1.9, -1.0, 0.24, 5.5],
    ["Ghana", 34, 4.0, 23.0, 77, 2.5, 3.5, 0.0, -0.1, 0.13, 6.0],
    ["Kenya", 56, 4.7, 5.5, 72, 4.0, -4.0, -0.8, -0.4, 0.22, 4.8],
    ["Egypt", 114, 3.0, 26.0, 90, 5.5, -5.5, -1.0, -0.6, 0.30, 7.5],
    ["South Africa", 63, 0.8, 4.5, 75, 4.8, -1.0, -0.3, 0.1, 0.38, 3.0],
    ["Côte d'Ivoire", 30, 6.2, 3.5, 58, 4.5, -4.5, -0.6, -0.4, 0.09, 3.8],
    ["Morocco", 38, 3.2, 1.5, 70, 6.0, -1.5, -0.3, -0.1, 0.12, 2.6],
    ["Ethiopia", 128, 7.0, 21.0, 40, 2.0, -3.5, -1.7, -0.5, 0.38, 8.5]],
    columns=["country", "population_m", "real_growth_pct", "inflation_pct", "public_debt_gdp_pct", "reserves_months_imports",
             "current_account_gdp_pct", "political_stability_wgi", "regulatory_quality_wgi", "fx_depreciation_12m",
             "eurobond_spread_pct"])
save(cr, "country_risk_panel.csv")

# =================================================================================================
# 14. miller_exposure_monthly.csv — a flour miller's FX & wheat exposure, 2019–2025 (Session 15)
# =================================================================================================
rng = np.random.default_rng(1515)
idx15 = pd.date_range("2019-01-01", "2025-12-01", freq="MS")
wheat = path([("2019-01", 220), ("2020-06", 200), ("2021-06", 260), ("2022-03", 420), ("2022-06", 400), ("2022-12", 330),
              ("2023-06", 260), ("2024-06", 240), ("2025-06", 230), ("2025-12", 225)], idx15, rng, 6)
fx15 = macro.set_index(pd.to_datetime(macro.date)).official_fx_ngn_usd.reindex(idx15).values
vol = 95 * (1 + 0.004 * np.arange(len(idx15))) * rng.lognormal(0, .04, len(idx15))      # thousand tonnes of flour
cost_usd = wheat * 1.32 * vol * 1000 / 1e6                                             # US$ m imported cost (incl. freight)
cost_ngn = cost_usd * fx15 / 1e3                                                         # ₦ bn
ngn_price = np.zeros(len(idx15)); p = None
for i in range(len(idx15)):  # price per kg of flour adjusts to costs with a lag and a cap
    target = 1.28 * cost_ngn[i] * 1e9 / (vol[i] * 1e6) * 1.15
    p = target if p is None else p + 0.35 * (target - p); ngn_price[i] = p
rev = ngn_price * vol * 1e6 / 1e9
save(pd.DataFrame({"month": idx15.strftime("%Y-%m-%d"), "wheat_usd_per_tonne": wheat.round(1),
                   "fx_ngn_usd": fx15.round(1), "flour_volume_kt": vol.round(2),
                   "imported_cost_usd_m": cost_usd.round(2), "imported_cost_ngn_bn": cost_ngn.round(2),
                   "flour_price_ngn_per_kg": ngn_price.round(1), "revenue_ngn_bn": rev.round(2),
                   "gross_margin_pct": (100 * (rev - cost_ngn * 1.12) / rev).round(1)}), "miller_exposure_monthly.csv")
print("done")
