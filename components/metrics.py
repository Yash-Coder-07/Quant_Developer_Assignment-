"""
Metrics component for displaying key analytics metrics.
"""
import streamlit as st
from typing import Dict, Any


def render_metrics(analytics: Dict[str, Any], symbol_a: str, symbol_b: str):
    """
    Render the metrics display section.
    
    Args:
        analytics: Dictionary containing analytics data
        symbol_a: Symbol for asset A
        symbol_b: Symbol for asset B
    """
    # Key metrics - 6 columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Current Z-Score", f"{analytics['current_zscore']:.2f}")
    
    with col2:
        st.metric("Hedge Ratio", f"{analytics['hedge_ratio']:.4f}")
        
    with col3:
        # Change format to scientific notation to see tiny numbers
        st.metric("Spread Mean", f"{analytics['spread_mean']:.2e}")
        
    with col4:
        # Change format to scientific notation
        st.metric("Spread Std", f"{analytics['spread_std']:.2e}")

    # ADF P-Value metric
    with col5:
        p_val = analytics.get('adf_pvalue', 1.0)
        # Color code it: Green if < 0.05 (Stationary), Red if > 0.05 (Non-Stationary)
        if p_val < 0.05:
            delta_val = "Stationary ✅"
            delta_color = "normal"
        else:
            delta_val = "Non-Stationary ⚠️"
            delta_color = "inverse"

        st.metric(
            "ADF P-Value", 
            f"{p_val:.4f}",
            delta=delta_val,
            delta_color=delta_color
        )
    
    with col6:
        rolling_corr = analytics.get('rolling_corr', 0.0)
        st.metric("Rolling Corr (30m)", f"{rolling_corr:.4f}")
