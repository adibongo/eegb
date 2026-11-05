# =============================================================================
# EEGB · Session 9 · Fiscal Policy, Debt & Sovereign Risk
# Replication script — regenerates every chart in the Session 9 deck (Python)
# Data: data/fgn_fiscal_annual.csv (stylised Federal Government finances, 2010–2025, ₦ trillion)
# Run from the project root:  python sessions/s09/python/s09_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
f = pd.read_csv("data/fgn_fiscal_annual.csv")
f["d"] = f.total_public_debt_ntn / f.nominal_gdp_ntn                 # debt-to-GDP ratio (a share)
f["g"] = f.nominal_gdp_ntn.pct_change()                               # nominal GDP growth
f["r"] = f.interest_payments_ntn / f.total_public_debt_ntn.shift(1)   # effective interest rate on last year's debt
f["pb_gdp"] = f.primary_balance_ntn / f.nominal_gdp_ntn               # primary balance as a share of GDP

# --- F01 · Debt is modest against GDP; revenue is tiny -----------------------------
fig, ax = plt.subplots()
ax.plot(f.year, f.debt_to_gdp_pct, color=NAVY, lw=3, marker="o", label="Public debt (% of GDP)")
ax.plot(f.year, f.revenue_to_gdp_pct, color=GOLD, lw=3, marker="o", label="FGN revenue (% of GDP)")
ax.text(2025.2, f.debt_to_gdp_pct.iloc[-1], f"{f.debt_to_gdp_pct.iloc[-1]:.0f}%", color=NAVY, va="center", fontsize=12)
ax.text(2025.2, f.revenue_to_gdp_pct.iloc[-1], f"{f.revenue_to_gdp_pct.iloc[-1]:.1f}%", color=GOLD, va="center", fontsize=12)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left"); ax.set_xlim(2009.5, 2026.3)
ax.set(title="Debt looks moderate next to GDP — the problem is how little revenue the state collects",
       ylabel="Share of nominal GDP")
note(fig); save(fig, "s09", "f01")

# --- F02 · Interest bill as a share of revenue ----------------------------------------------
fig, ax = plt.subplots()
cols = [RUST if v >= 60 else TEAL for v in f.interest_to_revenue_pct]
ax.bar(f.year, f.interest_to_revenue_pct, color=cols)
for x, v in zip(f.year, f.interest_to_revenue_pct):
    ax.text(x, v + 1.5, f"{v:.0f}", ha="center", fontsize=10, color=INK)
ax.axhline(100, color=INK, lw=1, ls="--"); ax.text(2010, 102, "every naira of revenue", fontsize=11, color=INK)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.set_ylim(0, 112)
ax.set(title="From 16 kobo to over 90 kobo of every revenue naira spent on interest",
       ylabel="Interest payments as % of FGN revenue")
note(fig); save(fig, "s09", "f02")

# --- F03 · Debt measured against revenue, not GDP ---------------------------------------------
f["debt_to_rev"] = f.total_public_debt_ntn / f.fgn_revenue_ntn
fig, ax = plt.subplots()
ax.plot(f.year, f.debt_to_rev, color=RUST, lw=3, marker="o")
ax.fill_between(f.year, f.debt_to_rev, color=RUST, alpha=.12)
i = f.debt_to_rev.idxmax()
ax.annotate(f"Peak: debt = {f.debt_to_rev[i]:.1f}× a year's revenue ({f.year[i]})", xy=(f.year[i], f.debt_to_rev[i]),
            xytext=(2011, f.debt_to_rev[i] * 0.9), arrowprops=dict(arrowstyle="->", color=NAVY), fontsize=12, color=NAVY)
ax.set(title="How many years of revenue would it take to repay the debt?", ylabel="Public debt ÷ FGN revenue (years)")
note(fig); save(fig, "s09", "f03")

# --- F04 · r versus g -------------------------------------------------------------------------
fig, ax = plt.subplots()
ax.plot(f.year, 100 * f.r, color=RUST, lw=3, marker="o", label="r: effective interest rate on debt")
ax.plot(f.year, 100 * f.g, color=TEAL, lw=3, marker="o", label="g: nominal GDP growth")
ax.fill_between(f.year, 100 * f.r, 100 * f.g, where=(f.g > f.r), color=TEAL, alpha=.15, interpolate=True, label="g > r: debt ratio drifts down")
ax.fill_between(f.year, 100 * f.r, 100 * f.g, where=(f.r > f.g), color=RUST, alpha=.15, interpolate=True, label="r > g: debt ratio drifts up")
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left", fontsize=11)
ax.set(title="Inflation has kept nominal growth above the interest rate — the debt ratio's friend",
       ylabel="Per cent per year")
note(fig); save(fig, "s09", "f04")

