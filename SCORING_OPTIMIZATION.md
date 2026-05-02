# Vera Composer — Scoring Optimization Roadmap

**From 38/50 → 45+/50 in 5 specific moves**

---

## Current State Analysis

**Estimated current scores** (based on composition engine review):

| Dimension | Current | Target | Gap | Difficulty | Impact |
|-----------|---------|--------|-----|------------|--------|
| **Decision Quality** | 8/10 | 9/10 | -1 | Easy | Low |
| **Specificity** | 9/10 | 10/10 | -1 | Easy | Low |
| **Category Fit** | 6/10 | 9/10 | -3 | Medium | High |
| **Merchant Fit** | 7/10 | 9/10 | -2 | Medium | High |
| **Engagement Compulsion** | 8/10 | 9/10 | -1 | Easy | Medium |
| **TOTAL** | **38/50** | **46/50** | **-8** | — | — |

---

## Priority 1: Category Fit (+3 points) — HIGHEST IMPACT

**Current issue**: Generic category usage. Composer knows category_slug but doesn't leverage category voice, peer benchmarks, or taboos.

### How to Improve

**1.1: Add category.voice rules check**

**Current code**:
```python
def compose_research_digest(category, merchant, trigger):
    category_slug = category.get("slug", "business")
    # Just uses slug, ignores voice
    body = f"One item relevant to your {category_slug}..."
```

**Improved code**:
```python
def compose_research_digest(category, merchant, trigger):
    category_slug = category.get("slug", "business")
    category_voice = category.get("voice", {})
    
    # Check if clinical category
    if "peer_clinical" in category_voice.get("style", []):
        # Use clinical tone for dentists, pharmacies
        tone = "clinical"
        body = f"One item relevant to your {category_slug}..."  # Keep clinical
    elif "visual_first" in category_voice.get("style", []):
        # Emphasize visual/appearance for salons
        tone = "visual"
        body = f"Quick read on new trends in {category_slug}..."
    else:
        # Community-driven for gyms
        tone = "community"
        body = f"Your {category_slug} community just shared..."
    
    return ComposedMessage(body=body, ...)
```

**1.2: Avoid category taboos**

**Current code**:
```python
# All categories use same tone
body = "Your performance spiked 25%! 🚀 What'd you do?"
```

**Improved code**:
```python
category_taboos = category.get("taboos", [])

if "emoji_free" in category_taboos:
    # Clinical/medical categories
    body = "Your performance spiked 25%. What changed?"  # No emoji
else if "no_hype" in category_taboos:
    # Professional categories
    body = "Your performance increased by 25%. What drove this?"  # Professional tone
else:
    # Casual categories (salons, gyms)
    body = "Your performance spiked 25%! 🚀 What'd you do?"  # Emoji OK
```

**1.3: Reference peer benchmarks from category**

**Current code**:
```python
# Extracted but not used in message
peer_stat = category.get("peer_stats", {}).get(f"avg_{metric}", 0)
```

**Improved code**:
```python
peer_stat = category.get("peer_stats", {}).get(f"avg_{metric}", 0)
current_value = perf.get(metric, 0)

if current_value > peer_stat:
    body = f"Your {metric} ({current_value}) beats peer avg ({peer_stat:.1f}%). Keep it up!"
else:
    body = f"Your {metric} ({current_value}) is below peer avg ({peer_stat:.1f}%). Let's close that gap."
```

**Impact**: +3 points (6→9 on category fit)

---

## Priority 2: Merchant Fit (+2 points) — HIGH IMPACT

**Current issue**: Merchant identity + performance used, but signals + history not leveraged.

### How to Improve

**2.1: Use merchant.signals for personalization**

**Current code**:
```python
# Signals extracted but not used
merchant_signals = merchant.get("signals", [])
```

