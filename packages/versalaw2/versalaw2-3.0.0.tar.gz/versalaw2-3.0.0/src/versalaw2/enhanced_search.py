"""
Enhanced Search Engine for VersaLaw2
Fixed version
"""

from typing import Dict, List, Any, Optional

class EnhancedSearchEngine:
    """Enhanced search engine for legal content"""
    
    def __init__(self, cases=None):
        self.cases = cases or []
        self.search_index = self._build_index()
        print("🔍 EnhancedSearchEngine initialized!")
    
    def _build_index(self):
        """Build search index from available cases"""
        return {
            "legal_terms": ["kontrak", "hukum", "perjanjian", "klausa", "yurisdiksi"],
            "ghost_contracts": ["bci", "neural", "quantum", "ai", "digital clone"],
            "risk_factors": ["berbahaya", "risiko", "liability", "jurisdiction"]
        }
    
    def search_legal_content(self, query: str, search_type: str = "all") -> Dict[str, Any]:
        """Search legal content with enhanced capabilities"""
        query_lower = query.lower()
        
        results = {
            "query": query,
            "search_type": search_type,
            "matches": [],
            "suggested_terms": []
        }
        
        # Simple search logic
        for category, terms in self.search_index.items():
            for term in terms:
                if term in query_lower:
                    results["matches"].append({
                        "category": category,
                        "term": term,
                        "relevance": "high" if term in query_lower else "medium"
                    })
        
        return results
    
    def advanced_search(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Advanced search with filters"""
        base_results = self.search_legal_content(query)
        
        if filters:
            base_results["filters_applied"] = filters
            base_results["filtered_matches"] = [
                match for match in base_results["matches"]
                if self._apply_filters(match, filters)
            ]
        
        return base_results
    
    def _apply_filters(self, match: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to search results"""
        for key, value in filters.items():
            if key in match and match[key] != value:
                return False
        return True
