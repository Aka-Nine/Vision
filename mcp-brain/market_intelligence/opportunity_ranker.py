class OpportunityRanker:
    def rank_opportunities(self, opportunities: list) -> list:
        """
        Expects a list of dictionaries with:
        demand_score
        trend_velocity
        competition_score (or competition_factor where lower competition = better score)
        """
        ranked = []
        for opp in opportunities:
            demand = opp.get("demand_score", 0.5)
            velocity = opp.get("trend_velocity", 1.0)
            
            # If competition_score represents how fiercely competitive it is, we might want inverse
            competition = opp.get("competition_score", 0.5)
            competition_factor = 1.0 - competition if competition <= 1.0 else 1.0
            
            # Opportunity Score = Demand Score × Trend Velocity × Competition Factor
            score = demand * velocity * competition_factor
            
            opp["opportunity_score"] = round(score, 3)
            ranked.append(opp)
            
        # Sort descending
        ranked.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
        return ranked

opportunity_ranker = OpportunityRanker()
