# =============================================================================
# EEGB · Session 11 · Exchange Rates, Capital Flows & the Impossible Trinity
# Replication script — regenerates every chart in the Session 11 deck (Python)
# Data: data/ng_macro_monthly.csv, data/ng_bop_quarterly.csv (stylised teaching data)
# Run from the project root:  python sessions/s11/python/s11_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])
b = pd.read_csv("data/ng_bop_quarterly.csv")
b["date"] = pd.PeriodIndex(b.quarter, freq="Q").to_timestamp()
ngn = FuncFormatter(lambda v, p: f"₦{v:,.0f}")

# --- F01 · Three regimes for the naira -----------------------------------------------------------
fig, ax = plt.subplots()
ax.plot(m.date, m.parallel_fx_ngn_usd, color=RUST, lw=2, label="Parallel market")
ax.plot(m.date, m.official_fx_ngn_usd, color=NAVY, lw=3, label="Official rate")
regimes = [("2015-01-01", "2016-06-01", "Hard peg\n(≈ ₦197–199)", "#EEF2F6"),
           ("2016-06-01", "2023-06-01", "Managed rate +\nmultiple windows", "#F6EFE2"),
           ("2023-06-01", "2025-12-31", "Unified, more\nmarket-determined", "#E6F0F4")]
for a, z, lab, c in regimes:
    ax.axvspan(pd.Timestamp(a), pd.Timestamp(z), color=c, zorder=0)
    ax.text(pd.Timestamp(a) + pd.Timedelta(days=40), 1750, lab, fontsize=11, color=NAVY, va="top")
ax.yaxis.set_major_formatter(ngn); ax.set_ylim(0, 1800); ax.legend(loc="center left")
ax.set(title="Three regimes in a decade: peg, managed float with rationing, then unification",
       ylabel="Naira per US dollar")
note(fig); save(fig, "s11", "f01")

# --- F02 · Rationing shows up as a premium: premium vs reserves ------------------------------------
m["premium"] = 100 * (m.parallel_fx_ngn_usd / m.official_fx_ngn_usd - 1)
fig, ax = plt.subplots()
ax.plot(m.date, m.premium, color=RUST, lw=2.6, label="Parallel premium (%)")
ax.set_ylabel("Parallel-market premium (%)", color=RUST)
ax2 = ax.twinx(); ax2.plot(m.date, m.fx_reserves_usd_bn, color=TEAL, lw=2.2, label="Reserves (US$ bn)")
ax2.set_ylabel("Gross reserves (US$ bn)", color=TEAL); ax2.grid(False); ax2.spines["right"].set_visible(True)
pre = m[m.date < "2023-06-01"].premium.mean(); post = m[m.date >= "2024-06-01"].premium.mean()
ax.set(title=f"Average premium: {pre:.0f}% before unification, {post:.0f}% after mid-2024")
note(fig); save(fig, "s11", "f02")

# --- F03 · The balance of payments, quarter by quarter ----------------------------------------------
fig, ax = plt.subplots()
x = b.date
pos = np.zeros(len(b)); neg = np.zeros(len(b))
for col, c, lab in [("trade_balance", TEAL, "Goods trade balance"), ("remittances", GOLD, "Remittances"),
                    ("services_income_net", SLATE, "Services & income (net)")]:
    v = b[col].values
    ax.bar(x, np.where(v > 0, v, 0), bottom=pos, width=70, color=c, label=lab)
    ax.bar(x, np.where(v < 0, v, 0), bottom=neg, width=70, color=c)
    pos += np.where(v > 0, v, 0); neg += np.where(v < 0, v, 0)
ax.plot(x, b.current_account, color=NAVY, lw=2.6, marker="o", ms=4, label="Current account")
ax.axhline(0, color=INK, lw=1); ax.legend(loc="lower left", ncol=2, fontsize=11)
ax.yaxis.set_major_formatter(FuncFormatter(usd_bn := (lambda v, p: f"${v:.0f}bn")))
ax.set(title="Remittances keep the current account afloat when oil exports weaken",
       ylabel="US$ bn per quarter")
note(fig); save(fig, "s11", "f03")

# --- F04 · Hot money: portfolio inflows and the carry ---------------------------------------------
mq = m.set_index("date").resample("QS").mean(numeric_only=True)
mq["real_rate"] = mq.mpr - mq.headline_inflation
bq = b.set_index("date").join(mq[["real_rate"]])
fig, ax = plt.subplots()
ax.bar(bq.index, bq.portfolio_inflows, width=70, color=TEAL2, label="Portfolio inflows (US$ bn)")
ax.set_ylabel("Portfolio inflows, US$ bn per quarter")
ax2 = ax.twinx(); ax2.plot(bq.index, bq.real_rate, color=RUST, lw=2.4, label="Real policy rate (pts)")
ax2.axhline(0, color=RUST, ls=":", lw=1); ax2.set_ylabel("Real policy rate (points)", color=RUST)
ax2.grid(False); ax2.spines["right"].set_visible(True)
r = np.corrcoef(bq.portfolio_inflows, bq.real_rate)[0, 1]
ax.set(title=f"Hot money follows the real return: inflows vs real policy rate (r = {r:.2f})")
note(fig); save(fig, "s11", "f04")

