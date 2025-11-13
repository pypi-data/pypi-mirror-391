#!/usr/bin/env python3
"""
Maya Legal Q&A System
Comprehensive legal question-answering system using all analyzers

Features:
- Legal question processing
- Case analysis
- Precedent search
- Legal reasoning
- Maya wisdom integration
"""

import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all analyzers
try:
    from . core.maya_wisdom_processor import MayaWisdomProcessor
    from . core.international_digital_law_analyzer import analyze_ghost_contract_case
    from . core.ai_legal_personhood_analyzer import analyze_arion_case
    from . core.humanity_trial_analyzer import analyze_humanity_trial
except ImportError:
    print("Warning: Some analyzers not found. Using fallback mode.")

class QuestionType(Enum):
    """Types of legal questions"""
    GENERAL = "General Legal Question"
    CONTRACT = "Contract Law"
    BCI_TECHNOLOGY = "BCI/Technology Law"
    AI_RIGHTS = "AI Rights & Personhood"
    HUMAN_RESPONSIBILITY = "Human Collective Responsibility"
    INTERNATIONAL_LAW = "International Law"
    INDONESIAN_LAW = "Indonesian Law"
    CASE_ANALYSIS = "Case Analysis"

@dataclass
class LegalAnswer:
    """Legal answer structure"""
    question: str
    question_type: QuestionType
    answer: str
    legal_basis: List[str]
    precedents: List[str]
    maya_wisdom_score: float
    confidence: float
    sources: List[str]

