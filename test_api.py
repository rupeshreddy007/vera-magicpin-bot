#!/usr/bin/env python3
"""Test bot_server endpoints"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("TESTING VERA COMPOSER BOT API (FastAPI)")
print("=" * 70)

# Give server time to start
time.sleep(2)

# Test 1: GET /v1/healthz
print("\n1. Testing GET /v1/healthz")
try:
    r = requests.get(f"{BASE_URL}/v1/healthz", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: GET /v1/metadata
print("\n2. Testing GET /v1/metadata")
try:
    r = requests.get(f"{BASE_URL}/v1/metadata", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: POST /v1/context (store merchant context)
print("\n3. Testing POST /v1/context (store merchant)")
context_payload = {
    "scope": "merchant",
    "context_id": "m_drmeera_001",
    "version": 1,
    "payload": {
        "identity": {
            "name": "Dr. Meera Dental",
            "owner_first_name": "Priya"
        },
        "performance": {
            "calls": 18,
            "views": 240,
            "ctr": 0.075
        },
        "signals": ["stale_photos"],
        "offers": [{"title": "Free cleaning", "status": "active"}]
    },
    "delivered_at": "2026-05-02T10:00:00Z"
}
try:
    r = requests.post(f"{BASE_URL}/v1/context", json=context_payload, timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: POST /v1/tick (compose message)
print("\n4. Testing POST /v1/tick (compose message)")
tick_payload = {
    "trigger_id": "perf_dip_001",
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
try:
    r = requests.post(f"{BASE_URL}/v1/tick", json=tick_payload, timeout=5
        }
    }
}
try:
    r = requests.post(f"{BASE_URL}/v1/tick", json=tick_payload, timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("TESTS COMPLETE")
print("=" * 70)