# --- F05 · The impossible trinity (conceptual) -----------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 7))
P = {"Fixed exchange rate": (0, 0), "Free capital flows": (10, 0), "Independent monetary policy": (5, 8.66)}
tri = np.array(list(P.values()) + [P["Fixed exchange rate"]])
ax.plot(tri[:, 0], tri[:, 1], color=NAVY, lw=3)
for k, (px, py) in P.items():
    ax.scatter(px, py, s=500, color=GOLD, zorder=3, edgecolor="white", lw=3)
    ax.text(px, py + (0.9 if py > 0 else -1.2), k, ha="center", fontsize=14, fontweight="bold", color=NAVY)
sides = [((5, -0.6), "Currency board / euro area\n(give up own monetary policy)"),
         ((1.6, 4.7), "Capital controls\n(China; Nigeria's FX rationing)"),
         ((8.4, 4.7), "Floating rate\n(US, UK; Nigeria since 2023–24)")]
for (sx, sy), lab in sides:
    ax.text(sx, sy, lab, ha="center", va="center", fontsize=11.5, color=TEAL,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=TEAL))
ax.set_xlim(-2.5, 12.5); ax.set_ylim(-3, 10.5); ax.axis("off")
ax.set_title("The impossible trinity: pick any two corners — each side is a policy choice", loc="left")
save(fig, "s11", "f05")

# --- F06 · Currency mismatch: a US$10m loan in naira ------------------------------------------------
loan_usd = 10e6
d0, d1 = pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")
fx0 = m.loc[m.date == d0, "official_fx_ngn_usd"].iloc[0]; fx1 = m.loc[m.date == d1, "official_fx_ngn_usd"].iloc[0]
path_ngn = m[(m.date >= d0) & (m.date <= d1)].assign(debt=lambda d: loan_usd * d.official_fx_ngn_usd / 1e9)
fig, ax = plt.subplots()
ax.fill_between(path_ngn.date, path_ngn.debt, color=RUST, alpha=.25)
ax.plot(path_ngn.date, path_ngn.debt, color=RUST, lw=3)
ax.axhline(loan_usd * fx0 / 1e9, color=SLATE, ls="--"); ax.text(d0, loan_usd * fx0 / 1e9 + .4, f"Borrowed: ₦{loan_usd * fx0 / 1e9:.1f}bn", color=SLATE, fontsize=12)
ax.text(d1, loan_usd * fx1 / 1e9 + .4, f"Owed: ₦{loan_usd * fx1 / 1e9:.1f}bn", color=RUST, fontsize=12, ha="right", fontweight="bold")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:.0f}bn")); ax.set_ylim(0, loan_usd * fx1 / 1e9 * 1.2)
ax.set(title=f"A US$10m loan with naira revenues: the debt grew {fx1 / fx0:.1f}× without borrowing a kobo more",
       ylabel="Loan value in naira")
note(fig); save(fig, "s11", "f06")

# --- F07 · Real exchange rate: did the naira really get cheaper? --------------------------------------
# Build price levels from year-on-year inflation (monthly approximation); US inflation assumed 2.5% a year.
mp = (1 + m.headline_inflation / 100) ** (1 / 12)
p_ng = mp.cumprod(); p_us = (1.025 ** (1 / 12)) ** np.arange(1, len(m) + 1)
rer = m.official_fx_ngn_usd * p_us / p_ng
rer = 100 * rer / rer.iloc[0]; nom = 100 * m.official_fx_ngn_usd / m.official_fx_ngn_usd.iloc[0]
fig, ax = plt.subplots()
ax.plot(m.date, nom, color=SLATE, lw=2.2, label="Nominal: naira per dollar")
ax.plot(m.date, rer, color=TEAL, lw=3, label="Real: adjusted for Nigerian vs US inflation")
ax.axhline(100, color=INK, lw=1)
ax.legend(loc="upper left"); ax.set_ylabel("Index, Jan 2015 = 100 (higher = cheaper naira)")
ax.set(title="In real terms the naira cheapened far less — and inflation is eroding the gain")
note(fig, "Real rate uses stylised CPI with US inflation assumed at 2.5% a year. EEGB stylised teaching data.")
save(fig, "s11", "f07")

# --- key numbers ----------------------------------------------------------------------------------------
print(f"premium before unification {pre:.1f}%, after mid-2024 {post:.1f}%, max {m.premium.max():.0f}%")
print(f"CA avg 2015-19 {b[b.date < '2020'].current_account.mean():.2f}, 2020Q2 {b.loc[b.quarter=='2020Q2','current_account'].iloc[0]:.2f}, remit avg {b.remittances.mean():.2f}")
print(f"corr inflows vs real rate {r:.2f}; fx0 {fx0:.0f} fx1 {fx1:.0f} debt0 {loan_usd*fx0/1e9:.2f} debt1 {loan_usd*fx1/1e9:.2f}")
print(f"nominal index end {nom.iloc[-1]:.0f}, real index end {rer.iloc[-1]:.0f}, real peak {rer.max():.0f} at {m.date[rer.idxmax()]:%b %Y}")
print(f"reserves min {m.fx_reserves_usd_bn.min():.1f} max {m.fx_reserves_usd_bn.max():.1f}")
