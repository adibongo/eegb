# =============================================================================
# EEGB · Session 10 · Financial Stability & Corporate Finance Conditions
# Replication script — regenerates every chart in the Session 10 deck (Python)
# Data: data/ng_yield_curves.csv (stylised FGN yield curves), data/bank_balance_sheet.csv (a fictional
#       Nigerian bank, ₦ bn), data/ng_macro_monthly.csv (inflation for real yields)
# Run from the project root:  python sessions/s10/python/s10_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
yc = pd.read_csv("data/ng_yield_curves.csv", parse_dates=["date"])
bs = pd.read_csv("data/bank_balance_sheet.csv")
m = pd.read_csv("data/ng_macro_monthly.csv", parse_dates=["date"])


def bond_price(coupon, yld, years, freq=2, face=100):
    """Price of a plain fixed-coupon bond (coupon and yield as decimals)."""
    n = int(round(years * freq)); c = coupon / freq * face; y = yld / freq
    t = np.arange(1, n + 1)
    return np.sum(c / (1 + y) ** t) + face / (1 + y) ** n


def mac_duration(coupon, yld, years, freq=2):
    n = int(round(years * freq)); c = coupon / freq * 100; y = yld / freq
    t = np.arange(1, n + 1); cf = np.full(n, c); cf[-1] += 100
    pv = cf / (1 + y) ** t
    return np.sum(t / freq * pv) / pv.sum()


# --- F01 · Five yield curves --------------------------------------------------------------
fig, ax = plt.subplots()
cols = {"2021-06-30": SKY, "2023-01-31": TEAL2, "2024-06-28": RUST, "2025-06-30": GOLD, "2025-12-31": NAVY}
for d, g in yc.groupby("date"):
    k = d.strftime("%Y-%m-%d")
    ax.plot(g.tenor_years, g.yield_pct, marker="o", lw=2.6 if k in ("2024-06-28", "2023-01-31") else 2,
            color=cols[k], label=d.strftime("%b %Y"))
ax.set_xscale("log"); ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20, 30], ["3m", "6m", "1y", "2y", "5y", "10y", "20y", "30y"])
ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(title=None, loc="lower right", ncol=2)
ax.set(title="The FGN yield curve: steep and low in 2021, high and inverted in 2024",
       xlabel="Time to maturity (log scale)", ylabel="Yield")
note(fig); save(fig, "s10", "f01")

# --- F02 · Bond prices fall when yields rise — long bonds fall most -----------------------------
ys = np.linspace(0.08, 0.24, 80)
fig, ax = plt.subplots()
for yrs, c in [(1, SKY), (5, TEAL), (10, NAVY), (20, RUST)]:
    ax.plot(100 * ys, [bond_price(0.13, y, yrs) for y in ys], color=c, lw=2.6, label=f"{yrs}-year bond")
ax.axvline(13, color=SLATE, ls="--", lw=1); ax.text(13.2, 145, "bought at 13%\n(price = 100)", color=SLATE, fontsize=11)
ax.axvline(18.8, color=RUST, ls=":", lw=1.4)
p10 = bond_price(0.13, 0.188, 10)
ax.annotate(f"10-year at 18.8%:\nprice {p10:.0f} ({p10 - 100:+.0f}%)", xy=(18.8, p10), xytext=(20, 105),
            arrowprops=dict(arrowstyle="->", color=NAVY), fontsize=12, color=NAVY)
ax.legend(loc="upper right"); ax.xaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title="Same 13% coupon, different maturities: the longer the bond, the bigger the fall",
       xlabel="Market yield", ylabel="Bond price (per ₦100 face value)")
note(fig); save(fig, "s10", "f02")

