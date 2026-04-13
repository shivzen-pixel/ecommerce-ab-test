# 📦 E-Commerce Priority Fulfillment A/B Test

**Does giving priority fulfillment to high-value orders lead to higher customer review scores?**

A rigorous statistical experiment on 96,478 real Brazilian e-commerce orders using propensity score matching, Mann-Whitney U testing, and segment analysis across 8 states.

🔴 **[Live Dashboard](https://ecommerce-ab-test-vrp26wcrrs9scvzhdzuejf.streamlit.app)** | 📄 **[Business Memo](memo/recommendation_memo.md)** | 📓 **[Project Brief](memo/project_brief.md)**

---

## 🎯 Business Question

> Does priority fulfillment for high-value orders (top 25% by payment value) lead to measurably higher customer review scores compared to regular orders?

---

## 🔍 Key Findings

| Metric | Result |
|---|---|
| High-Value Mean Review Score | 4.052 |
| Regular Mean Review Score | 4.164 |
| Mean Difference | **-0.11 points** |
| Statistical Significance | ✅ p < 0.05 |
| Practical Significance | ❌ Below 0.5-point threshold |
| Guardrail: Delivery Delay | 🚨 Breached (8.78% vs 7.66%) |
| Guardrail: Cancellation Rate | ✅ Not breached |

**Recommendation: Do not roll out priority fulfillment.** High-value orders score statistically lower than regular orders, the effect is negligibly small, and delivery delays increased — suggesting the fulfillment system cannot reliably prioritize these orders without operational impact.

---

## 🏗️ Methodology

### 1. Experiment Design
- **Treatment group:** Orders with `payment_value` ≥ R$176.33 (top 25%, Q4 threshold)
- **Control group:** Remaining orders (bottom 75%)
- **Primary metric:** Review score (1–5 stars)
- **Guardrail metrics:** Delivery delay rate, cancellation rate
- **Success criteria:** p < 0.05 AND effect ≥ 0.5 points

### 2. Causal Inference — Propensity Score Matching
Since this is observational data (not a randomized experiment), high-value and regular orders differ systematically. Propensity score matching was applied to balance covariates before analysis.

| Feature | HV Before | Regular Before | HV After | Regular After |
|---|---|---|---|---|
| Payment Installments | 4.51 | 2.40 | 4.51 | 4.05 |
| Estimated Delivery Days | 25.19 | 22.76 | 25.19 | 25.22 |
| Propensity Score | 0.344 | 0.218 | 0.344 | 0.316 |

### 3. Statistical Testing
- **Primary test:** Mann-Whitney U (chosen for skewed, ordinal review scores)
- **Effect size:** Cliff's Delta (rank-biserial correlation)
- **Confidence intervals:** Bootstrap CIs (1,000 iterations)
- **Sensitivity check:** Independent t-test
- **Multiple testing correction:** Bonferroni correction for segment analysis

### 4. Power Analysis
With 23,920 matched pairs, the minimum detectable effect is **0.027 review score points** — well below our 0.5-point business threshold, confirming the study is well-powered.

---

## 📊 Results Summary

### Primary Analysis
High-value orders score statistically significantly lower than regular orders (p = 6.6e-11), but Cliff's Delta = -0.031 indicates a negligible effect size. The -0.11 point difference does not meet the 0.5-point business significance threshold.

### Segment Analysis (8 States, Bonferroni Corrected)
The negative effect is consistent across all states. SP, RJ, and PR show statistically significant differences:

| State | HV Mean | Regular Mean | Difference | Significant |
|---|---|---|---|---|
| SP | 4.151 | 4.256 | -0.105 | ✅ |
| RJ | 3.825 | 4.032 | -0.207 | ✅ |
| MG | 4.121 | 4.200 | -0.079 | ❌ |
| RS | 4.082 | 4.171 | -0.088 | ❌ |
| PR | 4.131 | 4.301 | -0.170 | ✅ |

### Guardrail Metrics
- **Delivery delay rate:** 8.78% (HV) vs 7.66% (regular) — **statistically significant breach**
- **Cancellation rate:** 0.00% both groups — **no breach**

---

## 🗂️ Project Structure

```
ecommerce-ab-test/
├── data/
│   ├── olist_orders_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── df_clean.csv              # processed dataset
│   └── df_matched.csv            # propensity matched dataset
├── notebooks/
│   ├── 01_eda.py                 # EDA & data cleaning
│   ├── 02_power_analysis.py      # Power analysis & MDE
│   ├── 03_propensity_matching.py # Propensity score matching
│   ├── 04_analysis.py            # Primary statistical analysis
│   └── 05_segments.py            # Guardrail & segment analysis
├── dashboard/
│   └── app.py                    # Streamlit dashboard
├── memo/
│   ├── project_brief.md          # Pre-analysis experiment design
│   └── recommendation_memo.md    # Business recommendation
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Purpose | Tool |
|---|---|
| Data wrangling | pandas, numpy |
| Statistical testing | scipy, statsmodels, pingouin |
| Causal inference | scikit-learn (propensity matching) |
| Visualization | matplotlib, seaborn, plotly |
| Dashboard | Streamlit |
| Environment | Python 3.11, venv |
| Version control | Git + GitHub |

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/shivzen-pixel/ecommerce-ab-test.git
cd ecommerce-ab-test

# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run analysis notebooks (in order)
cd notebooks
python3 01_eda.py
python3 02_power_analysis.py
python3 03_propensity_matching.py
python3 04_analysis.py
python3 05_segments.py

# Launch dashboard
cd ../dashboard
streamlit run app.py
```

---

## 📁 Data Source

[Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 100k+ real orders from 2016–2018, made publicly available by Olist on Kaggle.

---

## ⚠️ Limitations

- Observational data — propensity matching reduces but does not eliminate selection bias
- No actual priority fulfillment treatment recorded — high-value status used as proxy
- Review score ceiling effect (~60% of orders receive 5 stars)
- Causal conclusions require a true randomized experiment