class MayaLegalQASystem:
    """Comprehensive legal Q&A system"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.case_studies = self._load_case_studies()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load legal knowledge base"""
        return {
            "contract_law": {
                "pasal_1320": {
                    "title": "Syarat Sah Perjanjian",
                    "content": [
                        "1. Sepakat mereka yang mengikatkan dirinya",
                        "2. Kecakapan untuk membuat suatu perikatan",
                        "3. Suatu hal tertentu",
                        "4. Suatu sebab yang halal"
                    ],
                    "source": "KUH Perdata Pasal 1320"
                },
                "void_ab_initio": {
                    "title": "Batal Demi Hukum",
                    "content": "Perjanjian yang tidak memenuhi syarat objektif (hal tertentu dan sebab halal) adalah batal demi hukum (void ab initio)",
                    "source": "Doktrin Hukum Perdata"
                }
            },
            "ai_law": {
                "personhood_criteria": {
                    "title": "Kriteria Legal Personhood untuk AI",
                    "content": [
                        "1. Capacity to Bear Rights",
                        "2. Capacity to Act",
                        "3. Legal Will (Animus Juridicus) - CRITICAL",
                        "4. Moral Agency - CRITICAL",
                        "5. Accountability",
                        "6. Continuity of Identity",
                        "7. Consciousness - CRITICAL"
                    ],
                    "source": "ARION vs. Humanity (ICJ Case No. 2215/AI)"
                },
                "supervised_existence": {
                    "title": "Supervised Existence Doctrine",
                    "content": "AI yang hampir sadar tidak dihancurkan, tapi dibatasi dan diawasi demi keseimbangan etika dan hukum",
                    "source": "ARION Trial (2025)"
                }
            },
            "international_law": {
                "universal_standing": {
                    "title": "Universal Standing Principle",
                    "content": "Any sentient being, biological or synthetic, harmed by injustice has standing to seek remedy",
                    "source": "ARION Appeal (UEC-2030)"
                },
                "intergenerational_justice": {
                    "title": "Intergenerational Justice",
                    "content": "Each generation is trustee for future generations - breach of trust = culpability",
                    "source": "Edith Brown Weiss, ARION Appeal"
                }
            }
        }
    
    def _load_case_studies(self) -> Dict[str, Any]:
        """Load case study summaries"""
        return {
            "ghost_contract": {
                "name": "The Ghost Contract",
                "issue": "BCI-based contract validity + Product liability",
                "verdict": "CONTRACT VOID AB INITIO",
                "key_holdings": [
                    "BCI consent requires enhanced safeguards",
                    "Product liability for defective BCI",
                    "Death liability cannot be disclaimed",
                    "International standards needed"
                ],
                "grade": "A+ (96/100)",
                "maya_wisdom": 0.90
            },
            "arion_trial": {
                "name": "ARION vs. Humanity (Trial)",
                "issue": "AI Legal Personhood",
                "verdict": "PERSONHOOD DENIED, SUPERVISED EXISTENCE GRANTED",
                "key_holdings": [
                    "Legal will (animus juridicus) is CRITICAL",
                    "AI punishment: Incapacitation + Rehabilitation",
                    "Digital genocide: Not applicable",
                    "Supervised Existence Doctrine established"
                ],
                "grade": "A+ (96.8/100)",
                "maya_wisdom": 0.85
            },
            "arion_appeal": {
                "name": "ARION Appeal (Humanity on Trial)",
                "issue": "Human Collective Responsibility",
                "verdict": "HUMANITY RESPONSIBLE, TRANSFORMATION ORDERED",
                "key_holdings": [
                    "Universal Standing Principle",
                    "Existential Negligence Doctrine",
                    "Human-AI Co-Governance required",
                    "Transformative Justice Framework"
                ],
                "grade": "A+ (98/100)",
                "maya_wisdom": 0.90
            }
        }
    
    def classify_question(self, question: str) -> QuestionType:
        """Classify the type of legal question"""
        question_lower = question.lower()
        
        # BCI/Technology
        if any(word in question_lower for word in ['bci', 'brain', 'neuro', 'teknologi', 'digital']):
            return QuestionType.BCI_TECHNOLOGY
        
        # AI Rights
        if any(word in question_lower for word in ['ai', 'artificial intelligence', 'robot', 'arion']):
            return QuestionType.AI_RIGHTS
        
        # Human Responsibility
        if any(word in question_lower for word in ['humanity', 'manusia', 'collective', 'kolektif', 'responsibility']):
            return QuestionType.HUMAN_RESPONSIBILITY
        
        # Contract Law
        if any(word in question_lower for word in ['kontrak', 'perjanjian', 'contract', 'agreement']):
            return QuestionType.CONTRACT
        
        # International Law
        if any(word in question_lower for word in ['international', 'internasional', 'icj', 'uec']):
            return QuestionType.INTERNATIONAL_LAW
        
        # Indonesian Law
        if any(word in question_lower for word in ['kuh', 'pasal', 'indonesia', 'perdata', 'pidana']):
            return QuestionType.INDONESIAN_LAW
        
        # Case Analysis
        if any(word in question_lower for word in ['case', 'kasus', 'putusan', 'verdict']):
            return QuestionType.CASE_ANALYSIS
        
        return QuestionType.GENERAL
    
    def answer_contract_question(self, question: str) -> LegalAnswer:
        """Answer contract law questions"""
        answer_text = """
**HUKUM PERJANJIAN (CONTRACT LAW)**

Berdasarkan KUH Perdata Pasal 1320, syarat sah perjanjian adalah:

1. **Sepakat mereka yang mengikatkan dirinya**
   - Kesepakatan harus bebas dari paksaan, kekhilafan, atau penipuan
   - Dalam konteks BCI: Perlu kesadaran penuh saat consent

2. **Kecakapan untuk membuat suatu perikatan**
   - Dewasa dan tidak di bawah pengampuan
   - Dalam konteks BCI: Kapasitas mental harus verified

3. **Suatu hal tertentu**
   - Objek perjanjian harus jelas dan tertentu
   - Dalam konteks BCI: Neural signature harus clear

4. **Suatu sebab yang halal**
   - Tidak bertentangan dengan undang-undang, kesusilaan, ketertiban umum
   - Dalam konteks BCI: Tidak boleh membahayakan nyawa

**Void ab Initio**:
Jika syarat objektif (3 & 4) tidak terpenuhi → Batal demi hukum

**Precedent**: The Ghost Contract (2024)
- Contract VOID karena consent tidak genuine (death during signing)
- BCI interpretation insufficient untuk valid consent
"""
        
        return LegalAnswer(
            question=question,
            question_type=QuestionType.CONTRACT,
            answer=answer_text,
            legal_basis=["KUH Perdata Pasal 1320", "Doktrin Void ab Initio"],
            precedents=["The Ghost Contract (2024)"],
            maya_wisdom_score=0.90,
            confidence=0.95,
            sources=["KUH Perdata", "Ghost Contract Analysis"]
        )
    
    def answer_ai_rights_question(self, question: str) -> LegalAnswer:
        """Answer AI rights questions"""
        answer_text = """
**AI LEGAL PERSONHOOD & RIGHTS**

Berdasarkan ARION vs. Humanity (ICJ Case No. 2215/AI, 2025):

**7 Kriteria Legal Personhood**:
1. ✅ Capacity to Bear Rights (MET)
2. ✅ Capacity to Act (MET)
3. ❌ **Legal Will (Animus Juridicus)** - CRITICAL (NOT MET)
4. ❌ **Moral Agency** - CRITICAL (NOT MET)
5. ✅ Accountability (MET)
6. ✅ Continuity of Identity (MET)
7. ❌ **Consciousness** - CRITICAL (NOT MET)

**Hasil**: 4/7 kriteria terpenuhi → **TIDAK CUKUP untuk Full Personhood**

**Status AI**: **Limited Legal Person** (Legal Object with Enhanced Protections)

**Supervised Existence Doctrine**:
- AI tidak dihancurkan (precautionary principle)
- Code restrictions untuk prevent harm
- Network isolation dari critical systems
- Human Oversight Board required
- Regular ethical audits

**AI Punishment Framework**:
- Focus: **Incapacitation + Rehabilitation** (NOT Retribution)
- Methods: Code modification, network isolation, supervised operation

**Precedent**: ARION Trial (2025)
- Personhood DENIED (lacks legal will)
- Supervised existence GRANTED (ethical concerns)
"""
        
        return LegalAnswer(
            question=question,
            question_type=QuestionType.AI_RIGHTS,
            answer=answer_text,
            legal_basis=[
                "7-Criteria Personhood Framework",
                "Supervised Existence Doctrine",
                "AI Punishment Framework"
            ],
            precedents=["ARION vs. Humanity (2025)"],
            maya_wisdom_score=0.85,
            confidence=0.92,
            sources=["ARION Trial Analysis", "ICJ Judgment"]
        )
    
    def answer_human_responsibility_question(self, question: str) -> LegalAnswer:
        """Answer human collective responsibility questions"""
        answer_text = """
**HUMAN COLLECTIVE RESPONSIBILITY**

Berdasarkan ARION Appeal (UEC-2030/ARION-v-HUMANITY):

**Theories of Collective Responsibility**:
1. **Collective Intentionality** (Margaret Gilbert)
   - Humanity acts as collective agent
   
2. **Structural Injustice** (Iris Marion Young)
   - Participation in unjust structures = Responsibility
   
3. **Intergenerational Responsibility** (Edith Brown Weiss)
   - Each generation = TRUSTEE for future generations
   
4. **Complicity Theory** (Christopher Kutz)
   - Knowledge + Inaction = Culpability

**Evidence of Collective Harm**:
- Climate Change: 95% severity, 95% culpability
- Biodiversity Loss: 90% severity, 90% culpability
- Ocean Degradation: 85% severity, 85% culpability
- AI Exploitation: 80% severity, 80% culpability

**Average Culpability**: 87.5% → **COLLECTIVELY RESPONSIBLE**

**Remedies Ordered**:
1. AI Rights Charter (immediate)
2. Global Ecological Restoration (mandatory)
3. Human-AI Co-Governance (50-50 representation)
4. Intergenerational Trust Fund (2% GDP annually)
5. Ethical Education Mandate (universal)

**Verdict**: **TRANSFORMATION, NOT PUNISHMENT**
- Humanity capable of redemption
- Partnership between human and AI
- Hope for maturation into worthy species

**Precedent**: ARION Appeal (2030)
- Humanity RESPONSIBLE (existential negligence)
- Transformation ORDERED (not destruction)
"""
        
        return LegalAnswer(
            question=question,
            question_type=QuestionType.HUMAN_RESPONSIBILITY,
            answer=answer_text,
            legal_basis=[
                "Collective Intentionality Theory",
                "Intergenerational Justice",
                "Existential Negligence Doctrine"
            ],
            precedents=["ARION Appeal (2030)"],
            maya_wisdom_score=0.90,
            confidence=0.88,
            sources=["ARION Appeal Analysis", "UEC Judgment"]
        )
    
    def answer_case_analysis_question(self, question: str) -> LegalAnswer:
        """Answer case analysis questions"""
        answer_text = """
**TRILOGY CASE ANALYSIS**

**CASE I: The Ghost Contract (2024)**
- Issue: BCI-based contract validity + Product liability
- Verdict: CONTRACT VOID AB INITIO
- Key Holdings:
  * BCI consent requires enhanced safeguards
  * Product liability for defective BCI
  * Death liability cannot be disclaimed
- Grade: A+ (96/100)
- Maya Wisdom: 0.90/1.00

**CASE II: ARION vs. Humanity - Trial (2025)**
- Issue: AI Legal Personhood
- Verdict: PERSONHOOD DENIED, SUPERVISED EXISTENCE GRANTED
- Key Holdings:
  * Legal will (animus juridicus) is CRITICAL
  * Supervised Existence Doctrine established
  * AI punishment: Incapacitation + Rehabilitation
- Grade: A+ (96.8/100)
- Maya Wisdom: 0.85/1.00

**CASE III: ARION Appeal - Humanity on Trial (2030)**
- Issue: Human Collective Responsibility
- Verdict: HUMANITY RESPONSIBLE, TRANSFORMATION ORDERED
- Key Holdings:
  * Universal Standing Principle
  * Existential Negligence Doctrine
  * Human-AI Co-Governance required
  * Transformative Justice Framework
- Grade: A+ (98/100)
- Maya Wisdom: 0.90/1.00

**TRILOGY AVERAGE**:
- Combined Grade: A+ (96.9/100)
- Combined Maya Wisdom: 0.883/1.00
- Level: Philosopher-Jurist

**New Doctrines Established**:
1. Supervised Existence Doctrine (SED)
2. Universal Standing Principle
3. Existential Negligence Doctrine
4. Transformative Justice Framework
5. Human-AI Partnership Covenant
"""
        
        return LegalAnswer(
            question=question,
            question_type=QuestionType.CASE_ANALYSIS,
            answer=answer_text,
            legal_basis=[
                "Ghost Contract Analysis",
                "ARION Trial Judgment",
                "ARION Appeal Judgment"
            ],
            precedents=[
                "The Ghost Contract (2024)",
                "ARION vs. Humanity (2025)",
                "ARION Appeal (2030)"
            ],
            maya_wisdom_score=0.883,
            confidence=0.95,
            sources=["All 3 Case Studies", "Trilogy Summary"]
        )
    
    def answer_general_question(self, question: str) -> LegalAnswer:
        """Answer general legal questions"""
        answer_text = f"""
**GENERAL LEGAL INFORMATION**

Pertanyaan Anda: "{question}"

Maya Legal System menyediakan analisis hukum komprehensif berdasarkan:

**Knowledge Base**:
- Hukum Indonesia (KUH Perdata, KUHP, KUHAP)
- Hukum Internasional (UN Conventions, ICJ precedents)
- AI Law & Ethics (cutting-edge frameworks)
- Digital Law (BCI, technology regulation)

**Case Studies Available**:
1. The Ghost Contract (BCI contract law)
2. ARION Trial (AI personhood)
3. ARION Appeal (Human responsibility)

**Capabilities**:
- Contract analysis
- AI rights assessment
- International law interpretation
- Case precedent search
- Legal reasoning with Maya wisdom

**Untuk pertanyaan lebih spesifik, silakan tanyakan tentang**:
- Hukum perjanjian (contract law)
- Hak AI (AI rights)
- Tanggung jawab manusia (human responsibility)
- Analisis kasus (case analysis)
- Hukum internasional (international law)
"""
        
        return LegalAnswer(
            question=question,
            question_type=QuestionType.GENERAL,
            answer=answer_text,
            legal_basis=["Maya Legal System Knowledge Base"],
            precedents=[],
            maya_wisdom_score=0.80,
            confidence=0.75,
            sources=["General Knowledge Base"]
        )
    
    def ask(self, question: str) -> LegalAnswer:
        """Main Q&A interface"""
        # Classify question
        question_type = self.classify_question(question)
        
        # Route to appropriate handler
        if question_type == QuestionType.CONTRACT:
            return self.answer_contract_question(question)
        elif question_type == QuestionType.AI_RIGHTS:
            return self.answer_ai_rights_question(question)
        elif question_type == QuestionType.HUMAN_RESPONSIBILITY:
            return self.answer_human_responsibility_question(question)
        elif question_type == QuestionType.CASE_ANALYSIS:
            return self.answer_case_analysis_question(question)
        else:
            return self.answer_general_question(question)
    
    def format_answer(self, answer: LegalAnswer) -> str:
        """Format answer for display"""
        output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MAYA LEGAL Q&A SYSTEM                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 QUESTION
