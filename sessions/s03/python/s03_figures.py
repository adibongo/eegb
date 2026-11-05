# =============================================================================
# EEGB · Session 3 · Demand Forecasting & Market Sizing
# Replication script — regenerates every chart in the Session 3 deck (Python)
# Data: data/cement_demand_monthly.csv (stylised Nigerian cement consumption, 2012–2025)
# Run from the project root:  python sessions/s03/python/s03_figures.py
# =============================================================================
import sys; sys.path.insert(0, "python")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from eegb_style import *

set_style()
c = pd.read_csv("data/cement_demand_monthly.csv", parse_dates=["month"])
c["t"] = np.arange(len(c)); c["m"] = c.month.dt.month; c["year"] = c.month.dt.year
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def X_ts(df, trend_deg=1):
    """Trend (polynomial in t, scaled) + 11 month dummies."""
    tt = df.t.values / 100
    cols = [np.ones(len(df))] + [tt ** k for k in range(1, trend_deg + 1)]
    cols += [(df.m == k).astype(float).values for k in range(2, 13)]
    return np.column_stack(cols)

def fit_predict(train, test, deg=1):
    b = np.linalg.lstsq(X_ts(train, deg), np.log(train.cement_mt), rcond=None)[0]
    return np.exp(X_ts(train, deg) @ b), np.exp(X_ts(test, deg) @ b), b

mape = lambda a, f: np.mean(np.abs(a - f) / a) * 100

# --- F01 · The raw series and its trend -----------------------------------------------------------
fig, ax = plt.subplots()
ax.plot(c.month, c.cement_mt, color=SKY, lw=1.6, label="Monthly consumption")
ax.plot(c.month, c.cement_mt.rolling(12, center=True).mean(), color=NAVY, lw=3, label="12-month moving average (trend)")
for s, e, lab in [("2016-01-01", "2016-12-01", "2016\nrecession"), ("2020-04-01", "2020-08-01", "COVID\nlockdown"), ("2024-01-01", "2024-12-01", "2024 price\nspike")]:
    ax.axvspan(pd.Timestamp(s), pd.Timestamp(e), color=GOLD, alpha=.18); ax.text(pd.Timestamp(s), 2.95, lab, fontsize=11, color=NAVY)
ax.set_ylim(0.7, 3.2); ax.legend(loc="lower right", ncol=2)
ax.set(title="Cement demand: a steady upward trend, a strong yearly rhythm, and occasional shocks", ylabel="Million tonnes per month")
note(fig); save(fig, "s03", "f01")
ann = c.groupby("year").cement_mt.sum()
cagr = (ann[2025] / ann[2012]) ** (1 / 13) - 1
print(f"annual 2012 {ann[2012]:.1f} mt, 2025 {ann[2025]:.1f} mt, CAGR {cagr*100:.1f}%")

# --- F02 · Seasonality --------------------------------------------------------------------------------
_, _, b_all = fit_predict(c, c)
seas = np.exp(np.r_[0, b_all[2:]]); seas = seas / seas.mean() * 100
fig, ax = plt.subplots(figsize=(10, 4.8))
cols = [RUST if k in (6, 7, 8, 9) else TEAL for k in range(1, 13)]
ax.bar(MON, seas, color=cols); ax.axhline(100, color=INK, lw=1)
for i, v in enumerate(seas): ax.text(i, v + 1, f"{v:.0f}", ha="center", fontsize=11, color=NAVY)
ax.set_ylim(60, 125)
ax.set(title=f"The rainy season (red) cuts demand: August is {100-seas[7]:.0f}% below an average month",
       ylabel="Seasonal index (average month = 100)")
note(fig); save(fig, "s03", "f02")
print("seasonal index:", dict(zip(MON, seas.round(0))))

