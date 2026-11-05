# =============================================================================
# EEGB · Session 6 · AD–AS in a Shock-Prone World
# Replication script — regenerates every chart in the Session 6 deck (Python)
# Data: data/ng_macro_monthly.csv (stylised Nigerian macro series, 2015–2025)
# Run from the project root:  python sessions/s06/python/s06_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
old = m[m.date < "2025-01-01"].copy()          # keep one CPI base for like-for-like comparisons

# --- F01 · Demand shock vs supply shock in the AD–AS diagram ------------------------------
q = np.linspace(0, 10, 100)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
for ax, kind in zip(axes, ["demand", "supply"]):
    as0, ad0 = 2 + 0.6 * q, 8 - 0.6 * q
    ax.plot(q, as0, color=SLATE, lw=2.5); ax.plot(q, ad0, color=TEAL, lw=2.5)
    ax.text(9.6, as0[-1], "AS", color=SLATE, fontsize=13, fontweight="bold")
    ax.text(9.6, ad0[-1] - .2, "AD", color=TEAL, fontsize=13, fontweight="bold")
    if kind == "demand":
        ad1 = 9.5 - 0.6 * q
        ax.plot(q, ad1, color=TEAL, lw=2.5, ls="--"); ax.text(0.4, 9.75, "new AD", color=TEAL, fontsize=13, fontweight="bold")
        e0, e1 = (5, 5), (6.25, 5.75)
        ax.set_title("Demand shock: prices UP, output UP", fontsize=13)
    else:
        as1 = 3.5 + 0.6 * q
        ax.plot(q, as1, color=RUST, lw=2.5, ls="--"); ax.text(4.6, 7.4, "new AS", color=RUST, fontsize=13, fontweight="bold")
        e0, e1 = (5, 5), (3.75, 5.75)
        ax.set_title("Supply shock: prices UP, output DOWN", fontsize=13)
    for (x, y), c in [(e0, NAVY), (e1, GOLD)]:
        ax.scatter(x, y, s=90, color=c, zorder=4)
        ax.plot([x, x], [0, y], color=c, ls=":", lw=1.2); ax.plot([0, x], [y, y], color=c, ls=":", lw=1.2)
    ax.annotate("", xy=e1, xytext=e0, arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, 10); ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    ax.set_xlabel("Real output (GDP)"); ax.set_ylabel("Price level")
fig.suptitle("Same rise in prices, opposite news for output", x=0.01, ha="left", fontsize=16, fontweight="bold", color=NAVY)
fig.tight_layout(); save(fig, "s06", "f01")

# --- F02 · The food–core gap: a supply-shock signature ------------------------------------
gap = old.food_inflation - old.core_inflation
fig, ax = plt.subplots()
ax.bar(old.date, gap, width=25, color=np.where(gap > 0, GOLD, TEAL))
ax.axhline(0, color=INK, lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:+.0f} pts"))
ax.set(title=f"Food inflation ran ahead of core almost every month (average gap {gap.mean():+.1f} pts)",
       ylabel="Food minus core inflation")
note(fig); save(fig, "s06", "f02")

# --- F03 · Exchange-rate pass-through: naira depreciation vs inflation ---------------------
d = m.set_index("date")
dep = 100 * (d.official_fx_ngn_usd / d.official_fx_ngn_usd.shift(12) - 1)
best = None
for lag in range(0, 13):
    x, y = dep.shift(lag), d.headline_inflation
    ok = x.notna() & y.notna() & (d.index < "2025-01-01")
    r = np.corrcoef(x[ok], y[ok])[0, 1]
    if best is None or r > best[1]: best = (lag, r)
lag, r = best
fig, ax = plt.subplots()
ax2 = ax.twinx()
ax.plot(dep.index, dep, color=RUST, lw=2.2, label="Naira depreciation vs a year ago (left)")
ax2.plot(d.index, d.headline_inflation, color=NAVY, lw=2.8, label="Headline inflation (right)")
ax.set_ylabel("Depreciation, % y/y", color=RUST); ax2.set_ylabel("Inflation, % y/y", color=NAVY)
ax2.grid(False); ax2.spines["right"].set_visible(True)
ax.axvline(pd.Timestamp("2025-01-01"), color=SLATE, ls="--", lw=1)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left")
ax.set(title=f"A weaker naira shows up in prices about {lag} months later (r = {r:.2f} at that lag)")
note(fig); save(fig, "s06", "f03")

# --- F04 · Stagflation: inflation up while activity falls ------------------------------------
periods = [("2015-01-01", "2019-12-01", "2015–19", SLATE), ("2020-01-01", "2022-12-01", "2020–22", TEAL),
           ("2023-01-01", "2024-12-01", "2023–24 reforms", RUST)]
fig, ax = plt.subplots()
for a, b, lab, c in periods:
    s = old[(old.date >= a) & (old.date <= b)]
    ax.scatter(s.pmi, s.headline_inflation, color=c, alpha=.75, s=45, label=f"{lab}: avg PMI {s.pmi.mean():.1f}, avg inflation {s.headline_inflation.mean():.1f}%")
