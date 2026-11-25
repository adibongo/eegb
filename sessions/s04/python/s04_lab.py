# =============================================================================
# EEGB · Session 4 LAB · Is the market too concentrated? (Python)
# Data (real): data/official/ng_mobile_market_shares.csv (NCC), platform_concentration.csv,
#              ng_nip_value.csv (NIBSS). Step 4 is an illustrative pricing model.
# Run from the project root, line by line (Ctrl/Cmd + Enter in RStudio or VS Code)
# =============================================================================
import pandas as pd
pd.set_option("display.width", 160); pd.set_option("display.max_columns", 10)

# ---- STEP 1 · Market shares and concentration, 2019–2025 ---------------------------------------
ms = pd.read_csv("data/official/ng_mobile_market_shares.csv")
print(ms[["period", "operator", "subscriptions_m", "share_pct"]].head(8))
tot = ms.groupby("period").subscriptions_m.transform("sum")
ms["share"] = ms.share_pct.fillna(100 * ms.subscriptions_m / tot)       # 2021: only counts are published
sh = ms.pivot(index="period", columns="operator", values="share")[["MTN", "Airtel", "Glo", "9mobile/T2"]]
conc = pd.DataFrame({"CR2": sh.apply(lambda r: r.nlargest(2).sum(), axis=1),   # top-two share
                     "HHI": (sh ** 2).sum(axis=1)})                            # sum of squared % shares
print(conc.round(0))

# ---- STEP 2 · Did MTN really grow from 39% to 51% in 2024? Look at the counts ----------------------
cnt = ms.pivot(index="period", columns="operator", values="subscriptions_m")[["MTN", "Airtel", "Glo", "9mobile/T2"]]
print((cnt.loc["2024-12"] - cnt.loc["2023-12"]).round(1))   # change in millions of lines, Dec 2023 → Dec 2024

# ---- STEP 3 · Merger screen: what would a merger do to the HHI? ---------------------------------------
def merger_screen(shares, a, b):
    post = shares.copy(); post[a] = shares[a] + shares[b]; post = post.drop(b)
    hhi0, hhi1 = (shares ** 2).sum(), (post ** 2).sum()
    flag = (hhi1 > 1800 and hhi1 - hhi0 > 100) or (post[a] > 30 and hhi1 - hhi0 > 100)
    return pd.Series({"HHI before": hhi0, "HHI after": hhi1, "change": hhi1 - hhi0,
                      "merged share %": post[a], "presumed harmful (US 2023 test)": flag})
latest = sh.loc["2025-09"]
print(pd.DataFrame({f"{a} + {b}": merger_screen(latest, a, b)
                    for a, b in [("Airtel", "Glo"), ("Glo", "9mobile/T2"), ("MTN", "9mobile/T2")]}).T)
# Note: change in HHI = 2 × share_a × share_b  (check it!)

# ---- STEP 4 · Monopoly pricing (illustrative): fee = 100 − Q, marginal cost ₦20 ------------------------
a, b, mc = 100, 1, 20
Qc, Pc = (a - mc) / b, mc                              # competition: price = marginal cost
Qm = (a - mc) / (2 * b); Pm = a - b * Qm               # monopoly: marginal revenue (a − 2bQ) = marginal cost
dwl = 0.5 * (Pm - mc) * (Qc - Qm)
elast = (1 / b) * Pm / Qm                              # |price elasticity| at the monopoly point
print(f"Competition: Q={Qc:.0f}m, fee ₦{Pc:.0f} | Monopoly: Q={Qm:.0f}m, fee ₦{Pm:.0f} | DWL ₦{dwl:,.0f}m")
print(f"Lerner index (P − MC)/P = {(Pm - mc) / Pm:.2f}  vs  1/|elasticity| = {1 / elast:.2f}")

# ---- STEP 5 · Platform markets: how concentrated? ------------------------------------------------------------
pc = pd.read_csv("data/official/platform_concentration.csv")
for mkt, g in pc.groupby("market", sort=False):
    lo = (g.share_pct ** 2).sum(); rest = max(0, 100 - g.share_pct.sum())
    print(f"{mkt:38s} HHI between {lo:,.0f} and {lo + rest ** 2:,.0f}")

# ---- STEP 6 · Growth of instant payments: nominal vs real vs dollars -------------------------------------------
nip = pd.read_csv("data/official/ng_nip_value.csv").set_index("year")
m = pd.read_csv("data/official/ng_official_monthly.csv", parse_dates=["date"]).set_index("date")
infl = m.cpi_headline_yoy.groupby(m.index.year).mean().loc[2019:2024]
price = pd.concat([pd.Series({2018: 1.0}), (1 + infl / 100).cumprod()])
fx = pd.read_csv("data/official/ng_worldbank_annual.csv").set_index("year").ngn_usd_avg
nip["real_2018_prices"] = nip.nip_value_ntn / price
nip["usd_bn"] = nip.nip_value_ntn * 1e3 / fx.loc[nip.index]
print(nip.drop(columns="source").round(1))

# ---- YOUR TURN ------------------------------------------------------------------------------------------------------
# (a) Recompute the HHI for Dec 2023 by hand from the four shares. Is the market 'highly concentrated'?
# (b) In Step 2, MTN LOST lines in 2024 yet its share rose 12 points. Explain in two sentences.
# (c) Which merger in Step 3 would a regulator block? Which might pass? Why might 'Glo + 9mobile/T2' still be good for customers?
# (d) If demand became MORE elastic (fee = 60 − 0.5Q), how would the monopoly fee change? Re-run Step 4.
# (e) Kenya's M-Pesa holds ~90% of mobile-money accounts, yet Kenya has near-universal inclusion. Is that market 'too concentrated'?
