
// Enhanced Geospatial Portfolio Dashboard JavaScript

let stocksData = [];
let filteredStocks = [];
let currentStock = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    setupEventListeners();
});

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', filterStocks);
    
    // Sector filter
    document.getElementById('sectorFilter').addEventListener('change', filterStocks);
}

async function loadDashboardData() {
    showLoading(true);
    
    try {
        // Load stocks data
        const stocksResponse = await fetch('/api/stocks');
        const stocksResult = await stocksResponse.json();
        
        if (stocksResult.success) {
            stocksData = stocksResult.data;
            filteredStocks = [...stocksData];
            updateDashboardStats(stocksResult);
            populateStocksTable();
            populateSectorFilter();
        }
        
        // Load portfolio performance
        const performanceResponse = await fetch('/api/portfolio/performance');
        const performanceResult = await performanceResponse.json();
        
        if (performanceResult.success) {
            updatePerformanceStats(performanceResult.data);
        }
        
        // Load sector analysis
        const sectorResponse = await fetch('/api/sectors');
        const sectorResult = await sectorResponse.json();
        
        if (sectorResult.success) {
            createSectorCharts(sectorResult.data);
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error loading dashboard data. Please try again.', 'danger');
    } finally {
        showLoading(false);
    }
}

function updateDashboardStats(result) {
    document.getElementById('totalStocks').textContent = result.total_stocks || 130;
    
    // Calculate success rate based on data availability
    const successRate = Math.round((result.data.filter(s => s.price > 0).length / result.total_stocks) * 100);
    document.getElementById('successRate').textContent = `${successRate}%`;
}

function updatePerformanceStats(performanceData) {
    const totalMarketCap = performanceData.total_market_cap || 0;
    const avgChange = performanceData.avg_change || 0;
    
    document.getElementById('totalMarketCap').textContent = formatCurrency(totalMarketCap);
    document.getElementById('avgChange').textContent = formatCurrency(avgChange);
}

function populateStocksTable() {
    const tbody = document.getElementById('stocksTableBody');
    tbody.innerHTML = '';
    
    filteredStocks.forEach(stock => {
        const row = createStockRow(stock);
        tbody.appendChild(row);
    });
}

function createStockRow(stock) {
    const row = document.createElement('tr');
    
    const change = stock.change || 0;
    const changePercent = stock.change_percent || 0;
    const changeClass = change > 0 ? 'positive-change' : change < 0 ? 'negative-change' : 'neutral-change';
    
    row.innerHTML = `
        <td><span class="stock-symbol">${stock.symbol || 'N/A'}</span></td>
        <td title="${stock.name || 'N/A'}">${truncateText(stock.name || 'N/A', 30)}</td>
        <td>${formatCurrency(stock.price || 0)}</td>
        <td class="${changeClass}">${formatCurrency(change)}</td>
        <td class="${changeClass}">${changePercent.toFixed(2)}%</td>
        <td>${formatNumber(stock.volume || 0)}</td>
        <td class="market-cap">${formatCurrency(stock.market_cap || 0)}</td>
        <td><span class="badge bg-secondary sector-badge">${stock.sector || 'Unknown'}</span></td>
        <td>${stock.country || 'Unknown'}</td>
        <td>
            <button class="btn btn-primary btn-sm" onclick="viewStockDetail('${stock.symbol}')">
                <i class="fas fa-eye"></i> View
            </button>
        </td>
    `;
    
    return row;
}

function populateSectorFilter() {
    const sectorFilter = document.getElementById('sectorFilter');
    const sectors = [...new Set(stocksData.map(stock => stock.sector).filter(s => s))];
    
    // Clear existing options except "All Sectors"
    sectorFilter.innerHTML = '<option value="">All Sectors</option>';
    
    sectors.sort().forEach(sector => {
        const option = document.createElement('option');
        option.value = sector;
        option.textContent = sector;
        sectorFilter.appendChild(option);
    });
}

function filterStocks() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const selectedSector = document.getElementById('sectorFilter').value;
    
    filteredStocks = stocksData.filter(stock => {
        const matchesSearch = !searchTerm || 
            (stock.symbol && stock.symbol.toLowerCase().includes(searchTerm)) ||
            (stock.name && stock.name.toLowerCase().includes(searchTerm));
            
        const matchesSector = !selectedSector || stock.sector === selectedSector;
        
        return matchesSearch && matchesSector;
    });
    
    populateStocksTable();
}

async function viewStockDetail(symbol) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/stock/${symbol}`);
        const result = await response.json();
        
        if (result.success) {
            currentStock = result.data;
            displayStockDetail(result.data);
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('stockDetailModal'));
            modal.show();
        } else {
            showAlert(`Error loading stock details: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error loading stock detail:', error);
        showAlert('Error loading stock details. Please try again.', 'danger');
    } finally {
        showLoading(false);
    }
}

