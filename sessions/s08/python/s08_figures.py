# =============================================================================
# EEGB · Session 8 · Monetary Policy from QE to QT
# Replication script — regenerates every chart in the Session 8 deck (Python)
# Data: data/ng_macro_monthly.csv and data/global_policy_rates.csv (stylised)
# Run from the project root:  python sessions/s08/python/s08_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
pr = pd.read_csv("data/global_policy_rates.csv", parse_dates=["date"])
names = {"us_fed": "US Fed", "euro_area_ecb": "ECB", "uk_boe": "Bank of England", "nigeria_cbn": "CBN (Nigeria)",
         "south_africa_sarb": "SARB (S. Africa)", "ghana_bog": "Bank of Ghana", "kenya_cbk": "CBK (Kenya)"}
cols = {"us_fed": NAVY, "euro_area_ecb": SKY, "uk_boe": SLATE, "nigeria_cbn": RUST, "south_africa_sarb": OLIVE,
        "ghana_bog": GOLD, "kenya_cbk": TEAL}

# --- F01 · A global tightening cycle ---------------------------------------------------
fig, ax = plt.subplots()
for c in names:
    ax.step(pr.date, pr[c], where="post", color=cols[c], lw=3 if c == "nigeria_cbn" else 2, label=names[c])
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(ncol=2, loc="upper left", fontsize=11)
ax.set(title="From near-zero to the fastest hikes in decades: 2022–24 was a global tightening",
       ylabel="Policy rate")
note(fig); save(fig, "s08", "f01")

# --- F02 · How much each central bank tightened ----------------------------------------
low = pr[(pr.date >= "2020-01-01") & (pr.date <= "2022-06-01")][list(names)].min()
high = pr[pr.date >= "2022-01-01"][list(names)].max()
hike = (high - low).sort_values()
fig, ax = plt.subplots()
bars = ax.barh([names[c] for c in hike.index], hike.values, color=[cols[c] for c in hike.index])
for b, (c, v) in zip(bars, hike.items()):
    ax.text(v + .2, b.get_y() + b.get_height() / 2, f"+{v:.2f} pts  ({low[c]:.2f}% → {high[c]:.2f}%)", va="center", fontsize=11.5)
ax.set_xlim(0, hike.max() * 1.6)
ax.set(title="Size of the tightening: from each bank's post-COVID low to its peak",
       xlabel="Increase in policy rate (percentage points)")
note(fig); save(fig, "s08", "f02")

# --- F03 · Policy rate, interbank rate and inflation in Nigeria --------------------------
fig, ax = plt.subplots()
ax.plot(m.date, m.headline_inflation, color=GOLD, lw=2.4, label="Headline inflation")
ax.step(m.date, m.mpr, where="post", color=NAVY, lw=3, label="Monetary policy rate (MPR)")
ax.plot(m.date, m.interbank_rate, color=TEAL, lw=1.6, alpha=.9, label="Interbank rate")
ax.axvline(pd.Timestamp("2025-01-01"), color=SLATE, ls="--", lw=1); ax.text(pd.Timestamp("2025-01-15"), 4, "CPI\nrebased", color=SLATE, fontsize=10)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left")
ax.set(title="The CBN chased inflation from behind until 2024", ylabel="Percent")
note(fig); save(fig, "s08", "f03")

# --- F04 · Liquidity: interbank minus MPR ------------------------------------------------
spread = m.interbank_rate - m.mpr
fig, ax = plt.subplots()
ax.fill_between(m.date, spread, 0, where=spread < 0, color=TEAL, alpha=.45, label="Interbank below MPR: cash is plentiful")
ax.fill_between(m.date, spread, 0, where=spread >= 0, color=RUST, alpha=.45, label="Interbank above MPR: cash is tight")
ax.plot(m.date, spread, color=NAVY, lw=1.6); ax.axhline(0, color=INK, lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:+.0f} pts")); ax.legend(loc="lower left", fontsize=11)
ax.set(title="The rate banks actually pay each other often strays far from the policy rate",
       ylabel="Interbank rate minus MPR")
note(fig); save(fig, "s08", "f04")

