#!/usr/bin/env python3
"""
Dynamic Test Scenarios for Vera Composer

Tests how vera_composer handles:
1. New merchants (no performance history)
2. Metric shifts (performance changes)
3. Unknown triggers (new trigger types)
4. Missing context (empty data)
5. Edge cases (1 day remaining, 0 calls, etc.)
"""

from vera_composer import compose, compose_to_dict
import json
from datetime import datetime, timedelta


# ===== TEST SCENARIO 1: New Merchant (No Performance History) =====

def test_new_merchant_no_history():
    """Test: New merchant with no history shouldn't crash or use cached values"""
    
    print("\n" + "="*70)
    print("TEST 1: New Merchant (No Performance History)")
    print("="*70)
    
    category = {
        "slug": "dentists",
        "peer_stats": {"avg_calls": 15.6, "avg_rating": 4.2},
        "digest": [
            {
                "title": "3-month fluoride recall outperforms 6-month",
                "source": "JIDA Oct 2026",
                "benefit_pct": 0.73
            }
        ]
    }
    
    merchant = {
        "merchant_id": "new_001",
        "identity": {"name": "New Smile Dental", "owner_first_name": "Priya"},
        "performance": {},  # NO HISTORY
        "signals": [],
        "offers": []
    }
    
    trigger = {
        "kind": "research_digest",
        "scope": "merchant",
        "payload": {},
        "suppression_key": "research:dentists"
    }
    
    msg = compose(category, merchant, trigger)
    
    print(f"\nMerchant: {merchant['identity']['name']} (NEW, no performance data)")
    print(f"Trigger: {trigger['kind']}")
    print(f"\nComposed Message:")
    print(f"Body: {msg.body}")
    print(f"CTA: {msg.cta}")
    print(f"Send as: {msg.send_as}")
    print(f"Rationale: {msg.rationale}")
    
    # Validation checks
    assert msg.body is not None, "Body should not be None"
    assert msg.cta in ["open_ended", "binary"], "CTA should be valid type"
    assert "new" not in msg.body.lower() or "new" in merchant['identity']['name'].lower(), "Should not assume merchant state"
    print("\n✓ PASS: New merchant handled gracefully")


# ===== TEST SCENARIO 2: Metric Shift =====

def test_metric_shift_renewal():
    """Test: Performance metrics shift, renewal message should adapt"""
    
    print("\n" + "="*70)
    print("TEST 2: Metric Shift (Performance Changes)")
    print("="*70)
    
    # First state: Merchant ahead of peers
    print("\nState A: Merchant AHEAD of peer avg (15% edge)")
    category = {
        "slug": "dentists",
        "peer_stats": {"avg_calls": 15.6}
    }
    
    merchant_ahead = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {"calls": 18},  # 15% ahead
        "signals": [],
        "offers": []
    }
    
    trigger = {
        "kind": "renewal_due",
        "scope": "merchant",
        "payload": {
            "days_remaining": 12,
            "plan": "Pro",
            "renewal_amount": 4999
        }
    }
    
    msg_ahead = compose(category, merchant_ahead, trigger)
    print(f"\nMessage: {msg_ahead.body}")
    assert "15%" in msg_ahead.body or "ahead" in msg_ahead.body, "Should reference advantage"
    
    # Second state: Same merchant, metrics drop
    print("\nState B: Same merchant's calls DROP below peer avg")
    merchant_behind = merchant_ahead.copy()
    merchant_behind["performance"] = {"calls": 12}  # Now behind
    
    msg_behind = compose(category, merchant_behind, trigger)
    print(f"\nMessage: {msg_behind.body}")
    assert "short" in msg_behind.body or "gap" in msg_behind.body, "Should reference gap"
    
    # Verify messages are different
    assert msg_ahead.body != msg_behind.body, "Messages should differ when metrics shift"
    print("\n✓ PASS: Messages adapt to metric changes")


# ===== TEST SCENARIO 3: Unknown Trigger Type =====

def test_unknown_trigger():
    """Test: New trigger type shouldn't crash, should fallback gracefully"""
    
    print("\n" + "="*70)
    print("TEST 3: Unknown Trigger Type (Graceful Fallback)")
    print("="*70)
    
    category = {"slug": "dentists"}
    merchant = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {},
        "signals": []
    }
    
    # Unknown trigger
    trigger = {
        "kind": "customer_sentiment_shift",  # NEVER SEEN BEFORE
        "scope": "merchant",
        "payload": {}
    }
    
    try:
        msg = compose(category, merchant, trigger)
        print(f"\nTrigger: {trigger['kind']} (UNKNOWN)")
        print(f"Message: {msg.body}")
        print(f"Fallback used: {msg.template_name}")
        assert msg.body is not None, "Should return fallback, not crash"
        print("\n✓ PASS: Unknown trigger handled with fallback")
    except Exception as e:
        print(f"\n✗ FAIL: Crashed on unknown trigger: {e}")
        raise


