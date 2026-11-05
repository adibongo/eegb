# =============================================================================
# EEGB · Session 15 · Corporate Macro Strategy: Hedging & Resilience
# Replication script — regenerates every chart in the Session 15 deck (Python)
# Data: data/miller_exposure_monthly.csv (a stylised flour miller, 2019–2025)
#       data/ng_macro_monthly.csv, data/global_policy_rates.csv (for forward prices and leading indicators)
# Run from the project root:  python sessions/s15/python/s15_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
mi = pd.read_csv("data/miller_exposure_monthly.csv", parse_dates=["month"])
mac = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
pr = pd.read_csv("data/global_policy_rates.csv", parse_dates=["date"])
OTHER = 1.12          # other costs (energy, packaging, labour) as a multiple of the imported wheat cost

# --- F01 · Two sources of risk: wheat in dollars, dollars in naira ----------------------------
base = mi.iloc[:12].mean(numeric_only=True)
idx = pd.DataFrame({"month": mi.month,
                    "Wheat price (US$)": 100 * mi.wheat_usd_per_tonne / base.wheat_usd_per_tonne,
                    "Exchange rate (₦ per US$)": 100 * mi.fx_ngn_usd / base.fx_ngn_usd,
                    "Wheat cost in naira (₦ per tonne)": 100 * (mi.wheat_usd_per_tonne * mi.fx_ngn_usd)
                    / (base.wheat_usd_per_tonne * base.fx_ngn_usd)})
fig, ax = plt.subplots()
for col, c, lw in [("Wheat price (US$)", GOLD, 2.2), ("Exchange rate (₦ per US$)", RUST, 2.2),
                   ("Wheat cost in naira (₦ per tonne)", NAVY, 3)]:
    ax.plot(idx.month, idx[col], color=c, lw=lw, label=col)
ax.axhline(100, color=SLATE, lw=1, ls="--")
ax.legend(loc="upper left")
ax.set(title=f"Wheat cost in naira rose {idx.iloc[-1, 3]:.0f}% of its 2019 level — the exchange rate did most of the work",
       ylabel="Index, 2019 average = 100")
ax.title.set_fontsize(14)
note(fig); save(fig, "s15", "f01")

# --- F02 · Decompose the rise: how much from wheat, how much from the naira? -------------------
y19, y25 = mi[mi.month.dt.year == 2019].mean(numeric_only=True), mi[mi.month.dt.year == 2025].mean(numeric_only=True)
lw = np.log(y25.wheat_usd_per_tonne / y19.wheat_usd_per_tonne)
lf = np.log(y25.fx_ngn_usd / y19.fx_ngn_usd)
tot = np.exp(lw + lf) - 1
share_fx = lf / (lw + lf)
fig, ax = plt.subplots(figsize=(10, 4.8))
parts = [("Wheat price in US$", lw, GOLD), ("Naira per US$", lf, RUST), ("Total (₦ per tonne)", lw + lf, NAVY)]
for i, (lab, v, c) in enumerate(parts):
    ax.barh(i, v * 100, color=c)
    ax.text(v * 100 + 2, i, f"{v * 100:+.0f} log-points", va="center", fontsize=13, color=c)
ax.set_yticks(range(3), [p[0] for p in parts]); ax.invert_yaxis(); ax.set_xlim(min(0, lw * 100) - 10, (lw + lf) * 100 + 45)
ax.axvline(0, color=INK, lw=1)
ax.set(title=f"2019 → 2025: naira wheat cost up {tot:.0%}; the exchange rate explains {share_fx:.0%} of it",
       xlabel="Change in log points (they add up; 100 log-points ≈ a 172% rise)")
note(fig); save(fig, "s15", "f02")

# --- F03 · Margin squeeze: prices catch up with costs, but with a lag -------------------------
fig, ax = plt.subplots()
ax.plot(mi.month, mi.gross_margin_pct, color=TEAL, lw=2.6)
ax.axhline(mi.gross_margin_pct.mean(), color=SLATE, ls="--", lw=1)
ax.text(mi.month.iloc[1], mi.gross_margin_pct.mean() + 0.6, f"average {mi.gross_margin_pct.mean():.1f}%", color=SLATE, fontsize=11)
worst = mi.nsmallest(3, "gross_margin_pct")
for _, r in worst.iterrows():
    ax.scatter(r.month, r.gross_margin_pct, color=RUST, s=60, zorder=3)
w = worst.iloc[0]
ax.annotate(f"Worst month: {w.gross_margin_pct:.1f}%\n({w.month:%b %Y})", xy=(w.month, w.gross_margin_pct),
            xytext=(pd.Timestamp("2020-06-01"), 4), arrowprops=dict(arrowstyle="->", color=NAVY), fontsize=12, color=NAVY)
