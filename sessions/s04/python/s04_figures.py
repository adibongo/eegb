# =============================================================================
# EEGB · Session 4 · Market Structure, Platforms & Competition Policy
# Replication script — regenerates every chart in the Session 4 deck (Python)
# Data (real, with the source on every row):
#   data/official/ng_mobile_market_shares.csv  — NCC year-end operator subscriptions and shares
#   data/official/ng_nip_value.csv             — NIBSS Instant Payment (NIP) value by year
#   data/official/platform_concentration.csv   — market shares in four platform markets
#   data/official/findex_accounts.csv          — World Bank Global Findex (refresh: tools/fetch_official_data.py)
#   data/official/ng_official_monthly.csv, ng_worldbank_annual.csv — CPI and ₦/$ (Session 1 files)
# F03 and F04 are ILLUSTRATIVE models, not data.
# Run from the project root:  python sessions/s04/python/s04_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
OPS = ["MTN", "Airtel", "Glo", "9mobile/T2"]; COL = {"MTN": GOLD, "Airtel": RUST, "Glo": TEAL, "9mobile/T2": OLIVE}

# ---- NCC shares: use published shares; where only counts are published, compute them --------------
ms = pd.read_csv("data/official/ng_mobile_market_shares.csv")
tot = ms.groupby("period").subscriptions_m.transform("sum")
ms["share"] = ms.share_pct.fillna(100 * ms.subscriptions_m / tot)
sh = ms.pivot(index="period", columns="operator", values="share")[OPS]
hhi = (sh ** 2).sum(axis=1)
print("HHI by period:\n", hhi.round(0))

# --- F01 · Nigeria's mobile market: shares and the HHI --------------------------------------
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.5, 6.6), gridspec_kw={"width_ratios": [1.5, 1]})
x = np.arange(len(sh)); lab = [p.replace("-12", "\nDec").replace("2025-09", "2025\nSep") for p in sh.index]
lab = [f"{l.split(chr(10))[1]} {l.split(chr(10))[0]}" if "\n" in l else l for l in lab]
for op in OPS:
    ax.plot(x, sh[op], "-o", color=COL[op], lw=2.6, label=op)
    ax.text(x[-1] + .15, sh[op].iloc[-1], f"{sh[op].iloc[-1]:.0f}%", color=COL[op], va="center", fontsize=12, fontweight="bold")
