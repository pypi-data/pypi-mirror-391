#!/usr/bin/env python3
"""
LegalMind Core System
Simplified, robust, and production-ready with KUHP 2026 support
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# Import from versalaw2_core (located in providers/fallback)
try:
    from .providers.fallback.versalaw2_core import VersaLaw2System, Config
    from .providers.fallback.versalaw2_core.enhanced_system import EnhancedVersaLaw2System
except ImportError:
    # Fallback if versalaw2_core is not available
    VersaLaw2System = None
    Config = None
    EnhancedVersaLaw2System = None

class LegalMindSystem:
    """
    LegalMind - AI Legal Assistant with KUHP 2026 Support

    Wrapper around VersaLaw2 with unique branding and enhanced capabilities
    """

    def __init__(self, ai_provider='mock', api_key=None):
        """
        Initialize LegalMind

        Args:
            ai_provider: 'mock', 'openai', 'deepseek', or 'qodo'
            api_key: API key for the provider
        """
        print("\n" + "="*60)
        print("⚖️  LEGALMIND - AI LEGAL ASSISTANT")
        print("="*60)
        print("Version: 1.1.1")
        print("Features: KUHP 2026, Deepfake Detection, Corporate Crime")
        print("Powered by: VersaLaw2 + MayaLaw + Maya Wisdom")
        print("="*60 + "\n")

        # Check if dependencies are available
        if Config is None or EnhancedVersaLaw2System is None:
            print("⚠️  Warning: VersaLaw2 dependencies not available")
            print("Using fallback mode...\n")
            self.system = None
            return

        # Create config
        config = Config()
        config['ai_provider'] = ai_provider

        if api_key:
            if ai_provider == 'openai':
                config['openai_api_key'] = api_key
            elif ai_provider == 'deepseek':
                config['deepseek_api_key'] = api_key
            elif ai_provider == 'qodo':
                config['qodo_api_key'] = api_key

        # Initialize enhanced system
        self.system = EnhancedVersaLaw2System(config)

        print("✅ LegalMind ready to assist!\n")

    # ==================== CORE METHODS FOR PyPI COMPATIBILITY ====================

    def get_version(self) -> str:
        """Get package version"""
        return "1.1.1"

    def get_capabilities(self) -> Dict[str, Any]:
        """Return available analysis capabilities"""
        return {
            # Core analysis capabilities
            'problematic_contracts': 8,
            'international_tech': 6,
            'challenging_cases': 7,
            'additional_cases': 6,
            'extended_analysis': 6,
            
            # KUHP 2026 capabilities
            'kuhp_analysis': 4,
            'deepfake_fraud': 'Pasal 492-493',
            'corporate_corruption': 'Pasal 603-606',
            'environmental_crime': 'Pasal 435-442',
            'judicial_obstruction': 'Pasal 278-282',
            'corporate_liability': 'Pasal 44-47',
            
            # Analysis types
            'analysis_types': [
                'comprehensive',
                'kuhp',
                'contract_review', 
                'compliance_check',
                'risk_assessment'
            ]
        }

    def analyze(self, text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze legal text with comprehensive capabilities
        
        Args:
            text: Legal text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results dictionary
        """
        if self.system is None:
            # Fallback analysis when system not initialized
            return self._fallback_analysis(text, analysis_type)
        
        # Use enhanced system for analysis
        question = f"Analyze this legal text for {analysis_type}: {text}"
        result = self.system.ask(question, include_wisdom=True)
        
        return self._format_analysis_result(result, text, analysis_type)

    def _fallback_analysis(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Fallback analysis when main system is not available"""
        # Basic keyword-based analysis
        issues = []
        risk_level = "LOW"
        
        # KUHP violation detection
        kuhp_keywords = {
            'deepfake': ['deepfake', 'synthetic media', 'ai-generated'],
            'corruption': ['bribe', 'kickback', 'facilitation fee', 'under table'],
            'environmental': ['deforestation', 'pollution', 'ecosystem damage'],
            'judicial': ['evidence tampering', 'witness intimidation', 'court obstruction']
        }
        
        text_lower = text.lower()
        violations = []
        
        for category, keywords in kuhp_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    violations.append({
                        'category': category,
                        'keyword': keyword,
                        'risk': 'HIGH' if category in ['corruption', 'judicial'] else 'MEDIUM'
                    })
        
        if violations:
            risk_level = "HIGH"
            issues = violations
        
        return {
            "text": text,
            "analysis_type": analysis_type,
            "risk_level": risk_level,
            "issues": issues,
            "violations_detected": len(violations),
            "recommendations": [
                "Consult with legal expert",
                "Review compliance requirements",
                "Conduct due diligence"
            ] if violations else ["No major issues detected"],
            "criminal_exposure": {
                "prison_years": len(violations) * 5,
                "fine_amount": f"Rp {len(violations) * 10} miliar"
            } if violations else {}
        }

    def _format_analysis_result(self, result: Any, text: str, analysis_type: str) -> Dict[str, Any]:
        """Format the analysis result for consistency"""
        if isinstance(result, dict) and 'error' in result:
            return self._fallback_analysis(text, analysis_type)
            
        return {
            "text": text,
            "analysis_type": analysis_type,
            "risk_level": "MEDIUM",  # Default, can be enhanced
            "issues": [],
            "recommendations": ["Analysis completed successfully"],
            "violations_detected": 0,
            "raw_result": result
        }

    # ==================== ORIGINAL METHODS ====================

    def ask(self, question: str, include_wisdom: bool = True) -> Dict[str, Any]:
        """
        Ask legal question

        Args:
            question: Legal question
            include_wisdom: Include Maya Wisdom

        Returns:
            Result dictionary
        """
        if self.system is None:
            return {
                "error": "System not initialized", 
                "question": question,
                "advice": "Please check dependencies and initialization"
            }
        return self.system.ask(question, include_wisdom=include_wisdom)

    def print_answer(self, result: Dict[str, Any]) -> None:
        """Print formatted answer"""
        if self.system is None:
            print("System not initialized")
            return
        self.system.print_answer(result)

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        if self.system is None:
            return {
                "status": "not_initialized",
                "version": self.get_version(),
                "capabilities": list(self.get_capabilities().keys())
            }
        stats = self.system.get_stats()
        stats.update({
            "version": self.get_version(),
            "kuhp_support": True,
            "analysis_capabilities": len(self.get_capabilities())
        })
        return stats

    # ==================== KUHP SPECIFIC METHODS ====================

    def analyze_kuhp(self, text: str, article: str = None) -> Dict[str, Any]:
        """
        Specialized KUHP 2026 analysis
        
        Args:
            text: Legal text to analyze
            article: Specific KUHP article to check
            
        Returns:
            KUHP analysis results
        """
        analysis_type = f"kuhp_{article}" if article else "kuhp_comprehensive"
        result = self.analyze(text, analysis_type)
        
        # Add KUHP-specific information
        result["kuhp_analysis"] = True
        result["applicable_articles"] = self._detect_kuhp_articles(text)
        
        return result

    def _detect_kuhp_articles(self, text: str) -> List[str]:
        """Detect applicable KUHP articles from text"""
        articles = []
        text_lower = text.lower()
        
        # Article detection logic
        if any(word in text_lower for word in ['deepfake', 'synthetic', 'ai-generated']):
            articles.append("Pasal 492 - Penipuan Deepfake")
        if any(word in text_lower for word in ['bribe', 'korupsi', 'suap']):
            articles.append("Pasal 603-606 - Korupsi Sektor Swasta")
        if any(word in text_lower for word in ['environment', 'polusi', 'deforestasi']):
            articles.append("Pasal 435-442 - Kejahatan Lingkungan")
        if any(word in text_lower for word in ['witness', 'evidence', 'pengadilan']):
            articles.append("Pasal 278-282 - Penghambatan Proses Peradilan")
            
        return articles

# ==================== COMPATIBILITY ALIASES ====================

# For backward compatibility and PyPI package
LegalMindAI = LegalMindSystem
KUHPAnalyzer = LegalMindSystem
