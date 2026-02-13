"""
HTTP Service Wrapper for RL Decision Brain
Stateless Flask service ready for Render deployment
"""

from flask import Flask, request, jsonify
from rl_decision_brain import RLDecisionBrain
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stateless agent instance (no state mutation)
agent = RLDecisionBrain()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify(agent.health_check()), 200

@app.route('/decide', methods=['POST'])
def decide():
    """
    Main decision endpoint
    
    Request body:
    {
        "environment": "dev" | "stage" | "prod",
        "event_type": str,
        "metrics": {
            "cpu_percent": float,
            "memory_percent": float,
            "error_rate": float
        }
    }
    
    Response:
    {
        "action": str,
        "reason": str,
        "demo_frozen": true,
        "timestamp": float,
        "environment": str,
        "safety_filtered": bool
    }
    """
    try:
        payload = request.get_json(force=True)
        logger.info(f"Decision request: {payload.get('environment', 'unknown')} - {payload.get('event_type', 'unknown')}")
        
        response = agent.decide(payload)
        logger.info(f"Decision response: {response['action']} - {response['reason']}")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "action": "noop",
            "reason": f"Internal error: {str(e)}",
            "demo_frozen": True,
            "timestamp": 0,
            "environment": "unknown",
            "safety_filtered": False
        }), 500

@app.route('/scope', methods=['GET'])
def scope():
    """Return action scope per environment"""
    return jsonify({
        "dev": ["noop", "scale_up", "scale_down", "restart"],
        "stage": ["noop", "scale_up", "scale_down"],
        "prod": ["noop", "restart"]
    }), 200

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        "service": "RL Decision Brain",
        "version": "1.0",
        "status": "healthy",
        "demo_frozen": True,
        "endpoints": {
            "health": "GET /health",
            "decide": "POST /decide",
            "scope": "GET /scope"
        },
        "documentation": "https://github.com/rityadani/rl-autonomous-decision-brain.py"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting RL Decision Brain on port {port}")
    logger.info("Demo-frozen mode: Learning DISABLED, Exploration DISABLED")
    app.run(host='0.0.0.0', port=port, debug=False)
