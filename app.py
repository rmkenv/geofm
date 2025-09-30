
"""
Enhanced Geospatial Portfolio Dashboard
Comprehensive stock tracking with multiple APIs, 5-year history, and PDF export
"""

import os
import json
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_file
import plotly.graph_objs as go
import plotly.utils
from api_clients.yahoo_client import YahooFinanceClient
from api_clients.alpha_vantage_client import AlphaVantageClient
from api_clients.finnhub_client import FinnhubClient
from utils.data_processor import DataProcessor
from utils.pdf_exporter import PDFExporter
from utils.database_manager import DatabaseManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geospatial-portfolio-dashboard-2024'

# Initialize components
db_manager = DatabaseManager()
data_processor = DataProcessor()
pdf_exporter = PDFExporter()

# API clients
yahoo_client = YahooFinanceClient()
alpha_vantage_client = AlphaVantageClient()
finnhub_client = FinnhubClient()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stocks')
def get_stocks():
    """Get all stocks with current data"""
    try:
        stocks_data = data_processor.get_enhanced_stocks_data()
        return jsonify({
            'success': True,
            'data': stocks_data,
            'total_stocks': len(stocks_data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock/<symbol>')
def get_stock_detail(symbol):
    """Get detailed data for a specific stock"""
    try:
        # Try multiple APIs for better coverage
        stock_data = None
        
        # Try Yahoo Finance first
        stock_data = yahoo_client.get_stock_data(symbol)
        if not stock_data:
            # Try Alpha Vantage
            stock_data = alpha_vantage_client.get_stock_data(symbol)
        if not stock_data:
            # Try Finnhub
            stock_data = finnhub_client.get_stock_data(symbol)
            
        if stock_data:
            # Get 5-year historical data
            historical_data = data_processor.get_historical_data(symbol, years=5)
            stock_data['historical'] = historical_data
            
            # Store in database
            db_manager.store_stock_data(symbol, stock_data)
            
            return jsonify({
                'success': True,
                'data': stock_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'success': False, 'error': 'Stock data not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolio/performance')
def get_portfolio_performance():
    """Get overall portfolio performance metrics"""
    try:
        performance_data = data_processor.calculate_portfolio_performance()
        return jsonify({
            'success': True,
            'data': performance_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sectors')
def get_sector_analysis():
    """Get sector-wise analysis"""
    try:
        sector_data = data_processor.get_sector_analysis()
        return jsonify({
            'success': True,
            'data': sector_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/pdf')
def export_pdf():
    """Export portfolio report as PDF"""
    try:
        # Get all necessary data
        stocks_data = data_processor.get_enhanced_stocks_data()
        performance_data = data_processor.calculate_portfolio_performance()
        sector_data = data_processor.get_sector_analysis()
        
        # Generate PDF
        pdf_path = pdf_exporter.generate_portfolio_report(
            stocks_data, performance_data, sector_data
        )
        
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f'portfolio_report_{datetime.now().strftime("%Y%m%d")}.pdf')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update/all')
def update_all_stocks():
    """Update all stock data - background process"""
    try:
        result = data_processor.update_all_stocks_data()
        return jsonify({
            'success': True,
            'message': 'Stock data update initiated',
            'updated_count': result.get('updated_count', 0),
            'failed_count': result.get('failed_count', 0)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trades')
def get_trades_data():
    """Get trading history data"""
    try:
        trades_data = data_processor.get_trades_analysis()
        return jsonify({
            'success': True,
            'data': trades_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    db_manager.initialize_database()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
