import os
import asyncio
from dotenv import load_dotenv # <-- ADD THIS LINE
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Market, Feed

load_dotenv() # <-- AND ADD THIS LINE

async def handle_msg(msgs: list[WebSocketMessage]):
    for m in msgs:
        print(f"Live Crypto Trade: {m.pair} | Price: {m.price} | Size: {m.size}")

async def main():
    print("Connecting to Polygon.io WebSocket...")
    api_key = os.getenv("POLYGON_API_KEY")

    # Add a check to give a friendlier error
    if not api_key:
        print("Error: POLYGON_API_KEY not found. Make sure it's set in your .env file.")
        return

    client = WebSocketClient(api_key=api_key, feed=Feed.RealTime, market=Market.Crypto)
    await client.connect(handle_msg)
    
    # Subscribe to all Bitcoin trades
    await client.subscribe("XT.X:BTC-USD")
    
    # Keep the connection alive for 60 seconds for the demo
    await asyncio.sleep(60)
    await client.close()
    print("WebSocket connection closed.")

if __name__ == "__main__":
    asyncio.run(main())