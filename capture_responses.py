#!/usr/bin/env python3
"""Capture actual API responses from running bot_server"""

import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 80)
print("VERA COMPOSER BOT — ACTUAL API RESPONSES")
print("=" * 80)
print(f"Testing {BASE_URL}\n")

def test_get(path):
    """Test GET endpoint and return actual response"""
    try:
        url = f"{BASE_URL}{path}"
        with urllib.request.urlopen(url) as response:
            status = response.status
            body = response.read().decode()
            data = json.loads(body)
            return status, data
    except Exception as e:
        return None, str(e)

def test_post(path, payload):
    """Test POST endpoint and return actual response"""
    try:
        url = f"{BASE_URL}{path}"
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode()
            data = json.loads(body)
            return status, data
    except Exception as e:
        return None, str(e)

# Test 1: Health check
print("1. GET /v1/healthz")
print("-" * 80)
status, resp = test_get("/v1/healthz")
print(f"Status: {status}")
print(f"Response:\n{json.dumps(resp, indent=2)}\n")

# Test 2: Metadata
print("2. GET /v1/metadata")
print("-" * 80)
status, resp = test_get("/v1/metadata")
print(f"Status: {status}")
if isinstance(resp, dict):
    print(f"Response:\n{json.dumps(resp, indent=2)}\n")
else:
    print(f"Error: {resp}\n")

# Test 3: Store merchant context
print("3. POST /v1/context (merchant)")
print("-" * 80)
merchant_ctx = {
    "scope": "merchant",
    "context_id": "m_drmeera_001",
    "version": 1,
    "payload": {
        "identity": {"name": "Dr. Meera Dental", "owner_first_name": "Priya"},
        "performance": {"calls": 18, "views": 240, "ctr": 0.075},
        "signals": ["stale_photos"],
        "offers": [{"title": "Free cleaning", "status": "active"}]
    },
    "delivered_at": "2026-05-02T10:00:00Z"
}
status, resp = test_post("/v1/context", merchant_ctx)
print(f"Status: {status}")
print(f"Response:\n{json.dumps(resp, indent=2)}\n")

# Test 4: Compose message
print("4. POST /v1/tick (compose)")
print("-" * 80)
tick_req = {
    "merchant_id": "m_drmeera_001",
    "category_slug": "dentists",
    "trigger": {
        "type": "performance_dip",
        "payload": {
            "metric": "calls",
            "delta_pct": -0.40,
            "attributed_cause": "stale_photos"
        }
    }
}
status, resp = test_post("/v1/tick", tick_req)
print(f"Status: {status}")
if isinstance(resp, dict):
    print(f"Response:\n{json.dumps(resp, indent=2)}\n")
else:
    print(f"Error: {resp}\n")

print("=" * 80)
