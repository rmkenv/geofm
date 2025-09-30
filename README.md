
# Enhanced Geospatial Portfolio Dashboard

A comprehensive stock portfolio tracking dashboard with multi-API integration, 5-year historical data, PDF export functionality, and database integration.

## Features

### 🚀 Enhanced Capabilities
- **Multi-API Integration**: Yahoo Finance, Alpha Vantage, and Finnhub APIs for maximum data coverage
- **Comprehensive Stock Coverage**: Process all 130+ active stocks with 90%+ success rate
- **5-Year Historical Data**: Complete historical tracking with database storage
- **PDF Export**: Generate detailed portfolio and individual stock reports
- **Real-time Dashboard**: Interactive web interface with live data updates
- **Database Integration**: SQLite database for persistent data storage
- **Performance Tracking**: Comprehensive analytics and sector analysis

### 📊 Dashboard Components
- **Portfolio Overview**: Total stocks, success rate, market cap, and performance metrics
- **Sector Analysis**: Distribution charts and performance by sector
- **Stock Table**: Searchable and filterable stock listings
- **Individual Stock Details**: Detailed view with 5-year charts
- **Trading History**: Analysis of historical trading data

### 🔧 Technical Features
- **Multiple Data Sources**: Fallback API system for maximum reliability
- **Rate Limiting**: Intelligent API usage management
- **Data Persistence**: SQLite database for historical data storage
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Export Functionality**: PDF reports with charts and tables

## Installation & Setup

### Prerequisites
- Python 3.8+
- Git

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rmkenv/geofm.git
   cd geofm
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:
   ```bash
   python -c "from utils.database_manager import DatabaseManager; DatabaseManager().initialize_database()"
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:5000`

## Configuration

### API Keys (Optional but Recommended)

For better performance and higher rate limits, configure your own API keys:

1. **Alpha Vantage**: Get free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. **Finnhub**: Get free API key from [Finnhub](https://finnhub.io/register)

Update the API clients in `api_clients/` directory with your keys:

```python
# In alpha_vantage_client.py
self.api_key = 'YOUR_ALPHA_VANTAGE_KEY'

# In finnhub_client.py  
self.api_key = 'YOUR_FINNHUB_KEY'
```

### Environment Variables

Create a `.env` file in the root directory:

```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key
FLASK_ENV=development
```

## Usage

### Dashboard Navigation

1. **Main Dashboard**: Overview of all stocks with key metrics
2. **Search & Filter**: Use the search bar and sector filter to find specific stocks
3. **Stock Details**: Click "View" on any stock for detailed information
4. **Export Reports**: Use the "Export PDF" button for comprehensive reports
5. **Data Refresh**: Click "Refresh" to update all stock data

### API Endpoints

- `GET /api/stocks` - Get all stocks data
- `GET /api/stock/<symbol>` - Get detailed stock information
- `GET /api/portfolio/performance` - Get portfolio performance metrics
- `GET /api/sectors` - Get sector analysis
- `GET /api/export/pdf` - Export portfolio PDF report
- `GET /api/trades` - Get trading history analysis

### Data Files

The dashboard uses several data files in the `data/` directory:

- `enhanced_stocks_for_dashboard.json` - 130 active stocks with enhanced data
- `api_priority_stocks.json` - Priority-ordered stocks for API calls
- `all_trades_raw_data.csv` - Historical trading data
- `portfolio.db` - SQLite database for persistent storage

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### Environment Setup for Production
```bash
export FLASK_ENV=production
export ALPHA_VANTAGE_API_KEY=your_key
export FINNHUB_API_KEY=your_key
```

### Cloud Deployment Options

#### Heroku
1. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### AWS/GCP/Azure
- Use the Docker container approach
- Set up environment variables in your cloud platform
- Configure database persistence if needed

## Architecture

### Project Structure
```
geofm/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/                 # Data files
│   ├── enhanced_stocks_for_dashboard.json
│   ├── api_priority_stocks.json
│   ├── all_trades_raw_data.csv
│   └── portfolio.db      # SQLite database
├── api_clients/          # API integration modules
│   ├── yahoo_client.py
│   ├── alpha_vantage_client.py
│   └── finnhub_client.py
├── utils/                # Utility modules
│   ├── data_processor.py
│   ├── pdf_exporter.py
│   └── database_manager.py
├── templates/            # HTML templates
│   └── dashboard.html
├── static/               # Static assets
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       └── dashboard.js
└── reports/              # Generated PDF reports
```

### Data Flow
1. **Data Sources**: Multiple APIs (Yahoo Finance, Alpha Vantage, Finnhub)
2. **Data Processing**: Python utilities for cleaning and analysis
3. **Storage**: SQLite database for persistence
4. **API Layer**: Flask REST endpoints
5. **Frontend**: Bootstrap + JavaScript dashboard
6. **Export**: PDF generation with ReportLab

## Performance & Monitoring

### Success Rate Tracking
- Target: 90%+ success rate for stock data retrieval
- Fallback system across multiple APIs
- Error logging and monitoring

### Rate Limiting
- Yahoo Finance: No strict limits (free tier)
- Alpha Vantage: 25 requests/day, 5 requests/minute
- Finnhub: 60 requests/minute

### Database Performance
- SQLite for development and small deployments
- Easily upgradeable to PostgreSQL/MySQL for production
- Indexed queries for fast data retrieval

## Troubleshooting

### Common Issues

1. **API Rate Limits**:
   - Solution: Configure your own API keys
   - Monitor usage in the database

2. **Database Errors**:
   - Solution: Reinitialize database with `DatabaseManager().initialize_database()`

3. **Missing Data**:
   - Solution: Check API connectivity and keys
   - Use the refresh function in the dashboard

4. **PDF Export Issues**:
   - Solution: Ensure ReportLab is properly installed
   - Check file permissions in the reports directory

### Logs and Debugging
- Enable debug mode: `FLASK_ENV=development`
- Check console logs in the browser
- Monitor API usage in the database

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the GitHub issues
3. Create a new issue with detailed information

## Roadmap

### Upcoming Features
- [ ] Real-time WebSocket updates
- [ ] Advanced charting with technical indicators
- [ ] Portfolio optimization suggestions
- [ ] Email/SMS alerts for significant changes
- [ ] Integration with more data sources
- [ ] Machine learning price predictions
- [ ] Mobile app companion

### Performance Improvements
- [ ] Caching layer for API responses
- [ ] Background job processing
- [ ] Database optimization
- [ ] CDN integration for static assets

---

**Enhanced Geospatial Portfolio Dashboard** - Comprehensive stock tracking with enterprise-grade features and multi-API reliability.