ax.yaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title="Each devaluation hit margins first; flour prices caught up only months later", ylabel="Gross margin")
note(fig); save(fig, "s15", "f03")

# --- F04/F05 · Simulate an FX forward hedge at 0%, 50% and 100% ---------------------------------
# Each month the miller orders wheat that it pays for 3 months later. It can lock in the naira
# price today with a 3-month forward. Forward rate = spot x (1 + (naira rate − US rate) x 3/12).
m2 = mac.set_index("date")[["official_fx_ngn_usd", "mpr"]].join(pr.set_index("date")[["us_fed"]], how="left")
m2["us_fed"] = m2.us_fed.fillna(2.5)
sim = mi.set_index("month").copy()
sim["spot_3m_ago"] = m2.official_fx_ngn_usd.shift(3).reindex(sim.index)
sim["fwd_3m_ago"] = (m2.official_fx_ngn_usd * (1 + (m2.mpr - m2.us_fed) / 100 * 3 / 12)).shift(3).reindex(sim.index)
sim = sim.dropna()
res = {}
for h in (0, 0.5, 1.0):
    rate = h * sim.fwd_3m_ago + (1 - h) * sim.fx_ngn_usd
    cost = sim.imported_cost_usd_m * rate / 1e3 * OTHER
    res[h] = 100 * (sim.revenue_ngn_bn - cost) / sim.revenue_ngn_bn
fig, ax = plt.subplots()
for h, c, lw_ in [(0, RUST, 2.2), (0.5, GOLD, 2.2), (1.0, TEAL, 2.6)]:
    ax.plot(res[h].index, res[h], color=c, lw=lw_, label=f"{int(h * 100)}% hedged  (sd {res[h].std():.1f} pts)")
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="lower left")
ax.set(title="Hedging FX three months ahead smooths the margin — at a price in calm times", ylabel="Gross margin")
note(fig, "Source: EEGB stylised teaching data. Forward = spot × (1 + (MPR − US policy rate) × 3/12). Illustrative only.")
save(fig, "s15", "f04")

summary = pd.DataFrame({"mean": [res[h].mean() for h in res], "sd": [res[h].std() for h in res],
                        "worst": [res[h].min() for h in res]}, index=["0%", "50%", "100%"])
calm = sim.index.year.isin([2019, 2021, 2022])
summary["mean_calm_years"] = [res[h][calm].mean() for h in res]
fig, axes = plt.subplots(1, 3, figsize=(12, 4.6))
for ax, col, t, c in zip(axes, ["mean", "sd", "worst"], ["Average margin", "Volatility (sd)", "Worst month"], [TEAL, GOLD, RUST]):
    ax.bar(summary.index, summary[col], color=c)
    for i, v in enumerate(summary[col]): ax.text(i, max(v, 0) + 0.3, f"{v:.1f}", ha="center", fontsize=13)
    ax.set_title(t, fontsize=13); ax.set_xlabel("Share of FX hedged"); ax.axhline(0, color=INK, lw=.8)
fig.suptitle("A 50% hedge gave the steadiest margin; 100% over-hedged because flour prices already pass on costs", x=0.01, ha="left",
             fontsize=15, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig); save(fig, "s15", "f05")

# --- F06 · Sensitivity (tornado): what moves the margin most? ----------------------------------
b = mi[mi.month.dt.year == 2025].mean(numeric_only=True)
def margin(fx=1, wheat=1, price=1, vol=1, other=1):
    rev = b.flour_price_ngn_per_kg * price * b.flour_volume_kt * vol * 1e6 / 1e9
    cost = b.wheat_usd_per_tonne * wheat * 1.32 * b.flour_volume_kt * vol * 1000 / 1e6 * b.fx_ngn_usd * fx / 1e3
    return 100 * (rev - cost * (1 + (OTHER - 1) * other)) / rev
m0 = margin()
shocks = [("Naira 20% weaker / stronger", dict(fx=1.2), dict(fx=0.8)),
          ("Wheat 20% dearer / cheaper", dict(wheat=1.2), dict(wheat=0.8)),
          ("Flour price 10% lower / higher", dict(price=0.9), dict(price=1.1)),
          ("Other costs 25% higher / lower", dict(other=1.25), dict(other=0.75)),
          ("Naira AND wheat 20% worse / better", dict(fx=1.2, wheat=1.2), dict(fx=0.8, wheat=0.8))]
tor = pd.DataFrame([(lab, margin(**bad) - m0, margin(**good) - m0) for lab, bad, good in shocks],
                   columns=["shock", "bad", "good"])
