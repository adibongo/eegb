# =============================================================================
# EEGB · Session 14 · Country Risk & Scenario Planning
# Replication script — regenerates every chart in the Session 14 deck (Python)
# Data: data/country_risk_panel.csv (stylised indicators for eight African markets)
# Run from the project root:  python sessions/s14/python/s14_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
cr = pd.read_csv("data/country_risk_panel.csv").set_index("country")

# ---- The scoring model ------------------------------------------------------------------------
# Each indicator is turned into a z-score where HIGHER = RISKIER, then weighted into four pillars.
RISKIER_IF_HIGH = {"inflation_pct": 1, "public_debt_gdp_pct": 1, "reserves_months_imports": -1, "current_account_gdp_pct": -1,
                   "political_stability_wgi": -1, "regulatory_quality_wgi": -1, "fx_depreciation_12m": 1,
                   "eurobond_spread_pct": 1, "real_growth_pct": -1}
PILLARS = {"Macro": ["inflation_pct", "real_growth_pct"], "External": ["reserves_months_imports", "current_account_gdp_pct", "fx_depreciation_12m"],
           "Fiscal & market": ["public_debt_gdp_pct", "eurobond_spread_pct"], "Political & policy": ["political_stability_wgi", "regulatory_quality_wgi"]}
LABELS = {"inflation_pct": "Inflation", "real_growth_pct": "Growth", "reserves_months_imports": "Reserves (months)",
          "current_account_gdp_pct": "Current account", "fx_depreciation_12m": "FX depreciation", "public_debt_gdp_pct": "Public debt",
          "eurobond_spread_pct": "Eurobond spread", "political_stability_wgi": "Political stability", "regulatory_quality_wgi": "Regulatory quality"}
z = pd.DataFrame({k: s * (cr[k] - cr[k].mean()) / cr[k].std() for k, s in RISKIER_IF_HIGH.items()})
pill = pd.DataFrame({p: z[cols].mean(axis=1) for p, cols in PILLARS.items()})


def score(w):
    """Weighted pillar score, rescaled to 0–100 (100 = riskiest in the group)."""
    s = sum(pill[p] * wt for p, wt in w.items()) / sum(w.values())
    return 100 * (s - s.min()) / (s.max() - s.min())


W = {"Base (equal)": {"Macro": 1, "External": 1, "Fiscal & market": 1, "Political & policy": 1},
     "Lender (external & fiscal)": {"Macro": .5, "External": 2, "Fiscal & market": 2, "Political & policy": .5},
     "Investor (macro & policy)": {"Macro": 2, "External": .5, "Fiscal & market": .5, "Political & policy": 2}}
scores = pd.DataFrame({k: score(w) for k, w in W.items()})
base = scores["Base (equal)"].sort_values()

# --- F01 · Heatmap of risk z-scores -------------------------------------------------------------------
order = base.index
cols = [c for p in PILLARS.values() for c in p]
fig, ax = plt.subplots(figsize=(11, 5.6))
im = ax.imshow(z.loc[order, cols].values, cmap="RdYlGn_r", vmin=-2, vmax=2, aspect="auto")
ax.set_xticks(range(len(cols)), [LABELS[c] for c in cols], rotation=30, ha="right")
ax.set_yticks(range(len(order)), order); ax.grid(False)
for i, c_ in enumerate(order):
    for j, k in enumerate(cols):
        ax.text(j, i, f"{cr.loc[c_, k]:g}", ha="center", va="center", fontsize=10, color=INK)
cb = fig.colorbar(im, ax=ax, shrink=.8); cb.set_label("Risk z-score (red = riskier)")
ax.set_title("Eight markets, nine indicators: numbers shown, colour = risk relative to the group", loc="left"); fig.subplots_adjust(bottom=0.3)
note(fig); save(fig, "s14", "f01")

# --- F02 · Composite score, base weights -----------------------------------------------------------
fig, ax = plt.subplots()
ax.barh(base.index, base.values, color=[RUST if v > 66 else GOLD if v > 33 else TEAL for v in base.values])
for i, v in enumerate(base.values): ax.text(v + 1.5, i, f"{v:.0f}", va="center", fontsize=12, fontweight="bold", color=NAVY)
ax.set_xlim(0, 112)
ax.set(title="Composite country-risk score with equal pillar weights (0 = safest, 100 = riskiest in the group)",
       xlabel="Risk score")
ax.title.set_fontsize(14)
note(fig); save(fig, "s14", "f02")

