"""
Core orchestration function for pair trading analytics.
"""
import pandas as pd
from database import Database
from analytics.data_processing import resample_to_ohlc
from analytics.calculations import (
    calculate_hedge_ratio,
    calculate_spread_and_zscore,
    calculate_adf
)


def get_pair_analytics(
    db: Database,
    symbol_a: str,
    symbol_b: str,
    window_minutes: int = 60,
    interval_seconds: int = 60
) -> dict:
    """
    Get complete analytics for a pair.
    
    Returns:
        Dictionary with all analytics data
    """
    # Get ticks from database
    ticks_a = db.get_ticks(symbol_a, window_minutes)
    ticks_b = db.get_ticks(symbol_b, window_minutes)
    
    if not ticks_a or not ticks_b:
        return {
            'asset_a': pd.DataFrame(),
            'asset_b': pd.DataFrame(),
            'hedge_ratio': 1.0,
            'spread_df': pd.DataFrame(),
            'current_zscore': 0.0,
            'spread_mean': 0.0,
            'spread_std': 1.0,
            'rolling_corr': 0.0,
            'error': 'Insufficient data'
        }
    
    # Resample to 1-minute bars
    ohlc_a = resample_to_ohlc(ticks_a, interval_seconds=interval_seconds)
    ohlc_b = resample_to_ohlc(ticks_b, interval_seconds=interval_seconds)
    
    if len(ohlc_a) < 2 or len(ohlc_b) < 2:
        return {
            'asset_a': ohlc_a,
            'asset_b': ohlc_b,
            'hedge_ratio': 1.0,
            'spread_df': pd.DataFrame(),
            'current_zscore': 0.0,
            'spread_mean': 0.0,
            'spread_std': 1.0,
            'rolling_corr': 0.0,
            'error': 'Insufficient bars after resampling'
        }
    
    # Calculate hedge ratio
    hedge_ratio = calculate_hedge_ratio(ohlc_a, ohlc_b)
    
    # Calculate spread and z-score
    spread_df, current_zscore, spread_mean, spread_std = calculate_spread_and_zscore(
        ohlc_a, ohlc_b, hedge_ratio
    )
    
    adf_pvalue = 1.0
    if not spread_df.empty and 'spread' in spread_df.columns:
        adf_pvalue = calculate_adf(spread_df['spread'])
    
    # Calculate rolling correlation
    rolling_corr = 0.0
    if not spread_df.empty and 'close_a' in spread_df.columns and 'close_b' in spread_df.columns:
        if len(spread_df) >= 30:
            # Calculate rolling correlation over 30-period window
            rolling_corr = spread_df['close_a'].rolling(window=30).corr(spread_df['close_b']).iloc[-1]
            if pd.isna(rolling_corr):
                rolling_corr = 0.0
        elif len(spread_df) > 1:
            # If less than 30 periods, use all available data
            rolling_corr = spread_df['close_a'].corr(spread_df['close_b'])
            if pd.isna(rolling_corr):
                rolling_corr = 0.0

    return {
        'asset_a': ohlc_a,
        'asset_b': ohlc_b,
        'hedge_ratio': hedge_ratio,
        'spread_df': spread_df,
        'current_zscore': current_zscore,
        'spread_mean': spread_mean,
        'spread_std': spread_std,
        'adf_pvalue': adf_pvalue,
        'rolling_corr': rolling_corr,
        'error': None
    }
