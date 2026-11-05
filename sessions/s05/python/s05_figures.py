# =============================================================================
# EEGB · Session 5 · Market Failures & Government Intervention
# Replication script — regenerates every chart in the Session 5 deck (Python)
# Data: data/fuel_subsidy_incidence.csv (stylised household budgets by consumption decile)
# Run from the project root:  python sessions/s05/python/s05_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
h = pd.read_csv("data/fuel_subsidy_incidence.csv")
D = [f"D{k}" for k in h.decile]               # D1 = poorest 10% of households ... D10 = richest 10%

# Assumptions used throughout (stylised, stated on the slides)
FARE_RISE, FOOD_RISE = 0.50, 0.10              # transport fares +50%, food prices +10% after removal (indirect effects)
TRANSFER, TARGET_DECILES = 10_000, 4           # ₦10,000 a month to the poorest 40% of households

h["subsidy"] = h.petrol_litres_month * h.subsidy_per_litre_pre                 # ₦ per household per month
h["subsidy_share"] = 100 * h.subsidy / h.subsidy.sum()
h["subsidy_pct_budget"] = 100 * h.subsidy / h.monthly_spend_naira
h["direct_pct"] = 100 * h.petrol_litres_month * (h.pump_price_post - h.pump_price_pre) / h.monthly_spend_naira
h["indirect_pct"] = 100 * (h.transport_share * FARE_RISE + h.food_share * FOOD_RISE)
h["total_pct"] = h.direct_pct + h.indirect_pct
annual_subsidy = (h.subsidy * h.households_m * 1e6 * 12).sum() / 1e12            # ₦ trillion
transfer_cost = TARGET_DECILES * h.households_m.iloc[0] * 1e6 * TRANSFER * 12 / 1e12
universal = transfer_cost * 1e12 / (h.households_m.sum() * 1e6 * 12)               # same budget, everyone
h["net_none"] = -h.total_pct
h["net_targeted"] = -h.total_pct + np.where(h.decile <= TARGET_DECILES, 100 * TRANSFER / h.monthly_spend_naira, 0)
h["net_universal"] = -h.total_pct + 100 * universal / h.monthly_spend_naira
print(h[["decile", "subsidy", "subsidy_share", "subsidy_pct_budget", "direct_pct", "indirect_pct", "total_pct",
         "net_targeted", "net_universal"]].round(1).to_string())
print(f"annual household petrol subsidy ₦{annual_subsidy:.1f}tn; targeted transfer cost ₦{transfer_cost:.2f}tn "
      f"({100*transfer_cost/annual_subsidy:.0f}% of subsidy); universal equivalent ₦{universal:,.0f}/month")
print(f"top decile share {h.subsidy_share.iloc[-1]:.1f}%, bottom 40% share {h.subsidy_share.iloc[:4].sum():.1f}%, "
      f"ratio top/bottom ₦ {h.subsidy.iloc[-1]/h.subsidy.iloc[0]:.0f}x")

# --- F01 · A negative externality: the generator next door ---------------------------------------------
q = np.linspace(0, 10, 200)
fig, ax = plt.subplots()
ax.plot(q, 9 - 0.7 * q, color=NAVY, lw=3, label="Demand (private benefit)")
ax.plot(q, 1 + 0.5 * q, color=TEAL, lw=3, label="Private cost (fuel, maintenance)")
ax.plot(q, 3 + 0.5 * q, color=RUST, lw=3, ls="--", label="Social cost (+ noise, fumes, health)")
qm, qs = 8 / 1.2, 6 / 1.2
ax.fill_between(np.linspace(qs, qm, 50), 9 - 0.7 * np.linspace(qs, qm, 50), 3 + 0.5 * np.linspace(qs, qm, 50), color=RUST, alpha=.3,
                label="Deadweight loss from over-use")
for x, t, c, dx, dy, ha in [(qm, "Market\noutcome", TEAL, .2, -1.1, "left"), (qs, "Best for\nsociety", RUST, -.2, .5, "right")]:
    y = 9 - 0.7 * x; ax.scatter(x, y, s=80, color=c, zorder=5); ax.text(x + dx, y + dy, t, color=c, fontsize=12, fontweight="bold", ha=ha)
ax.annotate("", xy=(1.0, 3.5), xytext=(1.0, 1.5), arrowprops=dict(arrowstyle="<->", color=GOLD, lw=2))
ax.text(1.15, 2.3, "external cost =\nthe right tax", color=GOLD, fontsize=11)
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_xticks([]); ax.set_yticks([]); ax.legend(loc="upper right", fontsize=11)
ax.set(title="When users don't pay the full cost, the market produces too much of it",
       xlabel="Hours of generator use", ylabel="Naira per hour")