# --- F03 · Mark-to-market loss: bonds bought in Jan 2023, valued in Jun 2024 --------------------
c23 = yc[yc.date == "2023-01-31"].set_index("tenor_years").yield_pct
c24 = yc[yc.date == "2024-06-28"].set_index("tenor_years").yield_pct
ten = [2, 3, 5, 7, 10, 15, 20]
loss = []
for t in ten:
    rem = max(t - 1.4, 0.25)                      # ~17 months later the bond is shorter
    loss.append(bond_price(c23[t] / 100, c24.reindex([t]).interpolate().iloc[0] / 100, rem) - 100)
fig, ax = plt.subplots()
ax.bar([f"{t}y" for t in ten], loss, color=[TEAL if l > -5 else RUST for l in loss])
for i, l in enumerate(loss): ax.text(i, l - 1.2, f"{l:.0f}%", ha="center", va="top", fontsize=11, color=INK)
ax.axhline(0, color=INK, lw=1); ax.set_ylim(min(loss) * 1.25, 3)
ax.set(title="A par bond bought in January 2023 had lost up to a fifth of its value by mid-2024",
       xlabel="Original maturity of the FGN bond", ylabel="Change in market price (%)")
note(fig); save(fig, "s10", "f03")

# --- F04 · The bank's balance sheet ----------------------------------------------------------
A = bs[bs.side == "asset"]; L = bs[bs.side == "liability"]
TA, TL = A.amount_ngn_bn.sum(), L.amount_ngn_bn.sum(); E = TA - TL   # equity = assets − liabilities (keeps the sheet balanced)
fig, ax = plt.subplots(figsize=(10, 6))
palA = [SLATE, SKY, RUST, TEAL, TEAL2, "#C9D3DD"]; palL = [NAVY, TEAL2, SKY, OLIVE]
b = 0
for (_, r), c in zip(A.iterrows(), palA):
    ax.bar(0, r.amount_ngn_bn, bottom=b, color=c, width=.95, edgecolor="white")
    small = r.amount_ngn_bn < 600
    ax.text(-0.5 if small else 0, b + r.amount_ngn_bn / 2, f"{r['item']}{' · ' if small else chr(10)}₦{r.amount_ngn_bn:,.0f}bn · D = {r.duration_years:g}y",
            ha="right" if small else "center", va="center", fontsize=10, color=INK if small or c in ("#C9D3DD", SKY) else "white")
    b += r.amount_ngn_bn
b = 0
for (_, r), c in zip(L.iterrows(), palL):
    ax.bar(1, r.amount_ngn_bn, bottom=b, color=c, width=.95, edgecolor="white")
    small = r.amount_ngn_bn < 600
    ax.text(1.5 if small else 1, b + r.amount_ngn_bn / 2, f"{r['item']}{' · ' if small else chr(10)}₦{r.amount_ngn_bn:,.0f}bn · D = {r.duration_years:g}y",
            ha="left" if small else "center", va="center", fontsize=10, color=INK if small else "white")
    b += r.amount_ngn_bn
ax.bar(1, E, bottom=b, color=GOLD, width=.95, edgecolor="white")
ax.text(1.5, b + E / 2, f"Equity ₦{E:,.0f}bn", ha="left", va="center", fontsize=11, fontweight="bold", color=INK)
ax.set_xticks([0, 1], ["Assets", "Liabilities + equity"]); ax.set_yticks([]); ax.grid(False); ax.set_xlim(-1.75, 2.75)
ax.set(title="A Nigerian bank: long FGN bonds funded by short deposits (D = duration)")
note(fig); save(fig, "s10", "f04")

