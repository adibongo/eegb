# =============================================================================
# EEGB · Session 7 · National Accounts, Productivity & Welfare
# Replication script — regenerates every chart in the Session 7 deck (Python)
# Data: data/ng_gdp_sectors.csv (stylised real GDP by sector, ₦ tn, 2010–2025)
#       data/peer_income.csv   (stylised cross-country snapshot)
# Run from the project root:  python sessions/s07/python/s07_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
g = pd.read_csv("data/ng_gdp_sectors.csv")
peers = pd.read_csv("data/peer_income.csv")
sectors = ["agriculture", "oil_and_gas", "manufacturing", "construction", "trade", "ict_telecom",
           "finance_insurance", "real_estate", "public_admin", "other_services"]
nice = {s: s.replace("_and_", " & ").replace("_", " ").replace("ict telecom", "ICT & telecom").capitalize() for s in sectors}
nice["ict_telecom"] = "ICT & telecom"; nice["oil_and_gas"] = "Oil & gas"; nice["finance_insurance"] = "Finance & insurance"

# --- F01 · Real growth and who contributed: oil vs non-oil ------------------------------
g["growth"] = 100 * g.real_gdp_total.pct_change()
g["non_oil"] = g.real_gdp_total - g.oil_and_gas
g["contrib_oil"] = 100 * g.oil_and_gas.diff() / g.real_gdp_total.shift(1)
g["contrib_non_oil"] = 100 * g.non_oil.diff() / g.real_gdp_total.shift(1)
d = g.dropna(subset=["growth"])
fig, ax = plt.subplots()
ax.bar(d.year, d.contrib_non_oil, color=TEAL, label="Non-oil contribution")
ax.bar(d.year, d.contrib_oil, bottom=np.where(d.contrib_oil < 0, 0, d.contrib_non_oil), color=GOLD, label="Oil & gas contribution")
ax.plot(d.year, d.growth, color=NAVY, marker="o", lw=2.4, label="Real GDP growth")
ax.axhline(0, color=INK, lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%")); ax.legend(loc="upper right")
ax.set(title="Non-oil activity drives growth; oil mostly subtracts or adds a little",
       ylabel="Percentage points of real GDP growth")
note(fig); save(fig, "s07", "f01")

# --- F02 · How the economy's structure changed: shares 2010 vs 2025 ------------------------
sh = pd.DataFrame({y: 100 * g.loc[g.year == y, sectors].iloc[0] / g.loc[g.year == y, "real_gdp_total"].iloc[0] for y in (2010, 2025)})
sh = sh.sort_values(2025)
fig, ax = plt.subplots()
yy = np.arange(len(sh))
ax.barh(yy - .2, sh[2010], height=.4, color="#C9D2DC", label="2010")
ax.barh(yy + .2, sh[2025], height=.4, color=TEAL, label="2025")
for i, (a, b) in enumerate(zip(sh[2010], sh[2025])):
    ax.text(b + .3, i + .2, f"{b:.1f}%", va="center", fontsize=11, color=NAVY)
ax.set_yticks(yy, [nice[s] for s in sh.index]); ax.legend(loc="lower right")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%"))
ax.set(title="ICT and services grew their share; oil's share of real GDP fell sharply",
       xlabel="Share of real GDP (constant prices)")
note(fig); save(fig, "s07", "f02")

# --- F03 · Total GDP vs GDP per person ----------------------------------------------------
g["gdp_pc"] = g.real_gdp_total * 1e12 / (g.population_m * 1e6)     # ₦ per person, constant prices
idx = pd.DataFrame({"year": g.year, "Real GDP": 100 * g.real_gdp_total / g.real_gdp_total.iloc[0],
                    "Population": 100 * g.population_m / g.population_m.iloc[0],
                    "Real GDP per person": 100 * g.gdp_pc / g.gdp_pc.iloc[0]})
fig, ax = plt.subplots()
for col, c, lw in [("Real GDP", TEAL, 2.6), ("Population", SLATE, 2.2), ("Real GDP per person", RUST, 3)]:
    ax.plot(idx.year, idx[col], color=c, lw=lw, label=col)
    ax.text(2025.2, idx[col].iloc[-1], f"{idx[col].iloc[-1]:.0f}", color=c, fontsize=12, va="center", fontweight="bold")
ax.axhline(100, color=INK, lw=1, ls=":")
ax.legend(loc="upper left"); ax.set_xlim(2010, 2026.5)
ax.set(title="The economy grew; the average Nigerian's real income barely moved",
       ylabel="Index, 2010 = 100")
note(fig); save(fig, "s07", "f03")

# --- F04 · Nominal vs real GDP and the GDP deflator -------------------------------------------
g["deflator"] = 100 * g.nominal_gdp_old_base / g.real_gdp_total
fig, ax = plt.subplots()
ax.plot(g.year, g.nominal_gdp_old_base, color=GOLD, lw=3, label="Nominal GDP (current prices)")
ax.plot(g.year, g.real_gdp_total, color=NAVY, lw=3, label="Real GDP (2010 prices)")
ax.fill_between(g.year, g.real_gdp_total, g.nominal_gdp_old_base, color=GOLD, alpha=.15)
ax.text(2018.3, 160, "the gap is\ninflation", color=GOLD, fontsize=13, fontweight="bold")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:.0f}tn")); ax.legend(loc="upper left")
ax.set(title=f"Nominal GDP rose {g.nominal_gdp_old_base.iloc[-1] / g.nominal_gdp_old_base.iloc[0]:.1f}×; real GDP only {g.real_gdp_total.iloc[-1] / g.real_gdp_total.iloc[0]:.2f}×",
       ylabel="₦ trillion")