# --- F05 · Transmission: money and credit after the policy moves --------------------------
fig, ax = plt.subplots()
ax.plot(m.date, m.m2_growth_yoy, color=TEAL, lw=2.4, label="Broad money (M2) growth")
ax.plot(m.date, m.private_credit_growth_yoy, color=GOLD, lw=2.4, label="Private-sector credit growth")
ax2 = ax.twinx(); ax2.step(m.date, m.mpr, where="post", color=NAVY, lw=2.2, ls="--", label="MPR (right)")
ax2.grid(False); ax2.spines["right"].set_visible(True); ax2.set_ylabel("MPR (%)", color=NAVY)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.set_ylabel("Growth, % y/y")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=11)
ax.axvspan(pd.Timestamp("2023-06-01"), pd.Timestamp("2024-06-01"), color=GOLD, alpha=.12)
ax.text(pd.Timestamp("2021-06-01"), 40, "Jun 2023–Jun 2024:\ndevaluation revalues\nFX balances →", fontsize=10.5, color=NAVY)
ax.set(title="Money and credit growth peaked in 2023–24, then slowed as tight policy bit")
note(fig); save(fig, "s08", "f05")

# --- F06 · An illustrative Taylor rule for Nigeria ----------------------------------------
target, neutral_real = 9.0, 2.0          # assumptions: top of a 6–9% target band; neutral real rate 2%
old = m[m.date < "2025-01-01"].copy()
gap = old.pmi - 50                        # crude activity gap: PMI above 50 = economy running hot
old["taylor"] = neutral_real + old.headline_inflation + 0.5 * (old.headline_inflation - target) + 0.5 * gap
fig, ax = plt.subplots()
ax.plot(old.date, old.taylor, color=GOLD, lw=2.6, label="Illustrative Taylor-rule rate")
ax.step(old.date, old.mpr, where="post", color=NAVY, lw=3, label="Actual MPR")
ax.fill_between(old.date, old.mpr, old.taylor, where=old.taylor > old.mpr, color=RUST, alpha=.18, label="Policy looser than the rule")
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left")
last = old.iloc[-1]
ax.set(title=f"By the rule, policy was too loose for most of the decade (Dec 2024: rule {last.taylor:.0f}% vs MPR {last.mpr:.1f}%)",
       ylabel="Percent")
note(fig, "Rule: rate = 2% + inflation + 0.5 × (inflation − 9%) + 0.5 × (PMI − 50). Illustrative assumptions; stylised data.")
save(fig, "s08", "f06")

# --- F07 · Interest differential vs the US: the carry for foreign investors -------------------
j = pr[["date", "us_fed"]].merge(m[["date", "mpr", "official_fx_ngn_usd"]], on="date")
j["diff"] = j.mpr - j.us_fed
j["dep_12m_ahead"] = 100 * (j.official_fx_ngn_usd.shift(-12) / j.official_fx_ngn_usd - 1)
fig, ax = plt.subplots()
ax.plot(j.date, j["diff"], color=TEAL, lw=2.8, label="CBN rate minus US Fed rate")
ax.plot(j.date, j.dep_12m_ahead, color=RUST, lw=2.2, ls="--", label="Naira depreciation over the NEXT 12 months")
ax.axhline(0, color=INK, lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}"))
ax.legend(loc="upper left")
ax.set(title="A big rate gap attracts dollars — unless the naira falls by more",
       ylabel="Percentage points / percent")
note(fig); save(fig, "s08", "f07")

if __name__ == "__main__":
    print(hike.round(2)); print(low.round(2)); print(high.round(2))
    print("spread min/max", spread.min().round(2), m.date[spread.idxmin()].date(), spread.max().round(2), m.date[spread.idxmax()].date())
    print("M2 peak", m.m2_growth_yoy.max(), m.date[m.m2_growth_yoy.idxmax()].date(), "credit peak", m.private_credit_growth_yoy.max(), m.date[m.private_credit_growth_yoy.idxmax()].date())
    print("M2 last", m.m2_growth_yoy.iloc[-1], "credit last", m.private_credit_growth_yoy.iloc[-1])
    print("taylor share above mpr", round((old.taylor > old.mpr).mean(), 2), "Dec24 taylor", round(last.taylor, 1))
    print(j[["date", "diff", "dep_12m_ahead"]].iloc[[0, 24, 41, 48, 54, 60, 66, 72]].round(1).to_string())
    print("mpr 2023-06", m.loc[m.date == "2023-06-01", "mpr"].values, "infl 2024-06", m.loc[m.date == "2024-06-01", "headline_inflation"].values)
