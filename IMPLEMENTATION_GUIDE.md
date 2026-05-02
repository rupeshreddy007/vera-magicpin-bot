# Vera Composer Improvements — 4 Judge Principles

**Code changes to implement decision quality, engagement, bold messaging, and specificity**

---

## Issue #1: Decision Quality (Choose ONE Signal)

**Problem**: compose_performance_dip lists 3 causes ("Photos old? Hours wrong?") — picking all signals instead of THE ONE.

**Current code**:
```python
body = f"{owner_salute} your {metric} dropped {dip_pct}% this week ({current_value} → check GBP). 
         Profile missing something? Photos old? Hours wrong? Let's diagnose. Quick 2-min audit?"
```

**Issue**: Judge wants ONE signal, not 3 options.

**Improved code**:
```python
# Pick THE ONE signal that matters most
merchant_signals = merchant.get("signals", [])

# Decision tree: pick ONE most impactful signal
if "stale_photos" in merchant_signals:
    diagnosis = "Your photos are stale."
    action = "Update 3 best photos this week—watch calls bounce back."
    
elif "incomplete_profile" in merchant_signals:
    diagnosis = "Your profile is incomplete."
    action = "Add missing categories + business hours. 5-min fix."
    
elif "low_rating" in merchant_signals:
    diagnosis = "Your rating dropped below peer avg."
    action = "Respond to 1 recent review. Builds trust."
    
else:
    # If we don't know the signal, ask for ONE reason
    diagnosis = f"Your {metric} dropped {dip_pct}%."
    action = "What changed this week? Let's fix it."

body = f"{owner_salute} {diagnosis} This week your {metric} dropped {dip_pct}%. {action}"
```

**Result**: 
- ❌ OLD: "Profile missing something? Photos old? Hours wrong?" (3 guesses)
- ✅ NEW: "Your photos are stale. Update 3 best photos this week—watch calls bounce back." (1 sharp action)

---

## Issue #2: Engagement (Low-Friction, One Clear Action)

**Problem**: "Let's diagnose. Quick 2-min audit?" is exploratory, not action-oriented.

**Current code**:
```python
cta = "binary"
body = "...Let's diagnose. Quick 2-min audit?"
# Judge doesn't know what YES means
```

**Issue**: CTA is vague. What does merchant do when they say Yes?

**Improved code**:
```python
# Make CTA a specific action, not exploration
if "stale_photos" in merchant_signals:
    action = "Update 3 photos now?"  # Specific. Merchant knows exactly what to do.
    cta = "binary"
    
elif "incomplete_profile" in merchant_signals:
    action = "Fill profile gaps right now?"
    cta = "binary"
    
elif "low_rating" in merchant_signals:
    action = "Reply to 1 review?"
    cta = "binary"

body = f"{owner_salute} {diagnosis} This week your {metric} dropped {dip_pct}%. {action}"
```

**Result**:
- ❌ OLD: "Let's diagnose. Quick 2-min audit?" (What happens after Yes?)
- ✅ NEW: "Update 3 photos now?" (Merchant knows exactly what to do)

---

## Issue #3: Bold High-Compulsion Messaging

**Problem**: compose_performance_spike uses emoji + vague ("What'd you do?") — not bold.

**Current code**:
```python
body = f"{owner_salute} your {metric} spiked {spike_pct}% yesterday! 🚀 What'd you do? 
         Updated photos? New offer? Let's double down on what worked."
```

**Issue**: Emoji + generic exploration. Not bold, not sharp.

**Improved code**:
```python
# Extract real context: what changed?
perf_history = merchant.get("performance_history", [])
recent_change = trigger.get("payload", {}).get("attributed_change", "")

# Pick ONE reason for spike (from real data)
if recent_change == "new_offer":
    body = f"{owner_salute} your {metric} spiked {spike_pct}% after your new offer. That offer works. Run it for 2 more weeks."
    
elif recent_change == "photo_update":
    body = f"{owner_salute} your {metric} spiked {spike_pct}% after photo update. Customers see you now. Keep updating weekly."
    
elif recent_change == "review_boost":
    body = f"{owner_salute} your {metric} spiked {spike_pct}% after your 5-star reviews. 3 of your last 4 reviews are 5-stars. You're crushing it—keep delivering."
    
else:
    # Fallback: acknowledge spike as signal, ask for ONE cause
    body = f"{owner_salute} your {metric} spiked {spike_pct}%. Something changed. What was it?"

cta = "binary"
body += " Keep going?"  # Direct ask, not exploration
```

**Result**:
- ❌ OLD: "What'd you do? Updated photos? New offer? Let's double down..." (Vague exploration)
- ✅ NEW: "Your offer works. Run it for 2 more weeks. Keep going?" (Sharp hook from real context)

---

## Issue #4: Generic Messages Lose

**Problem**: compose_renewal_due is too generic ("Ready to keep growing?")

