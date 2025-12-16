"""
Data transformation and processing functions for pair trading analytics.
"""
import pandas as pd
from analytics.calculations import (
    calculate_hedge_ratio,
    calculate_spread_and_zscore,
    calculate_adf
)


def resample_to_ohlc(ticks: list, interval_seconds: int = 60) -> pd.DataFrame:
    """
    Resample ticks to OHLC bars.
    
    Args:
        ticks: List of (timestamp, price, quantity) tuples
        interval_seconds: Bar interval in seconds (default 60 for 1-minute bars)
    
    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
    """
    if not ticks:
        return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    df = pd.DataFrame(ticks, columns=['timestamp', 'price', 'quantity'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    
    # Resample to OHLC bars
    ohlc = df['price'].resample(f'{interval_seconds}S').ohlc()
    volume = df['quantity'].resample(f'{interval_seconds}S').sum()
    
    result = ohlc.copy()
    result['volume'] = volume
    result.reset_index(inplace=True)
    result.dropna(inplace=True)
    
    return result


def get_pair_analytics_from_uploaded_csv(uploaded_df: pd.DataFrame) -> dict:
    """
    Calculate analytics from uploaded CSV data.
    
    Args:
        uploaded_df: DataFrame with columns that include timestamp and price columns.
                    Accepts variations like 'Timestamp', 'Date', 'Time' for timestamp,
                    and columns containing 'price' or 'close' for price data.
    
    Returns:
        Dictionary with all analytics data (same format as get_pair_analytics)
    """
    # Make a copy to avoid modifying original
    df = uploaded_df.copy()
    
    # Step 1: Normalize all column names to lowercase
    df.columns = df.columns.str.lower().str.strip()
    
    # Step 2: Rename timestamp column variants to 'timestamp'
    timestamp_variants = ['timestamp', 'date', 'time']
    timestamp_col = None
    for variant in timestamp_variants:
        if variant in df.columns:
            timestamp_col = variant
            break
    
    if timestamp_col and timestamp_col != 'timestamp':
        df.rename(columns={timestamp_col: 'timestamp'}, inplace=True)
    
    # Step 3: Identify and rename price columns
    # Find columns that contain "price" or "close" in their name
    price_cols = [col for col in df.columns if 'price' in col or 'close' in col]
    
    # Exclude columns that are already named 'close_a' or 'close_b'
    price_cols = [col for col in price_cols if col not in ['close_a', 'close_b']]
    
    if len(price_cols) >= 2:
        # Sort alphabetically
        price_cols.sort()
        # Rename first to 'close_a', second to 'close_b'
        df.rename(columns={price_cols[0]: 'close_a', price_cols[1]: 'close_b'}, inplace=True)
    elif len(price_cols) == 1:
        # Only one price column found, use it for both (fallback)
        df.rename(columns={price_cols[0]: 'close_a'}, inplace=True)
        df['close_b'] = df['close_a']
    
    # Step 4: Validate required columns now exist
    required_cols = ['timestamp', 'close_a', 'close_b']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        return {
            'asset_a': pd.DataFrame(),
            'asset_b': pd.DataFrame(),
            'hedge_ratio': 1.0,
            'spread_df': pd.DataFrame(),
            'current_zscore': 0.0,
            'spread_mean': 0.0,
            'spread_std': 1.0,
            'rolling_corr': 0.0,
            'adf_pvalue': 1.0,
            'error': f'CSV must contain timestamp column and at least 2 price columns. Missing: {", ".join(missing_cols)}'
        }
    
    # Convert timestamp to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except:
            try:
                # Try as unix timestamp
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            except:
                return {
                    'asset_a': pd.DataFrame(),
                    'asset_b': pd.DataFrame(),
                    'hedge_ratio': 1.0,
                    'spread_df': pd.DataFrame(),
                    'current_zscore': 0.0,
                    'spread_mean': 0.0,
                    'spread_std': 1.0,
                    'rolling_corr': 0.0,
                    'adf_pvalue': 1.0,
                    'error': 'Could not parse timestamp column'
                }
    
    # Drop rows with missing values
    df = df[['timestamp', 'close_a', 'close_b']].dropna()
    
    if len(df) < 2:
        return {
            'asset_a': pd.DataFrame(),
            'asset_b': pd.DataFrame(),
            'hedge_ratio': 1.0,
            'spread_df': pd.DataFrame(),
            'current_zscore': 0.0,
            'spread_mean': 0.0,
            'spread_std': 1.0,
            'rolling_corr': 0.0,
            'adf_pvalue': 1.0,
            'error': 'Insufficient data in uploaded CSV'
        }
    
    # Create asset_a and asset_b DataFrames with 'timestamp' and 'close' columns
    asset_a = df[['timestamp', 'close_a']].copy()
    asset_a.rename(columns={'close_a': 'close'}, inplace=True)
    
    asset_b = df[['timestamp', 'close_b']].copy()
    asset_b.rename(columns={'close_b': 'close'}, inplace=True)
    
    # Sort by timestamp
    asset_a = asset_a.sort_values('timestamp').reset_index(drop=True)
    asset_b = asset_b.sort_values('timestamp').reset_index(drop=True)
    
    # Calculate hedge ratio
    hedge_ratio = calculate_hedge_ratio(asset_a, asset_b)
    
    # Calculate spread and z-score
    spread_df, current_zscore, spread_mean, spread_std = calculate_spread_and_zscore(
        asset_a, asset_b, hedge_ratio
    )
    
    # Calculate ADF p-value
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
    
    # Create ohlc-like DataFrames for compatibility (using close for all OHLC)
    ohlc_a = asset_a.copy()
    ohlc_a['open'] = ohlc_a['close']
    ohlc_a['high'] = ohlc_a['close']
    ohlc_a['low'] = ohlc_a['close']
    ohlc_a['volume'] = 0.0  # Volume not available from CSV
    
    ohlc_b = asset_b.copy()
    ohlc_b['open'] = ohlc_b['close']
    ohlc_b['high'] = ohlc_b['close']
    ohlc_b['low'] = ohlc_b['close']
    ohlc_b['volume'] = 0.0  # Volume not available from CSV
    
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
