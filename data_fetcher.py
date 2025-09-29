import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pprint import pprint
from cerebras.cloud.sdk import Cerebras # <-- Import the new SDK

# --- Configuration ---
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
# The SDK automatically finds the CEREBRAS_API_KEY from the .env file
STOCK_SYMBOL = "NVDA"

# --- Data Fetching (Unchanged) ---
def fetch_stock_data(symbol: str):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}'
    print(f"Fetching live market data for {symbol}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        time_series = data.get("Time Series (5min)")
        if not time_series:
            print("Error: Could not find time series data.")
            pprint(data)
            return None
        return time_series
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the Alpha Vantage API request: {e}")
        return None

# --- Local Anomaly Detection (Unchanged) ---
def detect_anomaly_local(time_series: dict):
    if not time_series: return None
    df = pd.DataFrame.from_dict(time_series, orient='index', dtype=float)
    df.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume': 'volume'}, inplace=True)
    df = df.iloc[::-1]
    
    window, std_dev_factor = 20, 2.5
    df['moving_average'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['moving_average'] + (df['std_dev'] * std_dev_factor)
    df['lower_band'] = df['moving_average'] - (df['std_dev'] * std_dev_factor)
    
    latest = df.iloc[-1]
    
    if latest['close'] > latest['upper_band']:
        return {"type": "Price Spike", "message": f"Price crossed the UPPER Bollinger Band. (${latest['close']:.2f} > ${latest['upper_band']:.2f})"}
    elif latest['close'] < latest['lower_band']:
        return {"type": "Price Drop", "message": f"Price crossed the LOWER Bollinger Band. (${latest['close']:.2f} < ${latest['lower_band']:.2f})"}
    
    return None

# --- REWRITTEN: Real Cerebras API Call using the SDK ---
def get_cerebras_analysis(anomaly_details: dict):
    """
    Calls the Cerebras Inference API using the official SDK to get a strategic analysis.
    """
    try:
        print("\n[Cerebras SDK]: Initializing client...")
        client = Cerebras() # The SDK automatically finds the API key from your environment
        
        # 1. Craft the messages payload
        system_prompt = (
            "You are 'Aether', an expert AI financial strategist. You will receive a financial anomaly report. "
            "Your mission is to provide a concise, professional analysis in three parts: "
            "1. **Event:** Briefly describe the event. "
            "2. **Potential Causes:** Suggest two plausible, hypothetical causes. "
            "3. **Strategic Action:** Suggest one potential next step for a trader."
        )
        user_prompt = f"Anomaly Report:\nSymbol: {anomaly_details['symbol']}\nType: {anomaly_details['type']}\nDetails: {anomaly_details['message']}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        print("[Cerebras SDK]: Sending anomaly data to Cerebras Cloud for strategic analysis...")
        
        # 2. Make the API call
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-4-scout-17b-16e-instruct", # Use a model name from the SDK docs
        )

        # 3. Extract the response
        analysis = chat_completion.choices[0].message.content
        print("[Cerebras SDK]: Analysis received.")
        return analysis.strip()

    except Exception as e:
        print(f"An error occurred during the Cerebras SDK call: {e}")
        return f"[Error] Failed to get analysis from Cerebras. Details: {e}"

# --- Main execution block (Unchanged) ---
if __name__ == "__main__":
    time_series_data = fetch_stock_data(STOCK_SYMBOL)
    
    if time_series_data:
        raw_anomaly = detect_anomaly_local(time_series_data)
        
        print("\n--- Aether Engine Result ---")
        if raw_anomaly:
            print("!! RAW ANOMALY DETECTED !!")
            raw_anomaly['symbol'] = STOCK_SYMBOL
            raw_anomaly['timestamp'] = list(time_series_data.keys())[0]
            pprint(raw_anomaly)
            
            strategic_analysis = get_cerebras_analysis(raw_anomaly)
            
            print("\n--- Cerebras Strategic Analysis ---")
            print(strategic_analysis)
            print("-----------------------------------\n")
            
        else:
            print("No significant anomaly detected by the local engine.")
        print("--------------------------\n")