ax.axvline(50, color=INK, ls="--", lw=1)
ax.text(50.2, 8, "PMI 50 = no change", fontsize=11, color=INK)
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(loc="upper left", fontsize=11)
ax.set(title="2023–24: inflation doubled while activity stalled near PMI 50 — a supply-shock signature",
       xlabel="Purchasing Managers' Index", ylabel="Headline inflation")
note(fig); save(fig, "s06", "f04")

# --- F05 · How inflation is measured: mean, median and trimmed mean ---------------------------
# Illustrative one-month basket (seeded): 12 items, weights and monthly price changes
rng = np.random.default_rng(6)
items = ["Bread & cereals", "Yam & tubers", "Meat & fish", "Vegetables", "Rent", "Electricity",
         "Petrol & transport", "Clothing", "Health", "Education", "Phone & data", "Restaurants"]
w = np.array([18, 9, 10, 8, 12, 5, 9, 7, 5, 6, 5, 6], float); w /= w.sum()
chg = np.array([3.4, 4.8, 2.6, 6.2, 1.4, 0.6, 9.5, 1.1, 1.6, 0.9, 0.4, 2.2])
order = np.argsort(chg); cw = np.cumsum(w[order])
keep = (cw - w[order] >= 0.15) & (cw <= 0.85 + 1e-9)
trim = np.sum(chg[order][keep] * w[order][keep]) / w[order][keep].sum()
mean = np.sum(w * chg); med = chg[order][np.searchsorted(cw, 0.5)]
fig, ax = plt.subplots()
cols = [GOLD if k else "#C9D2DC" for k in keep]
ax.barh(np.array(items)[order], chg[order], color=cols)
for v, lab, c in [(mean, f"weighted mean {mean:.1f}%", NAVY), (trim, f"trimmed mean {trim:.1f}%", TEAL), (med, f"weighted median {med:.1f}%", RUST)]:
    ax.axvline(v, color=c, lw=2.2, ls="--"); ax.text(6.0, 2.2 - [mean, trim, med].index(v) * 1.0, lab, color=c, fontsize=12, fontweight="bold")
ax.set_xlim(0, 11)
ax.set(title="Trimmed mean: drop the most extreme price moves, average the middle 70%",
       xlabel="Price change this month (%)  — grey items are trimmed")
note(fig, "Illustrative basket generated in the script; not NBS data."); save(fig, "s06", "f05")

# --- F06 · Persistence: this year's inflation vs last year's ---------------------------------
s = old.copy(); s["lag12"] = s.headline_inflation.shift(12); s = s.dropna(subset=["lag12"])
X = np.column_stack([np.ones(len(s)), s.lag12]); b = np.linalg.lstsq(X, s.headline_inflation, rcond=None)[0]
fig, ax = plt.subplots()
ax.scatter(s.lag12, s.headline_inflation, color=TEAL, alpha=.7)
xx = np.linspace(s.lag12.min(), s.lag12.max(), 50)
ax.plot(xx, b[0] + b[1] * xx, color=GOLD, lw=3, label=f"fitted line: slope {b[1]:.2f}")
ax.plot(xx, xx, color=SLATE, ls="--", lw=1.2, label="45° line: inflation unchanged")
ax.legend(loc="upper left")
ax.set(title=f"Inflation is sticky: last year's rate is the best single guide to this year's (slope {b[1]:.2f})",
       xlabel="Inflation 12 months earlier (%)", ylabel="Inflation now (%)")
note(fig); save(fig, "s06", "f06")

# --- F07 · The expectations-augmented Phillips curve -----------------------------------------
u = np.linspace(2, 10, 100)
fig, ax = plt.subplots()
for pe, c, lab in [(10, TEAL, "Expected inflation 10%"), (20, GOLD, "Expected inflation 20%"), (30, RUST, "Expected inflation 30%")]:
    ax.plot(u, pe + 2.2 * (6 - u), color=c, lw=2.8, label=lab)
ax.axvline(6, color=SLATE, ls=":", lw=1.2); ax.text(6.1, 3, "natural level\nof slack", color=SLATE, fontsize=11)
ax.legend(loc="upper right")
ax.set(title="When expectations rise, the whole curve shifts up: same slack, higher inflation",
       xlabel="Slack in the economy (unemployment / spare capacity)", ylabel="Inflation (%)")
ax.set_ylim(0, 42)
note(fig, "Conceptual diagram."); save(fig, "s06", "f07")

if __name__ == "__main__":
    pk = old.loc[old.headline_inflation.idxmax()]
    print(f"peak inflation {pk.headline_inflation:.1f} in {pk.date:%b %Y}; food-core gap mean {gap.mean():.2f}")
    print(f"pass-through best lag {lag}, r={r:.2f}; persistence slope {b[1]:.2f}, intercept {b[0]:.2f}")
    print(f"basket mean {mean:.2f} trimmed {trim:.2f} median {med:.2f}")
    for a, bb, lab, c in periods:
        s2 = old[(old.date >= a) & (old.date <= bb)]
        print(lab, round(s2.pmi.mean(), 1), round(s2.headline_inflation.mean(), 1))
    print("dep at 2024-06:", round(dep.loc["2024-06-01"], 1), "max dep:", round(dep.max(), 1), dep.idxmax())
