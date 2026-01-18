"""
Stock News Collector - Web Dashboard Application

A Flask web application that collects and displays news for stock tickers
from free sources like Yahoo Finance and Google News RSS feeds.
"""

from flask import Flask, render_template, jsonify, request
from news_collector import NewsCollector, get_stock_info

app = Flask(__name__)
collector = NewsCollector()


@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')


@app.route('/api/news/<ticker>')
def get_news(ticker: str):
    """
    API endpoint to fetch news for a specific ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Query params:
        limit: Maximum number of news items (default: 20, max: 50)

    Returns:
        JSON response with stock info and news items
    """
    try:
        limit = min(int(request.args.get('limit', 20)), 50)
    except ValueError:
        limit = 20

    # Validate ticker
    ticker = ticker.upper().strip()
    if not ticker or len(ticker) > 10 or not ticker.isalpha():
        return jsonify({
            'error': 'Invalid ticker symbol',
            'message': 'Please provide a valid stock ticker (e.g., AAPL, GOOGL)'
        }), 400

    # Get stock info and news
    stock_info = get_stock_info(ticker)
    news_items = collector.get_news(ticker, limit=limit)

    # Convert datetime objects to strings for JSON serialization
    for item in news_items:
        if item.get('published_date'):
            item['published_date'] = item['published_date'].isoformat()

    return jsonify({
        'stock': stock_info,
        'news': news_items,
        'count': len(news_items)
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'stock-news-collector'})


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    app.run(debug=True, host='0.0.0.0', port=port)
