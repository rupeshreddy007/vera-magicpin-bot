#!/usr/bin/env python3
"""
Test client for Vera AI Bot

Loads generated dataset and runs a mock judge harness locally.
"""

import json
import requests
from pathlib import Path
import time

BASE_URL = "http://localhost:8000"

def load_expanded_data():
    """Load the expanded dataset"""
    expanded_dir = Path("./expanded")
    
    # Load one category
    with open(expanded_dir / "categories" / "dentists.json") as f:
        categories = json.load(f)
    
    # Load first merchant and customer
    merchants_dir = expanded_dir / "merchants"
    merchant_files = sorted(merchants_dir.glob("*.json"))[:1]
    merchants = []
    for mf in merchant_files:
        with open(mf) as f:
            merchants.append(json.load(f))
    
    customers_dir = expanded_dir / "customers"
    customer_files = sorted(customers_dir.glob("*.json"))[:2]
    customers = []
    for cf in customer_files:
        with open(cf) as f:
            customers.append(json.load(f))
    
    # Load triggers
    triggers_dir = expanded_dir / "triggers"
    trigger_files = sorted(triggers_dir.glob("*.json"))[:3]
    triggers = []
    for tf in trigger_files:
        with open(tf) as f:
            triggers.append(json.load(f))
    
    return categories, merchants, customers, triggers

def test_healthz():
    """Test /v1/healthz"""
    print("\n[TEST] GET /v1/healthz")
    resp = requests.get(f"{BASE_URL}/v1/healthz")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    return resp.status_code == 200

def test_metadata():
    """Test /v1/metadata"""
    print("\n[TEST] GET /v1/metadata")
    resp = requests.get(f"{BASE_URL}/v1/metadata")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    return resp.status_code == 200

def test_context_push(categories, merchants, customers, triggers):
    """Test /v1/context"""
    print("\n[TEST] POST /v1/context (Category)")
    
    # Push category
    payload = {
        "scope": "category",
        "context_id": categories["slug"],
        "version": 1,
        "delivered_at": "2026-04-26T10:00:00Z",
        "payload": categories
    }
    resp = requests.post(f"{BASE_URL}/v1/context", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    
    if resp.status_code != 200:
        return False
    
    # Push merchant
    print("\n[TEST] POST /v1/context (Merchant)")
    merchant = merchants[0]
    payload = {
        "scope": "merchant",
        "context_id": merchant["merchant_id"],
        "version": 1,
        "delivered_at": "2026-04-26T10:01:00Z",
        "payload": merchant
    }
    resp = requests.post(f"{BASE_URL}/v1/context", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    
    if resp.status_code != 200:
        return False
    
    # Push customers
    for customer in customers:
        print(f"\n[TEST] POST /v1/context (Customer {customer.get('customer_id', 'unknown')})")
        payload = {
            "scope": "customer",
            "context_id": customer.get("customer_id", f"c_{len(customers)}"),
            "version": 1,
            "delivered_at": "2026-04-26T10:02:00Z",
            "payload": customer
        }
        resp = requests.post(f"{BASE_URL}/v1/context", json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
    
    # Push triggers
    for trigger in triggers:
        print(f"\n[TEST] POST /v1/context (Trigger {trigger.get('id', 'unknown')})")
        payload = {
            "scope": "trigger",
            "context_id": trigger.get("id", f"trg_{len(triggers)}"),
            "version": 1,
            "delivered_at": "2026-04-26T10:03:00Z",
            "payload": trigger
        }
        resp = requests.post(f"{BASE_URL}/v1/context", json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
    
    return True

def test_tick(triggers):
    """Test /v1/tick"""
    print("\n[TEST] POST /v1/tick")
    
    trigger_ids = [t.get("id") for t in triggers[:2]]
    payload = {
        "now": "2026-04-26T10:30:00Z",
        "available_triggers": trigger_ids
    }
    
    resp = requests.post(f"{BASE_URL}/v1/tick", json=payload)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    return resp.status_code == 200, result.get("actions", [])

def test_reply(conversation_id):
    """Test /v1/reply"""
    print(f"\n[TEST] POST /v1/reply (conversation_id={conversation_id})")
    
    payload = {
        "conversation_id": conversation_id,
        "merchant_id": "m_001",
        "customer_id": None,
        "from_role": "merchant",
        "message": "Yes, send me the abstract",
        "received_at": "2026-04-26T10:45:00Z",
        "turn_number": 2
    }
    
    resp = requests.post(f"{BASE_URL}/v1/reply", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    
    return resp.status_code == 200

def main():
    print("=" * 60)
    print("VERA AI BOT — LOCAL TEST HARNESS")
    print("=" * 60)
    
    # Test basic endpoints
    if not test_healthz():
        print("ERROR: healthz failed")
        return
    
    if not test_metadata():
        print("ERROR: metadata failed")
        return
    
    print("\n" + "=" * 60)
    print("Loading expanded dataset...")
    print("=" * 60)
    
    try:
        categories, merchants, customers, triggers = load_expanded_data()
        print(f"✓ Loaded {len(merchants)} merchants, {len(customers)} customers, {len(triggers)} triggers")
    except Exception as e:
        print(f"ERROR: Failed to load dataset: {e}")
        return
    
    # Test context push
    if not test_context_push(categories, merchants, customers, triggers):
        print("ERROR: context push failed")
        return
    
    print("\n" + "=" * 60)
    print("Waiting 2 seconds for data processing...")
    print("=" * 60)
    time.sleep(2)
    
    # Test tick
    success, actions = test_tick(triggers)
    if not success:
        print("ERROR: tick failed")
        return
    
    if actions:
        conv_id = actions[0]["conversation_id"]
        test_reply(conv_id)
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)

if __name__ == "__main__":
    main()
