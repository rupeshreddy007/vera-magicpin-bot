#!/usr/bin/env python3
"""
Full 5-Phase Judge Flow Test (no LLM needed)
=============================================
Mimics the judge's exact testing protocol against our bot_server.
Starts the server, runs all 5 phases, prints scores, then stops.
"""

import subprocess
import http.client
import json
import time
import sys
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DATASET_DIR = Path("dataset")
BASE_URL = "http://127.0.0.1:8000"

# ===== Persistent HTTP connection =====

conn = None

def get_conn():
    global conn
    if conn is None:
        conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=30)
    return conn

def reset_conn():
    global conn
    try:
        if conn:
            conn.close()
    except:
        pass
    conn = None

def get(path):
    try:
        c = get_conn()
        c.request("GET", path)
        r = c.getresponse()
        return r.status, json.loads(r.read().decode())
    except Exception as e:
        reset_conn()
        raise

def post(path, data):
    try:
        c = get_conn()
        body = json.dumps(data).encode()
        c.request("POST", path, body=body, headers={"Content-Type": "application/json"})
        r = c.getresponse()
        return r.status, json.loads(r.read().decode())
    except Exception as e:
        reset_conn()
        raise

def push_context(scope, context_id, version, payload):
    return post("/v1/context", {
        "scope": scope,
        "context_id": context_id,
        "version": version,
        "payload": payload,
        "delivered_at": datetime.utcnow().isoformat() + "Z"
    })

def tick(trigger_ids):
    return post("/v1/tick", {
        "now": datetime.utcnow().isoformat() + "Z",
        "available_triggers": trigger_ids
    })

def reply(conv_id, message, turn, from_role="merchant"):
    return post("/v1/reply", {
        "conversation_id": conv_id,
        "from_role": from_role,
        "message": message,
        "turn_number": turn
    })

# ===== Load Dataset =====

def load_dataset():
    categories = {}
    merchants = {}
    customers = {}
    triggers = {}

    cat_dir = DATASET_DIR / "categories"
    if cat_dir.exists():
        for f in cat_dir.glob("*.json"):
            data = json.load(open(f))
            categories[data.get("slug", f.stem)] = data

    for fname, store, key in [
        ("merchants_seed.json", merchants, "merchant_id"),
        ("customers_seed.json", customers, "customer_id"),
        ("triggers_seed.json", triggers, "id"),
    ]:
        path = DATASET_DIR / fname
        if path.exists():
            data = json.load(open(path))
            # Handle both flat list and nested structure
            items = data if isinstance(data, list) else data.get("merchants", data.get("customers", data.get("triggers", [])))
            if isinstance(items, list):
                for item in items:
                    if key in item:
                        store[item[key]] = item

    return categories, merchants, customers, triggers

# ===== Scoring (heuristic, no LLM) =====

def score_message(body, cta, category, merchant, trigger):
    """Heuristic scorer — approximates LLM judge dimensions."""
    scores = {}

    # 1. Specificity: numbers, percentages, dates
    nums = re.findall(r'\d+', body)
    pcts = re.findall(r'\d+%', body)
    scores["specificity"] = min(10, 3 + len(nums) * 2 + len(pcts))

    # 2. Category fit: check voice match
    cat_slug = category.get("slug", "")
    voice = category.get("voice", {})
    tone = voice.get("tone", "")
    has_emoji = bool(re.search(r'[\U0001f600-\U0001f9ff]', body))
    emoji_ok = voice.get("emoji", True)
    scores["category_fit"] = 7
    if has_emoji and not emoji_ok:
        scores["category_fit"] -= 3
    if cat_slug == "dentists" and ("patient" in body.lower() or "dr" in body.lower()):
        scores["category_fit"] += 2

    # 3. Merchant fit: uses owner name, merchant name
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    name = merchant.get("identity", {}).get("name", "")
    scores["merchant_fit"] = 5
    if owner and owner.lower() in body.lower():
        scores["merchant_fit"] += 3
    if name and name.lower() in body.lower():
        scores["merchant_fit"] += 2

    # 4. Trigger relevance: references trigger data
    trigger_kind = trigger.get("kind", "")
    scores["trigger_relevance"] = 6
    if trigger_kind in body.lower() or any(k in body.lower() for k in ["drop", "dip", "spike", "renew", "festival"]):
        scores["trigger_relevance"] += 2

    # 5. Engagement: has CTA, urgency words
    urgency_words = ["this week", "today", "by friday", "now", "before", "deadline"]
    scores["engagement"] = 5
    if cta and cta != "none":
        scores["engagement"] += 2
    if any(w in body.lower() for w in urgency_words):
        scores["engagement"] += 2
    if "?" in body:
        scores["engagement"] += 1

    # Cap at 10
    for k in scores:
        scores[k] = min(10, max(0, scores[k]))

    scores["total"] = sum(scores.values())
    scores["max"] = 50
    return scores

