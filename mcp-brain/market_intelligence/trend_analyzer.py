import google.generativeai as genai
import json
import requests
from app.config import settings

class TrendAnalyzer:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    async def analyze(self, designs: list):
        if not self.model:
            return {"popular_sections": ["hero with gradient", "feature grid"]}
        
        # Build the payload for the multi-modal Gemini prompt
        gemini_payload = []
        
        prompt = f"""
        You are an expert AI UI/UX Designer and Frontend Engineer.
        Analyze the provided scraped design references (screenshots + page context).
        I need you to look intimately at the pixels and extract:
        1. The exact structural layout and sections you see.
        2. Minute visual details: the typography style, textures, button shapes, color palette.
        3. Motion/Animation hints: do you see scrolling banners, parallax, hover state indicators, or dropdowns?
        4. Spatial understanding: map out where you see key components. For each component, provide rough normalized coordinates [x, y, width, height] where values are roughly between 0.0 and 1.0. 
        5. If page context is provided (headings/CTAs/html snippet), use it to disambiguate what the UI is trying to do.
        
        Return ONLY pure valid JSON in the exact format:
        {{
            "popular_sections": ["section1", "section2", "section3"],
            "typography": "description of text",
            "colors": ["string color scheme"],
            "implied_animations": ["animation detail", "animation detail"],
            "annotations": [
                 {{
                     "component": "pricing_card",
                     "coordinates": [0.1, 0.4, 0.8, 0.3]
                 }}
            ]
        }}
        
        Raw Metadata: {json.dumps(designs)}
        """
        gemini_payload.append(prompt)
        
        # We loop through the designs to find real visual images to pass directly to Gemini's "eyes"
        try:
            for design in designs:
                # 1) Reference pages (preferred): local screenshots + structured text context
                for ref in design.get("reference_pages", []) or []:
                    ss = ref.get("local_screenshot")
                    if ss:
                        with open(ss, "rb") as img_file:
                            gemini_payload.append({"mime_type": "image/png", "data": img_file.read()})
                
                # 2) Legacy: local screenshot on the design record
                if design.get("local_screenshot"):
                    with open(design["local_screenshot"], "rb") as img_file:
                        gemini_payload.append({"mime_type": "image/png", "data": img_file.read()})

                # 3) Or, if we grabbed native image URLs from Dribbble/Pinterest:
                for url in design.get("image_urls", []):
                    # We dynamically physically download the image into memory
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        content_type = resp.headers.get("Content-Type", "image/jpeg")
                        gemini_payload.append({
                            "mime_type": content_type,
                            "data": resp.content
                        })
                    
                    # We process a maximum of 2 images to avoid token overload
                    if len(gemini_payload) > 3:
                        break
        except Exception as e:
            print("Failed to map image arrays to Gemini visual input. Falling back to text-only.", e)
            
        try:
            # We pass the full multi-modal array (Text Prompt + Multiple Raw Images) to Gemini
            response = self.model.generate_content(gemini_payload)
            
            text = response.text.strip()
            if text.startswith("```json"):
                text = text.split("```json")[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            
            return json.loads(text.strip())
        except Exception as e:
            return {"error": str(e), "popular_sections": ["hero with gradient", "feature grid", "pricing table"]}