# --- F03 · Sensitivity to weights: does the ranking hold? ---------------------------------------------
ranks = scores.rank()
fig, ax = plt.subplots()
xs = range(len(W))
for c_ in ranks.index:
    hl = c_ == "Nigeria"
    ax.plot(xs, ranks.loc[c_], marker="o", lw=3.5 if hl else 1.6, ms=9 if hl else 6, color=RUST if hl else SLATE, alpha=1 if hl else .7)
    ax.text(len(W) - 1 + .07, ranks.loc[c_].iloc[-1], c_, va="center", fontsize=11, color=RUST if hl else INK,
            fontweight="bold" if hl else "normal")
ax.set_xticks(list(xs), list(W.keys())); ax.set_xlim(-.2, len(W) - .3)
ax.set_yticks(range(1, 9)); ax.set_ylabel("Rank (8 = riskiest)")
ax.set(title="Change the weights and the ranking moves — the middle of the table is fragile")
note(fig); save(fig, "s14", "f03")

# --- F04 · Risk vs opportunity map --------------------------------------------------------------------
opp = cr.population_m * (1 + cr.real_growth_pct / 100) ** 5
fig, ax = plt.subplots()
ax.scatter(base.reindex(cr.index), opp, s=cr.population_m * 4, color=TEAL, alpha=.6, edgecolor=NAVY)
for c_ in cr.index:
    ax.text(base[c_] + 2.5, opp[c_], c_, fontsize=11, va="center", color=RUST if c_ == "Nigeria" else INK)
ax.set_yscale("log"); ax.axvline(50, color=SLATE, ls="--", lw=1)
ax.set(title="Big markets are not always safe markets: opportunity vs risk",
       xlabel="Risk score (base weights)", ylabel="Market size in 5 years (population × growth, log scale)")
note(fig); save(fig, "s14", "f04")

# ---- A simple Nigeria plan model -------------------------------------------------------------------
# A consumer-goods subsidiary: ₦120bn revenue, 45% of costs imported in US$, 15% EBITDA margin today.
REV, COST_SHARE_IMP, MARGIN = 120.0, 0.45, 0.15
def plan_ebitda(fx_change, demand_growth, price_pass, rate_rise):
    """Next-year EBITDA (₦ bn) given FX move (+ = naira weaker), real demand growth, share of cost passed on, rate rise (pts)."""
    cost = REV * (1 - MARGIN)
    imp = cost * COST_SHARE_IMP * (1 + fx_change); dom = cost * (1 - COST_SHARE_IMP) * 1.15
    new_cost = imp + dom
    price = 1 + price_pass * (new_cost / cost - 1)
    vol = (1 + demand_growth) * price ** -0.8                        # demand elasticity −0.8
    rev = REV * price * vol
    finance = 4.0 * (1 + rate_rise / 25)                              # ₦4bn interest bill scales with rates
    return rev - new_cost * vol - (finance - 4.0)

SCEN = pd.DataFrame({"Reform pays off": [0.35, 0.05, 0.10, 0.80, -3], "Muddle through": [0.45, 0.25, 0.01, 0.60, 0],
                     "Relapse": [0.20, 0.80, -0.04, 0.40, 6]}, index=["prob", "fx_change", "demand_growth", "price_pass", "rate_rise"]).T
SCEN["ebitda"] = [plan_ebitda(r.fx_change, r.demand_growth, r.price_pass, r.rate_rise) for _, r in SCEN.iterrows()]
ev = (SCEN.prob * SCEN.ebitda).sum()
today = REV * MARGIN

# --- F05 · Scenario tree outcomes --------------------------------------------------------------------
fig, ax = plt.subplots()
cols5 = [TEAL, GOLD, RUST]
ax.bar(SCEN.index, SCEN.ebitda, color=cols5, width=.55)
for i, (k, r) in enumerate(SCEN.iterrows()):
    ax.text(i, r.ebitda + (.6 if r.ebitda >= 0 else -.6), f"₦{r.ebitda:.1f}bn\np = {r.prob:.0%}", ha="center",
            va="bottom" if r.ebitda >= 0 else "top", fontsize=12, color=NAVY, fontweight="bold")