ax.axvspan(4.5, 5.5, color=SLATE, alpha=.12)
ax.text(5, 23, "NIN-SIM barring\nand a reporting\ncorrection", ha="center", fontsize=10, color=INK)
ax.set_xticks(x, [l.replace(" ", "\n") for l in lab], fontsize=11); ax.set_ylim(0, 62); ax.yaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title="Share of active mobile subscriptions", ylabel="% of all lines"); ax.legend(loc="upper left", ncol=4, fontsize=11)
ax2.bar(x, hhi, color=[NAVY] * 5 + [RUST, RUST])
for xi, v in zip(x, hhi): ax2.text(xi, v + 60, f"{v:,.0f}", ha="center", fontsize=11)
ax2.axhline(1800, color=GOLD, ls="--", lw=1.6); ax2.text(-.4, 4500, "Dashed line = 1,800, the US merger-guidelines\nthreshold for a highly concentrated market (2023)", fontsize=9.5, color=INK)
ax2.set_xticks(x, [l.split(" ")[1] if l.startswith("Dec") else "Sep\n2025" for l in lab], fontsize=10.5); ax2.set_ylim(0, 5100)
ax2.set(title="Concentration (HHI)")
fig.suptitle("Nigeria's mobile market: MTN and Airtel now hold 86% of active lines", x=0.01, ha="left", fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout()
note(fig, "Source: NCC year-end subscriber reports (2019–2024); NCC data via ThisDay for Sep 2025. 2021 shares computed from operator counts.\n"
          "The Dec 2024 drop reflects NIN-SIM barring and a 'major discrepancy rectified by an MNO' (NCC 2024 report).")
save(fig, "s04", "f01")

# --- F02 · How concentrated are platform markets? (HHI from published shares) ----------------
pc = pd.read_csv("data/official/platform_concentration.csv")
rows = []
for mkt, g in pc.groupby("market", sort=False):
    known = (g.share_pct ** 2).sum(); rest = max(0, 100 - g.share_pct.sum())
    rows.append((f"{mkt}\n({g.period.iloc[0]})", known, known + rest ** 2))   # lower and upper bound
rows += [("Nigeria mobile telephony (lines)\n(2023-12, before the break)", hhi["2023-12"], hhi["2023-12"]),
         ("Benchmark: 10 equal firms", 1000, 1000), ("Benchmark: 5 equal firms", 2000, 2000)]
d = pd.DataFrame(rows, columns=["market", "lo", "hi"]).sort_values("lo")
fig, ax = plt.subplots(figsize=(11, 5.8))
c = [SLATE if "Benchmark" in m else (GOLD if "Nigeria" in m else TEAL) for m in d.market]
ax.barh(d.market, d.lo, color=c)
ax.barh(d.market, d.hi - d.lo, left=d.lo, color=c, alpha=.35)
for i, (lo, hi) in enumerate(zip(d.lo, d.hi)):
    ax.text(hi + 80, i, f"{lo:,.0f}" + (f"–{hi:,.0f}" if hi - lo > 5 else ""), va="center", fontsize=11.5)
ax.axvline(1800, color=RUST, ls="--", lw=1.5); ax.text(1850, len(d) - .6, "1,800", color=RUST, fontsize=11)
ax.axvline(10000, color=SLATE, lw=1); ax.text(9950, len(d) - .6, "monopoly = 10,000", ha="right", fontsize=10.5, color=SLATE)
ax.set_xlim(0, 10400); ax.tick_params(axis="y", labelsize=10.5)
ax.set(title="Four platform markets, all far above the merger-screen line", xlabel="Herfindahl–Hirschman Index (sum of squared % shares)")
note(fig, "Sources: NCC; Communications Authority of Kenya (via The Star); iResearch (via CnTechPost); US v. Google (D.D.C., Aug 2024). "
          "Pale bar = range when some firms' shares are not published.")
save(fig, "s04", "f02")

# --- F03 · Monopoly vs competition (ILLUSTRATIVE, Mankiw ch. 15) -------------------------------
a, b, mc = 100, 1, 20                       # demand P = 100 − Q ; constant marginal cost ₦20
Qc, Pc = (a - mc) / b, mc                   # competition: P = MC
Qm = (a - mc) / (2 * b); Pm = a - b * Qm    # monopoly: MR = a − 2bQ = MC
q = np.linspace(0, 100, 200)
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(q, a - b * q, color=NAVY, lw=3, label="Demand (price customers will pay)")
ax.plot(q[q <= 50], a - 2 * b * q[q <= 50], color=TEAL2, lw=2, ls="--", label="Marginal revenue")
ax.axhline(mc, color=SLATE, lw=2, label="Marginal cost = ₦20")
ax.fill_between([0, Qm], mc, Pm, color=GOLD, alpha=.35, label=f"Monopoly profit ₦{(Pm - mc) * Qm:,.0f}m")
ax.fill_between(q[(q >= Qm) & (q <= Qc)], mc, (a - b * q)[(q >= Qm) & (q <= Qc)], color=RUST, alpha=.4,
                label=f"Deadweight loss ₦{0.5 * (Pm - mc) * (Qc - Qm):,.0f}m")
for (qq, pp, t) in [(Qm, Pm, f"Monopoly: {Qm:.0f}m transactions at ₦{Pm:.0f}"), (Qc, Pc, f"Competition: {Qc:.0f}m at ₦{Pc:.0f}")]:
    ax.plot(qq, pp, "o", color=INK, ms=8); ax.annotate(t, (qq, pp), xytext=(qq + 3, pp + 7), fontsize=11.5, color=INK)
ax.set(xlim=(0, 100), ylim=(0, 105), xlabel="Transactions per month (millions)", ylabel="Fee per transaction (₦)",
       title="A monopolist sells less, charges more — and some trades never happen")
ax.legend(loc="upper right", fontsize=11)
note(fig, "Illustrative numbers. Demand: fee = 100 − Q; marginal cost ₦20. Competition: P = MC. Monopoly: MR = MC (Mankiw, ch. 15).")
save(fig, "s04", "f03")

# --- F04 · Network effects and tipping (ILLUSTRATIVE simulation) -------------------------------
def simulate(beta, quality_b=0.15, s0=0.55, T=36, churn=0.15):
    s = [s0]
    for _ in range(T):
        pa = 1 / (1 + np.exp(-(beta * (2 * s[-1] - 1) - quality_b)))   # chance a new or switching user picks A
        s.append((1 - churn) * s[-1] + churn * pa)
    return np.array(s) * 100
fig, ax = plt.subplots(figsize=(10, 5.6))
for beta, c, l in [(0.0, SLATE, "No network effect"), (1.5, TEAL, "Moderate network effect"), (4.0, RUST, "Strong network effect")]:
    path = simulate(beta); ax.plot(path, color=c, lw=3, label=l)
    ax.text(36.4, path[-1], f"{path[-1]:.0f}%", color=c, va="center", fontsize=12, fontweight="bold")
ax.axhline(50, color=GRID, lw=1.5)
ax.set(title="With strong network effects the early leader takes the market — even against a better rival",
       xlabel="Months", ylabel="Platform A's share of users", ylim=(0, 100), xlim=(0, 39))
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="lower left", fontsize=11.5)
note(fig, "Illustrative simulation. A starts with 55% of users; B is slightly better (quality edge 0.15). Each month 15% of users choose again, "
          "weighing quality and how many people are already on each platform.")
