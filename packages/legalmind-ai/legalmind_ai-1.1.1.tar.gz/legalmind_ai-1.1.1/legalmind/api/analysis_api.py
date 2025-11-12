# legalmind/api/analysis_api.py
"""
PRODUCTION ANALYSIS API - REST API untuk semua analysis capabilities
"""
from flask import Flask, request, jsonify
from legalmind.unified_analysis_engine import UnifiedAnalysisEngine

app = Flask(__name__)
engine = UnifiedAnalysisEngine()

@app.route('/api/analyze', methods=['POST'])
def analyze_legal_case():
    """API endpoint untuk analysis legal cases"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Query parameter required"}), 400
        
        query = data['query']
        context = data.get('context', '')
        
        # Get analysis recommendation
        analysis_result = engine.analyze_with_best_fit(query, context)
        
        return jsonify({
            "status": "success",
            "query": query,
            "analysis": analysis_result,
            "available_capabilities": len(engine.analyzers)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    """Get semua available analysis capabilities"""
    try:
        capabilities = engine.list_all_capabilities()
        return jsonify({
            "status": "success",
            "capabilities": capabilities
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "analyzers_loaded": len(engine.analyzers),
        "total_capabilities": sum(len(analyzer["capabilities"]) for analyzer in engine.analyzers.values())
    })

if __name__ == '__main__':
    print("🚀 LEGALMIND AI ANALYSIS API STARTING...")
    print(f"📊 Loaded {len(engine.analyzers)} analyzers")
    app.run(host='0.0.0.0', port=5000, debug=True)
