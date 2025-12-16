"""
Analysis charts: statistical signals and spread visualization.
"""
import pandas as pd
import plotly.graph_objects as go


def create_zscore_chart(spread_df: pd.DataFrame, threshold: float):
    """Create z-score chart with threshold lines."""
    if len(spread_df) == 0:
        return go.Figure()
    
    fig = go.Figure()
    
    # Z-score line
    fig.add_trace(go.Scatter(
        x=spread_df['timestamp'],
        y=spread_df['zscore'],
        mode='lines',
        name='Z-Score',
        line=dict(color='#26A69A', width=2),
        fill='tozeroy',
        fillcolor='rgba(38, 166, 154, 0.1)'
    ))
    
    # Threshold lines
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Upper Threshold (+{threshold})",
        annotation_position="right"
    )
    fig.add_hline(
        y=-threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Lower Threshold (-{threshold})",
        annotation_position="right"
    )
    
    # Zero line
    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="gray",
        annotation_text="Mean",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Z-Score Chart (Entry/Exit Signals)",
        xaxis_title="Time",
        yaxis_title="Z-Score",
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


def create_spread_chart(spread_df: pd.DataFrame, spread_mean: float, symbol_a: str, symbol_b: str):
    """Create raw spread line chart."""
    if spread_df.empty:
        return go.Figure()
    
    fig_spread = go.Figure()
    fig_spread.add_trace(go.Scatter(
        x=spread_df['timestamp'],
        y=spread_df['spread'],
        mode='lines',
        name='Raw Spread',
        line=dict(color='#AB47BC', width=2)  # Purple
    ))
    fig_spread.add_hline(y=spread_mean, line_dash="dot", annotation_text="Mean")
    
    fig_spread.update_layout(
        title=f"Raw Price Spread ({symbol_a} - Hedge * {symbol_b})",
        height=350,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E6EDF3"),
        xaxis=dict(gridcolor="#2A2F3A", showgrid=True),
        yaxis=dict(gridcolor="#2A2F3A", showgrid=True),
        template="plotly_dark"
    )
    
    return fig_spread
