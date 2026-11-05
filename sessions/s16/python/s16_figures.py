# =============================================================================
# EEGB · Session 16 · Capstone & Integrative Review
# Replication script — regenerates every chart in the Session 16 deck (Python)
# Data: data/ng_macro_monthly.csv, data/miller_exposure_monthly.csv, data/cement_demand_monthly.csv,
#       data/global_policy_rates.csv (all stylised teaching data)
# Run from the project root:  python sessions/s16/python/s16_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
mi = pd.read_csv("data/miller_exposure_monthly.csv", parse_dates=["month"])
ce = pd.read_csv("data/cement_demand_monthly.csv", parse_dates=["month"])
pr = pd.read_csv("data/global_policy_rates.csv", parse_dates=["date"])
REFORM = pd.Timestamp("2023-06-01")

# --- F01 · Policy to profits: one shock, four panels --------------------------------------------
w = m[m.date >= "2022-01-01"]
wm = mi[mi.month >= "2022-01-01"]
fig, axes = plt.subplots(4, 1, figsize=(10, 8.4), sharex=True)
rows = [(w.date, w.official_fx_ngn_usd, RUST, "1 · Exchange rate (₦ per US$)"),
        (w.date, w.headline_inflation, NAVY, "2 · Headline inflation (%)"),
        (w.date, w.mpr, TEAL, "3 · CBN policy rate (%)"),
        (wm.month, wm.gross_margin_pct, GOLD, "4 · A flour miller's gross margin (%)")]
for ax, (x, y, c, t) in zip(axes, rows):
    ax.plot(x, y, color=c, lw=2.6); ax.axvline(REFORM, color=SLATE, ls="--", lw=1.1)
    ax.set_title(t, fontsize=12.5, loc="left", pad=4)
axes[0].text(REFORM, axes[0].get_ylim()[1] * 0.92, "  June 2023: FX unification\n  & subsidy removal", fontsize=10.5, color=SLATE, va="top")
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.suptitle("One reform, four steps: currency → prices → policy rate → company margins", x=0.01, ha="left",
             fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig); save(fig, "s16", "f01")

# --- F02 · The course on one page: an integrative map --------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6.4)); ax.set_xlim(0, 12); ax.set_ylim(0, 6.4); ax.axis("off")
cols = [("PART I · Micro & markets", TEAL, ["1 Data literacy", "2 Demand & elasticity", "3 Forecasting & sizing",
                                            "4 Platforms & competition", "5 Market failures"]),
        ("PART II · Macro, policy & risk", NAVY, ["6 AD–AS & inflation", "7 National accounts", "8 Monetary policy",
                                                  "9 Fiscal policy & debt", "10 Financial stability"]),
        ("PART III · Open economy", RUST, ["11 FX & capital flows", "12 Trade & industrial policy"]),
        ("PART IV · Strategy", GOLD, ["13 Climate & transition", "14 Country risk & scenarios", "15 Hedging & resilience",
                                      "16 Board memo"])]
for i, (head, c, items) in enumerate(cols):
    x = 0.2 + i * 3.0
    ax.add_patch(FancyBboxPatch((x, 5.4), 2.7, 0.7, boxstyle="round,pad=0.02,rounding_size=0.12", color=c))
    ax.text(x + 1.35, 5.75, head, ha="center", va="center", color="white", fontsize=11.5, fontweight="bold")
    for j, it in enumerate(items):
        y = 4.75 - j * 0.78
        ax.add_patch(FancyBboxPatch((x, y - 0.28), 2.7, 0.56, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    facecolor=LIGHT, edgecolor=c, lw=1.6))
        ax.text(x + 0.15, y, it, va="center", fontsize=11.5, color=INK)
    if i < 3:
        ax.annotate("", xy=(x + 3.0, 5.75), xytext=(x + 2.72, 5.75), arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=2))
for k, (lab, y) in enumerate([("micro → macro", 0.55), ("domestic → global", 0.55), ("policy → profits", 0.55)]):
    ax.text(1.55 + k * 3.0 + 1.5, 1.0, lab, ha="center", fontsize=12.5, color=SLATE, style="italic")
ax.text(0.2, 0.35, "Every board memo travels the whole map: a market question, the macro forces on it, the global links, and a decision with a hedge.",
        fontsize=12, color=NAVY)
ax.set_title("Sixteen sessions, one argument", loc="left")
save(fig, "s16", "f02")

# --- F03 · Three scenarios for 2026 ----------------------------------------------------------------
last = m.iloc[-1]
months = pd.date_range("2026-01-01", "2026-12-01", freq="MS")
scen = {"Upside: reforms stick, oil firm": (-0.004, 13.0, GREEN := "#2E7D5B"),
        "Base: gradual disinflation": (0.008, 15.0, TEAL),
        "Downside: oil slump, renewed FX pressure": (0.030, 24.0, RUST)}
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
hist = m[m.date >= "2024-01-01"]
axes[0].plot(hist.date, hist.official_fx_ngn_usd, color=INK, lw=2.4, label="History")
axes[1].plot(hist.date, hist.headline_inflation, color=INK, lw=2.4, label="History")
scen_end = {}
for name, (g, infl_end, c) in scen.items():
    fx = last.official_fx_ngn_usd * (1 + g) ** np.arange(1, 13)
    inf = np.linspace(last.headline_inflation, infl_end, 13)[1:]
    axes[0].plot(months, fx, color=c, lw=2.4, ls="--", label=name)
    axes[1].plot(months, inf, color=c, lw=2.4, ls="--")
    scen_end[name] = (fx[-1], inf[-1])
