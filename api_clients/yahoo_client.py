
"""
Yahoo Finance API Client
Free API for stock data with good coverage
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

class YahooFinanceClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_stock_data(self, symbol):
        """Get current stock data from Yahoo Finance"""
        try:
            # Clean symbol format
            symbol = symbol.replace(':', '.')
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                return None
                
            # Get current price and basic info
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': info.get('regularMarketPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('regularMarketVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'country': info.get('country', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown'),
                'source': 'yahoo_finance',
                'timestamp': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, period='5y'):
        """Get historical data for a stock"""
        try:
            symbol = symbol.replace(':', '.')
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
                
            # Convert to list of dictionaries
            historical_data = []
            for date, row in hist.iterrows():
                historical_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
                
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks(self, symbols, max_batch_size=50):
        """Get data for multiple stocks efficiently"""
        results = {}
        
        # Process in batches to avoid rate limits
        for i in range(0, len(symbols), max_batch_size):
            batch = symbols[i:i + max_batch_size]
            
            for symbol in batch:
                stock_data = self.get_stock_data(symbol)
                if stock_data:
                    results[symbol] = stock_data
                    
                # Small delay to respect rate limits
                time.sleep(0.1)
                
        return results
