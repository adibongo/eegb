# =============================================================================
# EEGB · Session 13 · Climate & Energy-Transition Economics
# Replication script — regenerates every chart in the Session 13 deck (Python)
# Data: data/firm_carbon_exposure.csv (40 fictional Nigerian listed companies, stylised)
# Run from the project root:  python sessions/s13/python/s13_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
f = pd.read_csv("data/firm_carbon_exposure.csv")
FX = 1500                                   # assumed ₦ per US$ for converting carbon prices
f["emissions_t"] = (f.scope1_kt_co2e + f.scope2_kt_co2e) * 1000

def carbon_cost_bn(emissions_t, usd_per_t):
    """Carbon bill in ₦ bn = tonnes × US$/tonne × ₦/US$ ÷ 1e9"""
    return emissions_t * usd_per_t * FX / 1e9

sec = f.groupby("sector").agg(revenue=("revenue_ngn_bn", "sum"), ebitda=("ebitda_ngn_bn", "sum"),
                              emissions_t=("emissions_t", "sum"), tcfd=("publishes_tcfd", "mean"), n=("firm_id", "count"))
sec["intensity"] = sec.emissions_t / (sec.revenue * 1000)          # tonnes CO2e per ₦ million of revenue
for p in (25, 50, 100):
    sec[f"cost_{p}_pct"] = 100 * carbon_cost_bn(sec.emissions_t, p) / sec.ebitda

# --- F01 · Emissions intensity by sector ------------------------------------------------------
s1 = sec.sort_values("intensity")
fig, ax = plt.subplots()
ax.barh(s1.index, s1.intensity, color=[RUST if v > 0.5 else TEAL for v in s1.intensity])
for i, v in enumerate(s1.intensity): ax.text(v + .02, i, f"{v:.2f}", va="center", fontsize=12)
ax.set(title="Carbon intensity differs a hundred-fold across sectors",
       xlabel="Tonnes of CO₂e per ₦1 million of revenue (scope 1 + 2)")
note(fig); save(fig, "s13", "f01")

# --- F02 · Carbon bill as a share of EBITDA at three prices --------------------------------------
s2 = sec.sort_values("cost_50_pct")
fig, ax = plt.subplots(figsize=(10, 6))
y = np.arange(len(s2)); h = .27
for k, (p, c) in enumerate([(25, SKY), (50, TEAL), (100, NAVY)]):
    ax.barh(y + (k - 1) * h, s2[f"cost_{p}_pct"], height=h, color=c, label=f"US${p} per tonne")
ax.set_yticks(y, s2.index); ax.xaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="lower right")
ax.set(title="At US$100 a tonne, steel and power would lose half or more of EBITDA; cement a third",
       xlabel="Carbon bill as % of EBITDA (no pass-through, no abatement)")
note(fig, f"Assumes ₦{FX:,}/US$. Source: EEGB stylised teaching data (data/). Not official statistics."); save(fig, "s13", "f02")

# --- F03 · Firm by firm: who is exposed? ---------------------------------------------------------
f["intensity"] = f.emissions_t / (f.revenue_ngn_bn * 1000)
f["margin"] = 100 * f.ebitda_ngn_bn / f.revenue_ngn_bn
f["cost50_pct"] = 100 * carbon_cost_bn(f.emissions_t, 50) / f.ebitda_ngn_bn
hot = f.cost50_pct > 20
fig, ax = plt.subplots()
ax.scatter(f.intensity[~hot], f.margin[~hot], s=f.revenue_ngn_bn[~hot] / 8, color=TEAL, alpha=.65, label="Carbon bill < 20% of EBITDA")
ax.scatter(f.intensity[hot], f.margin[hot], s=f.revenue_ngn_bn[hot] / 8, color=RUST, alpha=.75, label="Carbon bill > 20% of EBITDA")
ax.set_xscale("log")
ax.legend(loc="lower left")
ax.set(title=f"{hot.sum()} of 40 firms would lose more than a fifth of EBITDA at US$50 a tonne",
       xlabel="Carbon intensity (t CO₂e per ₦m revenue, log scale)", ylabel="EBITDA margin (%)")
note(fig); save(fig, "s13", "f03")

# --- F04 · The case: cement vs solar as the carbon price rises -------------------------------------
prices = np.arange(0, 151, 5)
fig, ax = plt.subplots()
for s, c in [("Cement", RUST), ("Steel & metals", GOLD), ("Breweries & beverages", SLATE), ("Solar & clean energy", TEAL)]:
    r = sec.loc[s]
    ax.plot(prices, 100 * (1 - carbon_cost_bn(r.emissions_t, prices) / r.ebitda), color=c, lw=3, label=s)
ax.axhline(100, color=SLATE, lw=1, ls=":")
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.set_ylim(0, 105); ax.legend(loc="lower left")
ax.set(title="Same carbon price, very different fates: EBITDA left after paying the carbon bill",
       xlabel="Carbon price (US$ per tonne CO₂e)", ylabel="EBITDA remaining (% of today)")
note(fig); save(fig, "s13", "f04")

