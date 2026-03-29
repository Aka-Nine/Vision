from agents.base_agent import BaseAgent
from market_intelligence.trend_collector import TrendCollector
from market_intelligence.design_scraper import DesignScraper
from market_intelligence.trend_analyzer import TrendAnalyzer
from market_intelligence.pattern_extractor import PatternExtractor
from market_intelligence.demand_estimator import DemandEstimator
from market_intelligence.reference_collector import ReferenceCollector
from market_intelligence.design_brief_generator import DesignBriefGenerator

from storage.metadata_store import metadata_store
from storage.dataset_manager import dataset_manager

from monitoring.metrics import metrics
from market_intelligence.deduplication_engine import deduplication_engine
from market_intelligence.structured_pattern_library import pattern_library
from market_intelligence.design_brief_validator import brief_validator
from market_intelligence.opportunity_ranker import opportunity_ranker
from market_intelligence.brief_scorer import brief_scorer
from market_intelligence.reputation_scorer import reputation_scorer
from market_intelligence.generator_validator import generator_validator
from semantic_content_engine.engine import SemanticContentEngine
import time

class MarketIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("MarketIntelligenceAgent", "Analyzes design market and generates product briefs")
        self.trend_collector = TrendCollector()
        self.design_scraper = DesignScraper()
        self.trend_analyzer = TrendAnalyzer()
        self.pattern_extractor = PatternExtractor()
        self.demand_estimator = DemandEstimator()
        self.reference_collector = ReferenceCollector()
        self.design_brief_generator = DesignBriefGenerator()
        self.semantic_engine = SemanticContentEngine()

    async def process(self, task_input):
        dataset_manager.enforce_retention_policy()
        
        await self.log_activity("trend_collection_started", {"info": "Collecting trends"})
        
        trends = await self.trend_collector.collect()
        metadata_store.save_trend(trends)
        
        designs = await self.design_scraper.scrape(trends)
        
        # Track provenence and reputability 
        source_score = reputation_scorer.get_source_score(designs.get("source", ""), trends.get("source", ""))
        designs["reputation_score"] = source_score
        
        if not deduplication_engine.is_duplicate(designs):
            metrics.scrape_success.inc()
        else:
            await self.log_activity("duplicate_designs_skipped", {"info": "Duplicate scraped designs found"})
        
        await self.log_activity("design_scraping_completed", {"info": "Scraped designs successfully"})
        
        start_time = time.time()
        analysis = await self.trend_analyzer.analyze([designs])
        metrics.set_llm_time(time.time() - start_time)
        
        patterns = await self.pattern_extractor.extract(analysis)
        metadata_store.save_ui_pattern(patterns)
        
        # Save structured pattern library
        pattern_library.save_pattern(patterns.get('style', 'generic'), patterns)
        await self.log_activity("pattern_extraction_completed", {"info": "UI patterns extracted"})
        
        demand = await self.demand_estimator.estimate(patterns)
        metadata_store.save_demand_score(demand)
        
        # Rank opportunities if demand is a list, otherwise just add it wrapped in a list
        opportunities = [demand] if isinstance(demand, dict) else demand
        ranked_opps = opportunity_ranker.rank_opportunities(opportunities)
        best_opp = ranked_opps[0] if ranked_opps else demand
        
        references = await self.reference_collector.collect(patterns)
        metadata_store.save_design_reference(references)
        
        brief = await self.design_brief_generator.generate(trends, designs, analysis, patterns, best_opp, references)
        brief = brief_scorer.score_brief(brief)
        
        # Data provenance tracking mapping source chain mapping back to final output
        brief["provenance"] = {
            "trend_source": trends.get("source"),
            "design_reference": designs.get("source"),
            "image_urls": designs.get("image_urls", []),
            "analysis_model": "gemini_2.5_pro",
            "source_reputation": source_score
        }
        
        # Component checking
        # Check validation logic keys
        is_valid, validation_msg = brief_validator.validate(brief)
        if not is_valid:
            await self.log_activity("design_brief_validation_failed", {"error": validation_msg})
            raise Exception(f"Invalid Design Brief Generated: {validation_msg}")
            
        is_generation_ready, gen_msg = generator_validator.is_compatible(brief)
        if not is_generation_ready:
            await self.log_activity("generator_compatibility_failed", {"error": gen_msg})
            raise Exception(f"Unstable Brief Generated: {gen_msg}")
            
        metrics.brief_generation_count.inc()
        metadata_store.save_design_brief(brief)
        
        await self.log_activity("design_brief_generated", {"brief": brief})
        
        # ── Phase 2.5: Semantic Content Engine ──────────────────────
        await self.log_activity("semantic_engine_started", {"info": "Running Phase 2.5 Semantic Content Engine"})
        
        # Build trend_data structure for the semantic engine
        trend_data = {
            "trends": [{"trend": trends.get("trend", ""), "popularity_score": trends.get("popularity_score", 0), "source": trends.get("source", "")}]
        } if isinstance(trends, dict) else {"trends": trends if isinstance(trends, list) else []}
        
        semantic_brief = await self.semantic_engine.process(
            deep_analysis=None,  # Auto-loads latest from storage
            trend_data=trend_data,
            brief_data=brief,
        )
        
        await self.log_activity("semantic_engine_completed", {
            "sections": semantic_brief.get("_stats", {}).get("total_sections", 0),
            "avg_confidence": semantic_brief.get("_stats", {}).get("avg_confidence", 0),
        })
        
        return {
            "status": "success",
            "brief": brief,
            "semantic_brief": semantic_brief,
            "demand_score": best_opp.get("demand_score"),
            "quality_score": brief.get("quality_score")
        }