note(fig); save(fig, "s07", "f04")

# --- F05 · Rebasing: same economy, a bigger measured GDP ---------------------------------------
r = g[g.year >= 2019]
fig, ax = plt.subplots()
x = np.arange(len(r))
ax.bar(x - .2, r.nominal_gdp_old_base, width=.4, color="#C9D2DC", label="Old base")
ax.bar(x + .2, r.nominal_gdp_new_base, width=.4, color=TEAL, label="New (rebased) series")
uplift = 100 * (r.nominal_gdp_new_base / r.nominal_gdp_old_base - 1)
for i, u in enumerate(uplift):
    ax.text(i + .2, r.nominal_gdp_new_base.iloc[i] + 6, f"+{u:.0f}%", ha="center", fontsize=11, color=NAVY)
ax.set_xticks(x, r.year); ax.legend(loc="upper left")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:.0f}tn"))
ax.set(title="Rebasing captured activity the old survey missed — the economy did not grow overnight",
       ylabel="Nominal GDP, ₦ trillion")
note(fig, "Source: EEGB stylised teaching data. The size of the uplift is illustrative, not the official NBS revision."); save(fig, "s07", "f05")

# --- F06 · Market exchange rates vs purchasing power parity -----------------------------------
p = peers.sort_values("gdp_per_capita_ppp")
fig, ax = plt.subplots()
yy = np.arange(len(p))
ax.hlines(yy, p.gdp_per_capita_usd, p.gdp_per_capita_ppp, color="#C9D2DC", lw=4)
ax.scatter(p.gdp_per_capita_usd, yy, color=RUST, s=80, zorder=3, label="At market exchange rates")
ax.scatter(p.gdp_per_capita_ppp, yy, color=TEAL, s=80, zorder=3, label="At purchasing power parity (PPP)")
ax.set_yticks(yy, p.country)
for i, c in enumerate(p.country):
    if c == "Nigeria":
        ratio = p.gdp_per_capita_ppp.iloc[i] / p.gdp_per_capita_usd.iloc[i]
        ax.text(p.gdp_per_capita_ppp.iloc[i] + 400, i, f"PPP ≈ {ratio:.1f}× market", va="center", color=NAVY, fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p_: f"${v/1000:g}k")); ax.legend(loc="lower right")
