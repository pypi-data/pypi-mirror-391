#!/usr/bin/env python3
"""
LegalMind Core System
Simplified, robust, and production-ready
"""

import sys
from pathlib import Path

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
    LegalMind - AI Legal Assistant
    
    Wrapper around VersaLaw2 with unique branding
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
        print("Version: 1.0.0")
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
    
    def ask(self, question, include_wisdom=True):
        """
        Ask legal question
        
        Args:
            question: Legal question
            include_wisdom: Include Maya Wisdom
        
        Returns:
            Result dictionary
        """
        if self.system is None:
            return {"error": "System not initialized", "question": question}
        return self.system.ask(question, include_wisdom=include_wisdom)
    
    def print_answer(self, result):
        """Print formatted answer"""
        if self.system is None:
            print("System not initialized")
            return
        self.system.print_answer(result)
    
    def get_stats(self):
        """Get system statistics"""
        if self.system is None:
            return {"status": "not_initialized"}
        return self.system.get_stats()