# --- F05 · CBAM: the EU's border carbon charge on cement and steel exports ----------------------------
EU_PRICE = 80                          # assumed EU carbon price, US$ per tonne
cb = f[f.sector.isin(["Cement", "Steel & metals"])].copy()
cb["cbam_bn"] = carbon_cost_bn(cb.scope1_kt_co2e * 1000 * cb.eu_export_share, EU_PRICE)
cb["cbam_pct_ebitda"] = 100 * cb.cbam_bn / cb.ebitda_ngn_bn
cb["cbam_pct_eu_sales"] = 100 * cb.cbam_bn / (cb.revenue_ngn_bn * cb.eu_export_share)
cb = cb.sort_values("cbam_pct_eu_sales")
fig, ax = plt.subplots()
ax.barh(cb.firm_id, cb.cbam_pct_eu_sales, color=[GOLD if s == "Steel & metals" else RUST for s in cb.sector])
for i, (v, e) in enumerate(zip(cb.cbam_pct_eu_sales, cb.cbam_pct_ebitda)):
    ax.text(v + .3, i, f"{v:.0f}% of EU sales  ({e:.1f}% of total EBITDA)", va="center", fontsize=10.5)
ax.set_xlim(0, cb.cbam_pct_eu_sales.max() * 1.6)
ax.xaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title="CBAM would eat a large slice of EU export revenue — a small slice of total profit",
       xlabel=f"Border charge as % of EU export revenue (EU carbon price US${EU_PRICE}/t, no carbon price paid at home)")
note(fig, "Rust = cement, gold = steel. Embedded emissions approximated by EU export share × scope 1. EEGB stylised data.")
save(fig, "s13", "f05")

# --- F06 · Who discloses? ---------------------------------------------------------------------------
s6 = sec.sort_values("tcfd")
fig, ax = plt.subplots()
ax.barh(s6.index, 100 * s6.tcfd, color=TEAL)
for i, (v, n) in enumerate(zip(s6.tcfd, s6.n)): ax.text(100 * v + 1, i, f"{v:.0%} of {n} firms", va="center", fontsize=11)
ax.set_xlim(0, 115); ax.xaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title=f"Only {f.publishes_tcfd.mean():.0%} of firms publish TCFD-style climate disclosures",
       xlabel="Share of firms publishing TCFD-aligned climate reports")
note(fig); save(fig, "s13", "f06")

# --- F07 · Can cement pass the cost on? ---------------------------------------------------------------
cem = sec.loc["Cement"]; cost = carbon_cost_bn(cem.emissions_t, 50)
pt = np.linspace(0, 1, 21)
fig, ax = plt.subplots()
for eps, c, lab in [(0.3, TEAL, "Demand elasticity −0.3 (few substitutes)"), (0.8, GOLD, "−0.8"), (1.5, RUST, "−1.5 (imports compete)")]:
    price_rise = pt * cost / cem.revenue                   # % price increase needed to pass through
    lost_volume = eps * price_rise                         # % volume lost
    hit = (1 - pt) * cost + lost_volume * 0.5 * cem.revenue  # 50% contribution margin on lost volume
    ax.plot(100 * pt, 100 * hit / cem.ebitda, color=c, lw=3, label=lab)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper right")
ax.set(title="Passing the carbon cost on helps — unless customers can switch",
       xlabel="Share of the US$50/t carbon bill passed on in prices (%)", ylabel="Fall in cement EBITDA")
note(fig, "Illustrative: 50% contribution margin on lost volume. EEGB stylised teaching data.")
save(fig, "s13", "f07")

# --- F08 · A marginal abatement cost curve for a cement plant (illustrative) -----------------------------
opts = pd.DataFrame({"option": ["Waste-heat recovery", "Clinker substitution", "Captive solar power", "Alternative fuels (biomass, waste)",
                                "Kiln efficiency upgrade", "Carbon capture (CCS)"],
                     "cost_usd_t": [-25, -10, 5, 20, 35, 110], "abatement_kt": [40, 110, 30, 70, 45, 200]})
x0 = 0
fig, ax = plt.subplots()
for _, r in opts.iterrows():
    ax.bar(x0, r.cost_usd_t, width=r.abatement_kt, align="edge", color=TEAL if r.cost_usd_t < 0 else (GOLD if r.cost_usd_t < 50 else RUST),
           edgecolor="white")
    ax.text(x0 + r.abatement_kt / 2, max(r.cost_usd_t, 0) + 4, r.option, ha="center", va="bottom", fontsize=10,
            rotation=0 if r.abatement_kt > 90 else 90)
    x0 += r.abatement_kt
ax.axhline(50, color=NAVY, ls="--", lw=1.5); ax.text(x0, 53, "carbon price US$50", ha="right", color=NAVY, fontsize=11)
ax.axhline(0, color=INK, lw=1)
ax.set_ylim(-45, 135)
ax.set(title="Cut the cheap tonnes first: below the carbon price, abatement pays",
       xlabel="Cumulative tonnes abated (thousand t CO₂e a year)", ylabel="Cost per tonne abated (US$)")
note(fig, "Illustrative abatement options for one 700 kt cement plant; costs are teaching assumptions, not engineering estimates.")
save(fig, "s13", "f08")

# --- key numbers for the slides --------------------------------------------------------------------------
pd.set_option("display.width", 160)
print(sec[["n", "intensity", "cost_25_pct", "cost_50_pct", "cost_100_pct", "tcfd"]].round(2).sort_values("intensity"))
print("firms >20% EBITDA at $50:", hot.sum(), "| overall TCFD share:", round(f.publishes_tcfd.mean(), 3))
print(cb[["firm_id", "sector", "eu_export_share", "cbam_bn", "cbam_pct_ebitda", "cbam_pct_eu_sales"]].round(2).to_string(index=False))
print("cement carbon bill at $50 (N bn):", round(cost, 1), "| as % revenue:", round(100 * cost / cem.revenue, 2), "| % EBITDA:", round(100 * cost / cem.ebitda, 1))
abate_below_50 = opts.loc[opts.cost_usd_t < 50, "abatement_kt"].sum()
print("MACC: abatement below $50:", abate_below_50, "of", opts.abatement_kt.sum())
