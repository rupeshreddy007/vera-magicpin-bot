# Judge Simulator Setup Guide

**How to run the official judge and get your vera_composer score**

---

## Step 1: Start Your Bot Server

```bash
# Terminal 1: Start bot server
python bot_server.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Press CTRL+C to quit
```

Verify it's running:
```bash
curl http://localhost:8000/v1/healthz
# {"status": "ok", "uptime_seconds": 1, "contexts_loaded": {...}}
```

---

## Step 2: Get an LLM API Key

The judge simulator needs an LLM to score your messages on the 5 dimensions. Choose one:

### Option A: OpenAI (Recommended)
```bash
# 1. Go to https://platform.openai.com/api/keys
# 2. Create new secret key
# 3. Copy the key (sk-...)
```

### Option B: Anthropic (Claude)
```bash
# 1. Go to https://console.anthropic.com/keys
# 2. Create new API key
# 3. Copy the key (sk-ant-...)
```

### Option C: Other Providers
- **Gemini**: https://aistudio.google.com/app/apikeys
- **Groq**: https://console.groq.com/keys
- **DeepSeek**: https://platform.deepseek.com/api_keys
- **OpenRouter**: https://openrouter.ai/keys
- **Ollama**: Local model (no API key needed)

---

## Step 3: Configure judge_simulator.py

Open `judge_simulator.py` and edit the **CONFIGURATION** section (lines 25-45):

```python
# =============================================================================
# ██████  CONFIGURATION - EDIT THIS SECTION ██████
# =============================================================================

# Your bot's URL (where your bot is running)
BOT_URL = "http://localhost:8000"  # Change port if needed

# Choose your LLM provider: "openai", "anthropic", "gemini", "deepseek", "groq", "ollama", "openrouter"
LLM_PROVIDER = "openai"  # Change to your provider

# Your API key (paste your key here)
LLM_API_KEY = "sk-..."  # PASTE YOUR KEY HERE

# Model to use (leave empty for default, or specify like "gpt-4o", "claude-3-5-sonnet-20241022", etc.)
LLM_MODEL = ""  # Leave empty for default, or specify model

# For Ollama only: local server URL
OLLAMA_URL = "http://localhost:11434"  # Only if using Ollama

# Which test to run by default
TEST_SCENARIO = "all"  # Options: "all", "merchant", "customer", "single", or "T01", "T02", etc.
```

**Example configurations**:

```python
# OpenAI (GPT-4)
LLM_PROVIDER = "openai"
LLM_API_KEY = "sk-proj-abc123..."
LLM_MODEL = "gpt-4o"

# Anthropic (Claude)
LLM_PROVIDER = "anthropic"
LLM_API_KEY = "sk-ant-abc123..."
LLM_MODEL = "claude-3-5-sonnet-20241022"

# Gemini
LLM_PROVIDER = "gemini"
LLM_API_KEY = "AIzaSyD..."
LLM_MODEL = ""  # Leave empty for default

# Ollama (local)
LLM_PROVIDER = "ollama"
LLM_API_KEY = ""  # No key needed
LLM_MODEL = "llama2"  # or whatever you have running
```

---

## Step 4: Run the Judge

```bash
# Terminal 2: Run judge simulator
python judge_simulator.py

# Wait for results (30-60 seconds)
```

---

## Step 5: Read the Results

The judge will output:

```
======================================================================
                    VERA AI JUDGE — FINAL REPORT
======================================================================

Total Score: 38/50

Breakdown:
  Decision Quality:      8/10  (Trigger selection and signal fit)
  Specificity:           9/10  (Real numbers, dates, offers)
  Category Fit:          6/10  (Business-type tone and vocabulary)
  Merchant Fit:          7/10  (Personalization and metrics)
  Engagement Compulsion: 8/10  (CTA strength and urgency)

Messages scored: 30 canonical test pairs
Timeout: None
Errors: 0

======================================================================
```

---

## Test Coverage

The judge will test **30 canonical test pairs**:

- **25 merchant-facing triggers** (research_digest, perf_dip, renewal_due, etc.)
- **5 customer-facing triggers** (recall_due, lapsed, welcome, etc.)

Each scored on **5 dimensions × 10 points = 50 max points**

---

## Interpreting Your Score

| Score | Interpretation | Action |
|-------|---|---|
| 40-50/50 | Excellent — Ready to submit | Deploy and share URL |
| 35-39/50 | Good — Improve category fit + merchant fit | Tune messages, add signals |
| 30-34/50 | Fair — Needs improvement | Review judge feedback |
| <30/50 | Needs work | Rewrite composition logic |

---

## Debugging Judge Issues

### Issue: "Connection refused at http://localhost:8000"
**Solution**: Make sure bot_server.py is running:
```bash
python bot_server.py
```

### Issue: "Invalid API key"
**Solution**: Check your LLM_API_KEY:
- Did you copy the full key?
- Did you add quotes around it?
- Is it the right provider?

