# =============================================================================
# EEGB · Session 4 · Market Structure, Platforms & Competition Policy
# Replication script — regenerates every chart in the Session 4 deck (Python)
# Data: data/payments_market_shares.csv (stylised; fictional providers except the 'Banks' aggregate)
# Run from the project root:  python sessions/s04/python/s04_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
p = pd.read_csv("data/payments_market_shares.csv")
ORDER = ["Banks (app & USSD)", "KoboLink", "SwiftNaira", "AgentPay", "PayFast", "Others"]
COL = dict(zip(ORDER, [SLATE, TEAL, GOLD, OLIVE, SKY, "#C9D1DA"]))
sh = p.pivot(index="year", columns="provider", values="share_of_value_pct")[ORDER]

# --- F01 · Market shares over time ---------------------------------------------------------------
fig, ax = plt.subplots()
ax.stackplot(sh.index, sh.T.values, colors=[COL[k] for k in ORDER], labels=ORDER, alpha=.95)
ax.set_xlim(2016, 2025); ax.set_ylim(0, 100); ax.yaxis.set_major_formatter(FuncFormatter(pct))
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3)
ax.set(title="Banks' share of mobile-payment value fell from 78% to 28% as fintech platforms grew", ylabel="Share of payment value")
note(fig); save(fig, "s04", "f01")

# --- F02 · Concentration (HHI) under two market definitions ------------------------------------------
hhi_agg = (sh ** 2).sum(axis=1)
# If the 'Banks' block were really ~10 banks of equal size, each would hold a tenth of that share
hhi_split = (sh.drop(columns="Banks (app & USSD)") ** 2).sum(axis=1) + 10 * (sh["Banks (app & USSD)"] / 10) ** 2
fig, ax = plt.subplots()
ax.plot(hhi_agg.index, hhi_agg, "o-", color=NAVY, lw=3, label="Banks counted as one block")
ax.plot(hhi_split.index, hhi_split, "o-", color=TEAL, lw=3, label="Banks counted as ~10 separate firms")
ax.axhspan(2500, 7000, color=RUST, alpha=.08); ax.axhspan(1500, 2500, color=GOLD, alpha=.10)
ax.text(2016.1, 2600, "highly concentrated (> 2,500)", color=RUST, fontsize=11)
ax.text(2016.1, 1600, "moderately concentrated (1,500–2,500)", color=GOLD, fontsize=11)
ax.set_ylim(0, 6800); ax.legend(loc="upper right")
ax.set(title="Concentration depends on how you define the market", ylabel="Herfindahl–Hirschman Index (HHI)")
note(fig, "Thresholds: US 2010 merger guidelines (the 2023 guidelines use lower cut-offs). Source: EEGB stylised teaching data.")
save(fig, "s04", "f02")
print("HHI agg:", hhi_agg.round(0).to_dict()); print("HHI split:", hhi_split.round(0).to_dict())

# --- F03 · Two-sided growth: users and merchants -------------------------------------------------------
tot = p.groupby("year")[["active_users_m", "merchants_m"]].sum()
slope = np.polyfit(np.log(tot.active_users_m), np.log(tot.merchants_m), 1)[0]
fig, ax = plt.subplots()
ax.plot(tot.active_users_m, tot.merchants_m, "o-", color=TEAL, lw=3, ms=9)
for y, r in tot.iterrows():
    if y in (2016, 2019, 2022, 2025): ax.annotate(str(y), (r.active_users_m, r.merchants_m), xytext=(-12, 10), textcoords="offset points", fontsize=12, color=NAVY)
ax.set(title=f"Each 1% more users came with about {slope:.1f}% more merchants: the two sides feed each other",
       xlabel="Active users (million)", ylabel="Merchants accepting mobile payments (million)")
ax.title.set_fontsize(14)
note(fig); save(fig, "s04", "f03")
print(f"users {tot.active_users_m.iloc[0]:.1f}->{tot.active_users_m.iloc[-1]:.1f}m, merchants {tot.merchants_m.iloc[0]:.2f}->{tot.merchants_m.iloc[-1]:.2f}m, slope {slope:.2f}")

