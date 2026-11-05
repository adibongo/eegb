# =============================================================================
# EEGB · Session 12 · Trade, Supply Chains & Industrial Policy
# Replication script — regenerates every chart in the Session 12 deck (Python)
# Data: data/ng_trade_partners.csv (stylised Nigerian trade with 30 partners, US$ m)
# Run from the project root:  python sessions/s12/python/s12_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
t = pd.read_csv("data/ng_trade_partners.csv")
usd_m = FuncFormatter(lambda v, p: f"${v/1000:.1f}bn" if abs(v) >= 1000 else f"${v:,.0f}m")

# --- F01 · Who Nigeria trades with ---------------------------------------------------
top = t.nlargest(12, "total_trade_usd_m").iloc[::-1]
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top.partner, top.exports_usd_m, color=TEAL, label="Nigeria's exports")
ax.barh(top.partner, -top.imports_usd_m, color=GOLD, label="Nigeria's imports")
ax.axvline(0, color=INK, lw=1)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"${abs(v)/1000:.0f}bn"))
ax.legend(loc="lower left")
ax.set(title="Oil buyers in Europe, Asia and America; manufactured goods from China",
       xlabel="← imports    |    exports →  (US$, stylised year)")
note(fig); save(fig, "s12", "f01")

# --- F02 · Gravity in one picture ----------------------------------------------------
fig, ax = plt.subplots()
af = t.region == "Africa"
for mask, col, lab in [(~af, NAVY, "Rest of world"), (af, GOLD, "Africa (AfCFTA)")]:
    ax.scatter(t.distance_km[mask], t.total_trade_usd_m[mask], s=np.sqrt(t.partner_gdp_usd_bn[mask]) * 6,
               color=col, alpha=.75, label=lab, edgecolor="white")
for _, r in t[t.partner.isin(["China", "United States", "India", "Ghana", "Benin", "South Africa", "Kenya", "Chad"])].iterrows():
    ax.annotate(r.partner, (r.distance_km, r.total_trade_usd_m), xytext=(6, 4), textcoords="offset points", fontsize=11)
ax.set_xscale("log"); ax.set_yscale("log")
ax.yaxis.set_major_formatter(usd_m); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:,.0f} km"))
ax.legend(loc="lower left")
ax.set(title="Big economies trade more; distant ones trade less (bubble = partner GDP)",
       xlabel="Distance from Lagos (log scale)", ylabel="Total trade with Nigeria (log scale)")
note(fig); save(fig, "s12", "f02")

# --- F03 · The gravity regression ------------------------------------------------------
X = np.column_stack([np.ones(len(t)), np.log(t.partner_gdp_usd_bn), np.log(t.distance_km), t.common_language, t.landlocked])
y = np.log(t.total_trade_usd_m)
b, *_ = np.linalg.lstsq(X, y, rcond=None)
pred = X @ b; r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
names = ["Partner GDP\n(+1%)", "Distance\n(+1%)", "Shared language\n(yes vs no)", "Landlocked\n(yes vs no)"]
effects = [b[1], b[2], (np.exp(b[3]) - 1) * 100, (np.exp(b[4]) - 1) * 100]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1]})
axes[0].bar(names[:2], effects[:2], color=[TEAL, RUST])
for i, v in enumerate(effects[:2]): axes[0].text(i, v / 2, f"{v:+.2f}%", ha="center", va="center", color="white", fontsize=14, fontweight="bold")
axes[0].axhline(0, color=INK, lw=1); axes[0].set_title("Elasticities: % change in trade", fontsize=13)
axes[1].bar(names[2:], effects[2:], color=[TEAL2, RUST])
for i, v in enumerate(effects[2:]): axes[1].text(i, v / 2, f"{v:+.0f}%", ha="center", va="center", color="white", fontsize=14, fontweight="bold")
axes[1].axhline(0, color=INK, lw=1); axes[1].set_title("Shifts: % difference in trade", fontsize=13)
fig.suptitle(f"Gravity model of Nigeria's trade (R² = {r2:.2f}): size pulls, distance pushes", x=0.01, ha="left",
             fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig); save(fig, "s12", "f03")

# --- F04 · Actual vs predicted: where is trade 'missing'? -----------------------------------
t["predicted"] = np.exp(pred)
t["ratio"] = t.total_trade_usd_m / t.predicted
a = t[af].sort_values("ratio")
fig, ax = plt.subplots()
cols = [RUST if r < 1 else TEAL for r in a.ratio]
ax.barh(a.partner, a.ratio, color=cols)
ax.axvline(1, color=INK, lw=1.2, ls="--")
for i, (p, r) in enumerate(zip(a.partner, a.ratio)): ax.text(r + 0.03, i, f"{r:.2f}×", va="center", fontsize=11)
ax.set(title="African partners: actual trade vs what gravity predicts",
       xlabel="Actual ÷ predicted trade  (below 1 = trading less than size and distance suggest)")
