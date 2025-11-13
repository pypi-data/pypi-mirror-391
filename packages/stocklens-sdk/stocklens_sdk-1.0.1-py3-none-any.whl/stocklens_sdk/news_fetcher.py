import requests
import os

# 🧩 Default StockLens-hosted n8n webhook URL
DEFAULT_N8N_WEBHOOK = "https://owl-winning-legally.ngrok-free.app/webhook/sentiment"

def fetch_news_from_n8n(symbol: str, n8n_webhook_url: str = None):
    """
    Fetches news articles for the given stock symbol from an n8n webhook.
    - symbol: Stock symbol (e.g., 'AAPL')
    - n8n_webhook_url: Optional custom webhook URL. If not provided, uses the StockLens default.
    
    Returns:
        dict: JSON response with articles and metadata.
    Raises:
        ValueError: if symbol is missing.
        RuntimeError: if request fails or response is invalid.
    """
    if not symbol:
        raise ValueError("Stock symbol is required")

    # 🧠 Use provided URL, environment variable, or fallback to StockLens default
    n8n_webhook_url = n8n_webhook_url or os.getenv("N8N_WEBHOOK_URL", DEFAULT_N8N_WEBHOOK)

    # Construct request URL
    url = f"{n8n_webhook_url}?stock={symbol}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Handle array-wrapped responses (n8n often returns lists)
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        data["symbol"] = symbol.upper()
        return data

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching news from n8n: {e}")
