# Render Deployment Guide

**For:** Shivam Pal (Orchestrator & Hosting Owner)  
**Service:** RL Decision Brain  
**Platform:** Render.com

---

## Prerequisites

1. GitHub repository with the RL Decision Brain code
2. Render account (free tier works)

---

## Deployment Steps

### Step 1: Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing the RL Decision Brain

---

### Step 2: Configure Service

**Basic Settings:**
- **Name:** `rl-decision-brain` (or your choice)
- **Region:** Choose closest to your users
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave blank (or specify if in subdirectory)

**Build & Deploy:**
- **Runtime:** `Python 3`
- **Build Command:** 
  ```
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```
  gunicorn app:app --bind 0.0.0.0:8080 --workers 2 --timeout 30
  ```

**Instance Type:**
- **Free tier** is sufficient for demo
- Upgrade to **Starter** for production

---

### Step 3: Environment Variables (Optional)

No environment variables required for demo mode.

If needed in future:
- `FLASK_ENV=production`
- `LOG_LEVEL=INFO`

---

### Step 4: Health Check Configuration

**Health Check Path:** `/health`  
**Expected Status Code:** `200`  
**Expected Response:**
```json
{
  "status": "healthy",
  "demo_frozen": true,
  "learning_enabled": false,
  "exploration_enabled": false,
  "stateless": true
}
```

---

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (usually 2-3 minutes)
3. Render will provide a URL: `https://rl-decision-brain-xxxx.onrender.com`

---

## Post-Deployment Verification

### Test 1: Health Check
```bash
curl https://rl-decision-brain-xxxx.onrender.com/health
```

**Expected:** HTTP 200 with health status

---

### Test 2: Action Scope
```bash
curl https://rl-decision-brain-xxxx.onrender.com/scope
```

**Expected:**
```json
{
  "dev": ["noop", "scale_up", "scale_down", "restart"],
  "stage": ["noop", "scale_up", "scale_down"],
  "prod": ["noop", "restart"]
}
```

---

### Test 3: Decision Endpoint
```bash
curl -X POST https://rl-decision-brain-xxxx.onrender.com/decide \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "dev",
    "event_type": "high_cpu",
    "metrics": {
      "cpu_percent": 85.0,
      "memory_percent": 50.0,
      "error_rate": 0.01
    }
  }'
```

**Expected:**
```json
{
  "action": "scale_up",
  "reason": "Deterministic decision for high_cpu in dev",
  "demo_frozen": true,
  "timestamp": 1234567890.123,
  "environment": "dev",
  "safety_filtered": false
}
```

---

## Integration with Orchestrator

### Base URL
```
https://rl-decision-brain-xxxx.onrender.com
```

### Primary Endpoint
```
POST /decide
Content-Type: application/json
```

### Example Integration Code (Python)

```python
import requests

RL_AGENT_URL = "https://rl-decision-brain-xxxx.onrender.com/decide"

def get_rl_decision(environment, event_type, metrics):
    """Get decision from RL agent"""
    payload = {
        "environment": environment,
        "event_type": event_type,
        "metrics": metrics
    }
    
    try:
        response = requests.post(RL_AGENT_URL, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Fallback to NOOP on error
        return {
            "action": "noop",
            "reason": f"RL agent error: {str(e)}",
            "demo_frozen": True,
            "timestamp": 0,
            "environment": environment,
            "safety_filtered": False
        }

# Example usage
decision = get_rl_decision(
    environment="dev",
    event_type="high_cpu",
    metrics={
        "cpu_percent": 85.0,
        "memory_percent": 50.0,
        "error_rate": 0.01
    }
)

print(f"Action: {decision['action']}")
print(f"Reason: {decision['reason']}")
```

---

## Monitoring & Logs

### View Logs
1. Go to Render Dashboard
2. Select your service
3. Click **"Logs"** tab
4. Monitor for errors or issues

### Expected Log Output
```
Starting RL Decision Brain on port 8080
Demo-frozen mode: Learning DISABLED, Exploration DISABLED
```

### Request Logs
```
Decision request: dev - high_cpu
Decision response: scale_up - Deterministic decision for high_cpu in dev
```

---

## Troubleshooting

### Problem: Service won't start
**Check:**
- Build logs for dependency errors
- Start command is correct
- Port 8080 is used (Render expects this)

**Solution:**
- Verify `requirements.txt` is present
- Verify `app.py` is present
- Check Python version (should be 3.11+)

---

### Problem: Health check failing
**Check:**
- `/health` endpoint returns 200
- Response is valid JSON

**Solution:**
- Test locally first: `python app.py`
- Check logs for startup errors

---

### Problem: Slow cold starts
**Cause:** Free tier services sleep after 15 minutes of inactivity

**Solutions:**
- Upgrade to Starter tier (no sleep)
- Use a ping service to keep it awake
- Accept 30-60 second cold start delay

---

### Problem: 502 Bad Gateway
**Cause:** Service crashed or not responding

**Solution:**
- Check logs for errors
- Verify gunicorn is running
- Restart service from dashboard

---

## Performance Notes

### Free Tier
- ✅ Sufficient for demo
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ 30-60 second cold start
- ✅ 512 MB RAM (plenty for this agent)

### Starter Tier ($7/month)
- ✅ No sleep
- ✅ Instant response
- ✅ 512 MB RAM
- ✅ Recommended for production demo

---

## Scaling Considerations

**Current Setup:**
- 2 gunicorn workers
- Stateless (safe for horizontal scaling)
- No database required
- No file storage required

**To Scale:**
1. Increase worker count in start command
2. Upgrade instance type
3. Add multiple instances (load balancer)

**Note:** Agent is stateless, so horizontal scaling is safe.

---

## Security Notes

### HTTPS
✅ Render provides free SSL/TLS  
✅ All traffic encrypted by default

### Authentication
⚠️ No authentication in current version  
⚠️ Add API key if exposing publicly

**To add API key (if needed):**
```python
# In app.py
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.environ.get('API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401
```

---

## Cost Estimate

| Tier | Cost | Use Case |
|------|------|----------|
| Free | $0/month | Testing, low-traffic demo |
| Starter | $7/month | Production demo, no sleep |
| Standard | $25/month | High-traffic production |

**Recommendation:** Start with Free, upgrade to Starter for demo day.

---

## Support

**RL Agent Issues:** Contact Ritesh Yadav  
**Deployment Issues:** Contact Shivam Pal  
**Render Support:** https://render.com/docs

---

## Checklist

- [ ] Repository connected to Render
- [ ] Build command configured
- [ ] Start command configured
- [ ] Health check configured
- [ ] Service deployed successfully
- [ ] Health check passing
- [ ] Decision endpoint tested
- [ ] URL shared with orchestrator team
- [ ] Logs monitored for errors

---

**Deployment complete? Update orchestrator with the live URL! 🚀**
