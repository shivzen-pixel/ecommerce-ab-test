import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_columns', None)

# ── 1. LOAD DATA ──────────────────────────────────────────────
orders    = pd.read_csv('data/olist_orders_dataset.csv')
reviews   = pd.read_csv('data/olist_order_reviews_dataset.csv')
payments  = pd.read_csv('data/olist_order_payments_dataset.csv')
customers = pd.read_csv('data/olist_customers_dataset.csv')

# ── 2. AGGREGATE PAYMENTS (fix installments issue) ────────────
payments_agg = payments.groupby('order_id')['payment_value'].sum().reset_index()

# ── 3. FIX DUPLICATE REVIEWS (keep highest score per order) ───
reviews_clean = reviews.sort_values('review_score', ascending=False)\
                       .drop_duplicates(subset='order_id', keep='first')

# ── 4. MERGE ALL TABLES ───────────────────────────────────────
df = orders.merge(payments_agg, on='order_id', how='left') \
           .merge(reviews_clean[['order_id', 'review_score']], on='order_id', how='left') \
           .merge(customers[['customer_id', 'customer_state']], on='customer_id', how='left')

print("Final shape:", df.shape)
print("Columns:", df.columns.tolist())

# ── 5. DATA QUALITY CHECK ─────────────────────────────────────
print("\n── Null counts ──")
print(df.isnull().sum())

print("\n── Duplicate order_ids ──")
print(df.duplicated(subset='order_id').sum())

# ── 6. FIX DATETIME COLUMNS ───────────────────────────────────
date_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    df[col] = pd.to_datetime(df[col])

print("\n── Date range ──")
print("Earliest order:", df['order_purchase_timestamp'].min())
print("Latest order:  ", df['order_purchase_timestamp'].max())

# ── 7. FILTER TO DELIVERED ORDERS ONLY ───────────────────────
print("\n── Order status counts ──")
print(df['order_status'].value_counts())

df = df[df['order_status'] == 'delivered'].copy()
print("\nDelivered orders only:", df.shape)

# ── 8. DISTRIBUTION: REVIEW SCORES ───────────────────────────
plt.figure(figsize=(8, 4))
df['review_score'].value_counts().sort_index().plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('Distribution of Review Scores')
plt.xlabel('Review Score')
plt.ylabel('Count')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('../data/review_score_dist.png')
plt.show()
print("\nReview score stats:")
print(df['review_score'].describe())

# ── 9. DISTRIBUTION: PAYMENT VALUE ───────────────────────────
plt.figure(figsize=(8, 4))
df['payment_value'].plot(kind='hist', bins=50, color='darkorange', edgecolor='black')
plt.title('Distribution of Payment Value')
plt.xlabel('Payment Value (BRL)')
plt.tight_layout()
plt.savefig('../data/payment_value_dist.png')
plt.show()
print("\nPayment value stats:")
print(df['payment_value'].describe())

# ── 10. DEFINE TREATMENT & CONTROL GROUPS ────────────────────
q75 = df['payment_value'].quantile(0.75)
print(f"\nQ4 threshold (top 25%): R${q75:.2f}")

df['group'] = np.where(df['payment_value'] >= q75, 'high_value', 'regular')
print("\nGroup counts:")
print(df['group'].value_counts())

# ── 11. BASELINE COMPARISON ───────────────────────────────────
print("\nBaseline review score by group:")
print(df.groupby('group')['review_score'].agg(['mean', 'median', 'count']))

# ── 12. SAVE CLEAN DATAFRAME ─────────────────────────────────
df.to_csv('data/df_clean.csv', index=False)
print("\n✅ Clean dataset saved to data/df_clean.csv")