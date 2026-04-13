Business Recommendation Memo
To: Operations Leadership
From: Shiva
Date: April 2026
Re: Priority Fulfillment for High-Value Orders — Experiment Results & Recommendation

TL;DR
We tested whether giving priority fulfillment to high-value orders (top 25% by payment value, ≥ R$176.33) leads to higher customer review scores. It does not. High-value orders scored statistically lower than regular orders, the effect is negligibly small, and a key operational guardrail was breached. We recommend against rolling out priority fulfillment at this time.

Recommendation
Do not implement priority fulfillment for high-value orders based on current operational capabilities.
The data shows no customer satisfaction benefit, and the fulfillment system appears unable to reliably prioritize high-value orders without introducing delivery delays — which risks damaging satisfaction across the broader customer base.

Evidence
1. No satisfaction improvement
After propensity score matching to control for order characteristics, high-value orders scored 0.11 points lower than regular orders (4.05 vs 4.16 on a 1–5 scale). While statistically significant (p < 0.05), this effect is far below our 0.5-point business significance threshold and represents a negligible practical difference.
2. Consistent negative pattern across regions
The effect held across all 8 states analyzed. SP, RJ, and PR showed statistically significant gaps after Bonferroni correction, with RJ showing the largest difference (-0.207 points). This rules out the result being a regional anomaly.
3. Guardrail breached — delivery delays increased
High-value orders experienced a statistically significant higher delivery delay rate (8.78% vs 7.66%, p < 0.05). This suggests that prioritizing high-value orders introduces operational strain that negatively impacts delivery reliability — the opposite of what priority fulfillment is intended to achieve.

Caveats & Limitations

Observational data: This dataset is historical, not from a randomized experiment. Propensity score matching was applied to reduce selection bias, but causal claims cannot be made with certainty.
No fulfillment treatment recorded: The dataset does not contain an actual "priority fulfillment" flag — high-value status is used as a proxy. A true A/B test with explicit treatment assignment would provide stronger evidence.
Review score ceiling effect: ~60% of all orders receive a 5-star review, which compresses the score distribution and limits our ability to detect upward movement.


Next Steps

Investigate why high-value orders experience more delays — is it product size, seller location, or carrier capacity? This operational question should be answered before any fulfillment priority changes.
Design a true randomized experiment — randomly assign a subset of high-value orders to an explicit priority fulfillment lane and measure the impact. This would provide causal evidence the current analysis cannot.
Explore alternative satisfaction levers — proactive delivery notifications, dedicated customer support for high-value orders, or post-delivery follow-ups may improve satisfaction without the operational risk of fulfillment prioritization.
Re-evaluate the high-value threshold — R$176.33 (Q4) captures 25% of orders. A tighter threshold (e.g., top 10%) might be more operationally feasible to prioritize and worth testing separately.


Full analysis, methodology, and interactive dashboard available at:
github.com/shivzen-pixel/ecommerce-ab-test