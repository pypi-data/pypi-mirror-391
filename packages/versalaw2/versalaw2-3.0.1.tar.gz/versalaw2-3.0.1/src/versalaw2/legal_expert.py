"""
Legal Expert System for VersaLaw2
Provides expert legal knowledge and insights
"""

from typing import Dict, List, Any, Optional

class LegalExpertSystem:
    """Expert system for legal knowledge and insights"""
    
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge_base()
        self.expert_areas = [
            "hukum kontrak", "hukum teknologi", "cyber law",
            "perlindungan data", "hukum internasional", "hukum bisnis"
        ]
        print("🧠 Legal Expert System initialized!")
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize the legal knowledge base"""
        return {
            "hukum_kontrak": {
                "prinsip_dasar": ["Kesepakatan", "Itikad baik", "Kausalitas", "Kepatutan"],
                "syarat_sah": ["Kompeten", "Kesepakatan", "Objek tertentu", "Sebab yang halal"],
                "klausa_penting": ["Force majeure", "Terminasi", "Ganti rugi", "Yurisdiksi"]
            },
            "cyber_law": {
                "uu_ite": ["Pasal 27", "Pasal 28", "Pasal 29", "Pasal 30", "Pasal 31"],
                "perlindungan_data": ["Konsent", "Purpose limitation", "Data minimization", "Security"]
            },
            "hukum_teknologi": {
                "kontrak_digital": ["E-signature", "Digital authentication", "Smart contracts"],
                "ai_regulation": ["Algorithm transparency", "Bias prevention", "Human oversight"]
            }
        }
    
    def get_legal_advice(self, question: str) -> Dict[str, Any]:
        """Get expert legal advice for a question"""
        
        area = self._identify_legal_area(question)
        advice = self._generate_advice(question, area)
        
        return {
            "question": question,
            "legal_area": area,
            "expert_advice": advice,
            "relevant_regulations": self._get_relevant_regulations(area),
            "risk_assessment": self._assess_legal_risk(question)
        }
    
    def query_knowledge_base(self, topic: str) -> Dict[str, Any]:
        """Query the legal knowledge base"""
        topic_lower = topic.lower()
        
        for area, knowledge in self.knowledge_base.items():
            if topic_lower in area or any(topic_lower in key for key in knowledge.keys()):
                return {
                    "topic": topic,
                    "area": area,
                    "knowledge": knowledge
                }
        
        return {
            "topic": topic,
            "area": "general",
            "knowledge": self.knowledge_base
        }
    
    def _identify_legal_area(self, question: str) -> str:
        """Identify the legal area of a question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["kontrak", "perjanjian", "klausa"]):
            return "hukum_kontrak"
        elif any(word in question_lower for word in ["digital", "teknologi", "ai", "cyber"]):
            return "hukum_teknologi"
        elif any(word in question_lower for word in ["data", "privasi", "perlindungan"]):
            return "cyber_law"
        else:
            return "hukum_umum"
    
    def _generate_advice(self, question: str, area: str) -> List[str]:
        """Generate expert advice based on legal area"""
        advice_map = {
            "hukum_kontrak": [
                "Pastikan semua syarat sah kontrak terpenuhi",
                "Perhatikan klausa force majeure dan terminasi",
                "Tinjau yurisdiksi dan hukum yang berlaku"
            ],
            "hukum_teknologi": [
                "Perhatikan regulasi khusus teknologi",
                "Tinjau aspek keamanan siber",
                "Pastikan compliance dengan UU ITE"
            ],
            "cyber_law": [
                "Implementasi perlindungan data pribadi",
                "Patuhi ketentuan UU PDP",
                "Perhatikan aspek跨境 data transfer"
            ]
        }
        
        return advice_map.get(area, [
            "Konsultasikan dengan ahli hukum terkait",
            "Tinjau dokumen secara komprehensif",
            "Pertimbangkan aspek preventif"
        ])
    
    def _get_relevant_regulations(self, area: str) -> List[str]:
        """Get relevant regulations for legal area"""
        regulations = {
            "hukum_kontrak": ["KUHPerdata Pasal 1234", "KUHPerdata Pasal 1320", "KUHPerdata Pasal 1338"],
            "hukum_teknologi": ["UU ITE No. 11/2008", "UU PDP No. 27/2022", "Peraturan Teknis Kemenkominfo"],
            "cyber_law": ["UU ITE Pasal 27-31", "UU PDP", "ISO 27001"]
        }
        
        return regulations.get(area, ["Peraturan perundang-undangan terkait"])
    
    def _assess_legal_risk(self, question: str) -> str:
        """Assess legal risk level"""
        risk_keywords = ["sengketa", "gugatan", "wanprestasi", "pidana", "denda"]
        
        if any(keyword in question.lower() for keyword in risk_keywords):
            return "high"
        else:
            return "medium"
