# legalmind/unified_analyzer.py
"""
UNIFIED ANALYZER - Integrasi semua 4,638 lines existing analysis code
"""
class UnifiedLegalAnalyzer:
    def __init__(self):
        self.analyzers = self.load_all_analyzers()
    
    def analyze_contract(self, contract_text, analysis_type="comprehensive"):
        """Unified contract analysis menggunakan semua existing capabilities"""
        results = {}
        
        # Gunakan problematic contracts analyzer
        results['problematic_analysis'] = self.use_problematic_analyzer(contract_text)
        
        # Gunakan international tech analyzer  
        results['international_analysis'] = self.use_international_analyzer(contract_text)
        
        # Integrasi dengan KUHP Baru
        results['kuhp_baru_compliance'] = self.integrate_kuhp_baru(contract_text)
        
        return results
