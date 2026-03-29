import google.generativeai as genai
import json
from app.config import settings

class PatternExtractor:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    async def extract(self, analysis_result: dict):
        if not self.model:
            return {
                "layout_type": "standard_saas",
                "structure": ["hero", "features", "pricing"]
            }
        
        prompt = f"""
        Extract the structured layout architecture from the following trend analysis.
        Return ONLY valid JSON: {{"layout_type": "string", "structure": ["sectionA", "sectionB"]}}
        
        Analysis: {json.dumps(analysis_result)}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            return {"layout_type": "saas_landing", "structure": ["hero", "features", "pricing", "testimonials"]}
