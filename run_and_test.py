#!/usr/bin/env python3
"""Start bot_server, test all endpoints, print responses, then stop."""

import subprocess
import urllib.request
import json
import time
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Start server as subprocess
print("Starting bot_server on port 8000...")
server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "bot_server:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(3)

def get(path):
    url = f"http://127.0.0.1:8000{path}"
    with urllib.request.urlopen(url) as r:
        return r.status, json.loads(r.read().decode())

def post(path, data):
    url = f"http://127.0.0.1:8000{path}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read().decode())

try:
    print("\n" + "=" * 80)
    print("VERA COMPOSER BOT — ACTUAL API RESPONSES")
    print("=" * 80)

    # 1. Healthz
    print("\n1. GET /v1/healthz")
    print("-" * 80)
    status, resp = get("/v1/healthz")
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    # 2. Metadata
    print("\n2. GET /v1/metadata")
    print("-" * 80)
    status, resp = get("/v1/metadata")
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    # 3. Context — store category
    print("\n3a. POST /v1/context (category)")
    print("-" * 80)
    cat_ctx = {
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": {
            "slug": "dentists",
            "display_name": "Dentists & Dental Clinics",
            "voice_rules": {"tone": "clinical", "emoji": False}
        },
        "delivered_at": "2026-05-02T10:00:00Z"
    }
    status, resp = post("/v1/context", cat_ctx)
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    # 3b. Context — store merchant
    print("\n3b. POST /v1/context (merchant)")
    print("-" * 80)
    merch_ctx = {
        "scope": "merchant",
        "context_id": "m_drmeera_001",
        "version": 1,
        "payload": {
            "category_slug": "dentists",
            "identity": {"name": "Dr. Meera Dental", "owner_first_name": "Priya"},
            "performance": {"calls": 18, "views": 240, "ctr": 0.075},
            "signals": ["stale_photos"],
            "offers": [{"title": "Free cleaning", "status": "active"}]
        },
        "delivered_at": "2026-05-02T10:00:00Z"
    }
    status, resp = post("/v1/context", merch_ctx)
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    # 3c. Context — store customer
    print("\n3c. POST /v1/context (customer)")
    print("-" * 80)
    cust_ctx = {
        "scope": "customer",
        "context_id": "c_rahul_001",
        "version": 1,
        "payload": {
            "name": "Rahul",
            "last_visit": "2026-04-15",
            "visits_count": 3
        },
        "delivered_at": "2026-05-02T10:00:00Z"
    }
    status, resp = post("/v1/context", cust_ctx)
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    # 3d. Context — store trigger
    print("\n3d. POST /v1/context (trigger)")
    print("-" * 80)
    trig_ctx = {
        "scope": "trigger",
        "context_id": "trig_perf_dip_001",
        "version": 1,
        "payload": {
            "merchant_id": "m_drmeera_001",
            "customer_id": "c_rahul_001",
            "kind": "perf_dip",
            "scope": "merchant",
            "payload": {
                "metric": "calls",
                "delta_pct": -0.40,
                "attributed_cause": "stale_photos"
            }
        },
        "delivered_at": "2026-05-02T10:00:00Z"
    }
    status, resp = post("/v1/context", trig_ctx)
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    # 4. Tick (compose message)
    print("\n4. POST /v1/tick")
    print("-" * 80)
    tick = {
        "now": "2026-05-02T19:55:00Z",
        "available_triggers": ["trig_perf_dip_001"]
    }
    status, resp = post("/v1/tick", tick)
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    # 5. Reply (judge format: only conversation_id, from_role, message, turn_number)
    print("\n5. POST /v1/reply")
    print("-" * 80)
    # Get conversation_id from tick response if available
    conv_id = "conv_test"
    if isinstance(resp, dict) and "actions" in resp:
        actions = resp["actions"]
        if actions:
            conv_id = actions[0].get("conversation_id", conv_id)
    reply = {
        "conversation_id": conv_id,
        "from_role": "merchant",
        "message": "Yes, send me the abstract",
        "turn_number": 2
    }
    status, resp = post("/v1/reply", reply)
    print(f"Status: {status}")
    print(json.dumps(resp, indent=2))

    print("\n" + "=" * 80)
    print("ALL ENDPOINTS WORKING")
    print("=" * 80)

except Exception as e:
    print(f"\nERROR: {e}")
    # Print server stderr for debugging
    server.terminate()
    err = server.stderr.read().decode()
    if err:
        print(f"\nServer logs:\n{err}")
    sys.exit(1)

finally:
    server.terminate()
    server.wait()
    print("\nServer stopped.")