save(fig, "s05", "f01")

# --- F02 · Who received the petrol subsidy? -----------------------------------------------------------------
fig, ax = plt.subplots()
cols = [TEAL] * 4 + [SLATE] * 5 + [RUST]
ax.bar(D, h.subsidy_share, color=cols)
for i, v in enumerate(h.subsidy_share): ax.text(i, v + .6, f"{v:.0f}%", ha="center", fontsize=12, color=NAVY)
ax.yaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title=f"The richest 10% received {h.subsidy_share.iloc[-1]:.0f}% of the subsidy; the poorest 40% just {h.subsidy_share.iloc[:4].sum():.0f}%",
       xlabel="Households grouped by consumption: D1 = poorest 10% … D10 = richest 10%", ylabel="Share of total petrol subsidy")
note(fig); save(fig, "s05", "f02")

# --- F03 · Subsidy in naira vs as a share of the budget ------------------------------------------------------
fig, ax1 = plt.subplots()
ax1.bar(D, h.subsidy / 1000, color=SKY, label="Subsidy per household (₦'000 a month, left)")
ax1.set_ylabel("₦'000 per household per month")
ax2 = ax1.twinx()
ax2.plot(D, h.subsidy_pct_budget, "o-", color=NAVY, lw=3, label="As % of the household budget (right)")
ax2.yaxis.set_major_formatter(FuncFormatter(pct)); ax2.set_ylim(0, 14); ax2.grid(False); ax2.spines["right"].set_visible(True)
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax1.legend(h1 + h2, l1 + l2, loc="upper left")
ax1.set_title(f"A rich household got ₦{h.subsidy.iloc[-1]:,.0f} a month, a poor one ₦{h.subsidy.iloc[0]:,.0f}", loc="left")
note(fig); save(fig, "s05", "f03")

# --- F04 · The cost of removal, direct and indirect -------------------------------------------------------------
fig, ax = plt.subplots()
ax.bar(D, h.direct_pct, color=RUST, label="Direct: dearer petrol for cars & generators")
ax.bar(D, h.indirect_pct, bottom=h.direct_pct, color=GOLD, label="Indirect: transport fares +50%, food +10%")
for i, v in enumerate(h.total_pct): ax.text(i, v + .4, f"{v:.0f}%", ha="center", fontsize=12, color=NAVY)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left")
ax.set(title="Removal raised living costs for everyone — the poor mostly through fares and food",
       xlabel="D1 = poorest 10% … D10 = richest 10%", ylabel="Extra cost, % of monthly budget")
note(fig, "Pump price ₦185 → ₦617 per litre; indirect effects are stylised assumptions. Source: EEGB stylised teaching data.")
save(fig, "s05", "f04")

# --- F05 · Compensation: targeted vs universal ---------------------------------------------------------------------
fig, ax = plt.subplots()
w = .27; x = np.arange(10)
ax.bar(x - w, h.net_none, w, color=SLATE, label="No compensation")
ax.bar(x, h.net_universal, w, color=GOLD, label=f"Same budget, everyone: ₦{universal:,.0f}/month")
ax.bar(x + w, h.net_targeted, w, color=TEAL, label=f"Targeted: ₦{TRANSFER:,}/month to poorest 40%")
ax.axhline(0, color=INK, lw=1); ax.set_xticks(x, D)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper right", fontsize=11)
ax.set(title="A targeted cash transfer can leave the poorest better off — for a fraction of the subsidy's cost",
       xlabel="D1 = poorest 10% … D10 = richest 10%", ylabel="Net change, % of monthly budget")
ax.title.set_fontsize(14)
note(fig); save(fig, "s05", "f05")

# --- F06 · The fiscal arithmetic ----------------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.6))
items = {"Household petrol subsidy\n(per year, before removal)": annual_subsidy,
         f"Targeted transfer\n(₦{TRANSFER:,}/month × poorest 40%)": transfer_cost}
ax.barh(list(items)[::-1], list(items.values())[::-1], color=[TEAL, RUST])
for i, v in enumerate(list(items.values())[::-1]): ax.text(v + .08, i, f"₦{v:.1f} trillion", va="center", fontsize=14, color=NAVY)
ax.set_xlim(0, annual_subsidy * 1.3)
ax.set(title=f"Compensating the poor costs about {100*transfer_cost/annual_subsidy:.0f}% of what the subsidy cost", xlabel="₦ trillion per year")
note(fig); save(fig, "s05", "f06")