axes[0].yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:,.0f}"))
axes[1].yaxis.set_major_formatter(FuncFormatter(pct))
axes[0].set_title("Naira per US$", fontsize=13); axes[1].set_title("Headline inflation", fontsize=13)
axes[0].legend(loc="upper left", fontsize=10)
for ax in axes: ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%y"))
fig.suptitle("Write the memo for three futures, not one forecast", x=0.01, ha="left", fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig, "Scenario paths are illustrative assumptions starting from the last data point, not forecasts."); save(fig, "s16", "f03")

# --- F04 · A memo evidence pack: the cement industry ------------------------------------------------
c2 = ce.set_index("month")
yoy = 100 * (c2.cement_mt.rolling(12).sum() / c2.cement_mt.rolling(12).sum().shift(12) - 1)
mm = m.set_index("date")
fig, axes = plt.subplots(2, 2, figsize=(12, 6.6))
a = axes[0, 0]; a.plot(yoy.index, yoy, color=TEAL, lw=2.3); a.axhline(0, color=INK, lw=.8)
a.set_title(f"Cement volumes, 12-month growth: {yoy.iloc[-1]:+.1f}% (latest)", fontsize=12, loc="left")
a = axes[0, 1]; a.plot(c2.index, c2.price_per_bag_naira, color=RUST, lw=2.3)
a.set_title(f"Price per bag: ₦{c2.price_per_bag_naira.iloc[-1]:,.0f} (latest)", fontsize=12, loc="left")
a.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:,.0f}"))
a = axes[1, 0]; real = mm.mpr - mm.headline_inflation
a.plot(real.index, real, color=NAVY, lw=2.3); a.axhline(0, color=INK, lw=.8)
a.set_title(f"Real policy rate: {real.iloc[-1]:+.1f} pts (mortgages & developer credit)", fontsize=12, loc="left")
a = axes[1, 1]; a.plot(mm.index, mm.pmi, color=GOLD, lw=2.3); a.axhline(50, color=RUST, ls="--", lw=1)
a.set_title(f"PMI: {mm.pmi.iloc[-1]:.1f} (above 50 = expanding)", fontsize=12, loc="left")
for a in axes.flat: a.xaxis.set_major_locator(mdates.YearLocator(3)); a.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.suptitle("Evidence pack for a cement board memo: demand, price, credit, activity", x=0.01, ha="left",
             fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig); save(fig, "s16", "f04")

# --- F05 · Nominal vs real: the price of a bag of cement -------------------------------------------
# Approximate monthly CPI index from year-on-year inflation: monthly factor = (1 + yoy)^(1/12)
cpi = (1 + mm.headline_inflation / 100) ** (1 / 12)
cpi = 100 * cpi.cumprod() / cpi.iloc[0]
bag = c2.price_per_bag_naira.reindex(cpi.index)
real_bag = bag / cpi * 100
nom_ch, real_ch = bag.iloc[-1] / bag.iloc[0] - 1, real_bag.iloc[-1] / real_bag.iloc[0] - 1
fig, ax = plt.subplots()
ax.plot(bag.index, bag, color=RUST, lw=2.4, label="Nominal price (₦)")
ax.plot(real_bag.index, real_bag, color=TEAL, lw=2.8, label="Real price (Jan 2015 naira)")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:,.0f}")); ax.legend(loc="upper left")
ax.set(title=f"A bag of cement: {nom_ch:+.0%} in naira since 2015, but {real_ch:+.0%} after inflation",
       ylabel="Price per 50kg bag")
note(fig, "Real price uses an approximate CPI built from year-on-year inflation; the 2025 rebasing adds noise. Stylised data.")
save(fig, "s16", "f05")

# --- F06 · Domestic meets global: policy rates compared ----------------------------------------------
fig, ax = plt.subplots()
for col, lab, c, lw_ in [("nigeria_cbn", "Nigeria (CBN)", NAVY, 3), ("ghana_bog", "Ghana", GOLD, 2),
                         ("kenya_cbk", "Kenya", TEAL2, 2), ("south_africa_sarb", "South Africa", OLIVE, 2),
                         ("us_fed", "United States (Fed)", RUST, 2.4)]:
    ax.plot(pr.date, pr[col], color=c, lw=lw_, label=lab)
gap = pr.nigeria_cbn.iloc[-1] - pr.us_fed.iloc[-1]
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left", fontsize=11)
ax.set(title=f"The Fed sets the global tide: the CBN–Fed gap is {gap:.1f} points (late 2025)", ylabel="Policy rate")
note(fig); save(fig, "s16", "f06")

print("F01 fx", m[m.date == "2023-05-01"].official_fx_ngn_usd.values, "->", w.official_fx_ngn_usd.max(),
      "| infl peak", w.headline_inflation.max(), "| mpr", w.mpr.min(), "->", w.mpr.max(), "| margin min", wm.gross_margin_pct.min())
print("F03 start fx", last.official_fx_ngn_usd, "infl", last.headline_inflation); print({k: (round(v[0]), round(v[1], 1)) for k, v in scen_end.items()})
print("F04 cement yoy", round(yoy.iloc[-1], 1), "| price", c2.price_per_bag_naira.iloc[-1], "| real rate", round(real.iloc[-1], 1), "| pmi", mm.pmi.iloc[-1])
print("F05 nominal", round(nom_ch * 100), "% real", round(real_ch * 100), "% | bag 2015", bag.iloc[0], "2025", bag.iloc[-1])
print("F06 gap", gap, pr.iloc[-1].to_dict())