**Current code**:
```python
body = f"{owner_salute} your {plan} plan renews in {days_remaining} days. 
         ₹{amount} for another year of Vera + profile optimization. Ready to keep growing?"
```

**Issue**: Generic value prop. Could apply to any business.

**Improved code**:
```python
# Use merchant-specific performance to justify renewal
perf = merchant.get("performance", {})
calls_last_month = perf.get("calls", 0)
peer_avg_calls = category.get("peer_stats", {}).get("avg_calls", 0)

if calls_last_month > peer_avg_calls:
    # Merchant performing well → emphasize growth
    call_growth = int((calls_last_month - peer_avg_calls) / peer_avg_calls * 100)
    reason = f"You're {call_growth}% ahead of peer avg. Keep that edge."
    
elif calls_last_month > 0:
    # Merchant has activity → emphasize optimization
    growth_needed = peer_avg_calls - calls_last_month
    reason = f"You're {growth_needed} calls short of peer avg. Let's close that gap."
    
else:
    # New merchant → emphasize quick wins
    reason = f"You just started. Profile optimization unlocks your first 20 calls."

body = f"{owner_salute} your {plan} plan renews in {days_remaining} days. ₹{amount} more. {reason} Ready?"
```

**Result**:
- ❌ OLD: "Ready to keep growing?" (Could be ANY business)
- ✅ NEW: "You're 25% ahead of peer avg. Keep that edge. Ready?" (Specific to THIS merchant)

---

## Implementation Priority

### Highest Impact (Do First)
1. **Decision Quality** — Pick ONE signal in compose_performance_dip
2. **Generic messages** — Add merchant-specific facts to renewal

### High Impact (Do Second)
3. **Engagement** — Make CTAs specific actions, not explorations
4. **Bold messaging** — Add real context hooks

### Medium Impact (Do Third)
5. Add signal-based routing to other compose functions

---

## Code Changes (Ready to Apply)

### Change #1: compose_performance_dip (Decision Quality)

Replace the body composition logic to pick ONE signal:

```python
def compose_performance_dip(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Performance dip detected — pick ONE signal and act"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    metric = payload.get("metric", "calls")
    delta_pct = payload.get("delta_pct", -0.20)
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    dip_pct = abs(int(delta_pct * 100))
    
    # DECISION QUALITY: Pick ONE signal
    merchant_signals = merchant.get("signals", [])
    
    if "stale_photos" in merchant_signals:
        diagnosis = "Your photos are stale."
        action = "Update 3 best photos now?"
    elif "incomplete_profile" in merchant_signals:
        diagnosis = "Your profile is incomplete."
        action = "Add missing categories + hours?"
    elif "low_rating" in merchant_signals:
        diagnosis = "Your rating's below peer avg."
        action = "Respond to 1 recent review?"
    else:
        diagnosis = f"Your {metric} dropped {dip_pct}%."
        action = "What changed this week?"
    
    body = f"{owner_salute} {diagnosis} {action}"
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_perf_dip_v1",
        template_params=[merchant_owner or merchant_name.split()[0], metric, str(dip_pct)],
        suppression_key=trigger.get("suppression_key", f"perf_dip:{metric}"),
        rationale=f"Performance dip ({metric} {delta_pct:.0%}). One actionable diagnosis based on merchant signals. Direct CTA."
    )
```

### Change #2: compose_performance_spike (Bold Messaging)

Add real context hooks:

```python
def compose_performance_spike(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Performance spike — identify the real reason and amplify"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    metric = payload.get("metric", "calls")
    delta_pct = payload.get("delta_pct", 0.25)
    attributed_cause = payload.get("attributed_cause", "unknown")  # e.g., "new_offer", "photos", "reviews"
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    spike_pct = int(delta_pct * 100)
    
    # BOLD MESSAGING: Sharp hook from real context
    if attributed_cause == "new_offer":
        reason = "Your new offer works. Keep running it for 2 more weeks."
        next_action = "Run it again?"
    elif attributed_cause == "photo_update":
        reason = "Your new photos are working. Customers are seeing you now."
        next_action = "Update photos weekly?"
    elif attributed_cause == "review_boost":
        reason = "Your recent reviews are gold. Customers see those 5-stars first."
        next_action = "Ask for more reviews?"
    else:
        reason = f"Something changed. {spike_pct}% more calls this week."
        next_action = "What was it?"
    
    body = f"{owner_salute} {reason} {next_action}"
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_perf_spike_v1",
        template_params=[merchant_owner or merchant_name.split()[0], metric, str(spike_pct)],
        suppression_key=trigger.get("suppression_key", f"perf_spike:{metric}"),
        rationale=f"Performance spike ({metric} +{spike_pct}%). Sharp hook from real attributed cause. Direct actionable CTA."
    )
```

### Change #3: compose_renewal_due (Grounded with Facts)

Add merchant-specific performance context:

