# Message Craft — Strong Messages vs Generic

**How to build messages that judges reward**

---

## The Generic Trap

### ❌ Generic Message (Gets Penalized)
```
Hi Doctor, want to run a discount campaign today to increase sales?
```

**Why it fails**:
- ❌ No trigger (why NOW?)
- ❌ No merchant fact (which doctor?)
- ❌ No category voice (could be any business)
- ❌ Vague CTA (what campaign?)
- ❌ No proof (just a guess)

**Judge score**: 15-20/50 (Generic penalty)

---

## The Strong Pattern

### ✅ Strong Message (Gets Rewarded)
```
190 people in your locality are searching for "Dental Check Up". 
Should I send them a discounted check up at ₹299?
```

**Why it works**:
- ✅ Real trigger (search volume data)
- ✅ Merchant fact (locality)
- ✅ Category voice (dental-specific offer)
- ✅ Specific CTA (yes/no on price)
- ✅ Four levers: Proof + Urgency + Curiosity + Action

**Judge score**: 40-45/50 (Specificity + engagement)

---

## The 4 Levers (Proof, Urgency, Curiosity, Action)

### 1. Proof (Real Data)
**Generic**: "People want check ups"
**Strong**: "190 people in your locality are searching for 'Dental Check Up'"

- Uses REAL benchmark (190)
- Uses REAL location (your locality)
- Uses REAL search term ("Dental Check Up")
- No invented claims

### 2. Urgency (Time-Sensitive)
**Generic**: "Consider a campaign"
**Strong**: "190 people are searching RIGHT NOW"

- Present tense (are searching NOW)
- Scarcity implied (if you don't act, they'll go elsewhere)
- Window closing (search trends change)

### 3. Curiosity (Hook)
**Generic**: "Increase sales"
**Strong**: "What's the best price to win these searches?"

- Specific offer (₹299, not "discount")
- Local context (your area)
- Actionable hook (these specific searches)

### 4. Action (One Clear CTA)
**Generic**: "Want to run a campaign?"
**Strong**: "Should I send them a discounted check up at ₹299?"

- Yes/No question (binary)
- Specific offer included (₹299)
- Clear next step (send to them)
- No exploration ("Let's discuss" = penalty)

---

## Vera Composer — Applied to Current Messages

### Example 1: Research Digest

**Current** (Missing Proof):
```
"Meera, JIDA Oct 2026 dropped. One item relevant to your dentists — 
3-month fluoride recall. Worth a 2-min read. Want me to pull abstract + draft copy?"
```

**Improved** (With Proof):
```
"Meera, 73% of high-risk adult patients benefit from 3-month recalls vs 6-month 
(JIDA Oct 2026). Your high-risk adult cohort: 240 patients. Should I draft 
a patient message to schedule recalls?"
```

**Levers**:
- Proof: 73% benefit + 240 of your patients
- Urgency: They're your existing patients (dormant potential)
- Curiosity: Specific patient segment + outcome
- Action: Draft message (yes/no)

---

### Example 2: Performance Dip (After Updates)

**Current**:
```
"Your photos are stale. Update 3 best photos now?"
```

**Improved** (With All 4 Levers):
```
"Your calls dropped 40% (18→11) after you stopped updating photos. 
Merchants who update weekly average 8 more calls/week. Update photos this week?"
```

**Levers**:
- Proof: 40% drop (18→11) + peer benchmark (8 more calls/week)
- Urgency: Drop already happened
- Curiosity: Specific number (+8 calls/week if you act)
- Action: Update this week (yes/no)

---

### Example 3: Renewal Due (After Updates)

**Current**:
```
"Your Pro plan renews in 12d. ₹4999. You're 15% ahead of peer avg. Keep that edge?"
```

**Improved** (With All 4 Levers):
```
"Your Pro plan renews in 12 days. ₹4999. You're 15% ahead of peers (18 calls vs 
peer avg 15.6). Merchants who renew maintain their edge for 1 year. Keep going?"
```

**Levers**:
- Proof: 18 calls vs peer avg 15.6 (real numbers)
- Urgency: 12 days (renewal window)
- Curiosity: "maintain edge for 1 year" (stakes)
- Action: Keep going (yes/no)

---

## The Session Rules (Hard Constraints)

### ✅ Do This
- One clear CTA per message
- Real data only (no invented claims)
- Specific benchmarks (numbers, not "people")
- Merchant facts (their offers, metrics, location)
- Category voice (clinical for dentists, visual for salons)

