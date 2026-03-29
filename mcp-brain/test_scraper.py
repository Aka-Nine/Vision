import asyncio
from market_intelligence.design_scraper import DesignScraper
import json

async def run_scraper():
    print("Initializing Playwright Scraper...")
    scraper = DesignScraper()
    
    # We pass a test trend specifically targeting Dribbble's web design search query
    trend_input = {"trend": "SaaS Platform UI"}
    print(f"Searching Dribbble for: {trend_input['trend']}")
    
    scraped = await scraper.scrape(trend_input)
    
    print("\n--- Scraper Finished ---")
    print(json.dumps(scraped, indent=2))

if __name__ == "__main__":
    asyncio.run(run_scraper())
