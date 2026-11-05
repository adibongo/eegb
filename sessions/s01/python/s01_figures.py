# =============================================================================
# EEGB · Session 1 · Course Overview & Data Literacy for Managers
# Replication script — regenerates every chart in the Session 1 deck (Python)
# Data (official):
#   data/official/ng_official_monthly.csv  — CBN statistics API (inflation, MPR, T-bill,
#        official N/$ central rate, BDC rate to Apr 2021, gross reserves) + FRED Brent (MCOILBRENTEU)
#   data/official/ng_worldbank_annual.csv  — World Bank WDI (GDP per capita, growth, population)
# Refresh both files with:  python tools/fetch_official_data.py
# Run from the project root:  python sessions/s01/python/s01_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
m = pd.read_csv("data/official/ng_official_monthly.csv", parse_dates=["date"]).set_index("date")
a = pd.read_csv("data/official/ng_worldbank_annual.csv").set_index("year")
m = m.loc["2015-01-01":]
CBN = "Source: CBN statistics (cbn.gov.ng/rates), accessed Nov 2026."

def vline(ax, date, text, y, color=SLATE, ha="left"):
    ax.axvline(pd.Timestamp(date), color=color, ls="--", lw=1.1)
    ax.text(pd.Timestamp(date), y, (" " + text) if ha == "left" else (text + " "), color=color, fontsize=10.5, va="top", ha=ha)

# --- F01 · Headline, food and core inflation with the two measurement breaks ----------
fig, ax = plt.subplots()
ax.plot(m.index, m.cpi_food_yoy, color=GOLD, lw=2, label="Food")
ax.plot(m.index, m.cpi_headline_yoy, color=NAVY, lw=3, label="Headline (all items)")
ax.plot(m.index, m.cpi_core_yoy, color=TEAL, lw=2, label="Core (excl. farm produce & energy)")
vline(ax, "2023-06-01", "Subsidy removal &\n FX unification", 44, RUST, ha="right")
vline(ax, "2025-01-01", "New CPI (2024 = 100)\n Jan 2025", 44)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.set_ylim(0, 45); ax.legend(loc="upper left")
ax.set(title="Inflation: food led, core followed — then the yardstick changed", ylabel="Year-on-year change")
note(fig, CBN + " 2025 values are NBS's revised (Dec 2025) series on the 2024 base; earlier values on the 2009 base.")
save(fig, "s01", "f01")

# --- F02 · The naira: official rate and the parallel (BDC) premium ------------------------
fig, ax = plt.subplots()
ax.plot(m.index, m.usd_official_avg, color=NAVY, lw=3, label="Official (CBN central rate, monthly average)")
ax.plot(m.index, m.usd_bdc_avg, color=RUST, lw=2, label="Bureau de change (CBN series ends Apr 2021)")
both = m[["usd_official_avg", "usd_bdc_avg"]].dropna()
ax.fill_between(both.index, both.usd_official_avg, both.usd_bdc_avg, color=GOLD, alpha=.25)
prem = (both.usd_bdc_avg / both.usd_official_avg - 1) * 100; i = prem.idxmax()
ax.annotate(f"Premium {prem[i]:.0f}% ({i:%b %Y})", xy=(i, both.usd_bdc_avg[i]), xytext=(pd.Timestamp("2015-03-01"), 900),
            arrowprops=dict(arrowstyle="->", color=NAVY), fontsize=11.5, color=NAVY)
vline(ax, "2023-06-01", "Unification\n Jun 2023", 1700, RUST)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"₦{x:,.0f}")); ax.legend(loc="upper left", fontsize=11)
ax.set(title="Naira per US dollar: rationing, then a reset", ylabel="₦ per US$")
note(fig, CBN); save(fig, "s01", "f02")

# --- F03 · Real policy rate (exact Fisher: (1+i)/(1+pi) - 1) -------------------------------
r = ((1 + m.policy_rate / 100) / (1 + m.cpi_headline_yoy / 100) - 1) * 100
r = r.dropna()
fig, ax = plt.subplots()
ax.fill_between(r.index, 0, r, where=r < 0, color=RUST, alpha=.35, label="Negative real rate")
ax.fill_between(r.index, 0, r, where=r >= 0, color=TEAL, alpha=.35, label="Positive real rate")
ax.plot(r.index, r, color=NAVY, lw=2.2); ax.axhline(0, color=SLATE, lw=1)
vline(ax, "2025-01-01", "New CPI", r.max() + 1)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.0f}%")); ax.legend(loc="lower left")
ax.set(title=f"Savers lost to inflation for most of a decade (latest: {r.iloc[-1]:+.1f}%, {r.index[-1]:%b %Y})",
       ylabel="Policy rate in real terms")
note(fig, CBN + " Real rate = (1 + MPR) / (1 + headline inflation) − 1."); save(fig, "s01", "f03")

# --- F04 · Oil price and reserves: same month vs 12 months later ---------------------------
d = m[["brent", "reserves_gross_usdbn"]].dropna()
same = d.brent.corr(d.reserves_gross_usdbn)
lag = d.brent.corr(d.reserves_gross_usdbn.shift(-12))
fig, ax = plt.subplots(); ax2 = ax.twinx()
ax.plot(d.index, d.brent, color=GOLD, lw=2.2, label="Brent crude (US$/bbl, left)")
ax2.plot(d.index, d.reserves_gross_usdbn, color=NAVY, lw=3, label="Gross external reserves (US$ bn, right)")
ax.set_ylabel("US$ per barrel"); ax2.set_ylabel("US$ billion"); ax2.grid(False)
ax2.spines["right"].set_visible(True)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=11)
ax.set(title=f"Oil and reserves: r = {same:.2f} in the same month, {lag:.2f} twelve months later")
note(fig, "Sources: CBN gross reserves (month-end); FRED MCOILBRENTEU (Brent, monthly average)."); save(fig, "s01", "f04")
print(f"F04 correlations: same month {same:.3f}; reserves 12 months later {lag:.3f}")

