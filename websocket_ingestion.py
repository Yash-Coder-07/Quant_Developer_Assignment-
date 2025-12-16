"""
WebSocket ingestion module for Binance trade data.
Runs as a background task to continuously fetch and store trade ticks.
"""
import asyncio
import json
import time
from datetime import datetime
from database import Database


class BinanceWebSocketIngestion:
    """Handles WebSocket connections to Binance and stores trade data."""
    
    def __init__(self, db: Database, symbols: list = None):
        self.db = db
        self.symbols = symbols or ["btcusdt", "ethusdt"]
        self.running = False
        self.ws_url = "wss://stream.binance.com:9443/ws/"

        self.tick_buffer = []  
        self.last_write_time = time.time()
    
    async def fetch_trades(self, symbol: str):
        """Fetch trade stream for a single symbol."""
        import aiohttp
        
        stream_name = f"{symbol}@trade"
        url = f"{self.ws_url}{stream_name}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url) as ws:
                    print(f"Connected to Binance stream for {symbol.upper()}")
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = json.loads(msg.data)
                                if data.get('e') == 'trade':
                                    # Extract trade data
                                    price = float(data['p'])
                                    quantity = float(data['q'])
                                    timestamp = float(data['T']) / 1000.0  # Convert ms to seconds
                                    
                                    self.tick_buffer.append((timestamp, symbol.upper(), price, quantity))
                                    
                                    # <--- CHANGED: Check time. If 1 second passed, write everything.
                                    current_time = time.time()
                                    if current_time - self.last_write_time >= 1.0:
                                        if self.tick_buffer:
                                            # Use the new batch function we wrote in Part 1
                                            self.db.insert_ticks_batch(self.tick_buffer)
                                            # Clear the buffer
                                            self.tick_buffer = []
                                            self.last_write_time = current_time
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                print(f"Error processing message for {symbol}: {e}")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print(f"WebSocket error for {symbol}: {ws.exception()}")
                            break
        except Exception as e:
            print(f"Connection error for {symbol}: {e}")
            await asyncio.sleep(5)  # Wait before retrying
            # Retry connection
            if self.running:
                await self.fetch_trades(symbol)
    
    async def run(self):
        """Run WebSocket ingestion for all symbols."""
        self.running = True
        print("Starting Binance WebSocket ingestion...")
        
        # Create tasks for each symbol
        tasks = [self.fetch_trades(symbol.lower()) for symbol in self.symbols]
        
        # Run all tasks concurrently
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("Stopping WebSocket ingestion...")
            self.running = False
    
    def start_background(self):
        """Start the ingestion in a background thread."""
        import threading
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run())
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        return thread


if __name__ == "__main__":
    # Test the ingestion
    db = Database()
    ingestion = BinanceWebSocketIngestion(db)
    ingestion.start_background()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