```python
def compose_renewal_due(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Subscription renewal — grounded in THIS merchant's facts"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    days_remaining = payload.get("days_remaining", 0)
    plan = payload.get("plan", "Pro")
    amount = payload.get("renewal_amount", 0)
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    
    # GROUNDED: Use real merchant facts, not generic
    perf = merchant.get("performance", {})
    calls_last_month = perf.get("calls", 0)
    peer_avg_calls = category.get("peer_stats", {}).get("avg_calls", 0)
    
    if calls_last_month > 0 and peer_avg_calls > 0:
        if calls_last_month > peer_avg_calls:
            # Merchant outperforming
            edge_pct = int((calls_last_month - peer_avg_calls) / peer_avg_calls * 100)
            value = f"You're {edge_pct}% ahead of peer avg on calls. Keep that edge."
        else:
            # Merchant below avg
            gap = peer_avg_calls - calls_last_month
            value = f"You're {gap} calls short of peer avg. Renewal gets you optimization to close it."
    else:
        # No data yet
        value = "Profile optimization unlocks your first calls."
    
    body = f"{owner_salute} your {plan} plan renews in {days_remaining}d. ₹{amount}. {value} Keep going?"
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_renewal_v1",
        template_params=[merchant_owner or merchant_name.split()[0], plan, str(days_remaining)],
        suppression_key=trigger.get("suppression_key", f"renewal:{merchant.get('merchant_id')}"),
        rationale=f"Renewal reminder ({days_remaining}d). Grounded in THIS merchant's performance vs peers. Direct ask."
    )
```

---

## Testing Changes

After implementing, test with:

```python
# test_improvements.py
from vera_composer import compose

# Test 1: Decision Quality
trigger = {
    "kind": "perf_dip",
    "scope": "merchant",
    "payload": {"metric": "calls", "delta_pct": -0.40}
}
msg = compose(category, merchant, trigger)
# Check: body has ONE diagnosis (not 3 options)
assert "?" not in msg.body.split(".")[-2]  # Last sentence doesn't have "?"

# Test 2: Engagement (Specific Action)
# Check: CTA is specific action, not exploration
assert "audit" not in msg.body.lower()  # No vague "audit"
assert "photos" in msg.body.lower() or "hours" in msg.body.lower()  # Specific action

# Test 3: Bold Messaging
trigger = {"kind": "perf_spike", "payload": {"attributed_cause": "new_offer"}}
msg = compose(category, merchant, trigger)
# Check: message references the REAL cause
assert "offer" in msg.body.lower()  # Not generic "What'd you do?"

# Test 4: Grounded Facts
trigger = {"kind": "renewal_due", "payload": {"days_remaining": 12}}
msg = compose(category, merchant, trigger)
# Check: message uses merchant's actual perf
# Should mention calls, peer avg, or specific gap
```

---

## Expected Score Improvement

After implementing these 4 changes:

| Dimension | Before | After | +Change |
|-----------|--------|-------|---------|
| Decision Quality | 8/10 | 9/10 | +1 |
| Engagement | 8/10 | 9/10 | +1 |
| Specificity | 9/10 | 9/10 | 0 |
| Category Fit | 6/10 | 7/10 | +1 |
| Merchant Fit | 7/10 | 9/10 | +2 |
| **TOTAL** | **38/50** | **43/50** | **+5** |

Then combine with Category Fit improvements (voice rules, peer benchmarks) for another +3 points → **46/50**

---

## Quick Implementation Path

### Step 1: Update compose_performance_dip (10 min)
- Pick ONE signal instead of 3
- Make CTA specific action

### Step 2: Update compose_performance_spike (10 min)
- Add attributed_cause logic
- Make message sharp hook

### Step 3: Update compose_renewal_due (10 min)
- Add perf comparison
- Make value specific to merchant

### Step 4: Test (5 min)
```bash
python test_composer.py
python judge_simulator.py  # Re-run baseline
```

**Total effort**: 35 minutes

**Expected improvement**: +5 points (38→43/50)

---

## Principle Checklist

After implementation, verify:

✅ **Decision Quality**
- [ ] Each message picks ONE signal, not many
- [ ] No "?" in multi-option diagnosis ("Photos old? Hours wrong?")
- [ ] Clear reason WHY this message now

✅ **Engagement**
- [ ] CTAs are specific actions ("Update photos now?")
- [ ] Not explorations ("Let's diagnose")
- [ ] Merchant knows what to do when they reply Yes

✅ **Bold High-Compulsion**
- [ ] Messages are sharp hooks from real context
- [ ] No invented claims ("potential", "could", "might")
- [ ] Real numbers + real reasons

✅ **Grounded Not Generic**
- [ ] Every message uses THIS merchant's facts
- [ ] Not copy-paste across different merchants
- [ ] Performance metrics, signals, or peer comparisons included

---

## Next Steps

1. Apply these 3 changes to vera_composer.py
2. Test with test_composer.py
3. Re-run judge_simulator.py
4. Then apply Category Fit improvements for final +3 points
5. Target: 45+/50
