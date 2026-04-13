import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# ── LOAD DATA ─────────────────────────────────────────────────
df       = pd.read_csv('data/df_clean.csv')
payments = pd.read_csv('data/olist_order_payments_dataset.csv')

# ── FEATURE 1: PAYMENT INSTALLMENTS ──────────────────────────
installments = payments.groupby('order_id')['payment_installments'].max().reset_index()
df = df.merge(installments, on='order_id', how='left')

# ── FEATURE 2: ESTIMATED DELIVERY DAYS ───────────────────────
df['order_purchase_timestamp']     = pd.to_datetime(df['order_purchase_timestamp'])
df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])

df['estimated_delivery_days'] = (
    df['order_estimated_delivery_date'] - df['order_purchase_timestamp']
).dt.days

print(df[['payment_installments', 'estimated_delivery_days']].describe())
print("\nNulls:")
print(df[['payment_installments', 'estimated_delivery_days']].isnull().sum())

# ── PREPARE FEATURES FOR PROPENSITY MODEL ────────────────────
df = df.dropna(subset=['payment_installments', 'review_score'])

# Encode customer_state as dummy variables
df_model = pd.get_dummies(df, columns=['customer_state'], drop_first=True)

# Define features for the model
feature_cols = ['payment_installments', 'estimated_delivery_days'] + \
               [col for col in df_model.columns if col.startswith('customer_state_')]

X = df_model[feature_cols]
y = (df_model['group'] == 'high_value').astype(int)

print(f"Features used: {len(feature_cols)}")
print(f"Treatment (high_value): {y.sum():,}")
print(f"Control (regular): {(y==0).sum():,}")

# ── FIT PROPENSITY SCORE MODEL ────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_scaled, y)

# ── ASSIGN PROPENSITY SCORES ──────────────────────────────────
df_model['propensity_score'] = model.predict_proba(X_scaled)[:, 1]

print("\nPropensity score distribution:")
print(df_model.groupby('group')['propensity_score'].describe())


# ── PROPENSITY SCORE MATCHING ─────────────────────────────────
# For each high-value order, find the closest regular order
# by propensity score (nearest neighbor matching)

treated  = df_model[df_model['group'] == 'high_value'].copy()
control  = df_model[df_model['group'] == 'regular'].copy()

# Sort control by propensity score for efficient matching
control_sorted = control.sort_values('propensity_score').reset_index(drop=True)

matched_control_indices = []

for ps in treated['propensity_score']:
    # Find closest control unit
    idx = (control_sorted['propensity_score'] - ps).abs().idxmin()
    matched_control_indices.append(control_sorted.loc[idx, 'order_id'])
    # Remove matched unit to avoid reuse
    control_sorted = control_sorted.drop(idx).reset_index(drop=True)

matched_control = df_model[df_model['order_id'].isin(matched_control_indices)]
matched_treated = treated.copy()

# ── COMBINE MATCHED DATASET ───────────────────────────────────
df_matched = pd.concat([matched_treated, matched_control])

print(f"Matched treated  : {len(matched_treated):,}")
print(f"Matched control  : {len(matched_control):,}")
print(f"Total matched    : {len(df_matched):,}")

# ── BALANCE CHECK ─────────────────────────────────────────────
print("\n── Balance BEFORE matching ──")
print(df_model.groupby('group')[['payment_installments', 
                                  'estimated_delivery_days',
                                  'propensity_score']].mean())

print("\n── Balance AFTER matching ──")
print(df_matched.groupby('group')[['payment_installments', 
                                    'estimated_delivery_days',
                                    'propensity_score']].mean())

# ── SAVE MATCHED DATASET ──────────────────────────────────────
df_matched.to_csv('data/df_matched.csv', index=False)
print("\n✅ Matched dataset saved to data/df_matched.csv")