### ❌ Don't Do This
- Multiple CTAs ("Do X or do Y?" = penalty)
- Fake claims ("could", "might", "potential")
- Generic benchmarks ("peer average")
- Generic offers ("discount" without price)
- Copy-paste same message for all merchants

---

## What Judges Change (Dynamic Testing)

After you submit, judges:

1. **Inject new digest items**
   - Your message must use real digest data
   - Not hard-coded examples

2. **Shift performance metrics**
   - Your message must adapt to real merchant metrics
   - "You're 15% ahead" only if they ARE 15% ahead

3. **Add new triggers**
   - Your compose() must handle triggers you've never seen
   - Must gracefully fallback without generic copy

4. **Add customer contexts**
   - Customer-facing messages use real customer data
   - Name, relationship, preferences, consent

**Implication**: Your composer CANNOT use hard-coded examples. Every value must come from:
- Category context
- Merchant context
- Trigger context
- Customer context (optional)

---

## Vera Composer — Compliance Check

### Is vera_composer ready for dynamic testing?

✅ **Proof** — Uses real data from contexts:
```python
calls_last_month = perf.get("calls", 0)  # Real merchant metric
peer_avg_calls = category.get("peer_stats", {}).get("avg_calls", 0)  # Real peer data
```

✅ **Urgency** — Uses trigger urgency:
```python
days_remaining = payload.get("days_remaining", 0)  # Real countdown
attributed_cause = payload.get("attributed_cause", "unknown")  # Real cause
```

✅ **Curiosity** — Uses merchant-specific offers:
```python
merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
offer_price = offer.get("price", 0)  # Real offer from merchant
```

✅ **Action** — One clear binary CTA:
```python
cta = "binary"  # Always yes/no, not exploration
```

✅ **No Fake Claims** — All values from context:
```python
# NOT: "Customers love fluoride"
# YES: "240 of your high-risk patients" (from customer cohort data)
```

---

## Template for Strong Messages

Use this framework for EVERY message:

```
[Merchant name], [PROOF: real benchmark].
[URGENCY: why now?].
[CURIOSITY: specific offer/action].
[ACTION: yes/no question?]
```

### Example 1: Research
```
"Meera, [PROOF: 73% of high-risk patients benefit from 3-month recalls] 
(JIDA Oct). [URGENCY: You have 240 in that cohort]. 
[CURIOSITY: Should I draft a patient message?] 
[ACTION: Yes or No?]"
```

### Example 2: Performance
```
"Meera, [PROOF: Your calls dropped 40% (18→11)]. 
[URGENCY: After you stopped photo updates]. 
[CURIOSITY: Merchants who update weekly average +8 calls]. 
[ACTION: Update photos this week?]"
```

### Example 3: Opportunity
```
"Meera, [PROOF: 190 people searching 'Dental Check Up' in your area]. 
[URGENCY: These searches happen daily]. 
[CURIOSITY: Discounted check ups at ₹299 convert 12% of searchers]. 
[ACTION: Target them?]"
```

---

## Vera Composer Update Checklist

For EACH compose function, verify:

- [ ] **Proof**: Message includes real number (%, count, metric)
- [ ] **Urgency**: Message explains why NOW (trigger, deadline, window)
- [ ] **Curiosity**: Message includes specific offer/action (not generic)
- [ ] **Action**: Message has ONE binary CTA (yes/no, not exploration)
- [ ] **No Fakes**: All data from context, not invented
- [ ] **Merchant Fact**: Uses THIS merchant's data (not generic copy)
- [ ] **Category Voice**: Tone matches business type
- [ ] **Dynamic**: Works with any context (not hard-coded examples)

---

## Current Vera Composer Status

### ✅ Strong Areas
1. **Proof** — Uses real merchant metrics and peer benchmarks ✓
2. **Action** — Binary CTAs (yes/no) ✓
3. **No Fakes** — All context-driven (no invented claims) ✓
4. **Category Voice** — Uses category_slug (partially) ✓

### ⚠️ Areas to Improve
1. **Urgency** — Could emphasize "why now" more explicitly
2. **Curiosity** — Some messages are still exploratory ("What'd you do?")
3. **Dynamic** — Need to handle new triggers gracefully
4. **Category Voice** — Need full voice rules (clinical, visual_first, etc.)

---

## Implementation Path