# --- F03 · Backtest: train to 2023, forecast 2024–2025 ------------------------------------------------
train, test = c[c.year <= 2023].copy(), c[c.year >= 2024].copy()
_, f_reg, _ = fit_predict(train, test)
f_snaive = train.cement_mt.values[-12:]; f_snaive = np.r_[f_snaive, f_snaive]              # same month last year
f_avg = np.full(len(test), train.cement_mt.values[-12:].mean())                             # flat average of last year
# judgemental: last year's same month + 5% growth (a typical budget rule)
f_judge = train.cement_mt.values[-12:] * 1.05; f_judge = np.r_[f_judge, f_judge * 1.05]
scores = {"Flat average\nof last year": mape(test.cement_mt, f_avg), "Same month\nlast year": mape(test.cement_mt, f_snaive),
          "Budget rule:\nlast year + 5%": mape(test.cement_mt, f_judge), "Trend +\nseasonal model": mape(test.cement_mt, f_reg)}
fig, ax = plt.subplots()
ax.plot(c.month[c.year >= 2021], c.cement_mt[c.year >= 2021], color=INK, lw=2.5, label="Actual")
ax.plot(test.month, f_snaive, color=GOLD, lw=2, ls="--", label="Same month last year")
ax.plot(test.month, f_reg, color=TEAL, lw=2.5, label="Trend + seasonal model")
ax.axvline(pd.Timestamp("2024-01-01"), color=SLATE, ls=":"); ax.text(pd.Timestamp("2024-01-15"), 1.35, "forecast period →", color=SLATE)
ax.legend(loc="upper left")
ax.set(title="Backtest: models built on 2012–2023 data, tested on 2024–2025", ylabel="Million tonnes per month")
note(fig); save(fig, "s03", "f03")
print("backtest MAPE:", {k.replace(chr(10), ' '): round(v, 1) for k, v in scores.items()})

# --- F04 · Forecast accuracy scoreboard ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.6))
ks, vs = list(scores), list(scores.values())
ax.barh(ks, vs, color=[SLATE, GOLD, OLIVE, TEAL])
for i, v in enumerate(vs): ax.text(v + .2, i, f"{v:.1f}%", va="center", fontsize=13, color=NAVY)
ax.invert_yaxis(); ax.xaxis.set_major_formatter(FuncFormatter(pct))
ax.set(title="Average forecast error (MAPE) on 2024–2025: simple, honest models win", xlabel="Mean absolute percentage error (lower is better)")
save(fig, "s03", "f04")

# --- F05 · Forecast for 2026 with an uncertainty band ------------------------------------------------------
fut = pd.DataFrame({"month": pd.date_range("2026-01-01", periods=12, freq="MS")})
fut["t"] = np.arange(len(c), len(c) + 12); fut["m"] = fut.month.dt.month
fit_in, f26, b = fit_predict(c, fut)
resid_sd = np.std(np.log(c.cement_mt) - np.log(fit_in), ddof=len(b))
lo, hi = f26 * np.exp(-1.645 * resid_sd), f26 * np.exp(1.645 * resid_sd)
# annual uncertainty: how far each past year's total sat from the model's fitted total
ann_dev = np.log(c.assign(fit=fit_in).groupby("year")[["cement_mt", "fit"]].sum().pipe(lambda g: g.cement_mt / g.fit))
sd_a = ann_dev.std(ddof=1)
tot = f26.sum(); tot_lo, tot_hi = tot * np.exp(-1.645 * sd_a), tot * np.exp(1.645 * sd_a)
fig, ax = plt.subplots()
h = c[c.year >= 2022]
ax.plot(h.month, h.cement_mt, color=INK, lw=2.2, label="Actual")
ax.fill_between(fut.month, lo, hi, color=TEAL, alpha=.25, label="90% range for each month")
ax.plot(fut.month, f26, color=TEAL, lw=3, label="2026 forecast")
ax.legend(loc="upper left")
ax.set(title=f"2026 forecast: about {tot:.1f} million tonnes (range roughly {tot_lo:.1f}–{tot_hi:.1f})", ylabel="Million tonnes per month")
note(fig); save(fig, "s03", "f05")
print(f"2026 forecast {tot:.2f} mt, range {tot_lo:.1f}-{tot_hi:.1f}; monthly resid sd {resid_sd:.3f}, annual sd {sd_a:.3f}")

