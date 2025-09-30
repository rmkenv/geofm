
"""
Alpha Vantage API Client
Free tier: 25 requests per day, 5 requests per minute
"""

import requests
import json
import time
from datetime import datetime
import logging

class AlphaVantageClient:
    def __init__(self, api_key=None):
        # Using demo key - users can replace with their own
        self.api_key = api_key or 'demo'
        self.base_url = 'https://www.alphavantage.co/query'
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.last_request_time = 0
        
    def _make_request(self, params):
        """Make rate-limited request to Alpha Vantage API"""
        # Rate limiting: max 5 requests per minute
        current_time = time.time()
        if current_time - self.last_request_time < 12:  # 12 seconds between requests
            time.sleep(12 - (current_time - self.last_request_time))
            
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            self.last_request_time = time.time()
            self.request_count += 1
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Alpha Vantage API request failed: {str(e)}")
            return None
    
    def get_stock_data(self, symbol):
        """Get current stock data from Alpha Vantage"""
        try:
            # Skip if we've hit rate limits
            if self.request_count >= 25:  # Daily limit
                return None
                
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            data = self._make_request(params)
            
            if not data or 'Global Quote' not in data:
                return None
                
            quote = data['Global Quote']
            
            if not quote or '05. price' not in quote:
                return None
                
            stock_data = {
                'symbol': symbol,
                'name': symbol,  # Alpha Vantage doesn't provide company name in quote
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                'volume': int(quote.get('06. volume', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'open': float(quote.get('02. open', 0)),
                'previous_close': float(quote.get('08. previous close', 0)),
                'source': 'alpha_vantage',
                'timestamp': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Alpha Vantage data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, outputsize='full'):
        """Get historical data from Alpha Vantage"""
        try:
            if self.request_count >= 25:
                return None
                
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            data = self._make_request(params)
            
            if not data or 'Time Series (Daily)' not in data:
                return None
                
            time_series = data['Time Series (Daily)']
            
            historical_data = []
            for date, values in time_series.items():
                historical_data.append({
                    'date': date,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
                
            # Sort by date (newest first)
            historical_data.sort(key=lambda x: x['date'], reverse=True)
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Alpha Vantage historical data for {symbol}: {str(e)}")
            return None
