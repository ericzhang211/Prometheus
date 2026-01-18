# Stock News Collector

A web dashboard application that collects and displays news for stock tickers from free sources.

## Features

- Search news by stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
- Aggregates news from multiple free sources:
  - Yahoo Finance RSS
  - Google News RSS
- Clean, responsive web dashboard
- Quick-access buttons for popular tickers
- Automatic deduplication of news items
- No API keys required

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Prometheus
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Enter a stock ticker symbol (e.g., AAPL, GOOGL, MSFT) and click Search

## API Endpoints

### GET /api/news/{ticker}

Fetch news for a specific stock ticker.

**Parameters:**
- `ticker` (path): Stock ticker symbol (e.g., AAPL)
- `limit` (query, optional): Maximum number of news items (default: 20, max: 50)

**Response:**
```json
{
  "stock": {
    "ticker": "AAPL",
    "name": "Apple Inc."
  },
  "news": [
    {
      "title": "News headline",
      "url": "https://...",
      "description": "Brief description...",
      "source": "Yahoo Finance",
      "published_str": "2 hours ago"
    }
  ],
  "count": 15
}
```

### GET /api/health

Health check endpoint.

## Project Structure

```
Prometheus/
├── app.py              # Flask application and routes
├── news_collector.py   # News fetching logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Dashboard HTML template
└── static/
    ├── style.css       # Dashboard styles
    └── app.js          # Frontend JavaScript
```

## License

MIT
