"""
Pure mathematical calculations for pair trading analytics.
"""
import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS
from statsmodels.tsa.stattools import adfuller
from typing import Tuple


def calculate_hedge_ratio(asset_a: pd.DataFrame, asset_b: pd.DataFrame) -> float:
    """
    Calculate hedge ratio using OLS regression.
    
    Args:
        asset_a: DataFrame with 'close' column (first asset)
        asset_b: DataFrame with 'close' column (second asset)
    
    Returns:
        Hedge ratio (slope of regression)
    """
    # Align the dataframes by timestamp
    merged = pd.merge(
        asset_a[['timestamp', 'close']],
        asset_b[['timestamp', 'close']],
        on='timestamp',
        suffixes=('_a', '_b')
    )
    
    if len(merged) < 2:
        return 1.0  # Default hedge ratio
    
    # Normalize prices (use first price as base)
    merged['price_a_norm'] = merged['close_a'] / merged['close_a'].iloc[0]
    merged['price_b_norm'] = merged['close_b'] / merged['close_b'].iloc[0]
    
    # OLS regression: price_a = alpha + beta * price_b
    X = merged['price_b_norm'].values.reshape(-1, 1)
    y = merged['price_a_norm'].values
    
    try:
        model = OLS(y, X).fit()
        hedge_ratio = model.params[0]
    except:
        hedge_ratio = 1.0
    
    return hedge_ratio


def calculate_spread_and_zscore(
    asset_a: pd.DataFrame,
    asset_b: pd.DataFrame,
    hedge_ratio: float
) -> Tuple[pd.DataFrame, float, float, float]:
    """
    Calculate spread and z-score.
    
    Args:
        asset_a: DataFrame with 'close' column
        asset_b: DataFrame with 'close' column
        hedge_ratio: Hedge ratio from OLS regression
    
    Returns:
        Tuple of (merged_df with spread, current_zscore, mean_spread, std_spread)
    """
    # Align dataframes
    merged = pd.merge(
        asset_a[['timestamp', 'close']],
        asset_b[['timestamp', 'close']],
        on='timestamp',
        suffixes=('_a', '_b')
    )
    
    if len(merged) < 2:
        return merged, 0.0, 0.0, 1.0
    
    # Normalize prices
    merged['price_a_norm'] = merged['close_a'] / merged['close_a'].iloc[0]
    merged['price_b_norm'] = merged['close_b'] / merged['close_b'].iloc[0]
    
    # Calculate spread: spread = price_a_norm - hedge_ratio * price_b_norm
    merged['spread'] = merged['price_a_norm'] - hedge_ratio * merged['price_b_norm']
    
    # Calculate z-score
    spread_mean = merged['spread'].mean()
    spread_std = merged['spread'].std()
    
    if spread_std == 0 or pd.isna(spread_std):
        spread_std = 1.0
    
    merged['zscore'] = (merged['spread'] - spread_mean) / spread_std
    
    current_zscore = merged['zscore'].iloc[-1] if len(merged) > 0 else 0.0
    
    return merged, current_zscore, spread_mean, spread_std


def calculate_adf(spread_series: pd.Series) -> float:
    """
    Checks if the spread is stationary using Augmented Dickey-Fuller test.
    Returns the p-value. (p < 0.05 implies stationarity).
    """
    # Drop NaNs and ensure we have enough data (ADF needs ~10-15 points minimum)
    clean_series = spread_series.dropna()
    
    if len(clean_series) < 20:
        return 1.0  # Not enough data, assume non-stationary
        
    try:
        # result[1] is the p-value
        result = adfuller(clean_series)
        return float(result[1])
    except:
        return 1.0
