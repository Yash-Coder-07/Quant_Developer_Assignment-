"""
Main script to launch WebSocket ingestion and Streamlit dashboard.
"""
import threading
import time
import subprocess
import sys
from database import Database
from websocket_ingestion import BinanceWebSocketIngestion


def start_ingestion():
    """Start the WebSocket ingestion in a background thread."""
    print("Initializing database...")
    db = Database()
    
    print("Starting Binance WebSocket ingestion...")
    ingestion = BinanceWebSocketIngestion(
        db=db,
        symbols=["BTCUSDT", "ETHUSDT"]
    )
    
    ingestion_thread = ingestion.start_background()
    print("WebSocket ingestion started in background thread.")
    
    return ingestion_thread


def start_streamlit():
    """Start the Streamlit dashboard."""
    print("Starting Streamlit dashboard...")
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard.py",
        "--server.headless",
        "true"
    ])


def main():
    """Main entry point."""
    print("=" * 60)
    print("Pair Trading Dashboard - Starting Services")
    print("=" * 60)
    
    # Start WebSocket ingestion
    ingestion_thread = start_ingestion()
    
    # Give ingestion a moment to connect
    print("Waiting 3 seconds for WebSocket connections to establish...")
    time.sleep(3)
    
    # Start Streamlit (this will block)
    try:
        start_streamlit()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()