function displayStockDetail(stockData) {
    const modalTitle = document.getElementById('stockDetailTitle');
    const modalBody = document.getElementById('stockDetailBody');
    
    modalTitle.textContent = `${stockData.symbol} - ${stockData.name || 'N/A'}`;
    
    const change = stockData.change || 0;
    const changeClass = change > 0 ? 'text-success' : change < 0 ? 'text-danger' : 'text-muted';
    
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Current Price Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>Current Price:</strong></td><td>${formatCurrency(stockData.price || 0)}</td></tr>
                    <tr><td><strong>Change:</strong></td><td class="${changeClass}">${formatCurrency(change)}</td></tr>
                    <tr><td><strong>Change %:</strong></td><td class="${changeClass}">${(stockData.change_percent || 0).toFixed(2)}%</td></tr>
                    <tr><td><strong>Volume:</strong></td><td>${formatNumber(stockData.volume || 0)}</td></tr>
                    <tr><td><strong>Market Cap:</strong></td><td>${formatCurrency(stockData.market_cap || 0)}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>Company Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>Sector:</strong></td><td>${stockData.sector || 'Unknown'}</td></tr>
                    <tr><td><strong>Industry:</strong></td><td>${stockData.industry || 'Unknown'}</td></tr>
                    <tr><td><strong>Country:</strong></td><td>${stockData.country || 'Unknown'}</td></tr>
                    <tr><td><strong>Exchange:</strong></td><td>${stockData.exchange || 'Unknown'}</td></tr>
                    <tr><td><strong>Currency:</strong></td><td>${stockData.currency || 'USD'}</td></tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6>5-Year Historical Chart</h6>
                <div id="stockChart" style="height: 300px;"></div>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <small class="text-muted">
                    Data Source: ${stockData.source || 'Multiple APIs'} | 
                    Last Updated: ${new Date(stockData.timestamp).toLocaleString()}
                </small>
            </div>
        </div>
    `;
    
    // Create historical chart if data is available
    if (stockData.historical && stockData.historical.length > 0) {
        createHistoricalChart(stockData.historical);
    } else {
        document.getElementById('stockChart').innerHTML = '<p class="text-center text-muted">Historical data not available</p>';
    }
}

function createHistoricalChart(historicalData) {
    const dates = historicalData.map(d => d.date);
    const prices = historicalData.map(d => d.close);
    
    const trace = {
        x: dates,
        y: prices,
        type: 'scatter',
        mode: 'lines',
        name: 'Close Price',
        line: { color: '#007bff', width: 2 }
    };
    
    const layout = {
        title: '5-Year Price History',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Price ($)' },
        margin: { t: 40, r: 40, b: 40, l: 60 }
    };
    
    Plotly.newPlot('stockChart', [trace], layout, { responsive: true });
}

function createSectorCharts(sectorData) {
    // Sector distribution pie chart
    const sectorNames = Object.keys(sectorData);
    const sectorCounts = sectorNames.map(sector => sectorData[sector].count);
    
    const pieTrace = {
        labels: sectorNames,
        values: sectorCounts,
        type: 'pie',
        textinfo: 'label+percent',
        textposition: 'outside'
    };
    
    const pieLayout = {
        title: 'Portfolio Distribution by Sector',
        margin: { t: 40, r: 40, b: 40, l: 40 }
    };
    
    Plotly.newPlot('sectorChart', [pieTrace], pieLayout, { responsive: true });
    
    // Sector performance bar chart
    const avgChanges = sectorNames.map(sector => sectorData[sector].avg_change || 0);
    
    const barTrace = {
        x: sectorNames,
        y: avgChanges,
        type: 'bar',
        marker: {
            color: avgChanges.map(change => change > 0 ? '#28a745' : '#dc3545')
        }
    };
    
    const barLayout = {
        title: 'Average Performance by Sector',
        xaxis: { title: 'Sector' },
        yaxis: { title: 'Average Change ($)' },
        margin: { t: 40, r: 40, b: 80, l: 60 }
    };
    
    Plotly.newPlot('performanceChart', [barTrace], barLayout, { responsive: true });
}

async function refreshData() {
    showAlert('Refreshing data...', 'info');
    await loadDashboardData();
    showAlert('Data refreshed successfully!', 'success');
}

async function exportPDF() {
    try {
        showLoading(true);
        showAlert('Generating PDF report...', 'info');
        
        const response = await fetch('/api/export/pdf');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `portfolio_report_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('PDF report downloaded successfully!', 'success');
        } else {
            throw new Error('Failed to generate PDF');
        }
    } catch (error) {
        console.error('Error exporting PDF:', error);
        showAlert('Error generating PDF report. Please try again.', 'danger');
    } finally {
        showLoading(false);
    }
}

async function exportStockPDF() {
    if (!currentStock) return;
    
    try {
        showLoading(true);
        showAlert('Generating stock PDF report...', 'info');
        
        // This would call a specific endpoint for individual stock PDF
        showAlert('Stock PDF export feature coming soon!', 'info');
        
    } catch (error) {
        console.error('Error exporting stock PDF:', error);
        showAlert('Error generating stock PDF report.', 'danger');
    } finally {
        showLoading(false);
    }
}

// Utility functions
function formatCurrency(value) {
    if (value === 0 || value === null || value === undefined) return '$0.00';
    
    if (Math.abs(value) >= 1e12) {
        return `$${(value / 1e12).toFixed(2)}T`;
    } else if (Math.abs(value) >= 1e9) {
        return `$${(value / 1e9).toFixed(2)}B`;
    } else if (Math.abs(value) >= 1e6) {
        return `$${(value / 1e6).toFixed(2)}M`;
    } else if (Math.abs(value) >= 1e3) {
        return `$${(value / 1e3).toFixed(2)}K`;
    } else {
        return `$${value.toFixed(2)}`;
    }
}

function formatNumber(value) {
    if (value === 0 || value === null || value === undefined) return '0';
    
    if (Math.abs(value) >= 1e9) {
        return `${(value / 1e9).toFixed(2)}B`;
    } else if (Math.abs(value) >= 1e6) {
        return `${(value / 1e6).toFixed(2)}M`;
    } else if (Math.abs(value) >= 1e3) {
        return `${(value / 1e3).toFixed(2)}K`;
    } else {
        return value.toLocaleString();
    }
}

function truncateText(text, maxLength) {
    if (!text) return 'N/A';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Auto-refresh data every 5 minutes
setInterval(refreshData, 5 * 60 * 1000);
