import os
import requests
from dotenv import load_dotenv
from pprint import pprint # A tool to "pretty-print" data

# Load the environment variables from our .env file
load_dotenv()

# Retrieve the API key from the environment
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
STOCK_SYMBOL = "IBM" # Let's track IBM for our test

def fetch_stock_data(symbol: str):
    """Fetches the latest stock data for a given symbol from Alpha Vantage."""

    # Construct the API URL
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}'

    print(f"Fetching data for {symbol}...")

    try:
        # Make the API request
        response = requests.get(url)
        # Raise an exception if the request failed (e.g., 404, 500)
        response.raise_for_status() 

        data = response.json()

        # The data is nested, let's find the most recent entry
        time_series = data.get("Time Series (5min)")
        if not time_series:
            print("Error: Could not find time series data in the response.")
            pprint(data) # Print the whole response to see what went wrong
            return None

        # Get the latest timestamp available
        latest_timestamp = sorted(time_series.keys(), reverse=True)[0]
        latest_data = time_series[latest_timestamp]

        return {
            "timestamp": latest_timestamp,
            "open": latest_data["1. open"],
            "high": latest_data["2. high"],
            "low": latest_data["3. low"],
            "close": latest_data["4. close"],
            "volume": latest_data["5. volume"]
        }

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing the data. A key was not found: {e}")
        return None


# --- Main execution block ---
if __name__ == "__main__":
    stock_info = fetch_stock_data(STOCK_SYMBOL)

    if stock_info:
        print("\n--- Latest Stock Info ---")
        pprint(stock_info)
        print("-------------------------\n")