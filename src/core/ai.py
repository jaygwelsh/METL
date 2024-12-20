# src/core/ai.py
from utils.logger import get_logger

logger = get_logger(__name__)

class AIPolicyRecommender:
    """
    A simple AI-based policy recommender that inspects file content
    and suggests compliance tags.
    """
    def __init__(self, config):
        self.enabled = config.get("enabled", True)

    def suggest_metadata(self, file_content):
        if not self.enabled:
            logger.info("AI metadata suggestion disabled.")
            return {}
        suggestions = {}
        content_lower = file_content.lower()
        if "patient" in content_lower:
            suggestions["compliance_tag"] = "HIPAA"
        if "financial" in content_lower:
            suggestions["compliance_tag"] = "SOX"
        if "personal data" in content_lower:
            suggestions["compliance_tag"] = "GDPR"
        if not suggestions:
            suggestions["compliance_tag"] = "GENERAL"
        return suggestions
