"""
Streamlit dashboard for real-time pair trading analysis.
"""
import streamlit as st
import pandas as pd
import time
from database import Database
from analytics import get_pair_analytics, get_pair_analytics_from_uploaded_csv
from components import render_sidebar, render_metrics
from charts.trading import create_overlay_chart, create_volume_chart
from charts.analysis import create_zscore_chart, create_spread_chart


# Page configuration
st.set_page_config(
    page_title="Pair Trading Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()

if 'symbol_a' not in st.session_state:
    st.session_state.symbol_a = "BTCUSDT"

if 'symbol_b' not in st.session_state:
    st.session_state.symbol_b = "ETHUSDT"


def main():
    """Main dashboard orchestrator."""
    # Render header
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='color: #E6EDF3; font-family: "Source Sans Pro", sans-serif; font-size: 3rem; font-weight: 600; margin-bottom: 0; letter-spacing: -1px;'>
                QUANT ANALYTICS <span style='color: #00E5FF;'>PRO</span>
            </h1>
            <p style='color: #9BA1A6; font-size: 1.1rem; margin-top: 5px;'>
                REAL-TIME EXECUTION & STATISTICAL ARBITRAGE
            </p>
            <hr style="border: 0; border-top: 1px solid #2A2F3A; margin-top: 20px;">
        </div>
    """, unsafe_allow_html=True)
    
    # Render sidebar and get settings
    settings = render_sidebar()
    
    # Load data based on settings
    if settings['uploaded_file'] is not None:
        # MODE: Historical Analysis (Uploaded Data)
        try:
            uploaded_df = pd.read_csv(settings['uploaded_file'])
            analytics = get_pair_analytics_from_uploaded_csv(uploaded_df)
            st.warning("⚠️ MODE: Historical Analysis (Uploaded Data)")
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
            # Fall back to live data on error
            analytics = get_pair_analytics(
                st.session_state.db,
                settings['symbol_a'],
                settings['symbol_b'],
                settings['window_size']
            )
    else:
        # MODE: Live Data (Database)
        analytics = get_pair_analytics(
            st.session_state.db,
            settings['symbol_a'],
            settings['symbol_b'],
            settings['window_size'],
            settings['timeframe_seconds']
        )
    
    # Error handling
    if analytics.get('error'):
        st.warning(f"⚠️ {analytics['error']}")
        st.info("Waiting for more data from Binance WebSocket...")
        if settings['auto_refresh']:
            time.sleep(settings['refresh_interval'])
            st.rerun()
        return
    
    # Render metrics
    render_metrics(analytics, settings['symbol_a'], settings['symbol_b'])
    
    # Alert banner
    current_zscore = analytics['current_zscore']
    if abs(current_zscore) >= settings['zscore_threshold']:
        if current_zscore > 0:
            st.error(f"🚨 **SELL SIGNAL TRIGGERED!** Z-Score ({current_zscore:.2f}) exceeds upper threshold (+{settings['zscore_threshold']})")
        else:
            st.success(f"🚨 **BUY SIGNAL TRIGGERED!** Z-Score ({current_zscore:.2f}) exceeds lower threshold (-{settings['zscore_threshold']})")
    else:
        st.info(f"ℹ️ Z-Score ({current_zscore:.2f}) within normal range (±{settings['zscore_threshold']})")
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Trading Signals", "📊 Market Depth & Volume", "📉 Raw Spread Analysis"])

    with tab1:
        # Trading Signals: Overlay and Z-Score
        col1, col2 = st.columns(2)
        with col1:
            overlay_fig = create_overlay_chart(
                analytics['asset_a'],
                analytics['asset_b'],
                analytics['hedge_ratio'],
                settings['symbol_a'],
                settings['symbol_b']
            )
            st.plotly_chart(overlay_fig, use_container_width=True)
        
        with col2:
            zscore_fig = create_zscore_chart(
                analytics['spread_df'],
                settings['zscore_threshold']
            )
            st.plotly_chart(zscore_fig, use_container_width=True)

    with tab2:
        # Volume Analysis
        if not analytics['asset_a'].empty:
            fig_vol = create_volume_chart(
                analytics['asset_a'],
                analytics['asset_b'],
                settings['symbol_a'],
                settings['symbol_b']
            )
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.info("Waiting for volume data...")

    with tab3:
        # Raw Spread Analysis
        if not analytics['spread_df'].empty:
            fig_spread = create_spread_chart(
                analytics['spread_df'],
                analytics['spread_mean'],
                settings['symbol_a'],
                settings['symbol_b']
            )
            st.plotly_chart(fig_spread, use_container_width=True)
        else:
            st.info("Waiting for spread data...")
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Processed Data")
    
    if len(analytics['spread_df']) > 0:
        display_df = analytics['spread_df'][['timestamp', 'close_a', 'close_b', 'spread', 'zscore']].copy()
        display_df.columns = ['Timestamp', f'{settings["symbol_a"]} Price', 
                             f'{settings["symbol_b"]} Price', 'Spread', 'Z-Score']
        display_df['Timestamp'] = pd.to_datetime(display_df['Timestamp'])
        st.dataframe(display_df, use_container_width=True, height=300)
        
        # Download CSV button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"pair_trading_data_{int(time.time())}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available yet. Waiting for WebSocket data...")
    
    # Auto refresh
    if settings['auto_refresh']:
        time.sleep(settings['refresh_interval'])
        st.rerun()


if __name__ == "__main__":
    main()
