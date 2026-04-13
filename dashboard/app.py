import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Fulfillment A/B Test",
    page_icon="📦",
    layout="wide"
)

# ── LOAD DATA ─────────────────────────────────────────────────
import os

@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df_clean   = pd.read_csv(os.path.join(base_path, 'data', 'df_clean.csv'))
    df_matched = pd.read_csv(os.path.join(base_path, 'data', 'df_matched.csv'))
    return df_clean, df_matched

df_clean, df_matched = load_data()

# ── SIDEBAR NAVIGATION ────────────────────────────────────────
st.sidebar.title("📦 A/B Test Dashboard")
st.sidebar.markdown("**E-Commerce Priority Fulfillment**")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Experiment Overview",
    "📊 Primary Results",
    "🗺️ Segment Analysis",
    "🛡️ Guardrail Metrics"
])

# ══════════════════════════════════════════════════════════════
# PAGE 1: EXPERIMENT OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "🏠 Experiment Overview":
    st.title("📦 E-Commerce Priority Fulfillment A/B Test")
    st.markdown("### Does priority fulfillment for high-value orders lead to higher review scores?")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders Analyzed", "96,478")
    col2.metric("High-Value Orders", "23,920")
    col3.metric("Regular Orders", "23,920")
    col4.metric("Date Range", "2016 – 2018")

    st.markdown("---")
    st.markdown("### Experiment Design")

    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **Hypothesis**
        
        High-value orders (top 25% by payment value) receiving 
        priority fulfillment will have higher review scores due 
        to faster and more reliable delivery.
        """)
        st.success("""
        **Treatment Group**
        
        Orders with payment_value ≥ R$176.33 (Q4 threshold)
        
        n = 23,920 orders
        """)

    with col2:
        st.warning("""
        **Methodology Note**
        
        This is an observational study, not a randomized experiment.
        Propensity score matching was applied to balance covariates
        between groups before analysis.
        """)
        st.error("""
        **Control Group**
        
        Orders with payment_value < R$176.33 (bottom 75%)
        
        n = 23,920 matched orders
        """)

    st.markdown("---")
    st.markdown("### Success Criteria")
    criteria = pd.DataFrame({
        'Criteria': ['Statistical Significance', 'Practical Significance', 'Guardrail: Delay Rate', 'Guardrail: Cancellation Rate'],
        'Threshold': ['p-value < 0.05', 'Δ ≥ 0.5 review points', 'No significant increase', 'No significant increase'],
        'Result': ['✅ Met', '❌ Not Met', '🚨 Breached', '✅ Met']
    })
    st.table(criteria)

# ══════════════════════════════════════════════════════════════
# PAGE 2: PRIMARY RESULTS
# ══════════════════════════════════════════════════════════════
elif page == "📊 Primary Results":
    st.title("📊 Primary Results")
    st.markdown("---")

    high_value = df_matched[df_matched['group'] == 'high_value']['review_score'].dropna()
    regular    = df_matched[df_matched['group'] == 'regular']['review_score'].dropna()

    _, p_value = stats.mannwhitneyu(high_value, regular, alternative='two-sided')
    mean_diff  = high_value.mean() - regular.mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("High-Value Mean Score", f"{high_value.mean():.3f}")
    col2.metric("Regular Mean Score",    f"{regular.mean():.3f}")
    col3.metric("Mean Difference",       f"{mean_diff:.3f}", delta=f"{mean_diff:.3f}")
    col4.metric("P-Value",               f"{p_value:.2e}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Review Score Distribution")
        dist_data = df_matched.groupby(['group', 'review_score']).size().reset_index(name='count')
        dist_data['proportion'] = dist_data.groupby('group')['count'].transform(lambda x: x / x.sum())
        fig = px.bar(dist_data, x='review_score', y='proportion', color='group',
                     barmode='group', color_discrete_map={'high_value': '#1f77b4', 'regular': '#ff7f0e'},
                     labels={'review_score': 'Review Score', 'proportion': 'Proportion', 'group': 'Group'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Bootstrap Confidence Interval")
        np.random.seed(42)
        boot_diffs = [
            np.median(np.random.choice(high_value, len(high_value), replace=True)) -
            np.median(np.random.choice(regular, len(regular), replace=True))
            for _ in range(1000)
        ]
        ci_lower = np.percentile(boot_diffs, 2.5)
        ci_upper = np.percentile(boot_diffs, 97.5)

        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(x=boot_diffs, nbinsx=40, name='Bootstrap Distribution',
                                    marker_color='steelblue', opacity=0.7))
        fig2.add_vline(x=0, line_dash='solid', line_color='black', line_width=2, annotation_text='Zero')
        fig2.add_vline(x=ci_lower, line_dash='dash', line_color='red', annotation_text=f'CI Lower: {ci_lower:.3f}')
        fig2.add_vline(x=ci_upper, line_dash='dash', line_color='red', annotation_text=f'CI Upper: {ci_upper:.3f}')
        fig2.update_layout(xaxis_title='Median Difference', yaxis_title='Frequency')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("### Interpretation")
    st.error("""
    **Finding:** High-value orders score statistically significantly LOWER than regular orders 
    (p < 0.05), but the effect size is negligible (-0.11 points). This does not meet our 
    0.5-point business significance threshold. **We do not recommend rolling out priority fulfillment.**
    """)

# ══════════════════════════════════════════════════════════════
# PAGE 3: SEGMENT ANALYSIS
# ══════════════════════════════════════════════════════════════
elif page == "🗺️ Segment Analysis":
    st.title("🗺️ Segment Analysis")
    st.markdown("---")

    segment_data = pd.DataFrame({
        'State': ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'PE'],
        'HV Mean': [4.151, 3.825, 4.121, 4.082, 4.131, 4.079, 3.880, 4.070],
        'Regular Mean': [4.256, 4.032, 4.200, 4.171, 4.301, 4.094, 3.936, 4.110],
        'Difference': [-0.105, -0.207, -0.079, -0.088, -0.170, -0.015, -0.055, -0.040],
        'Significant': [True, True, False, False, True, False, False, False]
    })

    state_filter = st.multiselect("Filter by State", segment_data['State'].tolist(),
                                   default=segment_data['State'].tolist())
    filtered = segment_data[segment_data['State'].isin(state_filter)]

    colors = ['#2ecc71' if s else '#95a5a6' for s in filtered['Significant']]

    fig = go.Figure(go.Bar(
        x=filtered['Difference'],
        y=filtered['State'],
        orientation='h',
        marker_color=colors,
        text=[f"{d:.3f}" for d in filtered['Difference']],
        textposition='outside'
    ))
    fig.add_vline(x=0, line_dash='dash', line_color='black', line_width=2)
    fig.add_vline(x=0.5, line_dash='dot', line_color='red', annotation_text='Business threshold')
    fig.add_vline(x=-0.5, line_dash='dot', line_color='red')
    fig.update_layout(
        title='Effect by State (Green = Significant after Bonferroni Correction)',
        xaxis_title='Mean Difference in Review Score (High-Value - Regular)',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### State-Level Summary")
    st.dataframe(filtered, use_container_width=True)

    st.info("""
    **Key Finding:** The negative effect of high-value status is consistent across all states. 
    SP, RJ, and PR show statistically significant differences after Bonferroni correction. 
    RJ shows the largest gap (-0.207 points).
    """)

# ══════════════════════════════════════════════════════════════
# PAGE 4: GUARDRAIL METRICS
# ══════════════════════════════════════════════════════════════
elif page == "🛡️ Guardrail Metrics":
    st.title("🛡️ Guardrail Metrics")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Guardrail 1: Delivery Delay Rate")
        st.error("🚨 BREACHED — p-value < 0.05")

        delay_data = pd.DataFrame({
            'Group': ['High-Value', 'Regular'],
            'Delay Rate (%)': [8.78, 7.66]
        })
        fig = px.bar(delay_data, x='Group', y='Delay Rate (%)',
                     color='Group', color_discrete_map={'High-Value': '#e74c3c', 'Regular': '#2ecc71'},
                     title='Delivery Delay Rate by Group')
        fig.add_hline(y=7.66, line_dash='dash', annotation_text='Regular baseline')
        st.plotly_chart(fig, use_container_width=True)
        st.warning("High-value orders are delayed 1.12 percentage points more than regular orders.")

    with col2:
        st.markdown("### Guardrail 2: Cancellation Rate")
        st.success("✅ NOT BREACHED — p-value = 1.0")

        cancel_data = pd.DataFrame({
            'Group': ['High-Value', 'Regular'],
            'Cancellation Rate (%)': [0.00, 0.00]
        })
        fig2 = px.bar(cancel_data, x='Group', y='Cancellation Rate (%)',
                      color='Group', color_discrete_map={'High-Value': '#2ecc71', 'Regular': '#2ecc71'},
                      title='Cancellation Rate by Group')
        st.plotly_chart(fig2, use_container_width=True)
        st.success("No difference in cancellation rates between groups.")

    st.markdown("---")
    st.markdown("### Guardrail Summary")
    st.error("""
    **Guardrail 1 (Delivery Delay) is breached.** High-value orders experience 
    higher delay rates (8.78% vs 7.66%), suggesting that the current fulfillment 
    system cannot reliably prioritize these orders without operational impact.
    This further supports the recommendation against rollout.
    """)
