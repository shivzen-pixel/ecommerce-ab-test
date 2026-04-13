import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt

# ── LOAD DATA ─────────────────────────────────────────────────
df_matched = pd.read_csv('data/df_matched.csv')
df_clean   = pd.read_csv('data/df_clean.csv')

df_matched['order_purchase_timestamp']      = pd.to_datetime(df_matched['order_purchase_timestamp'])
df_matched['order_delivered_customer_date'] = pd.to_datetime(df_matched['order_delivered_customer_date'])
df_matched['order_estimated_delivery_date'] = pd.to_datetime(df_matched['order_estimated_delivery_date'])

high_value = df_matched[df_matched['group'] == 'high_value']
regular    = df_matched[df_matched['group'] == 'regular']


# ── FIX: merge customer_state back from df_clean ─────────────
df_clean = pd.read_csv('data/df_clean.csv')
df_matched = df_matched.merge(
    df_clean[['order_id', 'customer_state']], 
    on='order_id', 
    how='left'
)
# ══════════════════════════════════════════════════════════════
# GUARDRAIL 1: DELIVERY DELAY RATE
# Was the order delivered AFTER the estimated date?
# ══════════════════════════════════════════════════════════════
df_matched['is_delayed'] = (
    df_matched['order_delivered_customer_date'] > 
    df_matched['order_estimated_delivery_date']
).astype(float)

hv_delay  = df_matched[df_matched['group'] == 'high_value']['is_delayed'].dropna()
reg_delay = df_matched[df_matched['group'] == 'regular']['is_delayed'].dropna()

delay_stat, delay_p = stats.mannwhitneyu(hv_delay, reg_delay, alternative='two-sided')

print("── Guardrail 1: Delivery Delay Rate ──")
print(f"High-value delay rate : {hv_delay.mean():.2%}")
print(f"Regular delay rate    : {reg_delay.mean():.2%}")
print(f"P-value               : {delay_p:.4f}")
print(f"Guardrail breached    : {'🚨 YES' if delay_p < 0.05 else '✅ NO'}\n")

# ══════════════════════════════════════════════════════════════
# GUARDRAIL 2: CANCELLATION RATE
# ══════════════════════════════════════════════════════════════
df_clean['is_cancelled'] = (df_clean['order_status'] == 'canceled').astype(float)

# Merge cancellation back to matched dataset
df_matched = df_matched.merge(
    df_clean[['order_id', 'is_cancelled']], on='order_id', how='left'
)

hv_cancel  = df_matched[df_matched['group'] == 'high_value']['is_cancelled'].dropna()
reg_cancel = df_matched[df_matched['group'] == 'regular']['is_cancelled'].dropna()

cancel_stat, cancel_p = stats.mannwhitneyu(hv_cancel, reg_cancel, alternative='two-sided')

print("── Guardrail 2: Cancellation Rate ──")
print(f"High-value cancel rate : {hv_cancel.mean():.2%}")
print(f"Regular cancel rate    : {reg_cancel.mean():.2%}")
print(f"P-value                : {cancel_p:.4f}")
print(f"Guardrail breached     : {'🚨 YES' if cancel_p < 0.05 else '✅ NO'}\n")

# ══════════════════════════════════════════════════════════════
# SEGMENT ANALYSIS: BY CUSTOMER STATE (top 8 states)
# ══════════════════════════════════════════════════════════════
top_states = df_matched['customer_state'].value_counts().head(8).index.tolist()

segment_results = []

for state in top_states:
    subset = df_matched[df_matched['customer_state'] == state]
    hv  = subset[subset['group'] == 'high_value']['review_score'].dropna()
    reg = subset[subset['group'] == 'regular']['review_score'].dropna()
    
    if len(hv) > 30 and len(reg) > 30:
        stat, p = stats.mannwhitneyu(hv, reg, alternative='two-sided')
        segment_results.append({
            'segment'   : state,
            'hv_mean'   : hv.mean(),
            'reg_mean'  : reg.mean(),
            'diff'      : hv.mean() - reg.mean(),
            'p_value'   : p,
            'hv_n'      : len(hv),
            'reg_n'     : len(reg)
        })

# ── MULTIPLE TESTING CORRECTION ───────────────────────────────
seg_df = pd.DataFrame(segment_results)
_, p_corrected, _, _ = multipletests(seg_df['p_value'], method='bonferroni')
seg_df['p_corrected'] = p_corrected
seg_df['significant'] = seg_df['p_corrected'] < 0.05

print("── Segment Analysis: By State (Bonferroni corrected) ──")
print(seg_df[['segment', 'hv_mean', 'reg_mean', 'diff', 
              'p_value', 'p_corrected', 'significant']].to_string(index=False))

# ══════════════════════════════════════════════════════════════
# SEGMENT ANALYSIS: BY ORDER SIZE BUCKET
# ══════════════════════════════════════════════════════════════
df_matched['order_size'] = pd.qcut(
    df_matched['payment_value'],
    q=4,
    labels=['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)'],
    duplicates='drop'
)

size_results = []

for bucket in df_matched['order_size'].cat.categories:
    subset = df_matched[df_matched['order_size'] == bucket]
    hv  = subset[subset['group'] == 'high_value']['review_score'].dropna()
    reg = subset[subset['group'] == 'regular']['review_score'].dropna()

    if len(hv) > 30 and len(reg) > 30:
        stat, p = stats.mannwhitneyu(hv, reg, alternative='two-sided')
        size_results.append({
            'segment' : str(bucket),
            'hv_mean' : hv.mean(),
            'reg_mean': reg.mean(),
            'diff'    : hv.mean() - reg.mean(),
            'p_value' : p,
            'hv_n'    : len(hv),
            'reg_n'   : len(reg)
        })

if len(size_results) > 0:
    size_df = pd.DataFrame(size_results)
    _, p_corrected2, _, _ = multipletests(size_df['p_value'], method='bonferroni')
    size_df['p_corrected'] = p_corrected2
    size_df['significant'] = size_df['p_corrected'] < 0.05
    print("\n── Segment Analysis: By Order Size ──")
    print(size_df[['segment', 'hv_mean', 'reg_mean', 'diff',
                   'p_value', 'p_corrected', 'significant']].to_string(index=False))
else:
    print("\n── Segment Analysis: By Order Size ──")
    print("⚠️ Insufficient samples per bucket after matching — skipping order size segmentation")
    size_df = pd.DataFrame()
# ══════════════════════════════════════════════════════════════
# FOREST PLOT
# ══════════════════════════════════════════════════════════════
all_segments = seg_df[['segment', 'diff', 'significant']]
if not size_df.empty:
    all_segments = pd.concat([all_segments, size_df[['segment', 'diff', 'significant']]])

colors = ['green' if s else 'gray' for s in all_segments['significant']]

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(all_segments['segment'], all_segments['diff'], color=colors, edgecolor='black')
ax.axvline(0, color='black', linewidth=1.5, linestyle='--')
ax.axvline(0.5, color='red', linewidth=1, linestyle=':', label='Business threshold (0.5)')
ax.axvline(-0.5, color='red', linewidth=1, linestyle=':')
ax.set_xlabel('Mean Difference in Review Score (High-Value - Regular)')
ax.set_title('Segment Analysis: Effect of High-Value Status on Review Score\n(Green = significant after Bonferroni correction)')
ax.legend()
plt.tight_layout()
plt.savefig('../data/forest_plot.png')
plt.show()

print("\n✅ Segment analysis complete!")