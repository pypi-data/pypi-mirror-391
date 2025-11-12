#!/usr/bin/env python3
"""
KUHP 2026 ANALYZER - Specialized analyzer for KUHP Baru 2026
Effective: 2 Januari 2026
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

class KUHP2026Analyzer:
    """
    Analyzer khusus untuk KUHP Baru 2026 (UU No. 1 Tahun 2023)
    """
    
    def __init__(self):
        self.effective_date = "2026-01-02"
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load KUHP 2026 knowledge base"""
        self.articles = {
            # Obstruction of Justice
            "278": {
                "title": "Obstruction of Judicial Process",
                "description": "Menyesatkan proses peradilan dengan pemalsuan bukti, saksi palsu, perusakan bukti, intimidasi",
                "max_prison": 8,
                "fine_category": "VI",
                "fine_amount": "Rp 500 juta - Rp 3 miliar",
                "keywords": ["evidence", "bukti", "witness", "saksi", "testimony", "kesaksian", "falsif", "palsu", "intimidat", "destroy", "rusak", "hilang"]
            },
            "280": {
                "title": "Obstruction of Court Facilities",
                "description": "Menghalangi, mengganggu, atau mengintimidasi petugas pengadilan",
                "max_prison": 5,
                "fine_category": "V",
                "fine_amount": "Rp 100 juta - Rp 500 juta",
                "keywords": ["court", "pengadilan", "staff", "petugas", "intimidat", "halangi", "ganggu"]
            },
            "282": {
                "title": "Witness/Victim Protection Violation",
                "description": "Intimidasi, ancaman, atau kekerasan terhadap saksi/korban yang dilindungi",
                "max_prison": 10,
                "fine_category": "VII",
                "fine_amount": "Rp 3 miliar - Rp 10 miliar",
                "keywords": ["witness", "saksi", "victim", "korban", "protect", "lindung", "intimidat", "ancam", "threat"]
            },
            
            # Environmental Crimes
            "435": {
                "title": "Pollution Causing Environmental Damage",
                "description": "Pencemaran lingkungan yang mengakibatkan kerusakan lingkungan hidup",
                "max_prison": 15,
                "fine_category": "VIII",
                "fine_amount": "Rp 10 miliar - Rp 100 miliar",
                "keywords": ["pollut", "cemar", "environment", "lingkungan", "damage", "rusak", "waste", "limbah", "effluent", "discharge", "buang"]
            },
            "437": {
                "title": "Destruction of Protected Ecosystems",
                "description": "Merusak ekosistem yang dilindungi undang-undang",
                "max_prison": 12,
                "fine_category": "VII",
                "fine_amount": "Rp 3 miliar - Rp 10 miliar",
                "keywords": ["ecosystem", "ekosistem", "forest", "hutan", "peatland", "gambut", "conservation", "konservasi", "habitat", "protect", "lindung", "burn", "bakar"]
            },
            "439": {
                "title": "Endangering Public Health via Pollution",
                "description": "Pencemaran yang membahayakan kesehatan masyarakat",
                "max_prison": 10,
                "fine_category": "VII",
                "fine_amount": "Rp 3 miliar - Rp 10 miliar",
                "keywords": ["health", "kesehatan", "public", "masyarakat", "pollut", "cemar", "danger", "bahaya", "toxic", "beracun"]
            },
            
            # Fraud (including Deepfake)
            "492": {
                "title": "Fraud (Including Deepfake)",
                "description": "Penipuan menggunakan nama palsu, kedudukan palsu, tipu muslihat, atau rangkaian kebohongan",
                "max_prison": 4,
                "fine_category": "V",
                "fine_amount": "Rp 100 juta - Rp 500 juta",
                "keywords": ["fraud", "tipu", "penipuan", "deepfake", "fake", "palsu", "false", "bohong", "decepti", "mislead", "sesat", "ai-generated", "likeness", "endorse"]
            },
            "493": {
                "title": "Aggravated Fraud",
                "description": "Penipuan dengan pemberatan (teknologi, korban vulnerable, massal)",
                "max_prison": 6,
                "fine_category": "VI",
                "fine_amount": "Rp 500 juta - Rp 3 miliar",
                "keywords": ["technology", "teknologi", "vulnerable", "rentan", "elderly", "lansia", "children", "anak", "mass", "massal"]
            },
            
            # Private Sector Corruption
            "603": {
                "title": "Private Sector Bribery (Giving)",
                "description": "Memberi atau menjanjikan sesuatu kepada pegawai swasta untuk berbuat bertentangan dengan kewajiban",
                "max_prison": 6,
                "fine_category": "VI",
                "fine_amount": "Rp 500 juta - Rp 3 miliar",
                "keywords": ["bribe", "suap", "gift", "hadiah", "facilitat", "fasilitasi", "consulting fee", "bonus", "incentive", "insentif", "kickback"]
            },
            "604": {
                "title": "Private Sector Bribery (Receiving)",
                "description": "Pegawai swasta menerima pemberian/janji untuk berbuat bertentangan dengan kewajiban",
                "max_prison": 6,
                "fine_category": "VI",
                "fine_amount": "Rp 500 juta - Rp 3 miliar",
                "keywords": ["receive", "terima", "accept", "bribe", "suap", "gift", "hadiah", "employee", "pegawai", "manager"]
            },
            "605": {
                "title": "Gratification in Private Sector",
                "description": "Pegawai swasta menerima gratifikasi yang berlawanan dengan kewajiban",
                "max_prison": 5,
                "fine_category": "V",
                "fine_amount": "Rp 100 juta - Rp 500 juta",
                "keywords": ["gratification", "gratifikasi", "gift", "hadiah", "discount", "diskon", "commission", "komisi", "facility", "fasilitas"]
            },
            "606": {
                "title": "Commercial Bribery",
                "description": "Pemberian dalam kegiatan perdagangan untuk memperoleh keuntungan tidak sah",
                "max_prison": 5,
                "fine_category": "VI",
                "fine_amount": "Rp 500 juta - Rp 3 miliar",
                "keywords": ["commercial", "perdagangan", "trade", "dagang", "business", "usaha", "tender", "procurement", "pengadaan", "exclusive", "eksklusif"]
            },
            
            # Corporate Criminal Liability
            "44": {
                "title": "Corporation as Criminal Subject",
                "description": "Korporasi merupakan subjek hukum yang dapat dipertanggungjawabkan secara pidana",
                "keywords": ["corporation", "korporasi", "company", "perusahaan", "PT", "CV", "entity", "badan"]
            },
            "45": {
                "title": "Corporate Penalties",
                "description": "Pidana terhadap korporasi: denda 10x, pencabutan izin, penutupan, pembubaran",
                "keywords": ["corporate", "korporasi", "penalty", "pidana", "fine", "denda", "license", "izin", "closure", "tutup", "dissolution", "bubar"]
            },
            "46": {
                "title": "Management Liability",
                "description": "Pertanggungjawaban pengurus korporasi",
                "keywords": ["management", "pengurus", "director", "direktur", "officer", "pejabat", "liable", "tanggung jawab"]
            },
            "47": {
                "title": "Substitute Penalties for Corporations",
                "description": "Pidana pengganti jika korporasi tidak mampu bayar denda",
                "keywords": ["substitute", "pengganti", "asset", "aset", "seizure", "rampas", "closure", "tutup"]
            },
            "48": {
                "title": "Actions Against Corporations",
                "description": "Tindakan yang dapat dijatuhkan terhadap korporasi",
                "keywords": ["action", "tindakan", "supervision", "pengawasan", "guardianship", "pengampuan", "remediation", "perbaikan"]
            },
            "49": {
                "title": "Corporate Dissolution",
                "description": "Pembubaran korporasi sebagai sanksi pidana",
                "keywords": ["dissolution", "pembubaran", "liquidation", "likuidasi", "repeated", "berulang", "serious", "serius"]
            }
        }
    
    def analyze_contract(self, contract_text: str) -> Dict:
        """
        Analyze contract for KUHP 2026 violations
        """
        contract_lower = contract_text.lower()
        
        violations = []
        total_risk_score = 0
        
        # Check each article
        for article_num, article_data in self.articles.items():
            if "keywords" in article_data:
                matches = self._check_keywords(contract_lower, article_data["keywords"])
                
                if matches:
                    violation = {
                        "article": f"Pasal {article_num}",
                        "title": article_data["title"],
                        "description": article_data["description"],
                        "matched_keywords": matches,
                        "severity": self._calculate_severity(article_data),
                        "max_prison": article_data.get("max_prison", 0),
                        "fine_category": article_data.get("fine_category", ""),
                        "fine_amount": article_data.get("fine_amount", "")
                    }
                    
                    violations.append(violation)
                    total_risk_score += violation["severity"]
        
        # Calculate Maya Wisdom score
        maya_score = self._calculate_maya_wisdom(violations, contract_text)
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_risk_score, len(violations))
        
        # Generate verdict
        verdict = self._generate_verdict(violations, risk_level, maya_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations)
        
        return {
            "violations": violations,
            "total_violations": len(violations),
            "risk_score": total_risk_score,
            "risk_level": risk_level,
            "maya_wisdom_score": maya_score,
            "verdict": verdict,
            "recommendations": recommendations,
            "corporate_liability": self._assess_corporate_liability(violations),
            "total_exposure": self._calculate_total_exposure(violations)
        }
    
    def _check_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Check if keywords are present in text"""
        matches = []
        for keyword in keywords:
            if keyword.lower() in text:
                matches.append(keyword)
        return matches
    
    def _calculate_severity(self, article_data: Dict) -> int:
        """Calculate severity score based on penalties"""
        prison_years = article_data.get("max_prison", 0)
        
        if prison_years >= 10:
            return 100  # Critical
        elif prison_years >= 6:
            return 80   # High
        elif prison_years >= 4:
            return 60   # Medium-High
        else:
            return 40   # Medium
    
    def _calculate_maya_wisdom(self, violations: List[Dict], contract_text: str) -> float:
        """Calculate Maya Wisdom ethical score"""
        if not violations:
            return 0.85  # No violations = relatively ethical
        
        # Base score starts at 1.0
        score = 1.0
        
        # Deduct based on violation types
        for violation in violations:
            article = violation["article"]
            
            # Crimes against justice system: -0.40
            if any(x in article for x in ["278", "280", "282"]):
                score -= 0.40
            
            # Environmental catastrophe: -0.35
            elif any(x in article for x in ["435", "437", "439"]):
                score -= 0.35
            
            # Systematic corruption: -0.30
            elif any(x in article for x in ["603", "604", "605", "606"]):
                score -= 0.30
            
            # Fraud: -0.25
            elif any(x in article for x in ["492", "493"]):
                score -= 0.25
        
        # Additional deductions for specific red flags
        text_lower = contract_text.lower()
        
        if "vulnerable" in text_lower or "elderly" in text_lower or "children" in text_lower:
            score -= 0.10  # Targeting vulnerable
        
        if "confidential" in text_lower and "not disclosed" in text_lower:
            score -= 0.10  # Systematic concealment
        
        if "waive" in text_lower and ("liability" in text_lower or "rights" in text_lower):
            score -= 0.10  # Unfair liability waiver
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _determine_risk_level(self, risk_score: int, violation_count: int) -> str:
        """Determine overall risk level"""
        if risk_score >= 200 or violation_count >= 5:
            return "CRITICAL"
        elif risk_score >= 150 or violation_count >= 3:
            return "HIGH"
        elif risk_score >= 80 or violation_count >= 2:
            return "MEDIUM"
        elif risk_score > 0:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_verdict(self, violations: List[Dict], risk_level: str, maya_score: float) -> str:
        """Generate legal verdict"""
        if risk_level == "CRITICAL":
            if maya_score < 0.10:
                return "CRIMINAL CONSPIRACY - IMMEDIATELY VOID"
            else:
                return "VOID AB INITIO - Criminal Contract"
        elif risk_level == "HIGH":
            return "VOIDABLE - Serious Legal Violations"
        elif risk_level == "MEDIUM":
            return "REQUIRES AMENDMENT - Legal Issues Present"
        elif risk_level == "LOW":
            return "REVIEW RECOMMENDED - Minor Concerns"
        else:
            return "ACCEPTABLE - No Major Issues"
    
    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        if not violations:
            recommendations.append("✅ Contract appears compliant with KUHP 2026")
            return recommendations
        
        # Critical recommendations
        if any("278" in v["article"] or "280" in v["article"] or "282" in v["article"] for v in violations):
            recommendations.append("🚨 DO NOT SIGN - Obstruction of justice violations detected")
            recommendations.append("📞 Report to Indonesian Bar Association immediately")
            recommendations.append("⚖️ Seek witness protection if threatened")
        
        if any("435" in v["article"] or "437" in v["article"] or "439" in v["article"] for v in violations):
            recommendations.append("🌍 DO NOT SIGN - Environmental crimes detected")
            recommendations.append("📞 Report to Ministry of Environment")
            recommendations.append("🌳 Seek environmental legal counsel")
        
        if any("603" in v["article"] or "604" in v["article"] or "605" in v["article"] or "606" in v["article"] for v in violations):
            recommendations.append("💰 DO NOT SIGN - Private sector corruption detected")
            recommendations.append("📞 Report to KPK if pressured")
            recommendations.append("🔍 Document all evidence")
        
        if any("492" in v["article"] or "493" in v["article"] for v in violations):
            recommendations.append("⚠️ DO NOT SIGN - Fraud provisions detected")
            recommendations.append("👥 Protect consumers from deceptive practices")
            recommendations.append("📝 Revise endorsement terms")
        
        # General recommendations
        recommendations.append("⚖️ Consult with legal counsel immediately")
        recommendations.append("📋 Preserve this contract as evidence")
        recommendations.append("🔒 Do not proceed without legal clearance")
        
        return recommendations
    
    def _assess_corporate_liability(self, violations: List[Dict]) -> Dict:
        """Assess corporate criminal liability under Pasal 44-49"""
        if not violations:
            return {"applicable": False}
        
        return {
            "applicable": True,
            "pasal_44_49": "Corporate Criminal Liability Applies",
            "fine_multiplier": "10x individual fine",
            "additional_sanctions": [
                "Pencabutan izin usaha (License revocation)",
                "Perampasan aset (Asset seizure)",
                "Penutupan tempat usaha (Business closure)",
                "Pembubaran korporasi (Corporate dissolution)"
            ],
            "management_liability": "Directors and officers personally liable",
            "warning": "Both corporation AND individuals can be prosecuted"
        }
    
    def _calculate_total_exposure(self, violations: List[Dict]) -> Dict:
        """Calculate total criminal exposure"""
        if not violations:
            return {"total_prison": 0, "total_fine": "Rp 0"}
        
        total_prison = sum(v.get("max_prison", 0) for v in violations)
        
        # Estimate total fine (use highest category)
        fine_categories = [v.get("fine_category", "") for v in violations if v.get("fine_category")]
        
        if fine_categories:
            highest_category = max(fine_categories)
            
            fine_ranges = {
                "I": "Rp 10 juta",
                "II": "Rp 50 juta",
                "III": "Rp 100 juta",
                "IV": "Rp 250 juta",
                "V": "Rp 500 juta",
                "VI": "Rp 3 miliar",
                "VII": "Rp 10 miliar",
                "VIII": "Rp 100 miliar"
            }
            
            individual_fine = fine_ranges.get(highest_category, "Unknown")
            corporate_fine = f"{individual_fine} x 10 (Corporate)"
        else:
            individual_fine = "Unknown"
            corporate_fine = "Unknown"
        
        return {
            "total_prison_years": total_prison,
            "individual_fine": individual_fine,
            "corporate_fine": corporate_fine,
            "cumulative_penalties": "Penalties can be cumulative",
            "warning": "This is MAXIMUM exposure - actual penalties determined by court"
        }
    
    def format_analysis_report(self, analysis: Dict) -> str:
        """Format analysis into readable report"""
        report = []
        
        report.append("="*80)
        report.append("🏛️  KUHP 2026 ANALYSIS REPORT")
        report.append("="*80)
        report.append("")
        
        # Summary
        report.append(f"📊 SUMMARY:")
        report.append(f"   Total Violations: {analysis['total_violations']}")
        report.append(f"   Risk Level: {analysis['risk_level']}")
        report.append(f"   Maya Wisdom Score: {analysis['maya_wisdom_score']:.2f}/1.0")
        report.append(f"   Verdict: {analysis['verdict']}")
        report.append("")
        
        # Violations
        if analysis['violations']:
            report.append("🚨 KUHP 2026 VIOLATIONS DETECTED:")
            report.append("")
            
            for i, violation in enumerate(analysis['violations'], 1):
                report.append(f"{i}. {violation['article']} - {violation['title']}")
                report.append(f"   Description: {violation['description']}")
                report.append(f"   Severity: {violation['severity']}/100")
                
                if violation.get('max_prison'):
                    report.append(f"   Max Prison: {violation['max_prison']} years")
                
                if violation.get('fine_amount'):
                    report.append(f"   Fine: {violation['fine_amount']}")
                
                report.append(f"   Matched Keywords: {', '.join(violation['matched_keywords'][:5])}")
                report.append("")
        
        # Corporate Liability
        if analysis['corporate_liability']['applicable']:
            report.append("🏢 CORPORATE CRIMINAL LIABILITY (Pasal 44-49):")
            report.append(f"   Status: {analysis['corporate_liability']['pasal_44_49']}")
            report.append(f"   Fine Multiplier: {analysis['corporate_liability']['fine_multiplier']}")
            report.append(f"   Management: {analysis['corporate_liability']['management_liability']}")
            report.append("")
            report.append("   Additional Sanctions:")
            for sanction in analysis['corporate_liability']['additional_sanctions']:
                report.append(f"   - {sanction}")
            report.append("")
        
        # Total Exposure
        report.append("⚖️  TOTAL CRIMINAL EXPOSURE:")
        report.append(f"   Prison: Up to {analysis['total_exposure']['total_prison_years']} years")
        report.append(f"   Individual Fine: {analysis['total_exposure']['individual_fine']}")
        report.append(f"   Corporate Fine: {analysis['total_exposure']['corporate_fine']}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            report.append(f"   {rec}")
        report.append("")
        
        report.append("="*80)
        report.append("🏆 LegalMind AI - KUHP 2026 Ready")
        report.append("="*80)
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    analyzer = KUHP2026Analyzer()
    
    # Test with deepfake contract
    test_contract = """
    INFLUENCER MARKETING AGREEMENT
    
    Content Creator authorizes Agency to:
    - Create AI-generated versions of Creator's likeness
    - Produce deepfake videos for brand endorsements
    - Make false claims about product effectiveness
    - Target vulnerable demographics (elderly, children)
    """
    
    analysis = analyzer.analyze_contract(test_contract)
    report = analyzer.format_analysis_report(analysis)
    print(report)
