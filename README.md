# Real-time Pair Trading Dashboard

A real-time pair trading dashboard that connects to Binance WebSocket API to fetch live trade data for BTCUSDT and ETHUSDT, analyzes the statistical spread between them, and visualizes it in real-time.

## Features

- **Real-time Data Ingestion**: Connects to Binance WebSocket API to fetch live trade data
- **Statistical Analysis**: Calculates hedge ratio using OLS regression, spread, and z-score
- **Interactive Dashboard**: Beautiful Streamlit interface with real-time charts
- **Entry/Exit Signals**: Visual alerts when z-score exceeds user-defined thresholds
- **Data Export**: Download processed data as CSV

git clone [https://github.com/Yash-Coder-07/Quant_Developer_Assignment-.git](https://github.com/Yash-Coder-07/Quant_Developer_Assignment-.git)

cd Quant_Developer_Assignment-

# Create virtual environment (Recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

## Usage

### Start the Dashboard

Run the main script to start both the WebSocket ingestion and Streamlit dashboard:

```bash
python run.py
```

This will:
- Start a background thread that connects to Binance WebSocket and stores trade data in SQLite
- Launch the Streamlit dashboard in your default web browser

The dashboard will be available at `http://localhost:8501`

### Dashboard Controls

- **Window Size**: Adjust the time window (in minutes) for analysis (5-240 minutes)
- **Z-Score Threshold**: Set the threshold for entry/exit signals (0.5-5.0)
- **Auto Refresh**: Enable/disable automatic data refresh
- **Refresh Interval**: Set how often the dashboard refreshes (1-10 seconds)

### Charts

1. **Normalized Price Overlay**: Shows normalized prices of both assets with the hedge ratio applied
2. **Z-Score Chart**: Displays the z-score over time with threshold lines for entry/exit signals

### Signals

- **SELL Signal**: Triggered when z-score exceeds the upper threshold (positive)
- **BUY Signal**: Triggered when z-score exceeds the lower threshold (negative)

## Project Structure

```
Quant-Dashboard/
├── requirements.txt          # Python dependencies
├── database.py               # SQLite database module
├── websocket_ingestion.py    # Binance WebSocket ingestion
├── analytics.py              # Analytics engine (OLS, spread, z-score)
├── dashboard.py              # Streamlit dashboard
├── run.py                    # Main entry point
├── README.md                 # This file
└── trades.db                 # SQLite database (created automatically)
```

## Technical Details

### Database Schema

The SQLite database stores trade ticks with the following schema:
- `id`: Primary key
- `timestamp`: Unix timestamp (seconds)
- `symbol`: Trading pair symbol (e.g., BTCUSDT)
- `price`: Trade price
- `quantity`: Trade quantity

### Analytics

1. **Hedge Ratio**: Calculated using OLS regression on normalized prices
2. **Spread**: `spread = price_a_norm - hedge_ratio * price_b_norm`
3. **Z-Score**: `zscore = (spread - mean) / std`

### Data Flow

1. WebSocket ingestion continuously receives trade events from Binance
2. Trades are stored in SQLite database
3. Analytics engine reads recent data and calculates metrics
4. Streamlit dashboard displays real-time visualizations

## Requirements

- Python 3.8+
- Internet connection (for Binance WebSocket)
- All dependencies listed in `requirements.txt`

## Notes

- The WebSocket ingestion runs in a background thread and doesn't block the Streamlit interface
- Data is automatically cleaned up (keeps last 24 hours by default)
- The dashboard requires at least 2 minutes of data to calculate meaningful statistics

## Troubleshooting

**No data showing:**
- Wait a few minutes for WebSocket data to accumulate
- Check your internet connection
- Verify Binance WebSocket is accessible

**Charts not updating:**
- Enable "Auto Refresh" in the sidebar
- Adjust the refresh interval
- Check that the WebSocket ingestion is running

## License

This project is for educational purposes.