# --- F05 · Debt dynamics decomposition --------------------------------------------------------
dd = f.dropna(subset=["r"]).copy()
dd["d_prev"] = f.d.shift(1)
dd["delta"] = dd.d - dd.d_prev
dd["interest_growth"] = (dd.r - dd.g) / (1 + dd.g) * dd.d_prev
dd["primary"] = -dd.pb_gdp
dd["residual"] = dd.delta - dd.interest_growth - dd.primary
fig, ax = plt.subplots()
x = dd.year.values
pos_bottom = np.zeros(len(dd)); neg_bottom = np.zeros(len(dd))
for col, lab, c in [("interest_growth", "Interest–growth effect (r − g)", TEAL), ("primary", "Primary deficit", GOLD),
                    ("residual", "Other: FX revaluation, CBN overdraft securitisation, sub-national debt", SLATE)]:
    v = 100 * dd[col].values
    b = np.where(v >= 0, pos_bottom, neg_bottom)
    ax.bar(x, v, bottom=b, color=c, label=lab, width=.7)
    pos_bottom += np.where(v >= 0, v, 0); neg_bottom += np.where(v < 0, v, 0)
ax.scatter(x, 100 * dd.delta, color=NAVY, zorder=4, s=40, label="Total change in debt/GDP")
ax.axhline(0, color=INK, lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:+.0f}"))
ax.legend(loc="upper left", fontsize=10)
ax.set(title="Why debt/GDP moved: not the deficit, but revaluations and one-off transfers",
       ylabel="Change in debt/GDP (percentage points)")
note(fig); save(fig, "s09", "f05")

# --- F06 · Three scenarios for the next decade ------------------------------------------------
def simulate(d0, r, g, pb, years=10, shock=None):
    path = [d0]
    for t in range(1, years + 1):
        d = (1 + r) / (1 + g) * path[-1] - pb
        if shock and t == shock[0]: d += shock[1]
        path.append(d)
    return np.array(path)
d0 = f.d.iloc[-1]
yrs = np.arange(2025, 2036)
scen = {"Reform: g 20%, r 13%, primary surplus 0.5% of GDP": (simulate(d0, .13, .20, .005), TEAL),
        "Baseline: g 17%, r 15%, primary deficit 1% of GDP": (simulate(d0, .15, .17, -.01), NAVY),
        "Adverse: g 14%, r 17%, deficit 2% + 2027 FX shock": (simulate(d0, .17, .14, -.02, shock=(2, .08)), RUST)}
fig, ax = plt.subplots()
for lab, (p, c) in scen.items():
    ax.plot(yrs, 100 * p, color=c, lw=3, label=lab)
    ax.text(2035.2, 100 * p[-1], f"{100 * p[-1]:.0f}%", color=c, va="center", fontsize=12, fontweight="bold")
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left", fontsize=11); ax.set_xlim(2024.5, 2036.5)
ax.set(title="Same starting debt, three futures: r, g and the primary balance decide the path",
       ylabel="Public debt (% of GDP)")
note(fig); save(fig, "s09", "f06")

# --- F07 · The oil share of revenue ------------------------------------------------------------
fig, ax = plt.subplots()
oil = f.fgn_revenue_ntn * f.oil_share_of_revenue; non = f.fgn_revenue_ntn - oil
ax.bar(f.year, oil, color=GOLD, label="Oil revenue")
ax.bar(f.year, non, bottom=oil, color=TEAL, label="Non-oil revenue (taxes, fees, other)")
ax2 = ax.twinx(); ax2.plot(f.year, 100 * f.oil_share_of_revenue, color=NAVY, lw=2.5, marker="o", label="Oil share (right)")
ax2.set_ylim(0, 100); ax2.yaxis.set_major_formatter(FuncFormatter(pct)); ax2.grid(False); ax2.spines["right"].set_visible(True)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:g}tn"))
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=11)
ax.set(title="Revenue grew in naira after 2022 — but oil still supplies over a third", ylabel="FGN revenue (₦ trillion)")
note(fig); save(fig, "s09", "f07")

# --- key numbers used on the slides -------------------------------------------------------------
print(f.loc[f.year.isin([2010, 2021, 2022, 2025]), ["year", "debt_to_gdp_pct", "revenue_to_gdp_pct", "interest_to_revenue_pct", "debt_to_rev"]].round(2))
print("r and g 2025:", round(100 * f.r.iloc[-1], 1), round(100 * f.g.iloc[-1], 1))
print(dd[["year", "delta", "interest_growth", "primary", "residual"]].assign(**{c: lambda x, c=c: (100 * x[c]).round(1) for c in ["delta", "interest_growth", "primary", "residual"]}).to_string())
for lab, (p, c) in scen.items(): print(lab, round(100 * p[-1], 1))
