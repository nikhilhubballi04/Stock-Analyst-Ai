import feedparser
from datetime import datetime

CATEGORIES = {
    "Economy News": "India economy RBI GDP inflation",
    "Corporate News": "India stock market quarterly results earnings",
    "Market Pulse": "stock market today Sensex Nifty US markets",
}


def fetch_news_category(query: str, limit: int = 6):
    """Fetch recent news headlines for a query via Google News RSS (free, no key needed)."""
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"

    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            published = entry.get("published_parsed")
            date_str = ""
            if published:
                date_str = datetime(*published[:6]).strftime("%d %b, %I:%M %p")

            items.append({
                "title": entry.title,
                "link": entry.link,
                "published": date_str,
                "source": entry.get("source", {}).get("title", "") if hasattr(entry, "source") else "",
            })
        return items
    except Exception:
        return []


def get_curated_news():
    """Fetch news across all categories."""
    result = {}
    for category, query in CATEGORIES.items():
        result[category] = fetch_news_category(query)
    return result