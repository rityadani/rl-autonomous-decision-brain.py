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
    """API home endpoint with simple dashboard"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>RL Decision Brain</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: #eee; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #16c79a; }
        .status { background: #0f3460; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .endpoint { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .badge { background: #16c79a; padding: 5px 10px; border-radius: 3px; color: #000; font-weight: bold; }
        button { background: #16c79a; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
        button:hover { background: #1dd1a1; }
        pre { background: #000; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 RL Decision Brain</h1>
        <div class="status">
            <p><span class="badge">HEALTHY</span> <span class="badge">DEMO-FROZEN</span></p>
            <p>Version: 1.0 | Stateless | Deterministic | Safety-Caged</p>
        </div>
        
        <h2>📡 API Endpoints</h2>
        <div class="endpoint">
            <strong>GET /health</strong> - Health check
            <button onclick="test('/health')">Test</button>
        </div>
        <div class="endpoint">
            <strong>POST /decide</strong> - Make decision
            <button onclick="testDecide()">Test</button>
        </div>
        <div class="endpoint">
            <strong>GET /scope</strong> - Action scope
            <button onclick="test('/scope')">Test</button>
        </div>
        
        <h2>📊 Response</h2>
        <pre id="response">Click a test button to see response...</pre>
        
        <h2>🎯 Action Scope</h2>
        <div class="endpoint">
            <strong>DEV:</strong> noop, scale_up, scale_down, restart<br>
            <strong>STAGE:</strong> noop, scale_up, scale_down<br>
            <strong>PROD:</strong> noop, restart
        </div>
        
        <p style="margin-top: 40px; text-align: center; color: #888;">
            <a href="https://github.com/rityadani/rl-autonomous-decision-brain.py" style="color: #16c79a;">GitHub</a>
        </p>
    </div>
    
    <script>
        async function test(endpoint) {
            try {
                const res = await fetch(endpoint);
                const data = await res.json();
                document.getElementById('response').textContent = JSON.stringify(data, null, 2);
            } catch(e) {
                document.getElementById('response').textContent = 'Error: ' + e.message;
            }
        }
        
        async function testDecide() {
            try {
                const res = await fetch('/decide', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        environment: 'dev',
                        event_type: 'high_cpu',
                        metrics: {cpu_percent: 85, memory_percent: 50, error_rate: 0.01}
                    })
                });
                const data = await res.json();
                document.getElementById('response').textContent = JSON.stringify(data, null, 2);
            } catch(e) {
                document.getElementById('response').textContent = 'Error: ' + e.message;
            }
        }
    </script>
</body>
</html>
    '''
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting RL Decision Brain on port {port}")
    logger.info("Demo-frozen mode: Learning DISABLED, Exploration DISABLED")
    app.run(host='0.0.0.0', port=port, debug=False)