**Improved code**:
```python
merchant_signals = merchant.get("signals", [])

if "stale_posts" in merchant_signals:
    # In perf_dip message, specifically mention photos
    body = f"Your {metric} dropped {dip_pct}%. Photos stale? Let's update GBP visuals."
    
elif "ctr_below_peer" in merchant_signals:
    # In research_digest, position as competitive advantage
    body = f"{owner}, this research gives you edge. Your CTR lags peers—this fix could close gap."
    
elif "renewal_at_risk" in merchant_signals:
    # In renewal message, acknowledge risk
    body = f"{owner}, your Pro plan renews in {days}d. Plans working? Let's review before renewal."
    
elif "high_engagement" in merchant_signals:
    # In research_digest, give premium insight
    body = f"{owner}, your customers engage deeply. Exclusive research on [topic] just dropped."
```

**2.2: Reference merchant conversation history**

**Current code**:
```python
# Conversation history not accessed
```

**Improved code**:
```python
convo_history = merchant.get("conversation_history", [])

if convo_history:
    # Find last interaction
    last_convo = convo_history[-1]
    last_topic = last_convo.get("topic", "")
    days_ago = last_convo.get("days_ago", 0)
    
    # Reference prior context
    if last_topic == "photo_update" and days_ago < 7:
        body = f"{owner}, remember the photo update last week? Your CTR improved 15%. Let's see if we can double it."
    elif last_topic == "offer" and days_ago < 14:
        body = f"{owner}, your new offer is performing well. Time to expand it?"
```

**2.3: Mention merchant's high-value customer cohorts**

**Current code**:
```python
# No cohort reference
body = "Your high-risk patients would benefit from this..."
```

**Improved code**:
```python
# Extract merchant's customer cohorts
customer_cohorts = merchant.get("customer_cohorts", [])
# e.g., ["high_risk_adults", "new_parents", "elderly"]

for cohort in customer_cohorts:
    if cohort == "high_risk_adults":
        body = "Your high-risk adult patients would benefit from this research..."
    elif cohort == "new_parents":
        body = "Your new parent segment would love this seasonal offer..."
```

**Impact**: +2 points (7→9 on merchant fit)

---

## Priority 3: Engagement Compulsion (+1 point) — MEDIUM IMPACT

**Current issue**: CTAs are good, but could add urgency + FOMO elements.

### How to Improve

**3.1: Add time urgency to CTAs**

**Current code**:
```python
cta = "binary"
body = "Want me to pull the abstract?"
```

**Improved code**:
```python
cta = "binary"
urgency = trigger.get("urgency", 3)

if urgency >= 4:
    # High urgency
    body = "Want me to pull the abstract + draft copy? This window closes Friday."
elif urgency >= 2:
    # Medium urgency
    body = "Want me to pull the abstract + draft copy? Available this week."
else:
    # Low urgency
    body = "Want me to pull the abstract + draft copy? No rush."
```

**3.2: Add reciprocity framing**

**Current code**:
```python
# Reciprocity present but minimal
body = "Want me to pull the abstract + draft a WhatsApp?"
```

**Improved code**:
```python
# Strengthen reciprocity
body = "Want me to pull the abstract + draft patient-ready copy? I'll do the heavy lifting, you send it."
# "I'll do the heavy lifting" = explicit value prop

# Or for offers:
body = "Planning a special offer? I can draft the post + WhatsApp campaign. Save you 30 mins."
# "Save you 30 mins" = quantified value
```

**3.3: Add social proof / FOMO**

**Current code**:
```python
body = "Your performance spiked 25%. What'd you do?"
```

**Improved code**:
```python
# Check peer performance
peer_avg_spike = category.get("peer_stats", {}).get("avg_spike_pct", 0)

if spike_pct > peer_avg_spike * 2:
    # Exceptional spike - FOMO
    body = f"Your performance spiked {spike_pct}%—most merchants see 5-8%. What'd you do? Let's double down before momentum fades."
else:
    body = f"Your performance spiked {spike_pct}%. What'd you do?"
```

**Impact**: +1 point (8→9 on engagement compulsion)

