# =============================================================================
# EEGB · Session 2 · Demand, Supply & Elasticity with Behavioural Insights
# Replication script — regenerates every chart in the Session 2 deck (Python)
# Data: data/fmcg_price_volume.csv (stylised weekly noodles sales, 3 regions, 2022–2025)
# Run from the project root:  python sessions/s02/python/s02_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
d = pd.read_csv("data/fmcg_price_volume.csv", parse_dates=["week"])
d["t"] = d.groupby("region").cumcount()                       # weeks since start (soaks up general inflation)
REG = {"Lagos": TEAL, "North": GOLD, "South-East": RUST}

# The demand model: log(units) on log(own price), log(competitor price), log(income), trend, region
def design(df):
    return np.column_stack([np.ones(len(df)), np.log(df.price_naira), np.log(df.competitor_price_naira),
                            np.log(df.income_index), df.t] + [(df.region == r).astype(float) for r in ["North", "South-East"]])
b = np.linalg.lstsq(design(d), np.log(d.units), rcond=None)[0]
own, cross, inc = b[1], b[2], b[3]
naive = np.polyfit(np.log(d.price_naira), np.log(d.units), 1)[0]
print(f"naive elasticity {naive:.2f} | own {own:.2f} cross {cross:.2f} income {inc:.2f}")

# --- F01 · A cost shock shifts supply ---------------------------------------------------
q = np.linspace(0, 10, 200)
dem = 900 - 50 * q
s0, s1 = 200 + 40 * q, 290 + 40 * q
q0, q1 = 700 / 90, 610 / 90
p0, p1 = 900 - 50 * q0, 900 - 50 * q1
fig, ax = plt.subplots()
ax.plot(q, dem, color=NAVY, lw=3, label="Demand")
ax.plot(q, s0, color=TEAL, lw=3, label="Supply before the flour shock")
ax.plot(q, s1, color=RUST, lw=3, ls="--", label="Supply after: costs up")
for qq, pp, c in [(q0, p0, TEAL), (q1, p1, RUST)]:
    ax.scatter(qq, pp, s=90, color=c, zorder=4)
    ax.plot([qq, qq], [0, pp], color=c, ls=":", lw=1.2); ax.plot([0, qq], [pp, pp], color=c, ls=":", lw=1.2)
ax.annotate("", xy=(2.5, 390), xytext=(2.5, 300), arrowprops=dict(arrowstyle="->", color=RUST, lw=2))
ax.text(2.6, 330, "costs up", color=RUST, fontsize=12)
ax.text(1.2, p1 + 120, f"New equilibrium: price up {100*(p1/p0-1):.0f}%,\nquantity down {100*(1-q1/q0):.0f}%", color=RUST, fontsize=12)
ax.set_xlim(0, 10); ax.set_ylim(0, 950); ax.set_xticks([]); ax.set_yticks([]); ax.legend(loc="upper right")
ax.set(title="A cost shock shifts supply up: the price rises by less than the cost, and volume falls",
       xlabel="Quantity of noodles", ylabel="Price")
save(fig, "s02", "f01")

# --- F02 · Three years of prices and volumes ----------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True)
for r, c in REG.items():
    g = d[d.region == r]
    axes[0].plot(g.week, g.price_naira, color=c, lw=2, label=r)
    axes[1].plot(g.week, g.units.rolling(4).mean() / 1000, color=c, lw=2, label=r)
axes[0].yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:,.0f}"))
axes[0].set_ylabel("Shelf price per pack"); axes[1].set_ylabel("Packs sold ('000, 4-week avg)")
axes[0].legend(ncol=3, loc="upper left"); axes[0].set_title("Prices more than tripled — yet volumes held up in two of three regions", loc="left")
save(fig, "s02", "f02")

# --- F03 · The naive picture: inflation hides the elasticity --------------------------------
fig, ax = plt.subplots()
for r, c in REG.items():
    g = d[d.region == r]; ax.scatter(g.price_naira, g.units / 1000, color=c, alpha=.55, s=22, label=r)
xs = np.linspace(d.price_naira.min(), d.price_naira.max(), 50)
a0 = np.polyfit(np.log(d.price_naira), np.log(d.units), 1)
ax.plot(xs, np.exp(np.polyval(a0, np.log(xs))) / 1000, color=NAVY, lw=3)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:,.0f}")); ax.legend()
ax.set(title=f"Naive view: price 'barely matters' (elasticity {naive:.2f}) — because everything else inflated too",
       xlabel="Shelf price per pack", ylabel="Packs sold per week ('000)")
ax.title.set_fontsize(14)
save(fig, "s02", "f03")

# --- F04 · The controlled estimates -----------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.6))
labs = ["Own-price elasticity", "Cross-price elasticity\n(competitor's price)", "Income elasticity", "Naive own-price\n(no controls)"]
vals = [own, cross, inc, naive]
cols = [RUST, TEAL, GOLD, "#B8C2CE"]
ax.barh(labs[::-1], vals[::-1], color=cols[::-1])
for i, v in enumerate(vals[::-1]):
    ax.text(v + (0.04 if v >= 0 else -0.04), i, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=13, color=NAVY)
