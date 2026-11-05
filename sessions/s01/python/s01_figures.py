# =============================================================================
# EEGB · Session 1 · Course Overview & Data Literacy for Managers
# Replication script — regenerates every chart in the Session 1 deck (Python)
# Data: data/ng_macro_monthly.csv (stylised Nigerian macro series, 2015–2025)
# Run from the project root:  python sessions/s01/python/s01_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
rebase = pd.Timestamp("2025-01-01")

# --- F01 · Three ways to measure inflation ------------------------------------------
fig, ax = plt.subplots()
ax.plot(m.date, m.food_inflation, color=GOLD, lw=2.2, label="Food")
ax.plot(m.date, m.headline_inflation, color=NAVY, lw=3, label="Headline (all items)")
ax.plot(m.date, m.core_inflation, color=TEAL, lw=2.2, label="Core (excl. farm produce & energy)")
ax.axvline(rebase, color=SLATE, ls="--", lw=1.2)
ax.text(rebase, 43, " CPI rebased\n Jan 2025", color=SLATE, fontsize=11, va="top")
ax.axvline(pd.Timestamp("2023-06-01"), color=RUST, ls=":", lw=1.2)
ax.text(pd.Timestamp("2023-06-01"), 6, "Subsidy removal &\nFX unification ", color=RUST, fontsize=11, ha="right")
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.set_ylim(0, 45); ax.legend(loc="upper left")
ax.set(title="Inflation: food led, core followed — and the 2025 rebasing broke the series",
       ylabel="Year-on-year change")
note(fig); save(fig, "s01", "f01")

# --- F02 · Official vs parallel exchange rate -----------------------------------------
fig, ax = plt.subplots()
ax.plot(m.date, m.parallel_fx_ngn_usd, color=RUST, lw=2.2, label="Parallel market")
ax.plot(m.date, m.official_fx_ngn_usd, color=NAVY, lw=3, label="Official window")
ax.fill_between(m.date, m.official_fx_ngn_usd, m.parallel_fx_ngn_usd, color=GOLD, alpha=.25, label="Premium")
prem = (m.parallel_fx_ngn_usd / m.official_fx_ngn_usd - 1) * 100
i = prem.idxmax()
ax.annotate(f"Premium peaks at {prem[i]:.0f}%\n({m.date[i]:%b %Y})", xy=(m.date[i], m.parallel_fx_ngn_usd[i]),
            xytext=(pd.Timestamp("2016-06-01"), 1100), arrowprops=dict(arrowstyle="->", color=NAVY), fontsize=12, color=NAVY)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:,.0f}")); ax.legend(loc="upper left")
ax.set(title="Two prices for one dollar: the gap closed only after the 2023–24 unification",
       ylabel="Naira per US dollar")
note(fig); save(fig, "s01", "f02")

# --- F03 · Correlation is not causation -------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
r_lv = np.corrcoef(m.private_credit_growth_yoy, m.headline_inflation)[0, 1]
axes[0].scatter(m.private_credit_growth_yoy, m.headline_inflation, color=TEAL, alpha=.7)
axes[0].set(title=f"Credit growth vs inflation: r = {r_lv:.2f}", xlabel="Private credit growth (%)", ylabel="Headline inflation (%)")
axes[0].title.set_fontsize(13)
d = m.set_index("date")[["brent_usd", "fx_reserves_usd_bn"]]
lag = d.fx_reserves_usd_bn.shift(-6)
ok = lag.notna()
r_oil = np.corrcoef(d.brent_usd[ok], lag[ok])[0, 1]
axes[1].scatter(d.brent_usd[ok], lag[ok], color=GOLD, alpha=.7)
axes[1].set(title=f"Oil price vs reserves 6 months later: r = {r_oil:.2f}", xlabel="Brent (US$/barrel)", ylabel="FX reserves (US$ bn)")
axes[1].title.set_fontsize(13)
fig.suptitle("A strong correlation with a muddled story, a weak one with a clear causal channel", x=0.01, ha="left",
             fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig); save(fig, "s01", "f03")

# --- F04 · A five-number board dashboard (last 36 months) ---------------------------------
last = m[m.date >= m.date.max() - pd.DateOffset(months=35)]
panels = [("headline_inflation", "Inflation (%)", NAVY), ("mpr", "Policy rate (%)", TEAL),
          ("official_fx_ngn_usd", "₦ per US$", RUST), ("brent_usd", "Brent (US$/bbl)", GOLD),
          ("fx_reserves_usd_bn", "Reserves (US$ bn)", TEAL2), ("pmi", "PMI (50 = no change)", OLIVE)]
fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharex=True)
for ax, (col, lab, c) in zip(axes.flat, panels):
    ax.plot(last.date, last[col], color=c, lw=2.4)
    ax.scatter(last.date.iloc[-1], last[col].iloc[-1], color=c, s=45, zorder=3)
    chg = last[col].iloc[-1] - last[col].iloc[-13]
    ax.set_title(f"{lab}\n{last[col].iloc[-1]:,.1f}  ({'+' if chg >= 0 else ''}{chg:,.1f} vs a year ago)", fontsize=12, loc="left")
    if col == "pmi": ax.axhline(50, color=SLATE, ls="--", lw=1)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%y")); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
fig.suptitle("The board's monthly macro page: six numbers, latest value, change on a year ago", x=0.01, ha="left",
             fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig); save(fig, "s01", "f04")

# --- F05 · Real interest rate: policy rate minus inflation ----------------------------------
real = m.mpr - m.headline_inflation
fig, ax = plt.subplots()
ax.fill_between(m.date, real, 0, where=real < 0, color=RUST, alpha=.35, label="Negative real rate")
ax.fill_between(m.date, real, 0, where=real >= 0, color=TEAL, alpha=.35, label="Positive real rate")
ax.plot(m.date, real, color=NAVY, lw=2.4)
ax.axhline(0, color=INK, lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="lower left")
ax.set(title=f"Savers lost to inflation for most of the decade (latest real rate: {real.iloc[-1]:+.1f} pts)",
       ylabel="Policy rate minus headline inflation")
note(fig); save(fig, "s01", "f05")

# --- F06 · Nowcasting with a survey: PMI as an early signal -----------------------------------
fig, ax = plt.subplots()
ax.plot(m.date, m.pmi, color=TEAL, lw=2.4)
ax.axhline(50, color=RUST, ls="--", lw=1.4); ax.text(m.date.iloc[2], 50.4, "50 = activity unchanged", color=RUST, fontsize=11)
for start, end, lab in [("2016-01-01", "2016-12-01", "2016 recession"), ("2020-04-01", "2020-09-01", "COVID-19"),
                        ("2023-11-01", "2024-07-01", "Reform\nsqueeze")]:
    ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color=GOLD, alpha=.18)
    ax.text(pd.Timestamp(start), 61, lab, fontsize=11, color=NAVY)
ax.set_ylim(35, 63)
ax.set(title="The PMI arrives weeks before GDP — and dipped below 50 in every downturn",
       ylabel="Purchasing Managers' Index")
note(fig); save(fig, "s01", "f06")
