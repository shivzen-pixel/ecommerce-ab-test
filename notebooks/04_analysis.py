import pandas as pd
import numpy as np
from scipy import stats
import pingouin as pg
import matplotlib.pyplot as plt

# ── LOAD MATCHED DATA ─────────────────────────────────────────
df = pd.read_csv('data/df_matched.csv')

high_value = df[df['group'] == 'high_value']['review_score'].dropna()
regular    = df[df['group'] == 'regular']['review_score'].dropna()

print(f"High-value n : {len(high_value):,}")
print(f"Regular n    : {len(regular):,}")

# ── PRIMARY TEST: MANN-WHITNEY U ──────────────────────────────
stat, p_value = stats.mannwhitneyu(high_value, regular, alternative='two-sided')

print(f"\n── Mann-Whitney U Test ──")
print(f"U statistic : {stat:,.0f}")
print(f"P-value     : {p_value:.4f}")
print(f"Significant : {'✅ YES' if p_value < 0.05 else '❌ NO'}")

# ── EFFECT SIZE: CLIFF'S DELTA ────────────────────────────────
cliffs_delta = pg.mwu(high_value, regular)
print(f"\n── Effect Size ──")
print(cliffs_delta)

# ── PRACTICAL SIGNIFICANCE ────────────────────────────────────
mean_diff = high_value.mean() - regular.mean()
print(f"\nMean difference     : {mean_diff:.4f} points")
print(f"Target MDE          : 0.5 points")
print(f"Practically significant: {'✅ YES' if abs(mean_diff) >= 0.5 else '❌ NO'}")

# ── BOOTSTRAP CONFIDENCE INTERVALS ───────────────────────────
np.random.seed(42)
n_bootstrap = 1000
boot_diffs = []

for _ in range(n_bootstrap):
    hv_sample  = np.random.choice(high_value, size=len(high_value), replace=True)
    reg_sample = np.random.choice(regular, size=len(regular), replace=True)
    boot_diffs.append(np.median(hv_sample) - np.median(reg_sample))

ci_lower = np.percentile(boot_diffs, 2.5)
ci_upper = np.percentile(boot_diffs, 97.5)

print(f"\n── Bootstrap 95% CI (median difference) ──")
print(f"Lower : {ci_lower:.4f}")
print(f"Upper : {ci_upper:.4f}")
print(f"CI includes zero: {'⚠️ YES' if ci_lower <= 0 <= ci_upper else '✅ NO'}")

# ── SENSITIVITY CHECK: T-TEST ─────────────────────────────────
t_stat, t_p = stats.ttest_ind(high_value, regular)
print(f"\n── Sensitivity Check: T-Test ──")
print(f"T-statistic : {t_stat:.4f}")
print(f"P-value     : {t_p:.4f}")
print(f"Consistent with Mann-Whitney: {'✅ YES' if (t_p < 0.05) == (p_value < 0.05) else '⚠️ NO'}")

# ── VISUALIZE RESULTS ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Review score distribution
df.groupby('group')['review_score'].value_counts(normalize=True)\
  .unstack(0).plot(kind='bar', ax=axes[0], color=['steelblue', 'darkorange'])
axes[0].set_title('Review Score Distribution by Group')
axes[0].set_xlabel('Review Score')
axes[0].set_ylabel('Proportion')
axes[0].tick_params(axis='x', rotation=0)

# Bootstrap CI
axes[1].hist(boot_diffs, bins=40, color='steelblue', edgecolor='black', alpha=0.7)
axes[1].axvline(ci_lower, color='red', linestyle='--', label=f'CI Lower: {ci_lower:.3f}')
axes[1].axvline(ci_upper, color='red', linestyle='--', label=f'CI Upper: {ci_upper:.3f}')
axes[1].axvline(0, color='black', linestyle='-', linewidth=2, label='Zero')
axes[1].set_title('Bootstrap Distribution of Median Difference')
axes[1].set_xlabel('Median Difference (High-Value - Regular)')
axes[1].legend()

plt.tight_layout()
plt.savefig('../data/primary_analysis.png')
plt.show()

print("\n✅ Primary analysis complete!")