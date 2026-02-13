# RL Decision Brain - Production-Hardened Agent

**Status:** Demo-Frozen | Stateless | Safety-Caged  
**Owner:** Ritesh Yadav  
**Consumer:** Shivam Pal (Orchestrator)

---

## What This Is

A deterministic, stateless RL agent that makes autonomous DevOps decisions under strict safety constraints.

**Guarantees:**
- ✅ Stateless (safe for cold starts, replicas)
- ✅ Deterministic (same input → same output)
- ✅ Safety-caged (environment-scoped actions)
- ✅ Demo-frozen (no learning, no exploration)
- ✅ Refusal-first (invalid input → NOOP)

---

## Quick Start

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_safety.py

# Start server
python app.py
```

Server runs on `http://localhost:8080`

### Test with curl
```bash
# Health check
curl http://localhost:8080/health

# Make decision
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

---

## Deployment (Render)

### Option 1: Web Service
1. Connect GitHub repo to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app --bind 0.0.0.0:8080`
4. Deploy

### Option 2: Docker (if needed)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
```

---

## Action Scope (LOCKED)

| Environment | Allowed Actions |
|-------------|----------------|
| **DEV** | noop, scale_up, scale_down, restart |
| **STAGE** | noop, scale_up, scale_down |
| **PROD** | noop, restart |

**Safety guarantee:** Agent will NEVER emit actions outside this scope.

---

## API Contract

See [INTEGRATION.md](INTEGRATION.md) for complete API documentation.

**Primary endpoint:**
```
POST /decide
```

**Input:**
```json
{
  "environment": "dev|stage|prod",
  "event_type": "high_cpu|high_memory|crash|low_load|...",
  "metrics": {
    "cpu_percent": float,
    "memory_percent": float,
    "error_rate": float
  }
}
```

**Output:**
```json
{
  "action": "noop|scale_up|scale_down|restart",
  "reason": "Deterministic decision for high_cpu in dev",
  "demo_frozen": true,
  "timestamp": 1234567890.123,
  "environment": "dev",
  "safety_filtered": false
}
```

---

## Safety Validation

Run the test suite to verify all safety guarantees:

```bash
python test_safety.py
```

**Tests cover:**
- ✅ Valid requests produce correct actions
- ✅ Illegal actions are filtered to NOOP
- ✅ Invalid inputs produce NOOP with reason
- ✅ Determinism (identical input → identical output)
- ✅ Action scope enforcement
- ✅ Health check

---

## What This Agent Will NOT Do

❌ Emit actions outside environment scope  
❌ Learn or mutate state between requests  
❌ Produce non-deterministic output  
❌ Execute actions directly (only returns JSON)  
❌ Persist data to disk or database  
❌ Require startup order or initialization  

---

## Files

- `rl_decision_brain.py` - Core agent logic (FROZEN)
- `app.py` - Flask HTTP wrapper
- `test_safety.py` - Safety validation suite
- `requirements.txt` - Python dependencies
- `INTEGRATION.md` - Integration guide for Shivam
- `test_curl.sh` - Example curl commands

---

## Contact

**Ritesh Yadav** - RL Decision Brain Owner  
Responsible for: Correctness, determinism, safety guarantees

**Shivam Pal** - Orchestrator & Hosting Owner  
Consumes RL via HTTP, owns live deployment

---

## Confirmation

✅ **Safe for live demo consumption**  
✅ **Interface locked and documented**  
✅ **All safety tests passing**  
✅ **Ready for Shivam's orchestrator integration**
