class SourceReputationScorer:
    def get_source_score(self, source_url: str, metadata_source: str = "") -> float:
        source = source_url.lower() + metadata_source.lower()
        
        if "dribbble.com" in source or "dribbble" in source:
            return 0.8
        elif "pinterest.com" in source or "pinterest" in source:
            return 0.6
        elif "reddit.com" in source or "reddit api" in source:
            return 0.7
        elif "hacker_news" in source or "ycombinator" in source:
            return 0.9
        else:
            # Assume live product site
            return 1.0

reputation_scorer = SourceReputationScorer()