ax.set(title="A dollar buys far more in Lagos than in New York: PPP corrects for that",
       xlabel="GDP per person, US$")
note(fig); save(fig, "s07", "f06")

# --- F07 · Informality and income ------------------------------------------------------------
fig, ax = plt.subplots()
ax.scatter(peers.gdp_per_capita_ppp, 100 * peers.informal_share_gdp, s=peers.population_m.clip(upper=400) * 2 + 40,
           color=TEAL, alpha=.6, edgecolor=NAVY)
for _, rw in peers.iterrows():
    ax.text(rw.gdp_per_capita_ppp + 300, 100 * rw.informal_share_gdp + .8, rw.country, fontsize=11,
            color=RUST if rw.country == "Nigeria" else INK, fontweight="bold" if rw.country == "Nigeria" else "normal")
X = np.column_stack([np.ones(len(peers)), peers.gdp_per_capita_ppp / 1000])
b = np.linalg.lstsq(X, 100 * peers.informal_share_gdp, rcond=None)[0]
xx = np.linspace(peers.gdp_per_capita_ppp.min(), peers.gdp_per_capita_ppp.max(), 50)
ax.plot(xx, b[0] + b[1] * xx / 1000, color=GOLD, lw=2.4, ls="--")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p_: f"${v/1000:g}k")); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p_: f"{v:.0f}%"))
ax.set(title=f"Poorer economies are more informal — about {abs(b[1]):.1f} pts less informality per $1k of PPP income",
       xlabel="GDP per person, PPP US$ (bubble size = population)", ylabel="Informal share of GDP")
note(fig); save(fig, "s07", "f07")

# --- F08 · The rule of 70: how long to double living standards? --------------------------------
rates = np.array([0.5, 1, 2, 3, 4, 5, 7])
fig, ax = plt.subplots()
yrs = np.log(2) / np.log(1 + rates / 100)
bars = ax.bar([f"{r:g}%" for r in rates], yrs, color=[RUST if r < 1.5 else TEAL for r in rates])
for bb, v in zip(bars, yrs):
    ax.text(bb.get_x() + bb.get_width() / 2, v + 2, f"{v:.0f} yrs", ha="center", fontsize=12, color=NAVY)
pc_growth = 100 * ((g.gdp_pc.iloc[-1] / g.gdp_pc.iloc[0]) ** (1 / (len(g) - 1)) - 1)
ax.set(title=f"At this data's {pc_growth:.1f}% a year per person, living standards double in about {np.log(2)/np.log(1+pc_growth/100):.0f} years",
       xlabel="Growth in real income per person, per year", ylabel="Years to double")
note(fig, "Years to double = ln 2 ÷ ln(1 + g) ≈ 70 ÷ g."); save(fig, "s07", "f08")

if __name__ == "__main__":
    print(d[["year", "growth", "contrib_oil", "contrib_non_oil"]].round(2).to_string())
    print(sh.round(1))
    print(idx.tail(1).round(1))
    print("pc growth %/yr", round(pc_growth, 2), "pc 2010", round(g.gdp_pc.iloc[0]), "pc 2025", round(g.gdp_pc.iloc[-1]))
    print("nominal x", round(g.nominal_gdp_old_base.iloc[-1] / g.nominal_gdp_old_base.iloc[0], 2), "real x", round(g.real_gdp_total.iloc[-1] / g.real_gdp_total.iloc[0], 2))
    print("deflator", g[["year", "deflator"]].round(0).tail(4).to_string())
    print("uplift", uplift.round(1).tolist())
    print("informality slope", b.round(2))
    print("avg growth 2016-2025", round(d[d.year >= 2016].growth.mean(), 2), "pop growth", round(100 * ((g.population_m.iloc[-1] / g.population_m.iloc[0]) ** (1 / 15) - 1), 2))
