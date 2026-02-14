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
    """Advanced interactive dashboard"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>RL Decision Brain - Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); margin-bottom: 20px; }
        .header h1 { color: #667eea; font-size: 32px; margin-bottom: 10px; }
        .badges { display: flex; gap: 10px; flex-wrap: wrap; }
        .badge { background: #10b981; color: white; padding: 8px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }
        .badge.frozen { background: #3b82f6; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        .card h3 { color: #667eea; margin-bottom: 15px; font-size: 18px; }
        .metric { font-size: 36px; font-weight: bold; color: #333; margin: 10px 0; }
        .label { color: #666; font-size: 14px; }
        .test-panel { background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; color: #333; font-weight: 600; margin-bottom: 5px; }
        select, input { width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 14px; }
        select:focus, input:focus { outline: none; border-color: #667eea; }
        button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; width: 100%; transition: transform 0.2s; }
        button:hover { transform: translateY(-2px); }
        button:active { transform: translateY(0); }
        .response-box { background: #1e293b; color: #e2e8f0; padding: 20px; border-radius: 8px; margin-top: 20px; max-height: 400px; overflow-y: auto; }
        .response-box pre { color: #94a3b8; font-size: 13px; white-space: pre-wrap; word-wrap: break-word; }
        .scope-item { background: #f3f4f6; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
        .scope-item strong { color: #667eea; }
        .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
        .action-tag { background: #667eea; color: white; padding: 5px 12px; border-radius: 5px; font-size: 12px; }
        .log-item { background: #f9fafb; padding: 12px; border-left: 4px solid #667eea; margin-bottom: 10px; border-radius: 5px; }
        .log-item.success { border-left-color: #10b981; }
        .log-item.error { border-left-color: #ef4444; }
        .log-time { color: #6b7280; font-size: 12px; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .loading { animation: pulse 1.5s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 RL Decision Brain</h1>
            <div class="badges">
                <span class="badge" id="statusBadge">● HEALTHY</span>
                <span class="badge frozen">❄️ DEMO-FROZEN</span>
                <span class="badge" style="background: #8b5cf6;">🔒 STATELESS</span>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📊 Total Requests</h3>
                <div class="metric" id="totalRequests">0</div>
                <div class="label">Since page load</div>
            </div>
            <div class="card">
                <h3>⚡ Last Action</h3>
                <div class="metric" id="lastAction">-</div>
                <div class="label">Most recent decision</div>
            </div>
            <div class="card">
                <h3>🎯 Success Rate</h3>
                <div class="metric" id="successRate">100%</div>
                <div class="label">API response rate</div>
            </div>
        </div>

        <div class="test-panel">
            <h3 style="color: #667eea; margin-bottom: 20px;">🧪 Test Decision Maker</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div class="form-group">
                    <label>Environment</label>
                    <select id="environment">
                        <option value="dev">DEV</option>
                        <option value="stage">STAGE</option>
                        <option value="prod">PROD</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Event Type</label>
                    <select id="eventType">
                        <option value="high_cpu">High CPU</option>
                        <option value="high_memory">High Memory</option>
                        <option value="crash">Crash</option>
                        <option value="low_load">Low Load</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>CPU %</label>
                    <input type="number" id="cpu" value="85" min="0" max="100">
                </div>
                <div class="form-group">
                    <label>Memory %</label>
                    <input type="number" id="memory" value="50" min="0" max="100">
                </div>
            </div>
            <button onclick="makeDecision()" id="testBtn">🚀 Get Decision</button>
            <div class="response-box" id="responseBox" style="display: none;">
                <pre id="response"></pre>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>🎯 Action Scope</h3>
                <div class="scope-item">
                    <strong>DEV</strong>
                    <div class="actions">
                        <span class="action-tag">noop</span>
                        <span class="action-tag">scale_up</span>
                        <span class="action-tag">scale_down</span>
                        <span class="action-tag">restart</span>
                    </div>
                </div>
                <div class="scope-item">
                    <strong>STAGE</strong>
                    <div class="actions">
                        <span class="action-tag">noop</span>
                        <span class="action-tag">scale_up</span>
                        <span class="action-tag">scale_down</span>
                    </div>
                </div>
                <div class="scope-item">
                    <strong>PROD</strong>
                    <div class="actions">
                        <span class="action-tag">noop</span>
                        <span class="action-tag">restart</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>📝 Recent Activity</h3>
                <div id="activityLog"></div>
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px; color: white;">
            <a href="https://github.com/rityadani/rl-autonomous-decision-brain.py" style="color: white; text-decoration: none; font-weight: bold;">📦 View on GitHub</a>
        </div>
    </div>

    <script>
        let requestCount = 0;
        let successCount = 0;

        async function checkHealth() {
            try {
                const res = await fetch('/health');
                const data = await res.json();
                document.getElementById('statusBadge').textContent = data.status === 'healthy' ? '● HEALTHY' : '● ERROR';
                document.getElementById('statusBadge').style.background = data.status === 'healthy' ? '#10b981' : '#ef4444';
            } catch(e) {
                document.getElementById('statusBadge').textContent = '● OFFLINE';
                document.getElementById('statusBadge').style.background = '#ef4444';
            }
        }

        async function makeDecision() {
            const btn = document.getElementById('testBtn');
            btn.textContent = '⏳ Processing...';
            btn.classList.add('loading');
            btn.disabled = true;

            const payload = {
                environment: document.getElementById('environment').value,
                event_type: document.getElementById('eventType').value,
                metrics: {
                    cpu_percent: parseFloat(document.getElementById('cpu').value),
                    memory_percent: parseFloat(document.getElementById('memory').value),
                    error_rate: 0.01
                }
            };

            try {
                requestCount++;
                const res = await fetch('/decide', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                successCount++;
                document.getElementById('responseBox').style.display = 'block';
                document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                document.getElementById('totalRequests').textContent = requestCount;
                document.getElementById('lastAction').textContent = data.action.toUpperCase();
                document.getElementById('successRate').textContent = Math.round((successCount/requestCount)*100) + '%';
                
                addLog(data.action, data.reason, true);
            } catch(e) {
                requestCount++;
                document.getElementById('responseBox').style.display = 'block';
                document.getElementById('response').textContent = 'Error: ' + e.message;
                document.getElementById('totalRequests').textContent = requestCount;
                document.getElementById('successRate').textContent = Math.round((successCount/requestCount)*100) + '%';
                
                addLog('error', e.message, false);
            } finally {
                btn.textContent = '🚀 Get Decision';
                btn.classList.remove('loading');
                btn.disabled = false;
            }
        }

        function addLog(action, reason, success) {
            const log = document.getElementById('activityLog');
            const time = new Date().toLocaleTimeString();
            const item = document.createElement('div');
            item.className = 'log-item ' + (success ? 'success' : 'error');
            item.innerHTML = `
                <div style="font-weight: bold; color: #333;">${action.toUpperCase()}</div>
                <div style="font-size: 13px; color: #666; margin-top: 5px;">${reason}</div>
                <div class="log-time">${time}</div>
            `;
            log.insertBefore(item, log.firstChild);
            if(log.children.length > 5) log.removeChild(log.lastChild);
        }

        checkHealth();
        setInterval(checkHealth, 5000);
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