save(fig, "s04", "f04")
print("F04 end shares:", [round(simulate(bb)[-1], 1) for bb in (0, 1.5, 4)])

# --- F05 · Nigeria's instant payments: nominal, real and in dollars ------------------------------
nip = pd.read_csv("data/official/ng_nip_value.csv").set_index("year")
m = pd.read_csv("data/official/ng_official_monthly.csv", parse_dates=["date"]).set_index("date")
infl = m.cpi_headline_yoy.groupby(m.index.year).mean()
price = (1 + infl.loc[2019:2024] / 100).cumprod(); price.loc[2018] = 1.0; price = price.sort_index()
fx = pd.read_csv("data/official/ng_worldbank_annual.csv").set_index("year").ngn_usd_avg
nip["real_2018_ntn"] = nip.nip_value_ntn / price
nip["usd_bn"] = nip.nip_value_ntn * 1e12 / fx.loc[nip.index] / 1e9
fig, ax = plt.subplots(figsize=(10.5, 5.6))
w = .38; xx = np.arange(len(nip))
ax.bar(xx - w / 2, nip.nip_value_ntn, w, color=TEAL, label="Nominal ₦ trillion")
ax.bar(xx + w / 2, nip.real_2018_ntn, w, color=NAVY, label="Real ₦ trillion (2018 prices)")
ax2 = ax.twinx(); ax2.plot(xx, nip.usd_bn, "-o", color=GOLD, lw=3, label="US$ billion (right)"); ax2.grid(False)
ax2.spines["right"].set_visible(True); ax2.set_ylim(0, 1100); ax2.set_ylabel("US$ billion")
g_nom = nip.nip_value_ntn[2024] / nip.nip_value_ntn[2018]; g_real = nip.real_2018_ntn[2024] / nip.real_2018_ntn[2018]; g_usd = nip.usd_bn[2024] / nip.usd_bn[2018]
ax.set_xticks(xx, nip.index); ax.set_ylabel("₦ trillion"); ax.set_ylim(0, 1200)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=11)
ax.set_title(f"Instant transfers, 2018→2024: ×{g_nom:.0f} in naira, ×{g_real:.1f} in real terms, ×{g_usd:.1f} in dollars")
note(fig, "Sources: NIBSS annual NIP values (via Techpoint, ThisDay, TheCable, Nairametrics); CBN headline CPI (annual average); "
          "World Bank official ₦/$ annual average (2018: ₦306; at the ₦362 market rate the dollar rise is ×3.3). 2024 CPI on the old 2009 base.")
save(fig, "s04", "f05")
print(nip.round(1)); print(f"F05 growth: nominal x{g_nom:.2f}, real x{g_real:.2f}, usd x{g_usd:.2f}")

# --- F06 · Mobile money: Kenya tipped early; Nigeria is catching up ----------------------------------
fxd = pd.read_csv("data/official/findex_accounts.csv").dropna(subset=["mobile_money_pct"])
fig, ax = plt.subplots(figsize=(10.5, 5.6))
for ctry, c in [("Kenya", RUST), ("Ghana", GOLD), ("Nigeria", NAVY), ("South Africa", TEAL), ("Egypt, Arab Rep.", SLATE)]:
    g = fxd[fxd.country == ctry].sort_values("year")
    ax.plot(g.year, g.mobile_money_pct, "-o", color=c, lw=3 if ctry == "Nigeria" else 2.2, label=ctry.replace(", Arab Rep.", ""))
    ax.text(2024.3, g.mobile_money_pct.iloc[-1] + {"Nigeria": 2.2, "South Africa": -2.2}.get(ctry, 0), f"{g.mobile_money_pct.iloc[-1]:.0f}%", color=c, va="center", fontsize=12, fontweight="bold")
ax.set(title="Adults with a mobile-money account: Nigeria went from 9% to 33% in three years",
       ylabel="% of adults (15+)", ylim=(0, 100), xlim=(2013.5, 2025.3))
ax.set_xticks([2014, 2017, 2021, 2024]); ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left", fontsize=11)
note(fig, "Source: World Bank Global Findex Database 2025 (survey years 2014, 2017, 2021, 2024), indicator mobileaccount.t.d.")
save(fig, "s04", "f06")
