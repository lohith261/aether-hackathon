import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pprint import pprint
from cerebras.cloud.sdk import Cerebras # <-- Import the new SDK

# --- Configuration ---
load_dotenv()
#ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
# The SDK automatically finds the CEREBRAS_API_KEY from the .env file
STOCK_SYMBOL = "NVDA"

# --- Data Fetching (Unchanged) ---
#def fetch_stock_data(symbol: str):
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

def fetch_market_data(ticker: str):
    """
    Fetches the latest time series data for any ticker (stocks, crypto, forex) from Polygon.io.
    Example tickers: "AAPL" for Apple, "X:BTC-USD" for Bitcoin, "C:EUR-USD" for Euro/USD.
    """
    # Polygon's API requires a date range. We'll get the last 2 days of 5-minute intervals.
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/5/minute/{yesterday}/{today}?adjusted=true&sort=desc&limit=100&apiKey={POLYGON_API_KEY}"

    print(f"Fetching live market data for {ticker} from Polygon.io...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("resultsCount") == 0 or "results" not in data:
            print(f"No data found for ticker {ticker}.")
            return None

        # Convert Polygon's results into the same format our anomaly detector expects
        time_series = {}
        for result in data["results"]:
            # Timestamp is in milliseconds, convert to a standard string format
            ts = datetime.fromtimestamp(result['t'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            time_series[ts] = {
                "1. open": str(result['o']),
                "2. high": str(result['h']),
                "3. low": str(result['l']),
                "4. close": str(result['c']),
                "5. volume": str(result['v'])
            }
        return time_series

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the Polygon.io API request: {e}")
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

