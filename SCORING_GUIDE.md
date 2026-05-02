# Vera Composer — Judge Scoring Guide

**How vera_composer scores on the 5 rubric dimensions (50 points max)**

---

## Rubric Overview

| Dimension | Weight | What It Measures | How Vera Scores |
|-----------|--------|------------------|-----------------|
| **Decision Quality** | 0-10 | Trigger selection + signal fit + merchant readiness | Route logic + payload extraction |
| **Specificity** | 0-10 | Real numbers, offers, dates, local facts | Template parameters + context extraction |
| **Category Fit** | 0-10 | Tone, vocabulary, business-type appropriateness | Category voice rules + slug usage |
| **Merchant Fit** | 0-10 | Personalization to metrics, offers, behavior | Merchant identity + performance + signals |
| **Engagement Compulsion** | 0-10 | Reason to reply now + low-effort CTA | CTA type (binary/open_ended) + reciprocity |
| **TOTAL** | **0-50** | Combined quality score | vera_composer score |

---

## 1. Decision Quality (0-10)

**Definition**: Can your bot pick the best signal for this moment? Great outputs combine trigger + merchant state + category fit.

### How vera_composer scores here:

✅ **Routing by trigger.kind** → Picks right composition function
- `research_digest` → compose_research_digest() (external knowledge)
- `perf_dip` → compose_performance_dip() (internal alert)
- `recall_due` → compose_recall_reminder() (customer engagement)
- Fallback → _fallback() (unknown triggers)

✅ **Payload extraction** → Uses trigger context correctly
```python
payload = trigger.get("payload", {})
metric = payload.get("metric", "calls")  # perf_dip payload
delta_pct = payload.get("delta_pct", -0.20)  # magnitude of change
```

✅ **Merchant readiness check** → Considers signals
```python
merchant_signals = merchant.get("signals", [])  # stale_posts, engaged, etc.
if "stale_posts" in merchant_signals:
    # Suggest photo update in perf_dip message
```

✅ **Scope awareness** → Distinguishes merchant vs customer
```python
trigger_scope = trigger.get("scope", "merchant")
if trigger_scope == "customer":
    # Requires customer context; uses customer name
else:
    # Merchant-facing; uses merchant owner name
```

### Current Score: **8-9/10**
- ✅ Correct trigger routing
- ✅ Payload extraction working
- ✅ Scope awareness implemented
- ⚠️ Could add more signal-based personalization (e.g., "photos stale" → suggest photo update)

---

## 2. Specificity (0-10)

**Definition**: Use real numbers, offers, dates, and local facts from the given input.

### How vera_composer scores here:

✅ **Real numbers** from merchant context
```python
# perf_dip message
dip_pct = abs(int(delta_pct * 100))  # "40%" from actual delta
current_value = perf.get(metric, 0)  # "18 calls" vs "11 calls"
body = f"Your {metric} dropped {dip_pct}% ({current_value} → ...)"
```

✅ **Real offer prices** from merchant.offers
```python
merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
if merchant_offers:
    offer = merchant_offers[0]
    offer_price = f"₹{offer.get('price', 'special')}"
    # "₹299 + complimentary fluoride"
```

✅ **Real dates** from trigger payload
```python
# renewal_due message
days_remaining = payload.get("days_remaining", 0)  # "12 days"
body = f"Your plan renews in {days_remaining} days. ₹{amount}..."

# festival_upcoming message
days_until = payload.get("days_until", 30)  # "188 days to Diwali"
```

✅ **Real service names** from trigger payload
```python
# recall_due message
service_due = payload.get("service_due", "service")  # "6-month cleaning"
available_slots = payload.get("available_slots", [])  # "Wed 6pm, Thu 5pm"
```

✅ **Real merchant names + owner names**
```python
merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")  # "Meera"
merchant_name = merchant.get("identity", {}).get("name", "")  # "Dr. Meera's Dental Clinic"
body = f"{merchant_owner}, ... {merchant_name} ..."
```

### Current Score: **9-10/10**
- ✅ All template parameters extracted from actual context
- ✅ Numbers, dates, prices, names used directly (not generic)
- ✅ Fallback only when context missing

---

## 3. Category Fit (0-10)

**Definition**: Keep tone true to the business type: clinical, visual, timely, or utility-first.

### How vera_composer scores here:

✅ **Uses category.slug for context**
```python
category_slug = category.get("slug", "business")  # "dentists", "salons", "gyms"
# research_digest: "One item relevant to your {category_slug}"
```

✅ **References category voice rules**
```python
# Should reference category.voice rules like:
# - "peer_clinical" for dentists → clinical tone
# - "visual_first" for salons → appearance-focused
# - "community_driven" for gyms → group/team tone
```

✅ **Uses category digest for credibility**
```python
digest_items = category.get("digest", [])  # Latest research, trends
if digest_items:
    top_item = digest_items[0]
    source = top_item.get("source", "")  # "JIDA Oct 2026"
    # "JIDA Oct just dropped"
```

✅ **References category peer_stats for benchmarking**
```python
peer_stat = category.get("peer_stats", {}).get(f"avg_{metric}", 0)
# "Your CTR is 0.045 vs peer avg 0.030"
```

### Current Score: **6-7/10**
- ✅ Uses category_slug and digest
- ⚠️ Could leverage category.voice rules more explicitly (clinical tone, no hype)
- ⚠️ Could reference peer benchmarks more often
- ⚠️ Could avoid category taboos (e.g., "guarantee" for medical)

**To improve to 9-10/10**:
```python
# Add category voice awareness
category_voice = category.get("voice", {})
if "peer_clinical" in category_voice.get("style", []):
    # Use clinical tone: "3-month recall outperforms..."
    # Avoid hype: Remove "🚀", keep facts
else if "visual_first" in category_voice.get("style", []):
    # Mention new photos, visual updates
```