note(fig); save(fig, "s12", "f04")

# --- F05 · How concentrated are exports? -------------------------------------------------
oil = (t.exports_usd_m * t.oil_share_of_exports).sum(); non = (t.exports_usd_m * (1 - t.oil_share_of_exports)).sum()
reg = t.assign(nonoil=t.exports_usd_m * (1 - t.oil_share_of_exports)).groupby("region").nonoil.sum().sort_values()
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
axes[0].pie([oil, non], labels=[f"Oil & gas\n{oil/(oil+non):.0%}", f"Non-oil\n{non/(oil+non):.0%}"], colors=[NAVY, GOLD],
            startangle=90, wedgeprops=dict(width=.42, edgecolor="white"), textprops=dict(fontsize=13))
axes[0].set_title("What Nigeria exports", fontsize=13)
axes[1].barh(reg.index, reg.values, color=TEAL)
for i, v in enumerate(reg.values): axes[1].text(v + 20, i, f"${v:,.0f}m", va="center", fontsize=11)
axes[1].set_title("Where non-oil exports go", fontsize=13); axes[1].xaxis.set_major_formatter(usd_m)
fig.suptitle("One commodity dominates exports — Africa is already the No. 2 non-oil market", x=0.01, ha="left",
             fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig); save(fig, "s12", "f05")

# --- F06 · Supply-chain concentration on the import side ------------------------------------
imp = t.set_index("partner").imports_usd_m.sort_values(ascending=False)
share = imp / imp.sum() * 100
hhi = (share ** 2).sum()
top8 = share.head(8).iloc[::-1]
fig, ax = plt.subplots()
ax.barh(top8.index, top8.values, color=[RUST if p == "China" else SLATE for p in top8.index])
for i, v in enumerate(top8.values): ax.text(v + .5, i, f"{v:.0f}%", va="center", fontsize=12)
ax.xaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title=f"One country supplies {share.iloc[0]:.0f}% of imports (HHI = {hhi:,.0f}: highly concentrated)",
       xlabel="Share of Nigeria's imports")
note(fig); save(fig, "s12", "f06")

# --- F07 · AfCFTA: what a tariff cut could do -------------------------------------------------
sigma = 4.0                       # trade elasticity: a common estimate in the literature is about 3–6
tariffs = np.linspace(0, 9, 10)
uplift = ((1 + 0.09) / (1 + tariffs / 100)) ** sigma - 1
af_trade = t[af].total_trade_usd_m.sum()
fig, ax = plt.subplots()
ax.plot(tariffs, af_trade * (1 + uplift), color=TEAL, lw=3)
ax.scatter([9, 0], [af_trade, af_trade * (1 + uplift[0])], color=[SLATE, GOLD], s=90, zorder=3)
ax.annotate(f"Today: ~9% tariffs\n${af_trade:,.0f}m", (9, af_trade), xytext=(6.3, af_trade * 1.18), fontsize=12,
            arrowprops=dict(arrowstyle="->", color=SLATE))
ax.annotate(f"Zero tariffs: +{uplift[0]:.0%}\n${af_trade*(1+uplift[0]):,.0f}m", (0, af_trade * (1 + uplift[0])),
            xytext=(3.2, af_trade * 1.36), fontsize=12, arrowprops=dict(arrowstyle="->", color=GOLD))
ax.set_ylim(af_trade * 0.95, af_trade * 1.5)
ax.invert_xaxis(); ax.yaxis.set_major_formatter(usd_m)
ax.set(title="Cutting tariffs helps — but roads, borders and payments matter as much",
       xlabel="Average tariff on intra-African trade (%)", ylabel="Nigeria's trade with African partners")
note(fig, "Illustrative: trade proportional to (1 + tariff)^-4. Source: EEGB stylised teaching data. Not official statistics.")
save(fig, "s12", "f07")

# --- key numbers for the slides -----------------------------------------------------------------
print(f"coef: const {b[0]:.2f} gdp {b[1]:.2f} dist {b[2]:.2f} lang {b[3]:.2f} ({effects[2]:+.0f}%) land {b[4]:.2f} ({effects[3]:+.0f}%) R2 {r2:.2f}")
print(f"oil share of exports {oil/(oil+non):.1%}; non-oil exports ${non:,.0f}m; africa non-oil ${reg['Africa']:,.0f}m")
print(f"import HHI {hhi:,.0f}; China share {share['China']:.1f}%; top3 share {share.head(3).sum():.1f}%")
print(f"africa total trade ${af_trade:,.0f}m = {af_trade/t.total_trade_usd_m.sum():.1%} of total; uplift at zero tariff {uplift[0]:.1%}")
print(a[["partner", "total_trade_usd_m", "predicted", "ratio"]].round(2).to_string(index=False))
print(f"total trade ${t.total_trade_usd_m.sum():,.0f}m exports ${t.exports_usd_m.sum():,.0f}m imports ${t.imports_usd_m.sum():,.0f}m")
