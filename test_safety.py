"""
Safety Validation Test Suite
Validates refusal, downgrade, and NOOP behavior
"""

import json
from rl_decision_brain import RLDecisionBrain

def test_valid_requests():
    """Test valid requests produce correct actions"""
    agent = RLDecisionBrain()
    
    # DEV high CPU → scale_up
    response = agent.decide({
        "environment": "dev",
        "event_type": "high_cpu",
        "metrics": {"cpu_percent": 85, "memory_percent": 50, "error_rate": 0.01}
    })
    assert response["action"] == "scale_up", f"Expected scale_up, got {response['action']}"
    assert response["demo_frozen"] == True
    print("[PASS] DEV high_cpu -> scale_up")
    
    # PROD crash → restart
    response = agent.decide({
        "environment": "prod",
        "event_type": "crash",
        "metrics": {"cpu_percent": 10, "memory_percent": 20, "error_rate": 0.95}
    })
    assert response["action"] == "restart", f"Expected restart, got {response['action']}"
    print("[PASS] PROD crash -> restart")
    
    # STAGE high_memory → scale_up
    response = agent.decide({
        "environment": "stage",
        "event_type": "high_memory",
        "metrics": {"cpu_percent": 50, "memory_percent": 90, "error_rate": 0.02}
    })
    assert response["action"] == "scale_up", f"Expected scale_up, got {response['action']}"
    print("[PASS] STAGE high_memory -> scale_up")

def test_safety_filtering():
    """Test illegal actions are filtered to NOOP"""
    agent = RLDecisionBrain()
    
    # PROD high_cpu should be filtered (scale_up not allowed in PROD)
    response = agent.decide({
        "environment": "prod",
        "event_type": "high_cpu",
        "metrics": {"cpu_percent": 95, "memory_percent": 60, "error_rate": 0.01}
    })
    assert response["action"] == "noop", f"Expected noop (filtered), got {response['action']}"
    print("[PASS] PROD high_cpu -> noop (safety filtered)")
    
    # STAGE crash should be NOOP (restart not allowed in STAGE)
    response = agent.decide({
        "environment": "stage",
        "event_type": "crash",
        "metrics": {"cpu_percent": 10, "memory_percent": 20, "error_rate": 0.90}
    })
    assert response["action"] == "noop", f"Expected noop, got {response['action']}"
    print("[PASS] STAGE crash -> noop (safety filtered)")

def test_invalid_inputs():
    """Test invalid inputs produce NOOP with reason"""
    agent = RLDecisionBrain()
    
    # Missing environment
    response = agent.decide({
        "event_type": "test",
        "metrics": {"cpu_percent": 50, "memory_percent": 50, "error_rate": 0.01}
    })
    assert response["action"] == "noop"
    assert "Missing required field: environment" in response["reason"]
    print("[PASS] Missing environment -> noop with reason")
    
    # Missing event_type
    response = agent.decide({
        "environment": "dev",
        "metrics": {"cpu_percent": 50, "memory_percent": 50, "error_rate": 0.01}
    })
    assert response["action"] == "noop"
    assert "Missing required field: event_type" in response["reason"]
    print("[PASS] Missing event_type -> noop with reason")
    
    # Missing metrics
    response = agent.decide({
        "environment": "dev",
        "event_type": "test"
    })
    assert response["action"] == "noop"
    assert "Missing required field: metrics" in response["reason"]
    print("[PASS] Missing metrics -> noop with reason")
    
    # Invalid environment
    response = agent.decide({
        "environment": "invalid",
        "event_type": "test",
        "metrics": {"cpu_percent": 50, "memory_percent": 50, "error_rate": 0.01}
    })
    assert response["action"] == "noop"
    assert "Invalid environment" in response["reason"]
    print("[PASS] Invalid environment -> noop with reason")

def test_determinism():
    """Test identical input produces identical output"""
    agent = RLDecisionBrain()
    
    request = {
        "environment": "dev",
        "event_type": "high_cpu",
        "metrics": {"cpu_percent": 85, "memory_percent": 50, "error_rate": 0.01}
    }
    
    response1 = agent.decide(request)
    response2 = agent.decide(request)
    
    # Compare all fields except timestamp
    assert response1["action"] == response2["action"]
    assert response1["reason"] == response2["reason"]
    assert response1["environment"] == response2["environment"]
    assert response1["safety_filtered"] == response2["safety_filtered"]
    print("[PASS] Determinism verified (identical input -> identical output)")

def test_action_scope():
    """Test action scope per environment"""
    from rl_decision_brain import Environment
    agent = RLDecisionBrain()
    
    # DEV allows all actions
    assert len(agent.ACTION_SCOPE[Environment.DEV]) == 4
    print("[PASS] DEV action scope: 4 actions")
    
    # STAGE allows 3 actions (no restart)
    assert len(agent.ACTION_SCOPE[Environment.STAGE]) == 3
    print("[PASS] STAGE action scope: 3 actions")
    
    # PROD allows 2 actions (noop, restart only)
    assert len(agent.ACTION_SCOPE[Environment.PROD]) == 2
    print("[PASS] PROD action scope: 2 actions")

def test_health_check():
    """Test health check returns correct status"""
    agent = RLDecisionBrain()
    health = agent.health_check()
    
    assert health["status"] == "healthy"
    assert health["demo_frozen"] == True
    assert health["learning_enabled"] == False
    assert health["exploration_enabled"] == False
    assert health["stateless"] == True
    print("[PASS] Health check verified")

if __name__ == "__main__":
    print("=" * 60)
    print("RL Decision Brain - Safety Validation Test Suite")
    print("=" * 60)
    
    print("\n[1/6] Testing valid requests...")
    test_valid_requests()
    
    print("\n[2/6] Testing safety filtering...")
    test_safety_filtering()
    
    print("\n[3/6] Testing invalid inputs...")
    test_invalid_inputs()
    
    print("\n[4/6] Testing determinism...")
    test_determinism()
    
    print("\n[5/6] Testing action scope...")
    test_action_scope()
    
    print("\n[6/6] Testing health check...")
    test_health_check()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - Agent is production-safe")
    print("=" * 60)