tor["range"] = tor.good - tor.bad; tor = tor.sort_values("range")
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(tor.shock, tor.bad, color=RUST); ax.barh(tor.shock, tor.good, color=TEAL)
for i, (bd, gd) in enumerate(zip(tor.bad, tor.good)):
    ax.text(bd - 0.5, i, f"{bd:+.1f}", ha="right", va="center", fontsize=12)
    ax.text(gd + 0.5, i, f"{gd:+.1f}", ha="left", va="center", fontsize=12)
ax.axvline(0, color=INK, lw=1); ax.set_xlim(tor.bad.min() - 7, tor.good.max() + 7)
ax.set(title=f"From a {m0:.1f}% base margin, the exchange rate and wheat dominate", xlabel="Change in gross margin (percentage points)")
note(fig); save(fig, "s15", "f06")

# --- F07 · The macro-risk heatmap ---------------------------------------------------------------
risks = pd.DataFrame([
    ["Naira devaluation", 4, 5], ["Wheat price spike", 3, 4], ["Policy rate hike", 3, 2],
    ["Port & shipping delays", 3, 3], ["Consumer demand slump", 3, 3], ["Import levy / FX restriction", 2, 4],
    ["Diesel & power costs", 4, 2], ["Bank credit tightening", 2, 3]], columns=["risk", "likelihood", "impact"])
fig, ax = plt.subplots(figsize=(11, 6))
L, I = np.meshgrid(np.arange(1, 6), np.arange(1, 6))
ax.imshow(L * I, origin="lower", extent=(0.5, 5.5, 0.5, 5.5), cmap="YlOrRd", alpha=.55)
offs = {}
for n, r in enumerate(risks.itertuples(), 1):
    k = (r.likelihood, r.impact); o = offs.get(k, 0); offs[k] = o + 1
    x = r.likelihood - 0.22 + 0.44 * o
    ax.scatter(x, r.impact, color=NAVY, s=420, zorder=3)
    ax.text(x, r.impact, str(n), color="white", ha="center", va="center", fontsize=12, fontweight="bold", zorder=4)
    ax.text(5.75, 5.3 - 0.55 * (n - 1), f"{n}  {r.risk}  (L{r.likelihood} × I{r.impact} = {r.likelihood * r.impact})",
            fontsize=12, color=NAVY, va="center", transform=ax.transData, clip_on=False)
ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5)
ax.set_xticks(range(1, 6), ["Rare", "Unlikely", "Possible", "Likely", "Almost\ncertain"])
ax.set_yticks(range(1, 6), ["Minor", "Moderate", "Serious", "Major", "Severe"]); ax.grid(False)
ax.set(title="The miller's macro-risk heatmap: act first on the top-right corner",
       xlabel="Likelihood over the next 12 months", ylabel="Impact on gross margin")
note(fig, "Scores are management judgements, informed by the sensitivity analysis (F06). Illustrative.")
save(fig, "s15", "f07")

# --- F08 · Leading indicators: does the FX premium warn of devaluation? ----------------------------
mm = mac.set_index("date")
prem = 100 * (mm.parallel_fx_ngn_usd / mm.official_fx_ngn_usd - 1)
fwd_dep = 100 * (mm.official_fx_ngn_usd.shift(-6) / mm.official_fx_ngn_usd - 1)
ok = fwd_dep.notna()
r = np.corrcoef(prem[ok], fwd_dep[ok])[0, 1]
fig, ax = plt.subplots()
ax.scatter(prem[ok], fwd_dep[ok], color=TEAL, alpha=.7)
big = (prem > 30) & ok
ax.scatter(prem[big], fwd_dep[big], color=RUST, alpha=.85, label="Premium above 30%")
ax.axvline(30, color=RUST, ls="--", lw=1); ax.legend(loc="upper left")
ax.xaxis.set_major_formatter(FuncFormatter(pct)); ax.yaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title=f"A wide parallel-market premium often came before a devaluation (r = {r:.2f})",
       xlabel="Parallel-market premium today", ylabel="Official naira depreciation over next 6 months")
note(fig); save(fig, "s15", "f08")

# --- key numbers for the slides ----------------------------------------------------------------
print("F01 last index naira cost:", round(idx.iloc[-1, 3], 0), "| fx idx", round(idx.iloc[-1, 2], 0), "| wheat idx", round(idx.iloc[-1, 1], 0))
print("F02 total rise", round(tot * 100), "% | fx share", round(share_fx * 100), "% | wheat logpts", round(lw * 100), "fx logpts", round(lf * 100))
print("F03 mean margin", round(mi.gross_margin_pct.mean(), 1), "| worst", worst[["month", "gross_margin_pct"]].values.tolist())
print("F05 summary\n", summary.round(1))
print("F06 base margin", round(m0, 1)); print(tor.round(1))
print("F08 r =", round(r, 2), "| mean 6m dep when prem>30:", round(fwd_dep[big].mean(), 1), "| when <=30:", round(fwd_dep[ok & ~big].mean(), 1))
