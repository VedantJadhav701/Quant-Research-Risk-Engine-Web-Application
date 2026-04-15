import yfinance as yf
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataIngestor:
    """
    Handles fetching market data and initial processing.
    """
    def __init__(self):
        pass

    def fetch_ticker_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical data for a ticker and computes basic metrics.
        """
        try:
            logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
            df = yf.download(ticker, start=start_date, end=end_date)
            
            if df.empty:
                raise ValueError(f"No data found for ticker {ticker}")
            
            # Handle MultiIndex for single tickers in newer yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Ensure we have a clean DataFrame with the Close price
            df = df[['Close']].copy()
            
            # Compute log returns
            df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
            
            # Compute rolling volatility (20-day window, annualized)
            df['rolling_vol'] = df['log_return'].rolling(window=20).std() * np.sqrt(252)
            
            # Moving averages
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            
            # Drop NaNs created by rolling windows/returns
            df = df.dropna()
            
            return df
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def process_custom_data(self, file_path: str) -> pd.DataFrame:
        """
        Processes a CSV file uploaded by the user.
        Expected format: Date as index or column, 'Close' price column.
        """
        try:
            df = pd.read_csv(file_path, parse_dates=True, index_col=0)
            if 'Close' not in df.columns:
                # If only one column, assume it's Close
                if len(df.columns) == 1:
                    df.columns = ['Close']
                else:
                    raise ValueError("Uploaded data must contain a 'Close' column.")
            
            df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
            df['rolling_vol'] = df['log_return'].rolling(window=20).std() * np.sqrt(252)
            df = df.dropna()
            return df
        except Exception as e:
            logger.error(f"Error processing custom data: {str(e)}")
            raise
