# =============================================================================
# EEGB · Session 4 LAB · Is the mobile-payments market competitive? (Python)
# Data: data/payments_market_shares.csv — stylised; providers are fictional except the 'Banks' aggregate
# Run from the project root, line by line (Ctrl/Cmd + Enter)
# =============================================================================
import numpy as np, pandas as pd

p = pd.read_csv("data/payments_market_shares.csv")

# ---- STEP 1 · Shares over time ---------------------------------------------------------------
sh = p.pivot(index="year", columns="provider", values="share_of_value_pct")
print(sh.round(1))

# ---- STEP 2 · Concentration: CR2 and the HHI ------------------------------------------------------
# CR2 = combined share of the two largest. HHI = sum of squared shares (0–10,000).
cr2 = sh.apply(lambda r: r.nlargest(2).sum(), axis=1)
hhi = (sh ** 2).sum(axis=1)
print(pd.DataFrame({"CR2": cr2, "HHI": hhi.round(0)}))

# ---- STEP 3 · Market definition matters ----------------------------------------------------------
# 'Banks (app & USSD)' is really many banks. Suppose it is 10 banks of equal size:
hhi_split = (sh.drop(columns="Banks (app & USSD)") ** 2).sum(axis=1) + 10 * (sh["Banks (app & USSD)"] / 10) ** 2
print(pd.DataFrame({"banks as one": hhi.round(0), "banks as ten": hhi_split.round(0)}))

# ---- STEP 4 · Two-sided network growth ------------------------------------------------------------
tot = p.groupby("year")[["active_users_m", "merchants_m"]].sum()
slope = np.polyfit(np.log(tot.active_users_m), np.log(tot.merchants_m), 1)[0]
print(tot.round(2)); print(f"1% more users goes with {slope:.2f}% more merchants")

# ---- STEP 5 · Market power: does the leader's fee rise with its share? -------------------------------
k = p[p.provider == "KoboLink"][["year", "share_of_value_pct", "avg_fee_pct"]]
print(k)
print("correlation share-fee:", round(k.share_of_value_pct.corr(k.avg_fee_pct), 2))

# ---- STEP 6 · A simple merger test: what if SwiftNaira and AgentPay merged in 2025? -------------------
s25 = sh.loc[2025]
delta = 2 * s25["SwiftNaira"] * s25["AgentPay"]          # change in HHI from a merger = 2 × s1 × s2
print(f"Merger raises HHI by {delta:.0f} points (banks-as-ten HHI goes from {hhi_split[2025]:.0f} to {hhi_split[2025] + delta:.0f})")

# ---- YOUR TURN ------------------------------------------------------------------------------------------
# (a) Is this market 'concentrated'? Give the answer under BOTH market definitions, and say which you prefer.
# (b) KoboLink's fee rose after it became the largest network. Is that proof of abuse? What else could explain it?
# (c) Write a 3-sentence note to the competition regulator (FCCPC) on the merger in Step 6.
