"""
Trading charts: price action and volume visualization.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_overlay_chart(asset_a: pd.DataFrame, asset_b: pd.DataFrame, hedge_ratio: float, symbol_a: str, symbol_b: str):
    """Create normalized price overlay chart."""
    if len(asset_a) == 0 or len(asset_b) == 0:
        return go.Figure()
    
    # Merge dataframes
    merged = pd.merge(
        asset_a[['timestamp', 'close']],
        asset_b[['timestamp', 'close']],
        on='timestamp',
        suffixes=('_a', '_b')
    )
    
    if len(merged) == 0:
        return go.Figure()
    
    # Normalize prices
    merged['price_a_norm'] = merged['close_a'] / merged['close_a'].iloc[0]
    merged['price_b_norm'] = merged['close_b'] / merged['close_b'].iloc[0]
    merged['price_b_hedged'] = merged['price_b_norm'] * hedge_ratio
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=merged['timestamp'],
        y=merged['price_a_norm'],
        mode='lines',
        name=f'{symbol_a} (Normalized)',
        line=dict(color='#00E5FF', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=merged['timestamp'],
        y=merged['price_b_hedged'],
        mode='lines',
        name=f'{symbol_b} (Hedged, Normalized)',
        line=dict(color='#FFA726', width=2)
    ))
    
    fig.update_layout(
        title="Normalized Price Overlay",
        xaxis_title="Time",
        yaxis_title="Normalized Price",
        hovermode='x unified',
        height=400,
        legend=dict(
            orientation="h",       # Horizontal orientation
            yanchor="bottom",      # Anchor to the bottom of the legend box
            y=1.02,                # Position it just above the chart area
            xanchor="right",       # Anchor to the right
            x=1                    # Align with the right edge
        ),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E6EDF3"),
        xaxis=dict(gridcolor="#2A2F3A", showgrid=True),
        yaxis=dict(gridcolor="#2A2F3A", showgrid=True),
        template="plotly_dark"
    )
    
    return fig


def create_volume_chart(asset_a: pd.DataFrame, asset_b: pd.DataFrame, symbol_a: str, symbol_b: str):
    """Create volume analysis chart with dual y-axes."""
    if asset_a.empty or asset_b.empty:
        return go.Figure()
    
    fig_vol = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Asset A Volume
    fig_vol.add_trace(go.Bar(
        x=asset_a['timestamp'], 
        y=asset_a['volume'],
        name=f"{symbol_a} Volume",
        marker_color='rgba(0, 229, 255, 0.5)'  # #00E5FF with 0.5 opacity
    ), secondary_y=False)
    
    # Asset B Volume
    fig_vol.add_trace(go.Bar(
        x=asset_b['timestamp'], 
        y=asset_b['volume'],
        name=f"{symbol_b} Volume",
        marker_color='rgba(255, 167, 38, 0.5)'  # #FFA726 with 0.5 opacity
    ), secondary_y=True)

    fig_vol.update_layout(
        title="Volume Analysis",
        hovermode='x unified',
        height=350,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E6EDF3"),
        xaxis=dict(gridcolor="#2A2F3A", showgrid=True),
        yaxis=dict(gridcolor="#2A2F3A", showgrid=True),
        template="plotly_dark"
    )
    
    return fig_vol
