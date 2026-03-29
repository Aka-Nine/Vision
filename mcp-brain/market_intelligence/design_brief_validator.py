import logging

class DesignBriefValidator:
    def __init__(self):
        self.required_fields = ["product_type", "target_market", "style", "sections", "animation_type"]

    def validate(self, brief: dict) -> tuple[bool, str]:
        if not brief:
            return False, "Brief is empty or None."
            
        for field in self.required_fields:
            if field not in brief or not brief[field]:
                return False, f"Missing required field: {field}"
                
        if not isinstance(brief.get("sections"), list) or len(brief.get("sections")) == 0:
            return False, "Sections must be a non-empty list."
            
        return True, "Valid"

brief_validator = DesignBriefValidator()
