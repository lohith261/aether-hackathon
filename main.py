from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the functions from your other file
from data_fetcher import fetch_stock_data, detect_anomaly_local, get_cerebras_analysis, STOCK_SYMBOL

# Create the FastAPI app
app = FastAPI()

# --- CORS Middleware ---
# This allows our future frontend (running on a different address) to talk to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Define the API Endpoint ---
@app.get("/analyze")
async def analyze_market():
    try:
    	"""
    	This endpoint triggers the full Aether analysis workflow.
    	"""
    	time_series_data = fetch_stock_data(STOCK_SYMBOL)
    
    	if not time_series_data:
    	    return {"error": "Could not fetch market data."}
    
    	raw_anomaly = detect_anomaly_local(time_series_data)
    
    	if not raw_anomaly:
    	    return {"status": "No significant anomaly detected by the local engine."}
    
    	# Add extra info to the anomaly details
    	raw_anomaly['symbol'] = STOCK_SYMBOL
    	raw_anomaly['timestamp'] = list(time_series_data.keys())[0]

    	# Get the final analysis from Cerebras
    	strategic_analysis = get_cerebras_analysis(raw_anomaly)
    
    	return {
     	   "status": "Anomaly Detected",
    	    "raw_anomaly_details": raw_anomaly,
    	    "strategic_analysis": strategic_analysis
    	}
    except Exception as e:
    	print(f"An unexpected error occurred: {e}")
    	# Return a structured error message to the frontend
    	return {"error": "An internal server error occurred. Please check the logs."}

# --- Optional: Run the app directly for testing ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)