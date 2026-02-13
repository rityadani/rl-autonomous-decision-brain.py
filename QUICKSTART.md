# Quick Start Guide

**Get the RL Decision Brain running in 60 seconds**

---

## Step 1: Install Dependencies (10 seconds)

```bash
pip install -r requirements.txt
```

---

## Step 2: Run Safety Tests (15 seconds)

```bash
python test_safety.py
```

**Expected output:**
```
============================================================
[SUCCESS] ALL TESTS PASSED - Agent is production-safe
============================================================
```

---

## Step 3: Start the Server (5 seconds)

```bash
python app.py
```

**Expected output:**
```
Starting RL Decision Brain on port 8080
Demo-frozen mode: Learning DISABLED, Exploration DISABLED
```

---

## Step 4: Test the Agent (30 seconds)

### Test 1: Health Check
```bash
curl http://localhost:8080/health
```

**Expected:**
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

### Test 2: Make a Decision
```bash
curl -X POST http://localhost:8080/decide \
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

### Test 3: Safety Filtering (PROD)
```bash
curl -X POST http://localhost:8080/decide \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "prod",
    "event_type": "high_cpu",
    "metrics": {
      "cpu_percent": 95.0,
      "memory_percent": 60.0,
      "error_rate": 0.01
    }
  }'
```

**Expected:**
```json
{
  "action": "noop",
  "reason": "Deterministic decision for high_cpu in prod",
  "demo_frozen": true,
  "timestamp": 1234567890.123,
  "environment": "prod",
  "safety_filtered": false
}
```

**Why NOOP?** PROD only allows `[noop, restart]`. `scale_up` is not allowed.

---

### Test 4: Invalid Input
```bash
curl -X POST http://localhost:8080/decide \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "invalid_env",
    "event_type": "test"
  }'
```

**Expected:**
```json
{
  "action": "noop",
  "reason": "Missing required field: metrics",
  "demo_frozen": true,
  "timestamp": 1234567890.123,
  "environment": "invalid_env",
  "safety_filtered": false
}
```

---

## ✅ Success Criteria

If all 4 tests pass, the agent is working correctly and is safe for deployment.

---

## Next Steps

1. ✅ Local testing complete
2. 📖 Read [INTEGRATION.md](INTEGRATION.md) for full API documentation
3. 🚀 Deploy to Render (see [README.md](README.md))
4. 🔗 Integrate with Shivam's orchestrator

---

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'flask'`  
**Solution:** Run `pip install -r requirements.txt`

**Problem:** Port 8080 already in use  
**Solution:** Edit `app.py` and change `port = 8080` to another port

**Problem:** Tests failing  
**Solution:** Check Python version (requires 3.11+)

---

## Files Overview

| File | Purpose |
|------|---------|
| `rl_decision_brain.py` | Core agent logic |
| `app.py` | Flask HTTP wrapper |
| `test_safety.py` | Safety validation tests |
| `requirements.txt` | Python dependencies |
| `INTEGRATION.md` | API documentation for Shivam |
| `README.md` | Main documentation |
| `PROOF_LOG.md` | Safety proof logs |
| `HANDOVER_CHECKLIST.md` | Handover checklist |

---

**Ready to deploy? See [README.md](README.md) for deployment instructions.**
