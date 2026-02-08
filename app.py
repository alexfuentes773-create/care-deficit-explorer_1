import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Config
st.set_page_config(page_title="Readiness Carve-Out Pilot Model", layout="wide")

st.title("Readiness Carve-Out Pilot Model (65% Separation)")
st.markdown("""
Pilot simulation for separating 65% of fixed readiness costs from CARE, funded centrally.  
Adjust sliders to see impacts on the statement of operations and key metrics.
""")

# Sidebar
st.sidebar.header("Pilot Parameters")
util_pct = st.sidebar.slider("Utilization (% of benchmark)", 50, 150, 70) / 100.0
staff_inc_pct = st.sidebar.slider("Staffing Increase (%)", 0, 30, 0) / 100.0
separation_pct = st.sidebar.slider("Readiness Separation (%)", 50, 75, 65) / 100.0
leakage_max = st.sidebar.slider("Max Leakage ($M)", 0.0, 60.0, 30.0)

# Baseline
BASE_GROSS = 182.1
BASE_MILPAY = 104.7
BASE_FIXED = 178.6
REIMB = 0.0

# Calculations
gross = BASE_GROSS * util_pct * (1 + 0.6 * staff_inc_pct)
milpay = BASE_MILPAY * (1 + staff_inc_pct)
net_earned = gross - milpay + REIMB

leakage = leakage_max * max(0, 1 - util_pct)

# Original
fixed_orig = BASE_FIXED * (1 + staff_inc_pct)
total_cost_orig = fixed_orig + leakage
deficit_orig = net_earned - total_cost_orig

# Pilot (separated)
fixed_residual = BASE_FIXED * (1 - separation_pct) * (1 + staff_inc_pct)
total_cost_pilot = fixed_residual + leakage
deficit_pilot = net_earned - total_cost_pilot

# Statement of Operations
st.subheader("Pilot Statement of Operations ($ Millions)")

ops_data = {
    "Line Item": [
        "Gross CARE Value",
        "− Military Pay Offset",
        "+ Reimbursable Revenue",
        "= Net Earned Funding",
        "Fixed Readiness Costs in CARE",
        "Variable Leakage Costs",
        "= Total Costs",
        "= Net Operating Position"
    ],
    "Original CARE": [
        round(gross, 1),
        round(-milpay, 1),
        REIMB,
        round(net_earned, 1),
        round(fixed_orig, 1),
        round(leakage, 1),
        round(total_cost_orig, 1),
        round(deficit_orig, 1)
    ],
    "Pilot (Separated)": [
        round(gross, 1),
        round(-milpay, 1),
        REIMB,
        round(net_earned, 1),
        round(fixed_residual, 1),
        round(leakage, 1),
        round(total_cost_pilot, 1),
        round(deficit_pilot, 1)
    ]
}

df_ops = pd.DataFrame(ops_data)
st.table(df_ops)

# Metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Original Net Position", f"${round(deficit_orig, 1):,.1f}M")
with col2:
    st.metric("Pilot Net Position", f"${round(deficit_pilot, 1):,.1f}M")

# Bar Chart
st.subheader("Key Metrics Comparison")

metrics = ['Net Earned', 'Fixed in CARE', 'Leakage', 'Net Position']
orig_values = [net_earned, fixed_orig, leakage, deficit_orig]
pilot_values = [net_earned, fixed_residual, leakage, deficit_pilot]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(metrics))
width = 0.35
ax.bar(x - width/2, [round(v, 1) for v in orig_values], width, label='Original CARE', color='red')
ax.bar(x + width/2, [round(v, 1) for v in pilot_values], width, label='Pilot (Separated)', color='green')
ax.set_ylabel('$ Millions')
ax.set_title('Original vs. Pilot Model – Financial Metrics')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()
ax.grid(True, axis='y', alpha=0.3)
st.pyplot(fig)

# Notes
st.markdown("**Pilot Notes**: 65% separation assumes central funding for readiness; CARE handles residual fixed + variables.")
