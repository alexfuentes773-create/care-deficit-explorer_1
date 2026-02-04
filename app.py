import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# APP CONFIGURATION
# =============================================================================
st.set_page_config(page_title="CARE Deficit Sensitivity Explorer",
                   page_icon="💰",
                   layout="wide")

st.title("CARE Deficit Sensitivity Explorer")
st.markdown("""
This interactive tool models structural deficits in the Military Health System's **CARE funding framework**  
based on FY2026 data from a large MTF. Adjust the sliders to explore how changes affect the net operating position.
""")

# =============================================================================
# BASELINE PARAMETERS (from your manuscript)
# =============================================================================
BASE_GROSS_CARE = 182.1      # $M at 100% utilization
BASE_MILPAY      = 104.7     # $M
BASE_FIXED       = 178.6     # $M total fixed (DHP + MERHCF)
BASE_LEAKAGE_MAX = 30.0      # $M maximum variable leakage at low utilization

# =============================================================================
# SIDEBAR CONTROLS
# =============================================================================
st.sidebar.header("Scenario Controls")

util_pct = st.sidebar.slider(
    "Provider Utilization (% of benchmark)",
    min_value=50, max_value=150, value=70, step=5
) / 100.0

staff_inc_pct = st.sidebar.slider(
    "Staffing Increase (%)",
    min_value=0, max_value=30, value=0, step=5
) / 100.0

readiness_multiplier = st.sidebar.slider(
    "Readiness Cost Multiplier (1.0 = baseline)",
    min_value=0.8, max_value=1.5, value=1.0, step=0.05
)

leakage_max = st.sidebar.slider(
    "Max Leakage at 0% Util ($M)",
    min_value=0.0, max_value=60.0, value=BASE_LEAKAGE_MAX, step=5.0
)

show_advanced = st.sidebar.checkbox("Show advanced options", value=False)

if show_advanced:
    milpay_scale_factor = st.sidebar.slider(
        "MILPAY scaling with staffing (1.0 = linear)",
        0.5, 1.5, 1.0, 0.1
    )
    earned_growth_factor = st.sidebar.slider(
        "Earned value growth from staffing (0.6 = sub-linear)",
        0.3, 1.0, 0.6, 0.05
    )
else:
    milpay_scale_factor = 1.0
    earned_growth_factor = 0.6

# =============================================================================
# CALCULATIONS
# =============================================================================
# Gross CARE scales with utilization
gross_care = BASE_GROSS_CARE * util_pct

# Staffing effects
gross_care += BASE_GROSS_CARE * earned_growth_factor * staff_inc_pct
fixed_adjusted = BASE_FIXED * readiness_multiplier * (1 + staff_inc_pct)
milpay_adjusted = BASE_MILPAY * (1 + staff_inc_pct * milpay_scale_factor)

# Leakage decreases linearly with utilization
leakage = leakage_max * max(0, 1 - util_pct)

# Net position
net_earned = gross_care - milpay_adjusted
total_cost = fixed_adjusted + leakage
deficit = net_earned - total_cost

# Color coding for display
deficit_color = "green" if deficit >= 0 else "red"
delta_str = f"+${deficit:,.1f}M surplus" if deficit >= 0 else f"-${abs(deficit):,.1f}M deficit"

# =============================================================================
# MAIN DISPLAY
# =============================================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Scenario Results")
    
    st.metric(
        label="Projected Net Operating Position",
        value=f"${deficit:,.1f}M",
        delta=delta_str if deficit != 0 else "Balanced",
        delta_color="normal" if deficit >= 0 else "inverse"
    )
    
    st.markdown(f"**Utilization:** {util_pct*100:.0f}% of benchmark")
    st.markdown(f"**Staffing Change:** +{staff_inc_pct*100:.0f}%")
    st.markdown(f"**Effective Fixed Costs:** ${fixed_adjusted:,.1f}M (readiness ×{readiness_multiplier:.2f})")
    st.markdown(f"**Estimated Leakage:** ${leakage:,.1f}M")

with col2:
    st.subheader("Quick Summary")
    st.write("**Earned Funding**", f"${net_earned:,.1f}M")
    st.write("**Total Costs**", f"${total_cost:,.1f}M")
    st.write("**Structural Gap?**", "Yes (deficit persists)" if deficit < 0 else "No (breakeven/surplus)")

# =============================================================================
# VISUALIZATION
# =============================================================================
st.subheader("Deficit Sensitivity Chart")

# Generate curve for utilization (fixed staffing & readiness)
util_range = np.linspace(0.5, 1.5, 21)
deficits = []
for u in util_range:
    g = BASE_GROSS_CARE * u + BASE_GROSS_CARE * earned_growth_factor * staff_inc_pct
    m = BASE_MILPAY * (1 + staff_inc_pct * milpay_scale_factor)
    f = BASE_FIXED * readiness_multiplier * (1 + staff_inc_pct)
    l = leakage_max * max(0, 1 - u)
    deficits.append((g - m) - (f + l))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(util_range * 100, deficits, marker='o', color='darkred', linewidth=2)
ax.axhline(0, color='gray', linestyle='--', linewidth=1)
ax.set_xlabel("Utilization (% of Benchmark)")
ax.set_ylabel("Net Position ($ Millions)")
ax.set_title(f"Net Position vs Utilization\n(Staffing +{staff_inc_pct*100:.0f}%, Readiness ×{readiness_multiplier:.2f})")
ax.grid(True, alpha=0.3)

# Mark current point
current_def = deficit
ax.plot(util_pct * 100, current_def, 'bo', markersize=12, label=f"Current: {util_pct*100:.0f}%")
ax.legend()

st.pyplot(fig)

# =============================================================================
# FOOTER / CAVEATS
# =============================================================================
st.markdown("---")
st.caption("""
**Notes & Caveats**  
• Model based on FY2026 large MTF baseline data.  
• Fixed costs assumed largely invariant to utilization (structural readiness/MERHCF).  
• Leakage modeled linearly — real behavior may be non-linear.  
• Not official DHA output — exploratory tool only.  
Views are author's and do not reflect official policy.
""")
