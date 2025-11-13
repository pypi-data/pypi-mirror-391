"""
Enhanced Database Integration for VersaLaw2
"""

import os
from typing import Dict, List, Any, Optional

class LegalDatabaseIntegrator:
    """Integrator for legal databases"""
    
    def __init__(self):
        self.package_dir = os.path.dirname(__file__)
        self.databases_loaded = False
        self._load_all_databases()
    
    def _load_all_databases(self):
        """Load all legal databases"""
        try:
            # Load KUHP 2026
            kuhp_path = os.path.join(self.package_dir, 'legal_databases', 'DATABASE_KUHP_BARU_2026.md')
            with open(kuhp_path, 'r', encoding='utf-8') as f:
                self.kuhp_2026_content = f.read()
            
            # Load UNIDROIT Principles
            unidroit_path = os.path.join(self.package_dir, 'legal_databases', 'DATABASE_UNIDROIT_PRINCIPLES_2016.md')
            with open(unidroit_path, 'r', encoding='utf-8') as f:
                self.unidroit_content = f.read()
            
            # Load other databases
            dangerous_clauses_path = os.path.join(self.package_dir, 'legal_databases', 'ANALISIS_KLAUSUL_BERBAHAYA_PERJANJIAN_INTERNASIONAL.md')
            with open(dangerous_clauses_path, 'r', encoding='utf-8') as f:
                self.dangerous_clauses_content = f.read()
            
            self.databases_loaded = True
            print("✅ All legal databases loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading databases: {e}")
            self.databases_loaded = False
    
    def search_kuhp_2026(self, keyword: str) -> Dict[str, Any]:
        """Search KUHP 2026 database"""
        if not self.databases_loaded:
            return {"error": "Databases not loaded"}
        
        # Simple keyword search
        lines = self.kuhp_2026_content.split('\n')
        relevant_lines = [line for line in lines if keyword.lower() in line.lower()]
        
        return {
            "keyword": keyword,
            "results_count": len(relevant_lines),
            "relevant_articles": relevant_lines[:10],  # First 10 results
            "database": "KUHP 2026"
        }
    
    def get_unidroit_principles(self, principle_type: str = None) -> Dict[str, Any]:
        """Get UNIDROIT principles"""
        if not self.databases_loaded:
            return {"error": "Databases not loaded"}
        
        # Extract principles based on type
        principles = {
            "formation": "Principles related to contract formation",
            "interpretation": "Principles for contract interpretation", 
            "performance": "Performance and breach principles",
            "remedies": "Remedies and damages principles"
        }
        
        return {
            "principle_type": principle_type,
            "available_types": list(principles.keys()),
            "content_sample": self.unidroit_content[:500] + "...",
            "total_length": len(self.unidroit_content)
        }
    
    def analyze_dangerous_clauses(self, contract_text: str) -> Dict[str, Any]:
        """Analyze contract for dangerous international clauses"""
        if not self.databases_loaded:
            return {"error": "Databases not loaded"}
        
        # Simple analysis based on dangerous clauses database
        dangerous_indicators = [
            "yurisdiksi asing", "arbitrase luar negeri", "hukum asing", 
            "limited liability", "force majeure luas", "perubahan sepihak"
        ]
        
        found_clauses = []
        for indicator in dangerous_indicators:
            if indicator in contract_text.lower():
                found_clauses.append(indicator)
        
        risk_level = "high" if len(found_clauses) >= 3 else "medium" if len(found_clauses) >= 1 else "low"
        
        return {
            "risk_level": risk_level,
            "dangerous_clauses_found": found_clauses,
            "total_indicators": len(dangerous_indicators),
            "matched_indicators": len(found_clauses)
        }

# Enhanced version of existing classes
class EnhancedLegalClassifierWithDB:
    """Enhanced legal classifier with database integration"""
    
    def __init__(self):
        from .core import EnhancedLegalClassifier
        self.base_classifier = EnhancedLegalClassifier()
        self.database_integrator = LegalDatabaseIntegrator()
    
    def comprehensive_analysis_with_db(self, text: str) -> Dict[str, Any]:
        """Enhanced analysis with database integration"""
        # Get base analysis
        base_result = self.base_classifier.comprehensive_analysis(text)
        
        # Add database insights
        db_insights = {
            "kuhp_2026_references": self.database_integrator.search_kuhp_2026(text),
            "international_standards": self.database_integrator.get_unidroit_principles(),
            "dangerous_clauses_analysis": self.database_integrator.analyze_dangerous_clauses(text)
        }
        
        # Combine results
        enhanced_result = {
            **base_result,
            "database_insights": db_insights,
            "analysis_level": "enhanced_with_database"
        }
        
        return enhanced_result
    
    def get_kuhp_2026_article(self, keyword: str) -> Dict[str, Any]:
        """Get KUHP 2026 articles by keyword"""
        return self.database_integrator.search_kuhp_2026(keyword)
    
    def analyze_with_international_standards(self, text: str) -> Dict[str, Any]:
        """Analyze with international standards"""
        base_analysis = self.base_classifier.comprehensive_analysis(text)
        international_analysis = self.database_integrator.get_unidroit_principles()
        
        return {
            "base_analysis": base_analysis,
            "international_standards": international_analysis,
            "compliance_level": "assessed"
        }
