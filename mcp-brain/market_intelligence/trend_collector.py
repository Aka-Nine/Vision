import requests
from bs4 import BeautifulSoup
from app.config import settings
import logging
import praw
from utils.cache import cache

class TrendCollector:
    async def collect(self):
        logging.info(f"TrendCollector running in {settings.market_data_provider} mode.")
        if settings.market_data_provider == "paid" and settings.apify_api_key:
            return {
                "trend": "SaaS Dark Mode (Apify Paid Data)",
                "popularity_score": 0.95,
                "source": "dribbble_apify"
            }
            
        cached_trend = cache.get("latest_trend")
        if cached_trend:
            logging.info("Returning cached trend.")
            return cached_trend
        
        # Try Reddit if configured
        if settings.reddit_client_id and settings.reddit_client_secret:
            try:
                reddit = praw.Reddit(
                    client_id=settings.reddit_client_id,
                    client_secret=settings.reddit_client_secret,
                    user_agent=settings.reddit_user_agent
                )
                
                # Check top UI/UX related subreddits for trends
                subreddit = reddit.subreddit("UI_Design+web_design+SaaS")
                top_post = next(subreddit.hot(limit=1))
                
                # Determine if the post links to an external design reference (e.g. a live website)
                reference_url = top_post.url if "reddit.com" not in top_post.url else None

                trend_data = {
                    "trend": f"Reddit Theme: {top_post.title}",
                    "popularity_score": min(top_post.score / 1000.0 + 0.5, 0.99), # Normalize reddit score to 0.5-0.99
                    "source": f"reddit_api: r/{top_post.subreddit.display_name}",
                    "reference_url": reference_url
                }
                cache.set("latest_trend", trend_data)
                return trend_data
            except Exception as e:
                logging.error(f"Reddit API failed: {e}")

        # Fallback to HackerNews if Reddit not configured or fails
        try:
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                top_id = response.json()[0]
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{top_id}.json"
                item_response = requests.get(item_url, timeout=5)
                title = item_response.json().get("title", "AI Web App Template")
                
                trend_data = {
                    "trend": f"UI for: {title}",
                    "popularity_score": 0.88,
                    "source": "hacker_news_free_api"
                }
                cache.set("latest_trend", trend_data)
                return trend_data
        except Exception as e:
            logging.error(f"Free TrendCollector failed: {e}")

        # Fallback
        fallback_data = {
            "trend": "AI SaaS landing page",
            "popularity_score": 0.89,
            "source": "fallback_data"
        }
        cache.set("latest_trend", fallback_data)
        return fallback_data
