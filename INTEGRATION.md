# RL Decision Brain - Integration Guide

## Overview
Demo-frozen, stateless RL agent for autonomous DevOps decisions.  
**Safe for live demo consumption.**

---

## Endpoint Contract

### Base URL
```
https://<your-render-url>.onrender.com
```

### 1. Health Check
```
GET /health
```

**Response:**
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

### 2. Decision Endpoint (PRIMARY)
```
POST /decide
Content-Type: application/json
```

**Request Schema (LOCKED):**
```json
{
  "environment": "dev" | "stage" | "prod",
  "event_type": "high_cpu" | "high_memory" | "crash" | "low_load" | <custom>,
  "metrics": {
    "cpu_percent": 75.5,
    "memory_percent": 60.2,
    "error_rate": 0.05
  }
}
```

**Response Schema (LOCKED):**
```json
{
  "action": "noop" | "scale_up" | "scale_down" | "restart",
  "reason": "Deterministic decision for high_cpu in dev",
  "demo_frozen": true,
  "timestamp": 1234567890.123,
  "environment": "dev",
  "safety_filtered": false
}
```

---

### 3. Action Scope Endpoint
```
GET /scope
```

**Response:**
```json
{
  "dev": ["noop", "scale_up", "scale_down", "restart"],
  "stage": ["noop", "scale_up", "scale_down"],
  "prod": ["noop", "restart"]
}
```

---

## Safe Demo Scenarios

### Scenario 1: DEV High CPU
```bash
curl -X POST https://<url>/decide \
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
**Expected:** `{"action": "scale_up", ...}`

---

### Scenario 2: PROD Crash
```bash
curl -X POST https://<url>/decide \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "prod",
    "event_type": "crash",
    "metrics": {
      "cpu_percent": 10.0,
      "memory_percent": 20.0,
      "error_rate": 0.95
    }
  }'
```
**Expected:** `{"action": "restart", ...}`

---

### Scenario 3: STAGE High CPU (Conservative)
```bash
curl -X POST https://<url>/decide \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "stage",
    "event_type": "high_cpu",
    "metrics": {
      "cpu_percent": 90.0,
      "memory_percent": 70.0,
      "error_rate": 0.02
    }
  }'
```
**Expected:** `{"action": "scale_up", ...}`

---

### Scenario 4: Invalid Input (NOOP)
```bash
curl -X POST https://<url>/decide \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "invalid_env",
    "event_type": "test"
  }'
```
**Expected:** `{"action": "noop", "reason": "Missing required field: metrics", ...}`

---

## What This Agent Will NOT Do

❌ **Never emit actions outside environment scope**  
- PROD will NEVER emit `scale_up` or `scale_down`
- STAGE will NEVER emit `restart`

❌ **Never learn or mutate state**  
- No Q-table updates
- No exploration
- No state persistence

❌ **Never produce non-deterministic output**  
- Same input → same output (guaranteed)

❌ **Never execute actions directly**  
- Only returns decision JSON
- Orchestrator owns execution

---

## Safety Guarantees

✅ **Stateless:** Safe for cold starts, multiple replicas  
✅ **Deterministic:** Identical input → identical output  
✅ **Safety-caged:** Environment-scoped action filtering  
✅ **Demo-frozen:** Learning disabled, exploration disabled  
✅ **Refusal-first:** Invalid input → NOOP with reason  

---

## Deployment Notes

- **Platform:** Render (or any container platform)
- **Port:** 8080
- **Dependencies:** Flask (see requirements.txt)
- **Health check:** `GET /health` (returns 200 when ready)
- **Cold start:** < 5 seconds

---

## Contact

**Ritesh Yadav** - RL Decision Brain Owner  
Responsible for: Correctness, determinism, safety guarantees
