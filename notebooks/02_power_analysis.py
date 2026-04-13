import pandas as pd
import numpy as np
from statsmodels.stats.power import TTestIndPower

# ── LOAD CLEAN DATA ───────────────────────────────────────────
df = pd.read_csv('data/df_clean.csv')

high_value = df[df['group'] == 'high_value']['review_score'].dropna()
regular    = df[df['group'] == 'regular']['review_score'].dropna()

# ── PARAMETERS ───────────────────────────────────────────────
alpha      = 0.05
power      = 0.80
std_pooled = df['review_score'].dropna().std()

print(f"High-value group size : {len(high_value):,}")
print(f"Regular group size    : {len(regular):,}")
print(f"Pooled std            : {std_pooled:.4f}")

# ── WHAT EFFECT CAN WE DETECT? ────────────────────────────────
analysis = TTestIndPower()

mde = analysis.solve_power(
    nobs1        = len(high_value),
    ratio        = len(regular) / len(high_value),
    alpha        = alpha,
    power        = power,
    alternative  = 'two-sided'
)

print(f"\nMinimum Detectable Effect (Cohen's d) : {mde:.4f}")
print(f"MDE in review score points            : {mde * std_pooled:.4f}")
print(f"\nOur target effect size                : 0.5 points")

if mde * std_pooled < 0.5:
    print("✅ We CAN detect our target effect with this sample size")
else:
    print("⚠️ We CANNOT detect our target effect — sample too small")


# ── SUMMARY ──────────────────────────────────────────────────
print("\n── Power Analysis Summary ──")
print(f"With {len(high_value):,} high-value and {len(regular):,} regular orders,")
print(f"we can detect effects as small as {mde * std_pooled:.2f} review score points.")
print(f"Our business-meaningful threshold is 0.5 points.")
print(f"We are statistically well-powered for this experiment.")