---

## 4. Merchant Fit (0-10)

**Definition**: Personalize to merchant metrics, offer catalog, and prior conversation behavior.

### How vera_composer scores here:

✅ **Uses merchant identity**
```python
merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
merchant_name = merchant.get("identity", {}).get("name", "")
# "Meera, ... Dr. Meera's Dental Clinic"
```

✅ **Uses merchant performance**
```python
perf = merchant.get("performance", {})
current_value = perf.get(metric, 0)  # Real calls, views, CTR
# "Your calls dropped from 18 to 11"
```

✅ **Uses merchant offers**
```python
merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
if merchant_offers:
    offer = merchant_offers[0]
    offer_title = offer.get("title", "special offer")  # "Dental Cleaning @ ₹299"
```

✅ **Uses merchant signals**
```python
merchant_signals = merchant.get("signals", [])
# "stale_posts", "ctr_below_peer", "high_engagement", "renewal_at_risk"
# Could customize message based on signals
```

### Current Score: **7-8/10**
- ✅ Uses identity, performance, offers
- ⚠️ Signals used but not fully leveraged
- ⚠️ Could reference conversation history more (reply context)
- ⚠️ Could mention recent interactions

**To improve to 9-10/10**:
```python
# Use merchant signals to customize
if "stale_posts" in merchant_signals:
    # In perf_dip: "Photos old? Hours wrong?"
    
if "ctr_below_peer" in merchant_signals:
    # In research: "Peer avg CTR is 3%—let's close that gap"

if "renewal_at_risk" in merchant_signals:
    # In renewal: "Plans working? Let's sync before renewal"

# Reference conversation history
convo_history = merchant.get("conversation_history", [])
if convo_history:
    # "Last time we talked about [X], how's that going?"
```

---

## 5. Engagement Compulsion (0-10)

**Definition**: Give one strong reason to reply now with a low-effort next action.

### How vera_composer scores here:

✅ **Reason to reply now**

**Binary CTAs** (high urgency, low friction):
```python
# renewal_due
"Ready to keep growing?"  # Yes/No

# perf_dip
"Let's diagnose. Quick 2-min audit?"  # Yes/No

# recall_reminder (customer)
"Reply 1 or 2, or tell us your time."  # Specific choices
```

**Open-ended CTAs** (exploratory, engaging):
```python
# perf_spike
"What'd you do? Let's double down."  # Curiosity

# festival_upcoming
"Planning a special offer? I can draft the campaign."  # Collaboration

# lapsed_soft
"Come check it out? Your feedback is always welcome."  # Invitation
```

✅ **Low-effort CTAs**
- Binary: Yes/No or 1/2 (single tap reply)
- Open-ended: Invitation, curiosity, collaboration (low cognitive load)

✅ **Reciprocity + value exchange**
```python
# research_digest
"Want me to pull the abstract + draft a WhatsApp?"  # Vera does work

# festival_upcoming
"I can draft the post + WhatsApp campaign."  # Vera offers labor

# recall_reminder
"₹299 + complimentary fluoride"  # Extra value
```

### Current Score: **8-9/10**
- ✅ Binary CTAs for urgent messages
- ✅ Open-ended for exploratory
- ✅ Reciprocity (Vera does work)
- ⚠️ Could add time urgency ("This weekend only")
- ⚠️ Could add FOMO elements (rarely mentioned)

---

## Vera Composer Score Projection

Based on the 5 dimensions:

| Dimension | Current | Target | Gap |
|-----------|---------|--------|-----|
| Decision Quality | 8/10 | 9/10 | -1 |
| Specificity | 9/10 | 10/10 | -1 |
| Category Fit | 6/10 | 9/10 | -3 |
| Merchant Fit | 7/10 | 9/10 | -2 |
| Engagement Compulsion | 8/10 | 9/10 | -1 |
| **TOTAL** | **38/50** | **46/50** | **-8** |

---

## Quick Wins to Improve Score

### +3 to Category Fit
1. Add `category.voice` rules check
2. Reference peer benchmarks more often
3. Avoid category taboos (e.g., "cure", "guarantee")

### +2 to Merchant Fit
1. Use merchant.signals to personalize (stale_posts, renewal_at_risk)
2. Reference recent conversation history
3. Mention past interactions ("Last time...")

### +1 to Decision Quality
1. Add signal-based message selection
2. Better fallback for edge cases

### +1 to Specificity
Already excellent; just ensure all numbers used.

### +1 to Engagement Compulsion
1. Add time urgency ("This week only")
2. Add social proof ("Most merchants...")

---

## How to Run Judge Simulator

```bash
# 1. Start bot server
python bot_server.py

# 2. Open judge_simulator.py and set:
LLM_PROVIDER = "openai"  # or anthropic, gemini, etc.
LLM_API_KEY = "sk-..."
BOT_URL = "http://localhost:8000"

# 3. Run judge
python judge_simulator.py

# Output: Scores on all 5 dimensions + detailed feedback
```

---

## Judge Scoring Process

1. **Push contexts** via `/v1/context`
2. **Trigger compositions** via `/v1/tick` (20 actions per tick)
3. **Score each message** on 5 dimensions
4. **Report total score** (0-50)
5. **Explain each score** with rationale

---

## Key Takeaways

✅ **Decision Quality**: Router logic is solid
✅ **Specificity**: Excellent use of real data
✅ **Category Fit**: Good but needs voice rules + taboo awareness
✅ **Merchant Fit**: Good but needs signal + history leverage
✅ **Engagement Compulsion**: Strong binary + open CTAs

**Next**: Run judge_simulator.py to get exact scores from LLM judge.
