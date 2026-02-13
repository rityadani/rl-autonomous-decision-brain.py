#!/bin/bash
# Example curl commands for testing RL Decision Brain
# Replace <URL> with your actual Render deployment URL

BASE_URL="http://localhost:8080"  # Change to https://<your-app>.onrender.com

echo "=========================================="
echo "RL Decision Brain - Test Commands"
echo "=========================================="

echo -e "\n[1] Health Check"
curl -X GET "$BASE_URL/health"

echo -e "\n\n[2] Action Scope"
curl -X GET "$BASE_URL/scope"

echo -e "\n\n[3] DEV High CPU (should scale_up)"
curl -X POST "$BASE_URL/decide" \
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

echo -e "\n\n[4] PROD Crash (should restart)"
curl -X POST "$BASE_URL/decide" \
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

echo -e "\n\n[5] STAGE High CPU (should scale_up)"
curl -X POST "$BASE_URL/decide" \
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

echo -e "\n\n[6] PROD High CPU (should noop - safety filtered)"
curl -X POST "$BASE_URL/decide" \
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

echo -e "\n\n[7] Invalid Input (should noop with reason)"
curl -X POST "$BASE_URL/decide" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "invalid_env",
    "event_type": "test"
  }'

echo -e "\n\n=========================================="
echo "All tests completed"
echo "=========================================="
