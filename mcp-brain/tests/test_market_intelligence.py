import pytest
import asyncio
from market_intelligence.trend_collector import TrendCollector
from market_intelligence.design_scraper import DesignScraper
from market_intelligence.pattern_extractor import PatternExtractor
from market_intelligence.design_brief_generator import DesignBriefGenerator
from pipelines.market_pipeline import MarketPipeline

@pytest.mark.asyncio
async def test_trend_collector():
    collector = TrendCollector()
    result = await collector.collect()
    assert "trend" in result
    assert result["popularity_score"] is not None

@pytest.mark.asyncio
async def test_scraper():
    scraper = DesignScraper()
    result = await scraper.scrape({"trend": "AI SaaS landing page"})
    assert "title" in result
    assert "components" in result

@pytest.mark.asyncio
async def test_pattern_extractor():
    extractor = PatternExtractor()
    result = await extractor.extract({"popular_sections": ["hero"]})
    assert "layout_type" in result
    assert "structure" in result

@pytest.mark.asyncio
async def test_design_brief_generator():
    generator = DesignBriefGenerator()
    result = await generator.generate({}, {}, {}, {}, {}, {})
    assert "product_type" in result
    assert "sections" in result

@pytest.mark.asyncio
async def test_market_pipeline():
    pipeline = MarketPipeline()
    pipeline_id, result = await pipeline.run("test input")
    assert pipeline_id is not None
    assert result["status"] == "success"
    assert "brief" in result
    assert "demand_score" in result