ax.axvline(0, color=INK, lw=1); ax.set_xlim(-2, 1.6)
ax.set(title="Once inflation, rivals and income are held constant, customers are price-sensitive", xlabel="% change in packs sold for a 1% change")
save(fig, "s02", "f04")

# --- F05 · What a price rise does to revenue, by elasticity ------------------------------------
rise = np.linspace(0, 40, 81)
fig, ax = plt.subplots()
for e, c in [(-0.5, TEAL), (-1.0, SLATE), (own, RUST), (-2.5, NAVY)]:
    rev = ((1 + rise / 100) * (1 + rise / 100) ** e - 1) * 100
    ax.plot(rise, rev, color=c, lw=3 if c == RUST else 2, label=f"elasticity {e:.1f}" + (" (our estimate)" if c == RUST else ""))
ax.axhline(0, color=INK, lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.xaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="lower left")
ax.set(title="Raise price on an elastic product and revenue falls; on an inelastic one it rises",
       xlabel="Price increase (other prices unchanged)", ylabel="Change in revenue")
save(fig, "s02", "f05")
r20 = ((1.2) * 1.2 ** own - 1) * 100
print(f"revenue change for +20% price at own elasticity: {r20:.1f}%")

# --- F06 · Reference prices: rises above 'normal' hurt extra -------------------------------------
d["res"] = np.log(d.units) - design(d) @ b
d["ref"] = d.groupby("region").price_naira.transform(lambda s: s.shift(1).ewm(alpha=0.2, adjust=False).mean())
d["gap"] = np.log(d.price_naira / d.ref)
bins = [-1, 0, 0.05, 0.10, 1]; names = ["Below usual\n(promotions)", "0–5% above\nusual", "5–10% above\nusual", "More than 10%\nabove usual"]
dd = d.dropna(subset=["gap"]).copy(); dd["bin"] = pd.cut(dd.gap, bins, labels=names)
rb = dd.groupby("bin", observed=False).res.mean() * 100
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.bar(rb.index.astype(str), rb.values, color=[TEAL, SLATE, GOLD, RUST])
for i, v in enumerate(rb.values): ax.text(i, v + (0.4 if v >= 0 else -1.2), f"{v:+.1f}%", ha="center", fontsize=13, color=NAVY)
ax.axhline(0, color=INK, lw=1); ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.set_ylim(-10, 6)
ax.set(title="Shoppers punish prices well above what they are used to — beyond the normal elasticity",
       ylabel="Extra sales vs model prediction")
ax.title.set_fontsize(14)
save(fig, "s02", "f06")
print("reference-price residuals (%):", rb.round(1).to_dict())

# --- F07 · Promotions: the volume lift by region --------------------------------------------------
lift = d.groupby(["region", "promo"]).units.mean().unstack()
lift = (lift[1] / lift[0] - 1) * 100
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.bar(lift.index, lift.values, color=[REG[r] for r in lift.index])
for i, v in enumerate(lift.values): ax.text(i, v + 0.8, f"+{v:.0f}%", ha="center", fontsize=14, color=NAVY)
ax.yaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title="A 15% promotional discount lifts weekly volume by roughly a third", ylabel="Volume in promo weeks vs normal weeks")
save(fig, "s02", "f07")
print("promo lift %:", lift.round(1).to_dict())

# --- F08 · How much of a 40% flour-cost rise to pass on? ---------------------------------------------
P0, C0, flour_share = 500.0, 350.0, 0.45            # stylised: ₦500 pack, ₦350 unit cost, flour = 45% of cost
dc = C0 * flour_share * 0.40                          # extra cost per pack from a 40% flour rise
pt = np.linspace(0, 1, 51)                            # pass-through: 0 = absorb all, 1 = pass on fully
fig, ax = plt.subplots()
for e, lab, c in [(own, "Rivals hold their price (own elasticity)", RUST), (own + cross, "Rivals raise prices too (own + cross)", TEAL)]:
    P = P0 + pt * dc
    Q = (P / P0) ** e
    profit = (P - (C0 + dc)) * Q / (P0 - C0) * 100
    vol = (Q[-1] - 1) * 100
    ax.plot(pt * 100, profit, color=c, lw=3, label=lab)
    ax.text(101, profit[-1], f"{profit[-1]:.0f}%\n(volume {vol:+.0f}%)", color=c, fontsize=12, va="center")
    print(f"{lab}: absorb -> {profit[0]:.0f}%, full pass-through -> {profit[-1]:.0f}% of pre-shock profit, volume {vol:+.1f}%")
ax.axhline(100, color=SLATE, ls="--", lw=1); ax.text(2, 101.5, "profit before the shock", color=SLATE, fontsize=11)
ax.set_xlim(0, 122); ax.set_ylim(50, 108)
ax.xaxis.set_major_formatter(FuncFormatter(pct)); ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="lower right")
ax.set(title=f"Flour up 40% adds ₦{dc:.0f} a pack: absorbing it is the costliest choice",
       xlabel="Share of the cost increase passed into price", ylabel="Profit, % of pre-shock level")
save(fig, "s02", "f08")
