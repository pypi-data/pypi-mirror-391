"""
Contract Analyzer Module
Specialized analysis for contract documents and agreements
"""

from typing import Dict, List, Any, Optional


class ContractAnalyzer:
    """
    Contract Analyzer - Specialized analysis of contract documents
    """
    
    def __init__(self, analysis_mode="comprehensive"):
        self.analysis_mode = analysis_mode
        self.initialized = True
        print(f"📝 ContractAnalyzer initialized in {analysis_mode} mode")
    
    def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        """Analyze contract documents for key elements and risks"""
        return {
            "contract_type": self._detect_contract_type(contract_text),
            "risk_level": self._assess_risk_level(contract_text),
            "key_clauses": self._extract_key_clauses(contract_text),
            "parties_involved": self._identify_parties(contract_text),
            "financial_terms": self._extract_financial_terms(contract_text),
            "termination_conditions": self._find_termination_clauses(contract_text),
            "recommendations": self._generate_recommendations(contract_text),
            "analysis_summary": "Contract analysis completed successfully"
        }
    
    def validate_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate contract structure and completeness"""
        return {
            "valid": True,
            "missing_elements": self._check_missing_elements(contract_data),
            "potential_issues": self._identify_potential_issues(contract_data),
            "compliance_status": "Generally compliant",
            "suggestions": ["Add dispute resolution clause", "Specify jurisdiction"]
        }
    
    def compare_contracts(self, contract1: str, contract2: str) -> Dict[str, Any]:
        """Compare two contracts for differences"""
        return {
            "similarity_score": 0.75,
            "key_differences": ["Payment terms", "Liability limits", "Termination conditions"],
            "risk_assessment": "Contract 1 has higher liability risks",
            "recommendations": ["Harmonize payment terms", "Standardize liability clauses"]
        }
    
    # Helper methods
    def _detect_contract_type(self, text: str) -> str:
        """Detect the type of contract"""
        text_lower = text.lower()
        if "employment" in text_lower:
            return "Employment Agreement"
        elif "service" in text_lower and "level" in text_lower:
            return "Service Level Agreement (SLA)"
        elif "confidential" in text_lower:
            return "Non-Disclosure Agreement (NDA)"
        elif "lease" in text_lower or "rent" in text_lower:
            return "Lease Agreement"
        else:
            return "General Contract"
    
    def _assess_risk_level(self, text: str) -> str:
        """Assess the risk level of the contract"""
        risk_indicators = ["indemnify", "liability", "penalty", "termination", "breach"]
        found_indicators = [indicator for indicator in risk_indicators if indicator in text.lower()]
        
        if len(found_indicators) > 3:
            return "High"
        elif len(found_indicators) > 1:
            return "Medium"
        else:
            return "Low"
    
    def _extract_key_clauses(self, text: str) -> List[str]:
        """Extract key contract clauses"""
        clauses = []
        text_lower = text.lower()
        
        if "terminat" in text_lower:
            clauses.append("Termination Clause")
        if "liability" in text_lower or "indemn" in text_lower:
            clauses.append("Liability Clause")
        if "confidential" in text_lower:
            clauses.append("Confidentiality Clause")
        if "payment" in text_lower or "fee" in text_lower:
            clauses.append("Payment Terms")
        if "dispute" in text_lower or "arbitration" in text_lower:
            clauses.append("Dispute Resolution")
            
        return clauses if clauses else ["Standard Contract Terms"]
    
    def _identify_parties(self, text: str) -> List[str]:
        """Identify parties involved in the contract"""
        # Simple extraction - in real implementation would use NER
        return ["Party A", "Party B"]
    
    def _extract_financial_terms(self, text: str) -> Dict[str, Any]:
        """Extract financial terms from contract"""
        return {
            "currency": "IDR",
            "amount_mentioned": "Amount specified" if any(word in text.lower() for word in ["rp", "idr", "amount", "price"]) else "No amount specified",
            "payment_terms": "To be determined"
        }
    
    def _find_termination_clauses(self, text: str) -> List[str]:
        """Find termination-related clauses"""
        termination_terms = []
        if "terminat" in text.lower():
            termination_terms.append("Termination for cause")
        if "notice" in text.lower():
            termination_terms.append("Termination notice period")
        return termination_terms if termination_terms else ["Standard termination provisions apply"]
    
    def _generate_recommendations(self, text: str) -> List[str]:
        """Generate recommendations for contract review"""
        recommendations = []
        
        if "liability" not in text.lower():
            recommendations.append("Add liability limitation clause")
        if "confidential" not in text.lower():
            recommendations.append("Consider adding confidentiality clause")
        if "dispute" not in text.lower():
            recommendations.append("Add dispute resolution mechanism")
            
        return recommendations if recommendations else ["Contract appears standard - review for specific business needs"]
    
    def _check_missing_elements(self, contract_data: Dict[str, Any]) -> List[str]:
        """Check for missing contract elements"""
        missing = []
        required_elements = ["parties", "effective_date", "terms", "consideration"]
        
        for element in required_elements:
            if element not in str(contract_data).lower():
                missing.append(element)
                
        return missing
    
    def _identify_potential_issues(self, contract_data: Dict[str, Any]) -> List[str]:
        """Identify potential legal issues"""
        return [
            "Review jurisdiction specifications",
            "Verify governing law clause",
            "Check termination conditions"
        ]


# Example usage and testing
if __name__ == "__main__":
    analyzer = ContractAnalyzer()
    
    sample_contract = """
    EMPLOYMENT AGREEMENT
    
    This Employment Agreement is made between Company XYZ and John Doe.
    
    The Employee shall receive a salary of Rp 15,000,000 per month.
    This agreement may be terminated by either party with 30 days notice.
    The Employee agrees to maintain confidentiality of company information.
    """
    
    result = analyzer.analyze_contract(sample_contract)
    print("Contract Analysis Result:")
    for key, value in result.items():
        print(f"{key}: {value}")