# ===== Main Test Flow =====

print("Starting bot_server...")
server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "bot_server:app", "--host", "127.0.0.1", "--port", "8000",
     "--timeout-keep-alive", "5"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(4)

try:
    categories, merchants, customers, triggers = load_dataset()
    print(f"Dataset: {len(categories)} categories, {len(merchants)} merchants, "
          f"{len(customers)} customers, {len(triggers)} triggers\n")

    all_scores = []

    # =========================================================================
    # PHASE 1: WARMUP
    # =========================================================================
    print("=" * 80)
    print("PHASE 1: WARMUP — Health + Metadata + Context Load")
    print("=" * 80)

    status, resp = get("/v1/healthz")
    print(f"  [{'PASS' if status == 200 else 'FAIL'}] GET /v1/healthz — status={resp.get('status')}")

    status, resp = get("/v1/metadata")
    print(f"  [{'PASS' if status == 200 else 'FAIL'}] GET /v1/metadata — team={resp.get('team_name')}")

    # Push all categories
    for slug, cat in categories.items():
        status, resp = push_context("category", slug, 1, cat)
        ok = "PASS" if resp.get("accepted") else "FAIL"
        print(f"  [{ok}] context/category/{slug}")

    # Push merchants
    for mid, m in list(merchants.items()):
        status, resp = push_context("merchant", mid, 1, m)
        ok = "PASS" if resp.get("accepted") else "FAIL"
        print(f"  [{ok}] context/merchant/{mid[:20]}")

    # Push customers (ALL — triggers reference later customer IDs)
    for cid, c in list(customers.items()):
        status, resp = push_context("customer", cid, 1, c)
        ok = "PASS" if resp.get("accepted") else "FAIL"
        print(f"  [{ok}] context/customer/{cid[:20]}")

    print()

    # =========================================================================
    # PHASE 2: TEST WINDOW (simulated 60 min, tick every 5 min = 12 ticks)
    # =========================================================================
    print("=" * 80)
    print("PHASE 2: TEST WINDOW — 12 ticks (simulated 60 minutes)")
    print("=" * 80)

    trigger_ids = list(triggers.keys())
    # Push all triggers
    for tid, trig in triggers.items():
        push_context("trigger", tid, 1, trig)

    total_actions = 0
    for tick_num in range(1, 13):
        # Each tick sends a subset of triggers
        batch_start = (tick_num - 1) * max(1, len(trigger_ids) // 12)
        batch_end = tick_num * max(1, len(trigger_ids) // 12)
        batch = trigger_ids[batch_start:batch_end] if trigger_ids else []

        if not batch:
            batch = trigger_ids[:3] if trigger_ids else []

        try:
            status, resp = tick(batch)
            actions = resp.get("actions", []) if isinstance(resp, dict) else []
            total_actions += len(actions)

            print(f"  Tick {tick_num:2d}/12 | triggers={len(batch):2d} | actions={len(actions)} ", end="")

            if actions:
                # Score first action
                action = actions[0]
                body = action.get("body", "")
                merchant_id = action.get("merchant_id", "")
                trigger_id = action.get("trigger_id", "")

                cat = categories.get(merchants.get(merchant_id, {}).get("category_slug", ""), {})
                merch = merchants.get(merchant_id, {})
                trig = triggers.get(trigger_id, {})

                scores = score_message(body, action.get("cta", ""), cat, merch, trig)
                all_scores.append(scores)
                print(f"| score={scores['total']}/50 | \"{body[:60]}...\"")
            else:
                print("| (no actions)")
        except Exception as e:
            print(f"  Tick {tick_num:2d}/12 | [TIMEOUT] {e}")
            reset_conn()
            time.sleep(1)

        time.sleep(0.3)  # Prevent connection exhaustion on Windows

    print(f"\n  Total actions composed: {total_actions}")
    print()

    # =========================================================================
    # PHASE 3: ADAPTIVE INJECTION — mid-test context changes
    # =========================================================================
    print("=" * 80)
    print("PHASE 3: ADAPTIVE INJECTION — Fresh data mid-test")
    print("=" * 80)

    # Reset connection and let server recover
    reset_conn()
    time.sleep(2)

    # Simulate metric shift for first merchant
    if merchants:
        mid = list(merchants.keys())[0]
        m = merchants[mid].copy()
        m["performance"] = {**m.get("performance", {}), "calls": 5, "views": 50, "ctr": 0.02}
        m["signals"] = ["stale_photos", "low_rating"]
        try:
            status, resp = push_context("merchant", mid, 2, m)
            print(f"  [INJECT] Metric shift for {mid[:20]} (v2) — accepted={resp.get('accepted')}")
        except Exception as e:
            print(f"  [WARN] Context push timed out: {e}")
            # Restart connection
            time.sleep(2)

    # Push a new trigger
    new_trigger = {
        "id": "trg_injected_festival",
        "merchant_id": list(merchants.keys())[0] if merchants else "m_test",
        "customer_id": list(customers.keys())[0] if customers else None,
        "kind": "festival_upcoming",
        "scope": "merchant",
        "payload": {"festival": "Diwali", "days_until": 7, "expected_demand_lift": 2.5}
    }
    try:
        push_context("trigger", "trg_injected_festival", 1, new_trigger)
        print(f"  [INJECT] New trigger: festival_upcoming (Diwali in 7 days)")
    except Exception as e:
        print(f"  [WARN] Trigger push failed: {e}")

    # Tick with injected trigger
    try:
        status, resp = tick(["trg_injected_festival"])
        actions = resp.get("actions", []) if isinstance(resp, dict) else []
        if actions:
            body = actions[0].get("body", "")
            print(f"  [RESULT] Bot composed: \"{body[:80]}...\"")
            cat = categories.get(merchants.get(new_trigger["merchant_id"], {}).get("category_slug", ""), {})
            scores = score_message(body, actions[0].get("cta", ""), cat,
                                 merchants.get(new_trigger["merchant_id"], {}), new_trigger)
            all_scores.append(scores)
            print(f"  [SCORE] {scores['total']}/50")
        else:
            print(f"  [RESULT] No action (bot chose not to send)")
    except Exception as e:
        print(f"  [WARN] Tick failed: {e}")

    print()

    # =========================================================================
    # PHASE 4: REPLAY TEST — replies, intent transitions, hostile
    # =========================================================================
    print("=" * 80)
    print("PHASE 4: REPLAY TEST — Replies, Intent Transitions, Hostile")
    print("=" * 80)

    reset_conn()
    time.sleep(1)

    try:
        # Get a conversation_id from previous tick
        conv_id = None
        if actions:
            conv_id = actions[0].get("conversation_id")

        if not conv_id:
            # Create one via tick
            if trigger_ids:
                push_context("trigger", trigger_ids[0], 1, triggers[trigger_ids[0]])
                status, resp = tick([trigger_ids[0]])
                acts = resp.get("actions", []) if isinstance(resp, dict) else []
                if acts:
                    conv_id = acts[0].get("conversation_id")

        # 4a. Positive reply
        print("\n  --- 4a. Merchant says YES ---")
        if conv_id:
            status, resp = reply(conv_id, "Yes, let's do it. What's next?", 2)
            print(f"  Action: {resp.get('action', '?')}")
            if resp.get("body"):
                print(f"  Body: \"{resp['body'][:80]}\"")
        else:
            print("  [SKIP] No conversation available")

        # 4b. Auto-reply detection
        print("\n  --- 4b. Auto-reply detection ---")
        auto_msg = "Thank you for contacting us! Our team will respond shortly."
        for turn in range(2, 6):
            status, resp = reply(f"conv_auto_test", auto_msg, turn)
            action = resp.get("action", "?")
            print(f"  Turn {turn}: action={action}", end="")
            if action == "end":
                print(" — Detected auto-reply!")
                break
            elif action == "wait":
                print(f" (wait {resp.get('wait_seconds', '?')}s)")
            else:
                print(f" body=\"{resp.get('body', '')[:40]}\"")

        # 4c. Hostile message
        print("\n  --- 4c. Hostile/spam complaint ---")
        status, resp = reply("conv_hostile_test", "Stop messaging me. This is useless spam. I will report you.", 2)
        action = resp.get("action", "?")
        print(f"  Action: {action}")
        if action == "end":
            print("  [PASS] Bot correctly ended conversation")
        elif action == "wait":
            print("  [PASS] Bot chose to wait (acceptable)")
        else:
            print(f"  [WARN] Bot sent: \"{resp.get('body', '')[:60]}\"")

        # 4d. Off-topic
        print("\n  --- 4d. Off-topic message ---")
        status, resp = reply("conv_offtopic_test", "What's the weather like today?", 2)
        print(f"  Action: {resp.get('action', '?')}")
        if resp.get("body"):
            print(f"  Body: \"{resp['body'][:60]}\"")

    except Exception as e:
        print(f"\n  [WARN] Phase 4 error: {e}")

    print()

    # =========================================================================
    # PHASE 5: SCORE REPORT
    # =========================================================================
    print("=" * 80)
    print("PHASE 5: SCORE REPORT")
    print("=" * 80)

    if all_scores:
        avg_spec = sum(s["specificity"] for s in all_scores) / len(all_scores)
        avg_cat = sum(s["category_fit"] for s in all_scores) / len(all_scores)
        avg_merch = sum(s["merchant_fit"] for s in all_scores) / len(all_scores)
        avg_trig = sum(s["trigger_relevance"] for s in all_scores) / len(all_scores)
        avg_eng = sum(s["engagement"] for s in all_scores) / len(all_scores)
        avg_total = sum(s["total"] for s in all_scores) / len(all_scores)

        print(f"\n  Messages scored: {len(all_scores)}")
        print(f"  {'─' * 50}")
        print(f"  {'Dimension':<25} {'Avg':>6} {'/ Max':>6}")
        print(f"  {'─' * 50}")
        print(f"  {'Specificity':<25} {avg_spec:>6.1f} {'/ 10':>6}")
        print(f"  {'Category Fit':<25} {avg_cat:>6.1f} {'/ 10':>6}")
        print(f"  {'Merchant Fit':<25} {avg_merch:>6.1f} {'/ 10':>6}")
        print(f"  {'Trigger Relevance':<25} {avg_trig:>6.1f} {'/ 10':>6}")
        print(f"  {'Engagement Compulsion':<25} {avg_eng:>6.1f} {'/ 10':>6}")
        print(f"  {'─' * 50}")
        print(f"  {'TOTAL AVERAGE':<25} {avg_total:>6.1f} {'/ 50':>6}")
        print(f"  {'─' * 50}")

        # Grade
        if avg_total >= 40:
            grade = "A+ (Excellent)"
        elif avg_total >= 35:
            grade = "A (Very Good)"
        elif avg_total >= 30:
            grade = "B (Good)"
        elif avg_total >= 25:
            grade = "C (Average)"
        else:
            grade = "D (Needs Work)"
        print(f"\n  GRADE: {grade}")
    else:
        print("  No messages were scored (bot returned no actions)")

    print(f"\n{'=' * 80}")
    print("JUDGE SIMULATION COMPLETE")
    print(f"{'=' * 80}\n")

except Exception as e:
    print(f"\nFATAL ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    server.terminate()
    server.wait()
    print("Server stopped.")