# --- F04 · Winner-takes-most inside the fintech segment -------------------------------------------------------
FIN = ["KoboLink", "SwiftNaira", "AgentPay", "PayFast"]
fin = sh[FIN].div(sh[FIN].sum(axis=1), axis=0) * 100
fig, ax = plt.subplots()
for k in FIN:
    ax.plot(fin.index, fin[k], "o-", color=COL[k], lw=3 if k == "KoboLink" else 2, label=k)
    ax.text(2025.15, fin[k].iloc[-1], f"{fin[k].iloc[-1]:.0f}%", color=COL[k], va="center", fontsize=12, fontweight="bold")
ax.set_xlim(2016, 2025.8); ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper center", bbox_to_anchor=(.5, -.08), ncol=4)
ax.set(title="Among the fintechs, the fastest grower pulled away: a 'winner-takes-most' pattern", ylabel="Share of fintech payment value")
note(fig); save(fig, "s04", "f04")
print("fintech-segment shares 2016:", fin.iloc[0].round(0).to_dict(), "2025:", fin.iloc[-1].round(0).to_dict())

# --- F05 · Market power: the leader's share and its fees ------------------------------------------------------
k = p[p.provider == "KoboLink"].set_index("year")
oth = p[p.provider != "KoboLink"].groupby("year").avg_fee_pct.mean()
fig, ax1 = plt.subplots()
ax1.bar(k.index, k.share_of_value_pct, color=TEAL, alpha=.35, label="KoboLink market share (left)")
ax1.yaxis.set_major_formatter(FuncFormatter(pct)); ax1.set_ylabel("Market share")
ax2 = ax1.twinx()
ax2.plot(k.index, k.avg_fee_pct, "o-", color=RUST, lw=3, label="KoboLink average fee (right)")
ax2.plot(oth.index, oth, "o--", color=SLATE, lw=2, label="Others' average fee (right)")
ax2.set_ylim(0.4, 0.8); ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, q: f"{v:.2f}%")); ax2.grid(False)
ax2.spines["right"].set_visible(True); ax2.set_ylabel("Average fee, % of transaction value")
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left")
ax1.set_title("The leader entered cheap — then nudged fees up once it was the biggest network", loc="left")
note(fig); save(fig, "s04", "f05")
print("KoboLink fee:", k.avg_fee_pct.round(3).to_dict())

# --- F06 · The cost of market power: monopoly vs competition --------------------------------------------------
q = np.linspace(0, 10, 300); D = 10 - q; MR = 10 - 2 * q; MC = np.full_like(q, 2.0)
qc, pc = 8, 2; qm, pm = 4, 6
fig, ax = plt.subplots()
ax.plot(q, D, color=NAVY, lw=3, label="Demand"); ax.plot(q[q <= 5], MR[q <= 5], color=SLATE, lw=2, ls="--", label="Marginal revenue")
ax.plot(q, MC, color=TEAL, lw=3, label="Marginal cost")
ax.fill_between([0, qm], pm, pc, color=GOLD, alpha=.35, label="Transferred from customers to the monopolist")
qq = np.linspace(qm, qc, 50); ax.fill_between(qq, 10 - qq, 2, color=RUST, alpha=.45, label="Deadweight loss: trades that never happen")
for x, y, t, c in [(qc, pc, "Competition", TEAL), (qm, pm, "Monopoly", RUST)]:
    ax.scatter(x, y, s=80, color=c, zorder=5); ax.text(x + .15, y + .25, t, color=c, fontsize=12, fontweight="bold")
ax.set_xlim(0, 10.5); ax.set_ylim(0, 10.5); ax.set_xticks([]); ax.set_yticks([]); ax.legend(loc="upper right", fontsize=11)
ax.set(title="A monopolist sells less at a higher price — and some value is simply lost", xlabel="Quantity", ylabel="Price")
save(fig, "s04", "f06")