# --- F05 · GDP per person: constant vs current dollars -------------------------------------
y = a.loc[2000:]
fig, ax = plt.subplots()
ax.plot(y.index, y.gdp_pc_current_usd, color=RUST, lw=2.2, label="Current US$ (prices and the exchange rate move it)")
ax.plot(y.index, y.gdp_pc_const2015_usd, color=NAVY, lw=3, label="Constant 2015 US$ (real output per person)")
for yr in (2014, 2024):
    ax.annotate(f"{yr}: ${y.gdp_pc_const2015_usd[yr]:,.0f} real\n         ${y.gdp_pc_current_usd[yr]:,.0f} current",
                xy=(yr, y.gdp_pc_const2015_usd[yr]), xytext=(2016.3 if yr == 2014 else 2015.3, 3350 if yr == 2014 else 900),
                fontsize=10.5, color=NAVY, arrowprops=dict(arrowstyle="->", color=SLATE))
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}")); ax.set_ylim(0, 3800); ax.legend(loc="upper left", fontsize=11)
ax.set(title="GDP per person: the dollar collapse is mostly the naira; real output fell ~10%")
note(fig, "Source: World Bank WDI (NY.GDP.PCAP.KD, NY.GDP.PCAP.CD), last updated Oct 2026. The 2019 jump in current US$ coincides with the start of NBS's rebased (2019-base) GDP series."); save(fig, "s01", "f05")

# --- F06 · The board's macro page: six official series ----------------------------------------
last3 = m.loc["2023-10-01":]
panels = [("cpi_headline_yoy", "Headline inflation (%)", NAVY), ("cpi_core_yoy", "Core inflation (%)", TEAL),
          ("policy_rate", "Monetary policy rate (%)", TEAL2), ("usd_official_avg", "₦ per US$ (official)", RUST),
          ("reserves_gross_usdbn", "Gross reserves (US$ bn)", NAVY), ("brent", "Brent crude (US$/bbl)", GOLD)]
fig, axes = plt.subplots(2, 3, figsize=(13, 6.4))
for ax, (col, lab, c) in zip(axes.flat, panels):
    s = last3[col].dropna(); ax.plot(s.index, s, color=c, lw=2.4); ax.plot(s.index[-1], s.iloc[-1], "o", color=c)
    yago = s.loc[: s.index[-1] - pd.DateOffset(months=12)].iloc[-1]
    ch = s.iloc[-1] - yago
    unit = " pp" if "%" in lab else ""
    ax.set_title(f"{lab}\n{s.iloc[-1]:,.1f}  ({ch:+,.1f}{unit} vs a year ago, {s.index[-1]:%b %y})", fontsize=11.5, loc="left")
    ax.tick_params(labelsize=9.5); ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %y"))
fig.suptitle("The board's macro page — latest value, three-year trend, change on a year ago", x=0.01, ha="left",
             fontsize=15, fontweight="bold", color=NAVY)
fig.tight_layout(); note(fig, "Sources: CBN statistics; FRED (Brent). Inflation series switches to the 2024 CPI base in Jan 2025.")
save(fig, "s01", "f06")

# --- F07 · The 30% question: one revenue figure, three answers (illustrative firm) -------------
nom = 52 / 40 - 1; infl = 0.3324; real = (1 + nom) / (1 + infl) - 1
usd0, usd1 = 40e9 / a.ngn_usd_avg[2023] / 1e6, 52e9 / a.ngn_usd_avg[2024] / 1e6; dusd = usd1 / usd0 - 1
fig, ax = plt.subplots(figsize=(10, 5.2))
vals = [nom * 100, real * 100, dusd * 100]; labs = ["Naira revenue\n(nominal)", "Real revenue\n(deflated by CPI)", "Revenue in\nUS dollars"]
bars = ax.bar(labs, vals, color=[TEAL, GOLD, RUST], width=.55); ax.axhline(0, color=SLATE, lw=1)
for b, v in zip(bars, vals): ax.text(b.get_x() + b.get_width() / 2, v + (2 if v > 0 else -5), f"{v:+.1f}%", ha="center", fontsize=15, fontweight="bold", color=INK)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.0f}%")); ax.set_ylim(-55, 40)
ax.set(title="FY2024 vs FY2023: 'sales up 30%' — or down 2%, or down 43%?")
note(fig, f"Illustrative firm: ₦40bn → ₦52bn. CPI: 2024 average inflation {infl*100:.1f}% (World Bank/NBS). "
          f"₦/$ annual averages {a.ngn_usd_avg[2023]:,.0f} (2023) and {a.ngn_usd_avg[2024]:,.0f} (2024), World Bank PA.NUS.FCRF.")
save(fig, "s01", "f07")
print(f"F07: nominal {nom:.4f} real {real:.4f}  usd {usd0:.1f}m -> {usd1:.1f}m ({dusd:.4f})")