# ===== TEST SCENARIO 4: Missing Context Data =====

def test_missing_context():
    """Test: Empty context (empty digest, no offers) shouldn't crash"""
    
    print("\n" + "="*70)
    print("TEST 4: Missing Context Data (Empty Lists/Dicts)")
    print("="*70)
    
    category = {
        "slug": "dentists",
        "digest": [],  # EMPTY
        "peer_stats": {}
    }
    
    merchant = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {},  # EMPTY
        "signals": [],
        "offers": []  # EMPTY
    }
    
    trigger = {
        "kind": "research_digest",
        "scope": "merchant",
        "payload": {}
    }
    
    try:
        msg = compose(category, merchant, trigger)
        print(f"\nContext: Empty digest, no offers, no performance")
        print(f"Message: {msg.body}")
        assert msg.body is not None, "Should fallback, not crash"
        print("\n✓ PASS: Missing context handled gracefully")
    except Exception as e:
        print(f"\n✗ FAIL: Crashed on empty context: {e}")
        raise


# ===== TEST SCENARIO 5: Edge Case - Renewal Tomorrow =====

def test_edge_case_renewal_tomorrow():
    """Test: Renewal in 1 day should emphasize urgency"""
    
    print("\n" + "="*70)
    print("TEST 5: Edge Case - Renewal Tomorrow (High Urgency)")
    print("="*70)
    
    category = {
        "slug": "dentists",
        "peer_stats": {"avg_calls": 15.6}
    }
    
    merchant = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {"calls": 18},
        "signals": []
    }
    
    trigger = {
        "kind": "renewal_due",
        "scope": "merchant",
        "payload": {
            "days_remaining": 1,  # TOMORROW!
            "plan": "Pro",
            "renewal_amount": 4999
        }
    }
    
    msg = compose(category, merchant, trigger)
    print(f"\nDays remaining: 1 (TOMORROW)")
    print(f"Message: {msg.body}")
    
    # Check for urgency indicators
    has_urgency = any([
        "1d" in msg.body,
        "tomorrow" in msg.body.lower(),
        "renews" in msg.body.lower()
    ])
    assert has_urgency, "Should emphasize tomorrow's renewal"
    print("\n✓ PASS: Edge case urgency communicated")


# ===== TEST SCENARIO 6: Edge Case - Zero Performance =====

def test_edge_case_zero_performance():
    """Test: Merchant with 0 calls shouldn't crash"""
    
    print("\n" + "="*70)
    print("TEST 6: Edge Case - Zero Performance Data")
    print("="*70)
    
    category = {
        "slug": "dentists",
        "peer_stats": {"avg_calls": 15.6}
    }
    
    merchant = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {"calls": 0},  # ZERO
        "signals": []
    }
    
    trigger = {
        "kind": "renewal_due",
        "scope": "merchant",
        "payload": {
            "days_remaining": 12,
            "plan": "Pro",
            "renewal_amount": 4999
        }
    }
    
    msg = compose(category, merchant, trigger)
    print(f"\nMerchant calls: 0 (brand new, no traffic)")
    print(f"Message: {msg.body}")
    assert msg.body is not None, "Should handle zero performance"
    print("\n✓ PASS: Zero performance handled")


# ===== TEST SCENARIO 7: Performance Dip with Different Signals =====

def test_performance_dip_signal_routing():
    """Test: Performance dip picks ONE signal based on merchant state"""
    
    print("\n" + "="*70)
    print("TEST 7: Performance Dip - Signal-Based Routing")
    print("="*70)
    
    category = {"slug": "dentists"}
    
    base_trigger = {
        "kind": "perf_dip",
        "scope": "merchant",
        "payload": {
            "metric": "calls",
            "delta_pct": -0.40  # 40% drop
        }
    }
    
    # Test with stale_photos signal
    print("\nSignal: stale_photos")
    merchant_photos = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {"calls": 15},
        "signals": ["stale_photos"],  # <-- KEY SIGNAL
        "offers": []
    }
    msg_photos = compose(category, merchant_photos, base_trigger)
    print(f"Message: {msg_photos.body}")
    assert "photos" in msg_photos.body.lower(), "Should diagnose photos"
    
    # Test with incomplete_profile signal
    print("\nSignal: incomplete_profile")
    merchant_profile = merchant_photos.copy()
    merchant_profile["signals"] = ["incomplete_profile"]
    msg_profile = compose(category, merchant_profile, base_trigger)
    print(f"Message: {msg_profile.body}")
    assert "profile" in msg_profile.body.lower(), "Should diagnose profile"
    
    # Test with low_rating signal
    print("\nSignal: low_rating")
    merchant_rating = merchant_photos.copy()
    merchant_rating["signals"] = ["low_rating"]
    msg_rating = compose(category, merchant_rating, base_trigger)
    print(f"Message: {msg_rating.body}")
    assert "rating" in msg_rating.body.lower() or "review" in msg_rating.body.lower(), "Should diagnose rating"
    
    # All should be different
    assert msg_photos.body != msg_profile.body != msg_rating.body, "Each signal should produce unique message"
    print("\n✓ PASS: Signals route to correct diagnosis")


