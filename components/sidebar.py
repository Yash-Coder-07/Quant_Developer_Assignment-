"""
Sidebar component for dashboard controls and configuration.
"""
import streamlit as st
from typing import Dict, Any


def render_sidebar() -> Dict[str, Any]:
    """
    Render the sidebar with all controls and return a dictionary of settings.
    
    Returns:
        Dictionary containing:
            - window_size: int
            - zscore_threshold: float
            - auto_refresh: bool
            - refresh_interval: int
            - symbol_a: str
            - symbol_b: str
            - uploaded_file: UploadedFile or None
    """
    with st.sidebar:
        st.header("⚙️ Controls")
        timeframe_name = st.selectbox(
            "Timeframe",
            options=["1 Second", "1 Minute", "5 Minutes"],
            index=1,  # Default to 1 Minute
            help="Resolution of the bars (OHLC)"
        )
        
        # Map the text to seconds
        timeframe_map = {"1 Second": 1, "1 Minute": 60, "5 Minutes": 300}
        timeframe_seconds = timeframe_map[timeframe_name]
        
        window_size = st.slider(
            "Window Size (minutes)",
            min_value=5,
            max_value=240,
            value=60,
            step=5,
            help="Time window for analysis"
        )
        
        zscore_threshold = st.slider(
            "Z-Score Threshold",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.1,
            help="Threshold for entry/exit signals"
        )
        
        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=True,
            help="Automatically refresh data every few seconds"
        )
        
        refresh_interval = st.slider(
            "Refresh Interval (seconds)",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            disabled=not auto_refresh
        )
        
        st.markdown("---")
        st.markdown("### 📈 Pair Configuration")
        symbol_a_input = st.text_input(
            "Asset A",
            value=st.session_state.symbol_a,
            key="symbol_a_input"
        )
        symbol_b_input = st.text_input(
            "Asset B",
            value=st.session_state.symbol_b,
            key="symbol_b_input"
        )
        # Update session state
        st.session_state.symbol_a = symbol_a_input
        st.session_state.symbol_b = symbol_b_input
        
        st.markdown("---")
        uploaded_file = st.file_uploader(
            "Upload CSV for Analysis",
            type=['csv'],
            key="ohlc_upload"
        )
    
    return {
        'window_size': window_size,
        'timeframe_seconds': timeframe_seconds,
        'zscore_threshold': zscore_threshold,
        'auto_refresh': auto_refresh,
        'refresh_interval': refresh_interval,
        'symbol_a': st.session_state.symbol_a,
        'symbol_b': st.session_state.symbol_b,
        'uploaded_file': uploaded_file
        
    }
