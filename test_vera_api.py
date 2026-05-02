#!/usr/bin/env python3
"""
Test vera_api.py endpoints locally
"""

import json
import requests
from time import sleep

BASE_URL = "http://localhost:5000"

def test_healthz():
    """Test health check"""
    print("\n=== TEST: /v1/healthz ===")
    resp = requests.get(f"{BASE_URL}/v1/healthz")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    assert resp.status_code == 200


def test_metadata():
    """Test metadata endpoint"""
    print("\n=== TEST: /v1/metadata ===")
    resp = requests.get(f"{BASE_URL}/v1/metadata")
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Name: {data['name']}")
    print(f"Version: {data['version']}")
    print(f"Features: {len(data['features'])}")
    print(f"Endpoints: {len(data['endpoints'])}")
    assert resp.status_code == 200


def test_store_context():
    """Test storing merchant context"""
    print("\n=== TEST: POST /v1/context (Merchant) ===")
    
    merchant_context = {
        "scope": "merchant",
        "context_id": "m_001_drmeera",
        "version": 1,
        "payload": {
            "identity": {
                "name": "Dr. Meera's Dental Clinic",
                "owner_first_name": "Meera"
            },
            "performance": {
                "calls": 18,
                "rating": 4.8
            },
            "offers": [
                {"title": "Cleaning ₹499", "status": "active"}
            ],
            "signals": ["stale_photos"]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/v1/context", json=merchant_context)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Accepted: {data['accepted']}")
    print(f"Ack ID: {data.get('ack_id')}")
    assert resp.status_code == 200
    assert data['accepted'] == True


def test_store_category():
    """Test storing category context"""
    print("\n=== TEST: POST /v1/context (Category) ===")
    
    category_context = {
        "scope": "category",
        "context_id": "cat_dentists",
        "version": 1,
        "payload": {
            "slug": "dentists",
            "name": "Dental Clinics",
            "peer_stats": {
                "avg_calls": 15.6,
                "avg_rating": 4.5
            },
            "digest": [
                {
                    "title": "3-month fluoride recall outperforms 6-month",
                    "source": "JIDA Oct 2026"
                }
            ]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/v1/context", json=category_context)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Accepted: {data['accepted']}")
    assert resp.status_code == 200


def test_compose_message():
    """Test message composition via /v1/tick"""
    print("\n=== TEST: POST /v1/tick (Compose Message) ===")
    
    trigger = {
        "trigger_id": "trig_perf_dip_001",
        "merchant_id": "m_001_drmeera",
        "category_id": "cat_dentists",
        "trigger_type": "performance_dip",
        "payload": {
            "metric": "calls",
            "delta_pct": -0.40,
            "signals": ["stale_photos"]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/v1/tick", json=trigger)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    
    if data['success']:
        msg = data['message']
        print(f"Trigger ID: {data['trigger_id']}")
        print(f"Message Body: {msg['body']}")
        print(f"CTA Type: {msg['cta']}")
        print(f"Template: {msg['template_name']}")
        print(f"Suppression Key: {msg['suppression_key']}")
        assert resp.status_code == 200
    else:
        print(f"Error: {data['error']}")
        assert False, "Composition failed"


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("VERA API TESTS")
    print("=" * 70)
    
    try:
        test_healthz()
        test_metadata()
        test_store_context()
        test_store_category()
        test_compose_message()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise


if __name__ == "__main__":
    print("Starting tests in 2 seconds... (make sure vera_api.py is running)")
    sleep(2)
    run_all_tests()