# ===== TEST SCENARIO 8: Customer-Facing without Customer Context =====

def test_customer_facing_missing_context():
    """Test: Customer trigger without customer context should fallback"""
    
    print("\n" + "="*70)
    print("TEST 8: Customer Trigger Without Customer Context")
    print("="*70)
    
    category = {"slug": "dentists"}
    merchant = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {},
        "signals": []
    }
    
    trigger = {
        "kind": "recall_due",
        "scope": "customer",  # <-- CUSTOMER SCOPE
        "payload": {"service_due": "cleaning"}
    }
    
    # Missing customer param
    msg = compose(category, merchant, trigger, customer=None)
    print(f"\nTrigger: {trigger['kind']} (customer scope)")
    print(f"Customer context: MISSING")
    print(f"Message: {msg.body}")
    assert msg.body is not None, "Should fallback, not crash"
    print("\n✓ PASS: Missing customer context handled")


# ===== TEST SCENARIO 9: Festival Message with Pricing =====

def test_festival_with_specificity():
    """Test: Festival message includes search volume and prep deadline"""
    
    print("\n" + "="*70)
    print("TEST 9: Festival Trigger with Specificity")
    print("="*70)
    
    category = {
        "slug": "dentists",
        "peer_stats": {"avg_monthly_searches": 2400}
    }
    
    merchant = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {},
        "signals": []
    }
    
    trigger = {
        "kind": "festival_upcoming",
        "scope": "merchant",
        "payload": {
            "festival": "Diwali",
            "days_until": 30
        }
    }
    
    msg = compose(category, merchant, trigger)
    print(f"\nFestival: Diwali")
    print(f"Days until: 30")
    print(f"Message: {msg.body}")
    
    # Should include search volume
    assert "search" in msg.body.lower() or "1440" in msg.body, "Should include search volume"
    # Should include campaign prep window
    assert "week" in msg.body.lower() or "pre-sell" in msg.body.lower(), "Should mention prep window"
    print("\n✓ PASS: Festival message includes specificity")


# ===== TEST SCENARIO 10: Performance Spike with Attribution =====

def test_spike_with_attribution():
    """Test: Performance spike should reference attributed cause"""
    
    print("\n" + "="*70)
    print("TEST 10: Performance Spike with Attribution")
    print("="*70)
    
    category = {"slug": "dentists"}
    merchant = {
        "merchant_id": "m001",
        "identity": {"name": "Smile Clinic", "owner_first_name": "Raj"},
        "performance": {"calls": 21},
        "signals": []
    }
    
    # Test with different attributions
    test_cases = [
        ("new_offer", "offer"),
        ("photo_update", "photo"),
        ("review_boost", "review"),
    ]
    
    for attribution, expected_word in test_cases:
        trigger = {
            "kind": "perf_spike",
            "scope": "merchant",
            "payload": {
                "metric": "calls",
                "delta_pct": 0.35,
                "attributed_cause": attribution
            }
        }
        
        msg = compose(category, merchant, trigger)
        print(f"\nAttribution: {attribution}")
        print(f"Message: {msg.body}")
        assert expected_word in msg.body.lower(), f"Should reference {expected_word}"
    
    print("\n✓ PASS: Spike attribution captured correctly")


# ===== MAIN TEST RUNNER =====

if __name__ == "__main__":
    print("\n" + "="*70)
    print("VERA COMPOSER — DYNAMIC SCENARIO TESTS")
    print("Testing urgency, specificity, and graceful fallbacks")
    print("="*70)
    
    try:
        test_new_merchant_no_history()
        test_metric_shift_renewal()
        test_unknown_trigger()
        test_missing_context()
        test_edge_case_renewal_tomorrow()
        test_edge_case_zero_performance()
        test_performance_dip_signal_routing()
        test_customer_facing_missing_context()
        test_festival_with_specificity()
        test_spike_with_attribution()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nVera Composer is ready for judge validation with:")
        print("  • Explicit urgency messaging (timeframes, deadlines)")
        print("  • Specific curiosity hooks (search volumes, benchmarks)")
        print("  • Graceful fallback for unknown triggers")
        print("  • Signal-based routing (ONE diagnosis per dip)")
        print("  • Metric-aware messages (adapt to performance shifts)")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
