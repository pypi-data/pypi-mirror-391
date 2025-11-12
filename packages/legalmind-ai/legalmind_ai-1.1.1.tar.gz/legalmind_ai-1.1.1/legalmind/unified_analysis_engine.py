# legalmind/unified_analysis_engine.py
"""
UNIFIED ANALYSIS ENGINE - Integrasi semua existing analyzers
"""
import sys
from pathlib import Path
from importlib.resources import files
import importlib.util

class UnifiedAnalysisEngine:
    def __init__(self):
        self.analyzers = {}
        self.load_existing_analyzers()
    
    def load_existing_analyzers(self):
        """Load semua existing analyze scripts secara dynamic"""
        print("🚀 LOADING EXISTING ANALYSIS CAPABILITIES...")
        
        analyzer_files = {
            "problematic_contracts": "analyze_real_problematic_contracts.py",
            "international_tech": "analyze_international_tech_cases.py", 
            "challenging_cases": "analyze_challenging_cases.py",
            "additional_cases": "analyze_5_additional_cases.py",
            "extended_analysis": "analyze_5_additional_cases_part2.py"
        }
        
        for analyzer_name, filename in analyzer_files.items():
            try:
                file_path = files('legalmind.study_cases') / filename
                if file_path.exists():
                    # Extract analysis capabilities tanpa execute
                    capabilities = self.analyze_script_capabilities(file_path)
                    self.analyzers[analyzer_name] = {
                        "file": filename,
                        "capabilities": capabilities,
                        "description": self.get_analyzer_description(capabilities)
                    }
                    print(f"✅ Loaded {analyzer_name}: {len(capabilities)} capabilities")
                    
            except Exception as e:
                print(f"⚠️  Could not load {analyzer_name}: {e}")
    
    def analyze_script_capabilities(self, file_path: Path) -> list:
        """Analyze capabilities dari script tanpa execute"""
        content = file_path.read_text(encoding='utf-8')
        capabilities = []
        
        # Detect analysis functions
        functions = self.extract_functions(content)
        for func in functions:
            if any(keyword in func.lower() for keyword in ['analyze', 'process', 'evaluate', 'assess']):
                capabilities.append(f"function:{func}")
        
        # Detect classes
        classes = self.extract_classes(content)
        for cls in classes:
            capabilities.append(f"class:{cls}")
        
        # Detect case studies
        cases = self.extract_case_studies(content)
        capabilities.extend([f"case:{case}" for case in cases])
        
        return capabilities
    
    def extract_functions(self, content: str) -> list:
        """Extract function names dari content"""
        import re
        return re.findall(r'def\s+(\w+)', content)
    
    def extract_classes(self, content: str) -> list:
        """Extract class names dari content"""
        import re
        return re.findall(r'class\s+(\w+)', content)
    
    def extract_case_studies(self, content: str) -> list:
        """Extract case studies dari content"""
        cases = []
        # Look for case patterns
        if "hambantota" in content.lower():
            cases.append("Sri Lanka Hambantota Port")
        if "pakistan" in content.lower() and "cpec" in content.lower():
            cases.append("Pakistan CPEC Projects") 
        if "1mdb" in content.lower() or "malaysia" in content.lower():
            cases.append("Malaysia 1MDB")
        if "international" in content.lower():
            cases.append("International Tech Cases")
        if "challenging" in content.lower():
            cases.append("Challenging Legal Cases")
        
        return cases
    
    def get_analyzer_description(self, capabilities: list) -> str:
        """Generate description berdasarkan capabilities"""
        if any("hambantota" in str(cap).lower() for cap in capabilities):
            return "International Contract Debt Trap Analysis"
        elif any("international" in str(cap).lower() for cap in capabilities):
            return "International Technology Law Analysis"
        elif any("challenging" in str(cap).lower() for cap in capabilities):
            return "Complex Legal Case Analysis"
        else:
            return "General Legal Analysis"
    
    def get_analysis_recommendation(self, query: str) -> dict:
        """Rekomendasi analyzer terbaik berdasarkan query"""
        query_lower = query.lower()
        recommendations = []
        
        for analyzer_name, analyzer_info in self.analyzers.items():
            score = 0
            
            # Score berdasarkan keyword matching
            keywords = {
                "problematic_contracts": ["contract", "problem", "debt", "trap", "hambantota", "cpec", "1mdb", "sovereignty", "port", "agreement"],
                "international_tech": ["international", "tech", "technology", "global", "cross-border", "ftx", "crypto", "cryptocurrency", "openai", "tesla", "autopilot"],
                "challenging_cases": ["challenging", "complex", "difficult", "complicated", "ai", "artificial intelligence", "space", "gene", "copyright", "content"],
                "additional_cases": ["general", "multiple", "various", "diverse", "google", "antitrust", "meta", "cambridge"],
                "extended_analysis": ["uber", "binance", "shell", "climate", "driver", "violation"]
            }
            
            if analyzer_name in keywords:
                for keyword in keywords[analyzer_name]:
                    if keyword in query_lower:
                        score += 1
            
            if score > 0:
                recommendations.append({
                    "analyzer": analyzer_name,
                    "score": score,
                    "description": analyzer_info["description"],
                    "file": analyzer_info["file"]
                })
        
        return sorted(recommendations, key=lambda x: x["score"], reverse=True)
    
    def analyze_with_best_fit(self, query: str, context: str = "") -> dict:
        """Analisis dengan rekomendasi terbaik"""
        recommendations = self.get_analysis_recommendation(query)
        
        if not recommendations:
            return {"error": "No suitable analyzer found", "available_analyzers": list(self.analyzers.keys())}
        
        best_match = recommendations[0]
        
        return {
            "recommended_analyzer": best_match["analyzer"],
            "confidence_score": best_match["score"] / 5.0,  # Normalize to 0-1
            "analyzer_file": best_match["file"],
            "description": best_match["description"],
            "all_recommendations": recommendations,
            "suggested_approach": self.get_suggested_approach(best_match["analyzer"], query)
        }
    
    def get_suggested_approach(self, analyzer_name: str, query: str) -> str:
        """Dapatkan suggested approach berdasarkan analyzer"""
        approaches = {
            "problematic_contracts": "Focus on debt trap analysis, sovereignty issues, and international contract risks",
            "international_tech": "Analyze technology transfer, IP rights, and cross-border compliance",
            "challenging_cases": "Use complex legal reasoning and multi-jurisdictional analysis", 
            "additional_cases": "Apply general legal analysis with multiple case comparisons"
        }
        
        return approaches.get(analyzer_name, "General legal analysis approach")
    
    def list_all_capabilities(self) -> dict:
        """List semua capabilities yang tersedia"""
        return {
            "total_analyzers": len(self.analyzers),
            "analyzers": self.analyzers,
            "total_capabilities": sum(len(analyzer["capabilities"]) for analyzer in self.analyzers.values())
        }
