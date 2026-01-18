"""
News collector module for fetching stock news from free sources.
Uses direct RSS parsing without feedparser dependency.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import Optional
import re
import html


class NewsCollector:
    """Collects news for stock tickers from multiple free sources."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_news(self, ticker: str, limit: int = 20) -> list[dict]:
        """
        Fetch news for a given stock ticker from multiple sources.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            limit: Maximum number of news items to return

        Returns:
            List of news items sorted by date (newest first)
        """
        ticker = ticker.upper().strip()
        all_news = []

        # Fetch from multiple sources
        all_news.extend(self._fetch_yahoo_finance_rss(ticker))
        all_news.extend(self._fetch_google_news_rss(ticker))

        # Remove duplicates based on title similarity
        unique_news = self._deduplicate_news(all_news)

        # Sort by date (newest first)
        unique_news.sort(key=lambda x: x.get('published_date') or datetime.min, reverse=True)

        return unique_news[:limit]

    def _parse_rss_feed(self, url: str, source: str) -> list[dict]:
        """Parse an RSS feed URL and return news items."""
        news_items = []

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml-xml')

            # Find all items in the RSS feed
            items = soup.find_all('item')

            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                pub_date_elem = item.find('pubDate')

                title = title_elem.get_text(strip=True) if title_elem else 'No title'
                link = link_elem.get_text(strip=True) if link_elem else ''
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                pub_date_str = pub_date_elem.get_text(strip=True) if pub_date_elem else ''

                # Parse publication date
                published_date = None
                if pub_date_str:
                    try:
                        published_date = date_parser.parse(pub_date_str)
                    except (ValueError, TypeError):
                        pass

                # Clean up description
                description = self._clean_html(description)
                if len(description) > 300:
                    description = description[:297] + '...'

                news_items.append({
                    'title': html.unescape(title),
                    'url': link,
                    'description': description,
                    'source': source,
                    'published_date': published_date,
                    'published_str': self._format_date(published_date)
                })

        except Exception as e:
            print(f"Error fetching RSS from {source}: {e}")

        return news_items

    def _fetch_yahoo_finance_rss(self, ticker: str) -> list[dict]:
        """Fetch news from Yahoo Finance RSS feed."""
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        return self._parse_rss_feed(url, 'Yahoo Finance')

    def _fetch_google_news_rss(self, ticker: str) -> list[dict]:
        """Fetch news from Google News RSS feed."""
        query = f"{ticker} stock"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        return self._parse_rss_feed(url, 'Google News')

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean up text."""
        if not text:
            return ''
        soup = BeautifulSoup(text, 'lxml')
        clean_text = soup.get_text(separator=' ')
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return html.unescape(clean_text)

    def _format_date(self, dt: Optional[datetime]) -> str:
        """Format datetime for display."""
        if not dt:
            return 'Unknown date'

        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago" if minutes != 1 else "1 minute ago"
            return f"{hours} hours ago" if hours != 1 else "1 hour ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return dt.strftime('%b %d, %Y')

    def _deduplicate_news(self, news_items: list[dict]) -> list[dict]:
        """Remove duplicate news items based on title similarity."""
        seen_titles = set()
        unique_items = []

        for item in news_items:
            # Normalize title for comparison
            normalized = re.sub(r'[^a-z0-9]', '', item['title'].lower())

            # Check if we've seen a similar title
            if normalized not in seen_titles and len(normalized) > 10:
                seen_titles.add(normalized)
                unique_items.append(item)

        return unique_items


def get_stock_info(ticker: str) -> dict:
    """Get basic stock information for display."""
    ticker = ticker.upper().strip()

    # Common stock names mapping
    stock_names = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'GOOG': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'TSLA': 'Tesla Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
        'JNJ': 'Johnson & Johnson',
        'WMT': 'Walmart Inc.',
        'PG': 'Procter & Gamble Co.',
        'MA': 'Mastercard Inc.',
        'HD': 'Home Depot Inc.',
        'DIS': 'Walt Disney Co.',
        'NFLX': 'Netflix Inc.',
        'PYPL': 'PayPal Holdings Inc.',
        'INTC': 'Intel Corporation',
        'AMD': 'Advanced Micro Devices Inc.',
    }

    return {
        'ticker': ticker,
        'name': stock_names.get(ticker, f'{ticker} Stock'),
    }