---

## Priority 4: Decision Quality (+1 point) — LOW IMPACT

**Current issue**: Routing logic solid, but could use signal-based message selection.

### How to Improve

**4.1: Route by merchant readiness + signal state**

**Current code**:
```python
# Route only by trigger.kind
if trigger_kind == "renewal_due":
    return compose_renewal_due(...)
```

**Improved code**:
```python
# Check merchant readiness BEFORE composing
merchant_signals = merchant.get("signals", [])
merchant_ctr = merchant.get("performance", {}).get("ctr", 0)
peer_ctr = category.get("peer_stats", {}).get("avg_ctr", 0)

if trigger_kind == "renewal_due":
    if "renewal_at_risk" in merchant_signals:
        # High risk - different message
        return compose_renewal_at_risk(...)
    elif merchant_ctr < peer_ctr * 0.5:
        # Very low CTR - condition renewal on optimization
        return compose_renewal_with_optimization_push(...)
    else:
        # Normal renewal
        return compose_renewal_due(...)
```

**Impact**: +1 point (8→9 on decision quality)

---

## Priority 5: Specificity (+1 point) — LOW IMPACT

**Current issue**: Already excellent (9/10), but ensure every template param filled.

### How to Improve

**5.1: Validate all template params before returning**

**Current code**:
```python
template_params = [merchant_owner or merchant_name.split()[0], source, title[:30]]
# Some params might be empty strings
```

**Improved code**:
```python
# Ensure no empty params
def _validate_params(params):
    return [p if p and str(p).strip() else "[DATA_MISSING]" for p in params]

template_params = _validate_params([
    merchant_owner or merchant_name.split()[0],
    source or "Latest Research",
    title[:30] or "Important Update"
])
```

**Impact**: +1 point (9→10 on specificity)

---

## Implementation Checklist

### Phase 1: Category Fit (+3 points) — Do First
- [ ] Add category.voice rules check to all compose functions
- [ ] Add taboo detection (emoji_free, no_hype, etc.)
- [ ] Reference peer benchmarks in 5+ functions
- [ ] Test output for tone changes

### Phase 2: Merchant Fit (+2 points) — Do Second
- [ ] Add merchant.signals usage in 5+ functions
- [ ] Add conversation history reference (if available)
- [ ] Add customer cohort mentions
- [ ] Test output for personalization

### Phase 3: Engagement Compulsion (+1 point) — Do Third
- [ ] Add urgency framing to CTAs
- [ ] Strengthen reciprocity language
- [ ] Add FOMO/social proof where relevant
- [ ] Test output for CTA strength

### Phase 4: Decision Quality (+1 point) — Do Fourth
- [ ] Add signal-based routing decisions
- [ ] Add merchant readiness checks
- [ ] Test routing logic

### Phase 5: Specificity (+1 point) — Do Last
- [ ] Add param validation
- [ ] Ensure no empty strings in output
- [ ] Test template params

---

## Testing & Validation

After implementing each change:

```bash
# 1. Run composer test
python test_composer.py
# Check if scores improve

# 2. Run bot server
python bot_server.py

# 3. Run judge
python judge_simulator.py
# Check final score

# Expected progression:
# Initial: 38/50
# After Phase 1 (Category): 41/50
# After Phase 2 (Merchant): 43/50
# After Phase 3 (Engagement): 44/50
# After Phase 4 (Decision): 45/50
# After Phase 5 (Specificity): 46/50
```

---

## Quick Wins (30 min implementation)

If you want quick improvements before full refactor:

**Add category voice awareness** (Phase 1.1):
```python
# In compose_research_digest(), add:
voice = category.get("voice", {}).get("style", [])
if "peer_clinical" in voice:
    # Remove emoji, keep clinical tone
    body = body.replace("🚀", "")
```

**Add merchant signals** (Phase 2.1):
```python
# In compose_performance_dip(), add:
if "stale_posts" in merchant.get("signals", []):
    body += " (Photos stale?)"
```