### Priority 1: Verify Dynamic Readiness
- [ ] No hard-coded examples (check all strings)
- [ ] All values from context
- [ ] Graceful fallback for unknown triggers

### Priority 2: Strengthen Urgency Messaging
- [ ] Add explicit "why now" to every message
- [ ] Use trigger urgency levels (1-5)
- [ ] Emphasize time windows (3 days, end of week, etc.)

### Priority 3: Add Category Voice Rules
- [ ] Clinical voice for medical (dentists, pharmacies)
- [ ] Visual voice for appearance (salons)
- [ ] Community voice for gyms
- [ ] Utility-first for restaurants

### Priority 4: Enhance Curiosity Hooks
- [ ] Real search volumes (not guesses)
- [ ] Real offer conversions (not generic)
- [ ] Real customer segments (not "people")

---

## Testing Strong Messages

Run judge with various scenarios:

### Test Scenario 1: New Merchant
```python
# New merchant with no history
# Message should use peer benchmarks + category defaults
# Should NOT reference their past performance
```

### Test Scenario 2: Trigger Shift
```python
# Inject new digest items
# Message should adapt to new research/trends
# Should NOT use old hard-coded examples
```

### Test Scenario 3: Metric Change
```python
# Shift merchant's performance numbers
# Message should reference new metrics
# Should NOT use cached old values
```

### Test Scenario 4: New Trigger Type
```python
# Trigger type never seen before
# Message should gracefully fallback
# Should NOT crash or return generic copy
```

---

## Judge's Lens

When judges evaluate your message, they ask:

1. **Proof**: "Is this real data or invented?"
   - Real: ✅ "190 people searching"
   - Fake: ❌ "People want discounts"

2. **Urgency**: "Why does merchant need to act NOW vs tomorrow?"
   - Real: ✅ "Window closes in 3 days"
   - Fake: ❌ "Consider this sometime"

3. **Curiosity**: "Is this specific to this merchant or generic?"
   - Real: ✅ "Your 240 high-risk patients"
   - Fake: ❌ "Your patients need care"

4. **Action**: "Can merchant reply with one simple yes/no?"
   - Real: ✅ "Should I send them at ₹299?"
   - Fake: ❌ "Let's discuss options"

5. **No Fakes**: "Is every claim verifiable from context?"
   - Real: ✅ All from merchant/category/trigger/customer
   - Fake: ❌ "Guaranteed results" (not in data)

---

## Strong Message Checklist

Before running judge, verify your messages:

```
Proof (Real Data)
☐ Uses real merchant metric (calls, views, ratings, etc.)
☐ Uses real peer benchmark (not generic "average")
☐ Uses real offer price (not "discount")
☐ Uses real location (not "your area")
☐ All numbers come from context

Urgency (Why Now)
☐ Mentions specific timeframe (3 days, 12 hours, etc.)
☐ Explains trigger (deadline, shift, opportunity window)
☐ Emphasizes scarcity (if you don't act, merchants lose)
☐ Creates tension (urgency without pressure)

Curiosity (Specific Hook)
☐ Mentions specific customer segment (not "people")
☐ Mentions specific offer (not "discount")
☐ Mentions specific opportunity (not "growth")
☐ Ties to merchant's business (relevant)

Action (One Clear CTA)
☐ Binary question (yes/no, not multi-option)
☐ Specific next step (not exploration)
☐ Follows session rule: one CTA per message
☐ Completes the ask (not open-ended)

No Fake Claims
☐ "Guaranteed" ❌ (not in data)
☐ "Could" ❌ (invented)
☐ "Might" ❌ (speculative)
☐ "Potential" ❌ (not real)
☐ All claims ✓ backed by context

Dynamic Ready
☐ Works with any merchant
☐ Works with new triggers
☐ Works with metric shifts
☐ No hard-coded examples
☐ Graceful fallback
```

---

## Your Vera Composer Now

After the 4-principle updates, vera_composer has:

✅ Decision quality (ONE signal)
✅ Engagement (specific CTAs)
✅ Bold messaging (sharp hooks)
✅ Grounded facts (THIS merchant)

**Next**: Ensure EVERY message follows Proof + Urgency + Curiosity + Action framework.

---

## Quick Action

1. **Read** this guide (already done ✓)
2. **Review** each compose_* function against the template
3. **Enhance** urgency/curiosity hooks
4. **Test** with dynamic scenarios
5. **Run** judge on new dataset

---

**Strong messages = High judge scores = Winning submission** 🎯
