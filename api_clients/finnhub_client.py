
"""
Finnhub API Client
Free tier: 60 API calls/minute
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging

class FinnhubClient:
    def __init__(self, api_key=None):
        # Using demo key - users can replace with their own
        self.api_key = api_key or 'demo'
        self.base_url = 'https://finnhub.io/api/v1'
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.last_minute_start = time.time()
        
    def _make_request(self, endpoint, params=None):
        """Make rate-limited request to Finnhub API"""
        # Rate limiting: max 60 requests per minute
        current_time = time.time()
        if current_time - self.last_minute_start >= 60:
            self.request_count = 0
            self.last_minute_start = current_time
            
        if self.request_count >= 60:
            sleep_time = 60 - (current_time - self.last_minute_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_minute_start = time.time()
        
        try:
            if params is None:
                params = {}
            params['token'] = self.api_key
            
            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
            self.request_count += 1
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Finnhub API request failed: {str(e)}")
            return None
    
    def get_stock_data(self, symbol):
        """Get current stock data from Finnhub"""
        try:
            # Get quote data
            quote_data = self._make_request('/quote', {'symbol': symbol})
            
            if not quote_data or 'c' not in quote_data:
                return None
                
            # Get company profile for additional info
            profile_data = self._make_request('/stock/profile2', {'symbol': symbol})
            
            stock_data = {
                'symbol': symbol,
                'name': profile_data.get('name', symbol) if profile_data else symbol,
                'price': float(quote_data.get('c', 0)),  # current price
                'change': float(quote_data.get('d', 0)),  # change
                'change_percent': float(quote_data.get('dp', 0)),  # change percent
                'high': float(quote_data.get('h', 0)),  # high price of the day
                'low': float(quote_data.get('l', 0)),  # low price of the day
                'open': float(quote_data.get('o', 0)),  # open price of the day
                'previous_close': float(quote_data.get('pc', 0)),  # previous close price
                'source': 'finnhub',
                'timestamp': datetime.now().isoformat()
            }
            
            # Add company profile data if available
            if profile_data:
                stock_data.update({
                    'country': profile_data.get('country', 'Unknown'),
                    'currency': profile_data.get('currency', 'USD'),
                    'exchange': profile_data.get('exchange', 'Unknown'),
                    'industry': profile_data.get('finnhubIndustry', 'Unknown'),
                    'market_cap': profile_data.get('marketCapitalization', 0) * 1000000 if profile_data.get('marketCapitalization') else 0,
                    'website': profile_data.get('weburl', ''),
                    'logo': profile_data.get('logo', '')
                })
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Finnhub data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, days=1825):  # 5 years
        """Get historical data from Finnhub"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'symbol': symbol,
                'resolution': 'D',  # Daily resolution
                'from': int(start_date.timestamp()),
                'to': int(end_date.timestamp())
            }
            
            data = self._make_request('/stock/candle', params)
            
            if not data or data.get('s') != 'ok':
                return None
                
            historical_data = []
            timestamps = data.get('t', [])
            opens = data.get('o', [])
            highs = data.get('h', [])
            lows = data.get('l', [])
            closes = data.get('c', [])
            volumes = data.get('v', [])
            
            for i in range(len(timestamps)):
                date = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                historical_data.append({
                    'date': date,
                    'open': float(opens[i]),
                    'high': float(highs[i]),
                    'low': float(lows[i]),
                    'close': float(closes[i]),
                    'volume': int(volumes[i])
                })
                
            # Sort by date (newest first)
            historical_data.sort(key=lambda x: x['date'], reverse=True)
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Finnhub historical data for {symbol}: {str(e)}")
            return None