**Add urgency to CTAs** (Phase 3.1):
```python
# In all compose functions, add:
urgency_phrase = " This week only." if trigger.get("urgency", 0) >= 4 else ""
body += urgency_phrase
```

---

## Code Diff Examples

### Example 1: Adding category voice to research_digest

```python
# BEFORE
def compose_research_digest(category, merchant, trigger):
    body = f"{owner}, {source} just dropped. One item relevant to your {category_slug}..."
    return ComposedMessage(body=body, ...)

# AFTER
def compose_research_digest(category, merchant, trigger):
    voice_style = category.get("voice", {}).get("style", [])
    
    if "peer_clinical" in voice_style:
        # Clinical tone - no emoji, facts-based
        body = f"{owner}, {source} published. Key finding: {title}. Relevant to your {category_slug}. Read?"
    elif "visual_first" in voice_style:
        # Visual tone - appearance-focused
        body = f"{owner}, new trends in {category_slug}. {source} just shared. Visual guide inside. Check it out?"
    else:
        # Default
        body = f"{owner}, {source} just dropped. One item relevant to your {category_slug}..."
    
    return ComposedMessage(body=body, ...)
```

### Example 2: Using merchant signals in perf_dip

```python
# BEFORE
def compose_performance_dip(category, merchant, trigger):
    body = f"{owner}, your {metric} dropped {dip_pct}%. Profile missing something?..."
    return ComposedMessage(body=body, ...)

# AFTER
def compose_performance_dip(category, merchant, trigger):
    signals = merchant.get("signals", [])
    
    # Personalize based on signals
    if "stale_posts" in signals:
        diagnosis = "Photos old? Hours wrong?"
    elif "missing_category" in signals:
        diagnosis = "Missing service category?"
    elif "low_rating" in signals:
        diagnosis = "Ratings lagging? New reviews might help."
    else:
        diagnosis = "Something in profile needs refresh?"
    
    body = f"{owner}, your {metric} dropped {dip_pct}%. {diagnosis} Let's diagnose. 2-min audit?"
    return ComposedMessage(body=body, ...)
```

---

## Validation Script

After implementing changes, run this to check improvements:

```bash
# test_improvements.py
import json
from vera_composer import compose
from expanded.dataset import merchants, customers, triggers, categories

test_cases = [
    ("m_001", "trg_001", None),  # Merchant-facing
    ("m_001", "trg_075", "c_001"),  # Customer-facing
]

for merchant_id, trigger_id, customer_id in test_cases:
    merchant = merchants[merchant_id]
    trigger = triggers[trigger_id]
    category = categories[merchant["category"]]
    customer = customers.get(customer_id)
    
    msg = compose(category, merchant, trigger, customer)
    
    print(f"\n{trigger_id}:")
    print(f"  Body: {msg.body[:80]}...")
    print(f"  CTA: {msg.cta}")
    print(f"  Rationale: {msg.rationale}")
```

---

## Expected Timeline

- **Phase 1** (Category Fit): 2-3 hours → +3 points
- **Phase 2** (Merchant Fit): 1-2 hours → +2 points
- **Phase 3** (Engagement): 30 min → +1 point
- **Phase 4** (Decision Quality): 1 hour → +1 point
- **Phase 5** (Specificity): 15 min → +1 point

**Total effort**: ~6-7 hours to reach 46+/50

---

## After You Hit 45+/50

Once your score is 45+/50:

1. ✅ Deploy bot to public URL
2. ✅ Share URL with challenge judge
3. ✅ Judge does final evaluation on their end
4. ✅ You're in the running for top submission

---

## Questions?

- **Scoring questions**: See [SCORING_GUIDE.md](SCORING_GUIDE.md)
- **Composition logic**: See [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md)
- **Setup questions**: See [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md)
- **Code**: See [vera_composer.py](vera_composer.py)

---

**Let's go from 38/50 → 46+/50!** 🚀