### Issue: "Timeout after 45 seconds"
**Solution**: Bot is too slow. Check:
```bash
# Test a single /v1/tick manually
curl -X POST http://localhost:8000/v1/tick \
  -H "Content-Type: application/json" \
  -d '{"available_triggers": ["trg_001"]}'

# Should respond in <1 second
```

### Issue: "No test pairs found"
**Solution**: Check that `expanded/test_pairs.json` exists:
```bash
ls expanded/test_pairs.json
# Should return the file path
```

---

## Quick Commands

```bash
# Check bot health
curl http://localhost:8000/v1/healthz

# Check bot metadata
curl http://localhost:8000/v1/metadata

# Run judge (all 30 test pairs)
python judge_simulator.py

# Run judge (single test pair)
python judge_simulator.py --test T01

# Run judge (merchant-only triggers)
python judge_simulator.py --scenario merchant

# Run judge (customer-only triggers)
python judge_simulator.py --scenario customer
```

---

## Judge Output Details

Each message will be scored like this:

```
Test T01: research_digest for Dr. Meera's Dental Clinic
─────────────────────────────────────────────────────────

Message:
"Meera, JIDA Oct 2026 dropped. 3-month fluoride recall cuts 
 caries 38% better than 6-month. Relevant to your high-risk 
 adult patients. Want me to pull the abstract + draft a patient-ed WhatsApp?"

Scores:
  Decision Quality (8/10):
    ✓ Correct trigger selection (research_digest)
    ✓ Payload extraction (JIDA Oct 2026)
    ✗ Could use merchant signals more

  Specificity (9/10):
    ✓ Real source: JIDA Oct 2026
    ✓ Real numbers: 38% improvement
    ✓ Real category: dentists, fluoride, recall
    ✗ Could mention patient cohort (high-risk adults)

  Category Fit (7/10):
    ✓ Clinical tone
    ✓ Category-appropriate vocab (fluoride, caries, recall)
    ✗ Could avoid hype (currently good)
    ✗ Could reference peer benchmarks

  Merchant Fit (7/10):
    ✓ Merchant owner name: Meera
    ✓ Category: dentists
    ✗ Could reference their performance vs peers
    ✗ Could mention their high-risk patient cohort

  Engagement Compulsion (8/10):
    ✓ Binary CTA (yes/no on "pull abstract")
    ✓ Reciprocity (Vera does work)
    ✓ Low-friction next action
    ✗ Could add urgency ("This week's top finding")

Overall: 39/50
```

---

## Next Steps After Getting Score

If score < 45/50:

1. **Read judge feedback** — Look at dimension scores
2. **Identify gaps**:
   - Low category fit? → Add voice rules, taboo awareness
   - Low merchant fit? → Use signals, conversation history
   - Low specificity? → Check that all template params filled
   - Low engagement? → Improve CTAs, add reciprocity
3. **Update vera_composer.py** — Enhance low-scoring dimensions
4. **Re-run judge** — `python judge_simulator.py`
5. **Iterate** until you reach 45+/50

If score ≥ 45/50:

1. ✅ **You're ready to deploy**
2. ✅ **Share your bot URL with the challenge judge**
3. ✅ **The judge will do final evaluation**

---

## Common High-Scoring Patterns

Judges score highest when you:

1. ✅ Use REAL merchant names, numbers, dates
2. ✅ Pick CORRECT trigger for this moment
3. ✅ Reference CATEGORY voice (not generic)
4. ✅ Personalize to MERCHANT signals + performance
5. ✅ Give ONE reason to reply + binary CTA

---

## Example Scoring Session

```bash
# Terminal 1: Bot server
$ python bot_server.py
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000

# Terminal 2: Judge
$ python judge_simulator.py

Loading test pairs...        [OK]
Validating bot endpoints...  [OK]
  /v1/healthz        [OK] 200ms
  /v1/metadata       [OK] 150ms
  /v1/context        [OK] 200ms
  /v1/tick           [OK] 450ms
  /v1/reply          [OK] 350ms

Scoring 30 canonical test pairs...
  T01 (research_digest)   [SCORE: 8.5/10]  ✓
  T02 (perf_dip)          [SCORE: 7.8/10]  ✓
  T03 (recall_due)        [SCORE: 8.2/10]  ✓
  ... (27 more tests)

Total Score: 39/50

Breakdown:
  Decision Quality:      8.0/10
  Specificity:           8.8/10
  Category Fit:          6.5/10
  Merchant Fit:          7.2/10
  Engagement Compulsion: 8.5/10

Ready for improvement! Focus on Category Fit and Merchant Fit.
```

---

## Support

If you get stuck:

1. Check [SCORING_GUIDE.md](SCORING_GUIDE.md) — Explains each dimension
2. Check [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md) — Composition logic
3. Check [vera_composer.py](vera_composer.py) — Actual code
4. Check error messages in judge output — Specific feedback

---

**Ready? Let's score!** 🚀

```bash
python judge_simulator.py
```