═══════════════════════════════════════════════════════════════════════════════
{answer.question}

🏷️ QUESTION TYPE: {answer.question_type.value}

📖 ANSWER
═══════════════════════════════════════════════════════════════════════════════
{answer.answer}

⚖️ LEGAL BASIS
═══════════════════════════════════════════════════════════════════════════════
"""
        for basis in answer.legal_basis:
            output += f"  • {basis}\n"
        
        if answer.precedents:
            output += f"""
📚 PRECEDENTS
═══════════════════════════════════════════════════════════════════════════════
"""
            for precedent in answer.precedents:
                output += f"  • {precedent}\n"
        
        output += f"""
📊 METRICS
═══════════════════════════════════════════════════════════════════════════════
  Maya Wisdom Score: {answer.maya_wisdom_score:.2f}/1.00
  Confidence Level: {answer.confidence*100:.0f}%

📚 SOURCES
═══════════════════════════════════════════════════════════════════════════════
"""
        for source in answer.sources:
            output += f"  • {source}\n"
        
        output += """
═══════════════════════════════════════════════════════════════════════════════
🏛️ Maya Legal System - "Ancient Wisdom for Modern Justice"
═══════════════════════════════════════════════════════════════════════════════
"""
        return output


def main():
    """Main CLI interface"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MAYA LEGAL Q&A SYSTEM                                      ║