# --- F06 · Scenarios for 2026 -----------------------------------------------------------------------------------
base = tot
scen = {"Downside:\nprice spike + weak\nincomes (−8%)": base * 0.92, "Base:\ntrend + season": base,
        "Upside:\nhousing & road\nprogramme (+6%)": base * 1.06}
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.bar(list(scen), list(scen.values()), color=[RUST, TEAL, GOLD], width=.55)
for i, v in enumerate(scen.values()): ax.text(i, v + .3, f"{v:.1f} mt", ha="center", fontsize=14, color=NAVY)
ax.axhline(ann[2025], color=SLATE, ls="--", lw=1.2); ax.text(2.32, ann[2025] + .3, f"2025: {ann[2025]:.1f}", color=SLATE)
ax.set_ylim(0, base * 1.2)
ax.set(title="Plan capacity for a range, not a point: three 2026 scenarios", ylabel="Million tonnes in 2026")
save(fig, "s03", "f06")
print("scenarios:", {k.split(':')[0]: round(v, 1) for k, v in scen.items()})

# --- F07 · Market sizing: top-down vs bottom-up -------------------------------------------------------------------
pop, kg_pc = 230, 140                                    # million people; kg per person per year (stylised)
top_down = pop * kg_pc / 1000                             # million tonnes
houses, t_house = 0.45, 32                                # million new homes a year; tonnes each (stylised)
parts = {"New homes": houses * t_house, "Repairs &\nextensions": 6.5, "Roads, bridges\n& public works": 6.0,
         "Commercial &\nindustrial": 4.5, "Blocks, pipes\n& precast": 2.4}
bottom_up = sum(parts.values())
fig, ax = plt.subplots()
left = 0
for (k, v), col in zip(parts.items(), [TEAL, TEAL2, GOLD, OLIVE, SKY]):
    ax.barh(1, v, left=left, color=col, label=k.replace("\n", " ")); ax.text(left + v / 2, 1, f"{v:.1f}", ha="center", va="center", fontsize=12, color="white", fontweight="bold")
    left += v
ax.barh(0, top_down, color=NAVY); ax.text(top_down / 2, 0, f"{pop}m people × {kg_pc} kg = {top_down:.1f} mt", ha="center", va="center", color="white", fontsize=12)
ax.set_yticks([0, 1], ["Top-down", "Bottom-up"]); ax.set_xlim(0, 36); ax.set_ylim(-.6, 2.1)
ax.legend(ncol=3, loc="upper left", fontsize=10.5)
ax.set(title=f"Two routes to market size: top-down {top_down:.1f} mt vs bottom-up {bottom_up:.1f} mt", xlabel="Million tonnes per year")
save(fig, "s03", "f07")
print(f"top-down {top_down:.1f}, bottom-up {bottom_up:.1f}, new homes {houses*t_house:.1f}")

# --- F08 · More complex is not more accurate (overfitting) ------------------------------------------------------------
degs = range(1, 9); tr_err, te_err = [], []
for k in degs:
    fi, fo, _ = fit_predict(train, test, k)
    tr_err.append(mape(train.cement_mt, fi)); te_err.append(mape(test.cement_mt, fo))
fig, ax = plt.subplots()
ax.plot(list(degs), tr_err, "o-", color=TEAL, lw=2.5, label="Error on the data used to fit (2012–2023)")
ax.plot(list(degs), te_err, "o-", color=RUST, lw=2.5, label="Error on new data (2024–2025)")
ax.set_yscale("log"); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:g}%"))
ax.legend(loc="upper left")
ax.set(title="Extra flexibility barely improves the fit — but wrecks the forecast",
       xlabel="Model complexity (degree of the trend curve)", ylabel="MAPE (log scale)")
save(fig, "s03", "f08")
print("overfit train:", np.round(tr_err, 1), "test:", np.round(te_err, 1))
