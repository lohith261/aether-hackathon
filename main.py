from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Use the upgraded Polygon data fetcher
from data_fetcher import fetch_market_data, detect_anomaly_local, get_cerebras_analysis

# Define the asset to analyze
MARKET_SYMBOL = "X:BTC-USD" # Example: Bitcoin. Can be "AAPL", "C:EUR-USD", etc.

# Create the FastAPI app
app = FastAPI()

# Add CORS Middleware to allow the frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """A simple endpoint to confirm the server is running."""
    return {"status": "Aether Engine is online and ready."}

@app.get("/analyze")
async def analyze_market():
    """
    This endpoint triggers the full Aether analysis workflow.
    """
    # 1. Fetch live data using the Polygon function
    time_series_data = fetch_market_data(MARKET_SYMBOL)
    
    if not time_series_data:
        return {"error": "Could not fetch market data from the API."}
    
    # 2. Run the local anomaly detector
    raw_anomaly = detect_anomaly_local(time_series_data)
    
    if not raw_anomaly:
    # Get the latest data point from the time series
    latest_timestamp = list(time_series_data.keys())[0]
    latest_data = time_series_data[latest_timestamp]

    return {
        "status": "No significant anomaly detected.",
        "latest_data": {
            "symbol": MARKET_SYMBOL,
            "timestamp": latest_timestamp,
            "close_price": latest_data.get("4. close")
        }
    }
    
    # 3. If an anomaly is found, get the AI analysis
    raw_anomaly['symbol'] = MARKET_SYMBOL
    raw_anomaly['timestamp'] = list(time_series_data.keys())[0]
    strategic_analysis = get_cerebras_analysis(raw_anomaly)
    
    return {
        "status": "Anomaly Detected",
        "raw_anomaly_details": raw_anomaly,
        "strategic_analysis": strategic_analysis
    }