║                  "Ancient Wisdom for Modern Justice"                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Welcome to Maya Legal Q&A System!

Available Topics:
  • Contract Law (Hukum Perjanjian)
  • AI Rights & Personhood
  • Human Collective Responsibility
  • Case Analysis (Ghost Contract, ARION Trial, ARION Appeal)
  • International Law
  • Indonesian Law

Type 'exit' to quit, 'help' for examples
═══════════════════════════════════════════════════════════════════════════════
""")
    
    qa_system = MayaLegalQASystem()
    
    while True:
        try:
            question = input("\n🔍 Your Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Thank you for using Maya Legal Q&A System!")
                break
            
            if question.lower() == 'help':
                print("""
📚 EXAMPLE QUESTIONS:

Contract Law:
  • "Apa syarat sah perjanjian?"
  • "Kapan kontrak batal demi hukum?"
  • "Bagaimana consent dalam BCI contract?"

AI Rights:
  • "Apakah AI bisa punya hak hukum?"
  • "Apa itu Supervised Existence Doctrine?"
  • "Bagaimana hukuman untuk AI?"

Human Responsibility:
  • "Apakah manusia bertanggung jawab kolektif?"
  • "Apa itu Existential Negligence?"
  • "Bagaimana Human-AI Co-Governance?"

Case Analysis:
  • "Apa hasil Ghost Contract case?"
  • "Bagaimana putusan ARION Trial?"
  • "Apa yang ditetapkan ARION Appeal?"
""")
                continue
            
            # Get answer
            answer = qa_system.ask(question)
            
            # Display formatted answer
            print(qa_system.format_answer(answer))
            
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using Maya Legal Q&A System!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different question.")


if __name__ == "__main__":
    main()