# --- F05 · Duration gap: what a rise in yields does to equity ---------------------------------
DA = (A.amount_ngn_bn * A.duration_years).sum() / TA
DL = (L.amount_ngn_bn * L.duration_years).sum() / TL
gap = DA - TL / TA * DL            # duration gap
y0 = 0.18
shocks = np.arange(0, 7.01, 0.5)
dE = -gap * TA * (shocks / 100) / (1 + y0)
fig, ax = plt.subplots()
ax.plot(shocks, E + dE, color=NAVY, lw=3, marker="o")
ax.axhline(0, color=RUST, lw=1.5, ls="--"); ax.text(0.1, 15, "equity wiped out", color=RUST, fontsize=12)
be = E * (1 + y0) / (gap * TA) * 100
ax.axvline(be, color=GOLD, ls=":", lw=1.5); ax.text(be + 0.1, E * 0.8, f"break-even shock\n≈ {be:.1f} points", color=GOLD, fontsize=12)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{'−' if v < 0 else ''}₦{abs(v):,.0f}bn")); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"+{v:g}"))
ax.set(title=f"Duration gap of {gap:.2f} years: a {be:.1f}-point rise in yields erases the bank's equity",
       xlabel="Parallel rise in interest rates (percentage points)", ylabel="Economic value of equity")
note(fig); save(fig, "s10", "f05")

# --- F06 · The SVB trap: unrealised loss on held-to-maturity bonds vs equity -------------------------
bonds = A[A["item"].str.contains("FGN bonds")].iloc[0]
mod_d = bonds.duration_years / (1 + bonds.rate_pct / 100)
dy = c24[10] - bonds.rate_pct
htm_loss = mod_d * dy / 100 * bonds.amount_ngn_bn
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.barh(["Equity (assets − liabilities)", "Unrealised loss on FGN bonds"], [E, htm_loss], color=[GOLD, RUST], height=.5)
for i, v in enumerate([E, htm_loss]): ax.text(v + 10, i, f"₦{v:,.0f}bn", va="center", fontsize=13, fontweight="bold", color=NAVY)
ax.set_xlim(0, max(E, htm_loss) * 1.25); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"₦{v:,.0f}bn"))
ax.set(title=f"If yields rise {dy:.1f} points, the hidden bond loss is bigger than the bank's equity")
note(fig); save(fig, "s10", "f06")

# --- F07 · Real 10-year yield ---------------------------------------------------------------------
rows = []
for d, g in yc.groupby("date"):
    infl = m.loc[m.date <= d, "headline_inflation"].iloc[-1]
    y10 = g.set_index("tenor_years").yield_pct[10]
    rows.append((d, y10, infl, y10 - infl))
ry = pd.DataFrame(rows, columns=["date", "y10", "infl", "real"])
fig, ax = plt.subplots()
lab = ry.date.dt.strftime("%b %Y")
ax.bar(lab, ry.real, color=[RUST if v < 0 else TEAL for v in ry.real], width=.6)
for i, r in ry.iterrows(): ax.text(i, r.real + (0.8 if r.real >= 0 else -0.8), f"{r.real:+.1f}", ha="center",
                                   va="bottom" if r.real >= 0 else "top", fontsize=12, fontweight="bold")
ax.axhline(0, color=INK, lw=1); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:+.0f}"))
ax.set_ylim(ry.real.min() - 4, ry.real.max() + 3)
ax.set(title="Real 10-year yield (yield minus inflation): negative throughout, near zero only by end-2025",
       ylabel="Percentage points")
note(fig); save(fig, "s10", "f07")

# --- key numbers -----------------------------------------------------------------------------------
print(f"TA={TA}, TL={TL}, E={E}, leverage(A/E)={TA / E:.1f}")
print(f"DA={DA:.2f}, DL={DL:.2f}, gap={gap:.2f}, break-even shock={be:.2f} pts")
print(f"10y bond 13% coupon at 18.8%: price {p10:.1f}; mac duration at 13%: {mac_duration(0.13, 0.13, 10):.2f}")
print("loss by tenor:", dict(zip(ten, np.round(loss, 1))))
print(f"HTM: modD={mod_d:.2f}, dy={dy:.1f}, loss={htm_loss:.0f}")
print(ry.round(1).to_string())
for s in (2, 5): print(f"shock +{s}: dE={-gap * TA * s / 100 / (1 + y0):.0f}")
