"""
VersaLaw2 - Advanced Indonesian Legal AI Assistant
with Ghost Contract Analysis & 100+ Expert Study Cases
"""

__version__ = "3.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core VersaLaw2 modules
from .core import EnhancedLegalClassifier
from .contract_analyzer import GhostContractAnalyzer
from .legal_expert import LegalExpertSystem
from .enhanced_database import LegalDatabaseIntegrator, EnhancedLegalClassifierWithDB

# Integrated Legalmind-AI modules (yang bekerja)
try:
    from .unified_analysis_engine import UnifiedAnalysisEngine
    UNIFIED_AVAILABLE = True
except ImportError as e:
    UNIFIED_AVAILABLE = False
    UnifiedAnalysisEngine = None
    print(f"⚠️ UnifiedAnalysisEngine not available: {e}")

try:
    from .enhanced_search import EnhancedSearchEngine
    SEARCH_AVAILABLE = True  
except ImportError as e:
    SEARCH_AVAILABLE = False
    EnhancedSearchEngine = None
    print(f"⚠️ EnhancedSearchEngine not available: {e}")

try:
    from .ai_anhancement import AIEnhancement
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    AIEnhancement = None
    print(f"⚠️ AIEnhancement not available: {e}")

try:
    from .prompt_templates import PromptTemplates
    PROMPTS_AVAILABLE = True
except ImportError as e:
    PROMPTS_AVAILABLE = False
    PromptTemplates = None
    print(f"⚠️ PromptTemplates not available: {e}")

try:
    from .config import LegalMindConfig
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    LegalMindConfig = None
    print(f"⚠️ LegalMindConfig not available: {e}")

__all__ = [
    # Core VersaLaw2
    "EnhancedLegalClassifier",
    "GhostContractAnalyzer",
    "LegalExpertSystem",
    "LegalDatabaseIntegrator",
    "EnhancedLegalClassifierWithDB",
    
    # Integrated Legalmind-AI (conditional)
    "UnifiedAnalysisEngine",
    "EnhancedSearchEngine", 
    "AIEnhancement",
    "PromptTemplates",
    "LegalMindConfig",
    
    # Availability flags
    "UNIFIED_AVAILABLE",
    "SEARCH_AVAILABLE",
    "AI_AVAILABLE", 
    "PROMPTS_AVAILABLE",
    "CONFIG_AVAILABLE"
]