ax.axhline(today, color=SLATE, ls="--"); ax.text(2.3, today + .4, f"today ₦{today:.0f}bn", color=SLATE, ha="right", fontsize=11)
ax.axhline(ev, color=NAVY, ls=":"); ax.text(-.25, ev + .4, f"probability-weighted ₦{ev:.1f}bn", color=NAVY, fontsize=11)
ax.axhline(0, color=INK, lw=1)
ax.set_ylim(min(0, SCEN.ebitda.min()) - 3, max(SCEN.ebitda.max(), today) + 4)
ax.set(title="Next-year EBITDA of the Nigeria plan under three scenarios", ylabel="EBITDA (₦ bn)")
note(fig, "Illustrative plan model: ₦120bn revenue, 45% of costs imported, elasticity −0.8. Scenario values are teaching assumptions.")
save(fig, "s14", "f05")

# --- F06 · Stress test: one shock at a time (tornado) ---------------------------------------------------
basecase = plan_ebitda(*SCEN.loc["Muddle through", ["fx_change", "demand_growth", "price_pass", "rate_rise"]])
mb = SCEN.loc["Muddle through"]
shocks = {"Naira 30% weaker": dict(fx_change=mb.fx_change + .30), "Demand 5 pts lower": dict(demand_growth=mb.demand_growth - .05),
          "Pass-through 30 pts lower": dict(price_pass=mb.price_pass - .30), "Rates +5 points": dict(rate_rise=mb.rate_rise + 5)}
imp = {}
for k, ch in shocks.items():
    args = dict(fx_change=mb.fx_change, demand_growth=mb.demand_growth, price_pass=mb.price_pass, rate_rise=mb.rate_rise); args.update(ch)
    imp[k] = plan_ebitda(**args) - basecase
imp = pd.Series(imp).sort_values()
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.barh(imp.index, imp.values, color=RUST)
for i, v in enumerate(imp.values): ax.text(v - .2, i, f"₦{v:.1f}bn", ha="right", va="center", fontsize=12, color=NAVY)
ax.axvline(0, color=INK, lw=1); ax.set_xlim(imp.min() * 1.35, 1)
ax.set(title=f"Stress test from the 'muddle through' case (₦{basecase:.1f}bn): pricing power matters most",
       xlabel="Change in EBITDA (₦ bn)")
note(fig, "Illustrative plan model. EEGB teaching assumptions.")
save(fig, "s14", "f06")

# --- F07 · Signposts: Nigeria's indicators vs trigger levels -------------------------------------------
sig = pd.DataFrame({"indicator": ["Reserves (months of imports)", "Inflation (%)", "Eurobond spread (%)", "12-month FX depreciation (%)", "Public debt (% GDP)"],
                    "value": [cr.loc["Nigeria", "reserves_months_imports"], cr.loc["Nigeria", "inflation_pct"], cr.loc["Nigeria", "eurobond_spread_pct"],
                              100 * cr.loc["Nigeria", "fx_depreciation_12m"], cr.loc["Nigeria", "public_debt_gdp_pct"]],
                    "amber": [5, 15, 5, 15, 50], "red": [3, 25, 8, 30, 70], "higher_is_worse": [False, True, True, True, True]})
def status(r):
    if r.higher_is_worse: return "red" if r.value >= r.red else "amber" if r.value >= r.amber else "green"
    return "red" if r.value <= r.red else "amber" if r.value <= r.amber else "green"
sig["status"] = sig.apply(status, axis=1)
colmap = {"green": TEAL, "amber": GOLD, "red": RUST}
fig, ax = plt.subplots(figsize=(10, 4.8))
for i, r in sig.iterrows():
    ax.barh(i, 1, color=colmap[r.status], height=.7)
    ax.text(0.03, i, f"{r.indicator}", va="center", fontsize=12.5, color="white", fontweight="bold")
    trig = f"amber {'≤' if not r.higher_is_worse else '≥'} {r.amber:g} · red {'≤' if not r.higher_is_worse else '≥'} {r.red:g}"
    ax.text(0.97, i, f"now {r.value:g}   ({trig})", va="center", ha="right", fontsize=11.5, color="white")
ax.set_yticks([]); ax.set_xticks([]); ax.grid(False); ax.invert_yaxis()
for s in ax.spines.values(): s.set_visible(False)
ax.set(title="Nigeria signpost board: agree the triggers before the crisis, not during it")
note(fig, "Trigger levels are illustrative; set your own with your treasury and risk teams. EEGB stylised teaching data.")
save(fig, "s14", "f07")

# --- key numbers -------------------------------------------------------------------------------------------
print(scores.round(0).sort_values("Base (equal)"))
print(ranks.loc["Nigeria"])
print(SCEN.round(2)); print(f"today {today:.1f}, EV {ev:.2f}, base {basecase:.2f}")
print(imp.round(2)); print(sig[["indicator", "value", "status"]])
