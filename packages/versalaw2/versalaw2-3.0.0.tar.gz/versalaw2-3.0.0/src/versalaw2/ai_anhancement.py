"""
AI Enhancement for VersaLaw2
Fixed version
"""

from typing import Dict, List, Any, Optional

class AIEnhancement:
    """AI enhancement capabilities for legal analysis"""
    
    def __init__(self):
        self.ai_capabilities = [
            "predictive_analysis",
            "natural_language_understanding", 
            "pattern_recognition",
            "risk_prediction",
            "recommendation_engine"
        ]
        print("🤖 AIEnhancement initialized!")
    
    def enhance_analysis(self, base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance existing analysis with AI capabilities"""
        
        enhanced_analysis = base_analysis.copy()
        
        # Add AI enhancements
        enhanced_analysis["ai_enhancements"] = {
            "confidence_score": 0.92,
            "pattern_insights": [
                "Similar clauses found in high-risk contracts",
                "Jurisdictional pattern detected",
                "Standard compliance issues identified"
            ],
            "predictive_analysis": {
                "potential_disputes": "low",
                "enforcement_difficulty": "medium",
                "regulatory_changes_impact": "low"
            },
            "recommendation_confidence": "high"
        }
        
        return enhanced_analysis
    
    def generate_legal_insights(self, legal_text: str) -> Dict[str, Any]:
        """Generate AI-powered legal insights"""
        
        return {
            "text_analysis": {
                "complexity_level": "high" if len(legal_text) > 500 else "medium",
                "key_topics": self._extract_topics(legal_text),
                "sentiment": "neutral"
            },
            "ai_insights": {
                "main_legal_issues": self._identify_legal_issues(legal_text),
                "suggested_reviews": self._suggest_reviews(legal_text),
                "compliance_gaps": self._identify_gaps(legal_text)
            }
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        topics = []
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["kontrak", "perjanjian"]):
            topics.append("contract_law")
        if any(term in text_lower for term in ["hukum", "uu", "peraturan"]):
            topics.append("legal_compliance") 
        if any(term in text_lower for term in ["bci", "neural", "ai"]):
            topics.append("emerging_technology")
            
        return topics
    
    def _identify_legal_issues(self, text: str) -> List[str]:
        """Identify potential legal issues"""
        issues = []
        text_lower = text.lower()
        
        if "yurisdiksi asing" in text_lower:
            issues.append("foreign_jurisdiction_risk")
        if "limited liability" in text_lower:
            issues.append("liability_limitation")
        if "arbitrase" in text_lower:
            issues.append("dispute_resolution_concerns")
            
        return issues
    
    def _suggest_reviews(self, text: str) -> List[str]:
        """Suggest areas for legal review"""
        suggestions = []
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["bci", "neural", "quantum"]):
            suggestions.append("technology_law_expert")
        if "internasional" in text_lower:
            suggestions.append("international_law_specialist")
            
        return suggestions
    
    def _identify_gaps(self, text: str) -> List[str]:
        """Identify compliance gaps"""
        gaps = []
        text_lower = text.lower()
        
        if "data pribadi" in text_lower and "perlindungan" not in text_lower:
            gaps.append("data_privacy_protection")
        if "terminasi" in text_lower and "pemberitahuan" not in text_lower:
            gaps.append("termination_notice_period")
            
        return gaps
