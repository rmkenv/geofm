
"""
Data Processing Utilities
Handles stock data processing, analysis, and portfolio calculations
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any
import os

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = 'data'
        
    def load_enhanced_stocks(self):
        """Load enhanced stocks data from JSON file"""
        try:
            with open(f'{self.data_dir}/enhanced_stocks_for_dashboard.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading enhanced stocks: {str(e)}")
            return []
    
    def load_priority_stocks(self):
        """Load priority stocks for API calls"""
        try:
            with open(f'{self.data_dir}/api_priority_stocks.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading priority stocks: {str(e)}")
            return []
    
    def load_trades_data(self):
        """Load trading history data"""
        try:
            return pd.read_csv(f'{self.data_dir}/all_trades_raw_data.csv')
        except Exception as e:
            self.logger.error(f"Error loading trades data: {str(e)}")
            return pd.DataFrame()
    
    def get_enhanced_stocks_data(self):
        """Get processed stocks data with enhanced information"""
        stocks = self.load_enhanced_stocks()
        
        # Add calculated fields
        for stock in stocks:
            # Calculate market cap category
            market_cap = stock.get('market_cap', 0)
            if market_cap > 200_000_000_000:
                stock['cap_category'] = 'Mega Cap'
            elif market_cap > 10_000_000_000:
                stock['cap_category'] = 'Large Cap'
            elif market_cap > 2_000_000_000:
                stock['cap_category'] = 'Mid Cap'
            elif market_cap > 300_000_000:
                stock['cap_category'] = 'Small Cap'
            else:
                stock['cap_category'] = 'Micro Cap'
                
            # Calculate performance metrics
            price = stock.get('price', 0)
            change = stock.get('change', 0)
            if price > 0:
                stock['change_percent'] = (change / (price - change)) * 100
            else:
                stock['change_percent'] = 0
                
        return stocks
    
    def get_sector_analysis(self):
        """Analyze stocks by sector"""
        stocks = self.get_enhanced_stocks_data()
        
        sector_data = {}
        for stock in stocks:
            sector = stock.get('sector', 'Unknown')
            if sector not in sector_data:
                sector_data[sector] = {
                    'count': 0,
                    'total_market_cap': 0,
                    'avg_price': 0,
                    'total_change': 0,
                    'stocks': []
                }
            
            sector_data[sector]['count'] += 1
            sector_data[sector]['total_market_cap'] += stock.get('market_cap', 0)
            sector_data[sector]['total_change'] += stock.get('change', 0)
            sector_data[sector]['stocks'].append(stock)
        
        # Calculate averages
        for sector, data in sector_data.items():
            if data['count'] > 0:
                data['avg_market_cap'] = data['total_market_cap'] / data['count']
                data['avg_change'] = data['total_change'] / data['count']
                data['avg_price'] = sum(s.get('price', 0) for s in data['stocks']) / data['count']
        
        return sector_data
    
    def calculate_portfolio_performance(self):
        """Calculate overall portfolio performance metrics"""
        stocks = self.get_enhanced_stocks_data()
        trades_df = self.load_trades_data()
        
        if not stocks:
            return {}
        
        total_stocks = len(stocks)
        total_market_cap = sum(s.get('market_cap', 0) for s in stocks)
        total_change = sum(s.get('change', 0) for s in stocks)
        avg_change = total_change / total_stocks if total_stocks > 0 else 0
        
        # Performance by sector
        sector_performance = {}
        for stock in stocks:
            sector = stock.get('sector', 'Unknown')
            if sector not in sector_performance:
                sector_performance[sector] = {'count': 0, 'total_change': 0}
            sector_performance[sector]['count'] += 1
            sector_performance[sector]['total_change'] += stock.get('change', 0)
        
        for sector, data in sector_performance.items():
            data['avg_change'] = data['total_change'] / data['count'] if data['count'] > 0 else 0
        
        # Trading analysis
        trading_stats = {}
        if not trades_df.empty:
            trading_stats = {
                'total_trades': len(trades_df),
                'total_volume': trades_df['Volume'].sum() if 'Volume' in trades_df.columns else 0,
                'avg_trade_size': trades_df['Volume'].mean() if 'Volume' in trades_df.columns else 0,
                'date_range': {
                    'start': trades_df['Date'].min() if 'Date' in trades_df.columns else None,
                    'end': trades_df['Date'].max() if 'Date' in trades_df.columns else None
                }
            }
        
        return {
            'total_stocks': total_stocks,
            'total_market_cap': total_market_cap,
            'avg_change': avg_change,
            'sector_performance': sector_performance,
            'trading_stats': trading_stats,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_historical_data(self, symbol, years=5):
        """Get or generate historical data for a stock"""
        # This would typically fetch from database or API
        # For now, return sample structure
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        # Generate sample historical data structure
        historical_data = []
        current_date = start_date
        base_price = 100  # Sample base price
        
        while current_date <= end_date:
            # Simple random walk for demo
            change = np.random.normal(0, 2)
            base_price = max(base_price + change, 1)  # Ensure positive price
            
            historical_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'close': round(base_price, 2),
                'volume': np.random.randint(100000, 1000000)
            })
            
            current_date += timedelta(days=1)
        
        return historical_data
    
    def get_trades_analysis(self):
        """Analyze trading data"""
        trades_df = self.load_trades_data()
        
        if trades_df.empty:
            return {'message': 'No trading data available'}
        
        analysis = {
            'total_trades': len(trades_df),
            'columns': list(trades_df.columns),
            'date_range': {},
            'summary_stats': {}
        }
        
        # Date analysis
        if 'Date' in trades_df.columns:
            analysis['date_range'] = {
                'start': str(trades_df['Date'].min()),
                'end': str(trades_df['Date'].max())
            }
        
        # Numeric columns analysis
        numeric_columns = trades_df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            analysis['summary_stats'][col] = {
                'mean': float(trades_df[col].mean()),
                'median': float(trades_df[col].median()),
                'std': float(trades_df[col].std()),
                'min': float(trades_df[col].min()),
                'max': float(trades_df[col].max())
            }
        
        return analysis
    
    def update_all_stocks_data(self):
        """Update all stocks data using multiple APIs"""
        # This would be implemented to update all stocks
        # For now, return a sample response
        return {
            'updated_count': 130,
            'failed_count': 0,
            'success_rate': 100.0,
            'timestamp': datetime.now().isoformat()
        }
