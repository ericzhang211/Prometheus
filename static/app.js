/**
 * Stock News Collector - Frontend Application
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const tickerInput = document.getElementById('ticker-input');
    const searchBtn = document.getElementById('search-btn');
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoading = searchBtn.querySelector('.btn-loading');
    const errorMessage = document.getElementById('error-message');
    const stockInfo = document.getElementById('stock-info');
    const stockName = document.getElementById('stock-name');
    const stockTicker = document.getElementById('stock-ticker');
    const newsCount = document.getElementById('news-count');
    const newsList = document.getElementById('news-list');
    const noNews = document.getElementById('no-news');
    const loading = document.getElementById('loading');

    // Quick ticker buttons
    document.querySelectorAll('.ticker-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const ticker = btn.dataset.ticker;
            tickerInput.value = ticker;
            fetchNews(ticker);
        });
    });

    // Search form submission
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const ticker = tickerInput.value.trim().toUpperCase();
        if (ticker) {
            fetchNews(ticker);
        }
    });

    /**
     * Fetch news for a given ticker symbol
     */
    async function fetchNews(ticker) {
        // Reset UI
        hideError();
        hideStockInfo();
        hideNewsList();
        showLoading();
        setButtonLoading(true);

        try {
            const response = await fetch(`/api/news/${encodeURIComponent(ticker)}?limit=20`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Failed to fetch news');
            }

            // Display results
            displayStockInfo(data.stock, data.count);
            displayNews(data.news);

            // Update URL for sharing (without page reload)
            window.history.replaceState({}, '', `?ticker=${ticker}`);

        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
            setButtonLoading(false);
        }
    }

    /**
     * Display stock information header
     */
    function displayStockInfo(stock, count) {
        stockName.textContent = stock.name;
        stockTicker.textContent = stock.ticker;
        newsCount.textContent = `${count} article${count !== 1 ? 's' : ''} found`;
        stockInfo.hidden = false;
    }

    /**
     * Display news items
     */
    function displayNews(news) {
        if (!news || news.length === 0) {
            noNews.hidden = false;
            return;
        }

        newsList.innerHTML = news.map(item => `
            <article class="news-item">
                <h3>
                    <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">
                        ${escapeHtml(item.title)}
                    </a>
                </h3>
                ${item.description ? `<p class="description">${escapeHtml(item.description)}</p>` : ''}
                <div class="news-meta">
                    <span class="news-source">${escapeHtml(item.source)}</span>
                    <span class="news-date">${escapeHtml(item.published_str)}</span>
                </div>
            </article>
        `).join('');

        newsList.parentElement.hidden = false;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * UI helper functions
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.hidden = false;
    }

    function hideError() {
        errorMessage.hidden = true;
    }

    function showLoading() {
        loading.hidden = false;
    }

    function hideLoading() {
        loading.hidden = true;
    }

    function hideStockInfo() {
        stockInfo.hidden = true;
    }

    function hideNewsList() {
        newsList.innerHTML = '';
        noNews.hidden = true;
    }

    function setButtonLoading(isLoading) {
        searchBtn.disabled = isLoading;
        btnText.hidden = isLoading;
        btnLoading.hidden = !isLoading;
    }

    // Check for ticker in URL on page load
    const urlParams = new URLSearchParams(window.location.search);
    const initialTicker = urlParams.get('ticker');
    if (initialTicker) {
        tickerInput.value = initialTicker.toUpperCase();
        fetchNews(initialTicker.toUpperCase());
    }
});
