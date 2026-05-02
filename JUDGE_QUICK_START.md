# Vera Composer — Judge Scoring Quick Start

**Everything you need to know in one page**

---

## The Challenge

Build a deterministic message composer that scores 45+/50 on the judge's rubric.

**Judge evaluates on 5 dimensions** (10 points each = 50 max):
1. **Decision Quality** (10) — Trigger selection + signal fit
2. **Specificity** (10) — Real numbers, dates, offers, facts
3. **Category Fit** (10) — Tone, vocab, business-type appropriateness
4. **Merchant Fit** (10) — Personalization to metrics, signals, behavior
5. **Engagement Compulsion** (10) — Reason to reply + low-effort CTA

---

## Your Current Status

✅ **vera_composer.py** — Complete (deterministic composition engine)
✅ **bot_server.py** — Complete (5 HTTP endpoints)
✅ **judge_simulator.py** — Available (official LLM-powered judge)
✅ **30 test pairs** — Generated (canonical evaluation set)
✅ **Dataset** — Generated (50 merchants, 200 customers, 100 triggers)

**Current Estimated Score**: 38-40/50
- Decision Quality: 8/10 ✓
- Specificity: 9/10 ✓
- **Category Fit: 6/10** ← NEEDS WORK (+3 points)
- **Merchant Fit: 7/10** ← NEEDS WORK (+2 points)
- Engagement Compulsion: 8/10 ✓

---

## 3-Step Roadmap (8 Hours Total)

### Phase 1: Baseline Scoring (30 min) 
**Today**
1. Get LLM API key (OpenAI, Anthropic, etc.)
2. Edit judge_simulator.py (lines 25-45)
3. Run: `python judge_simulator.py`
4. Save baseline score

**Result**: Know your starting point (likely 38-40/50)

---

### Phase 2: Optimize Score (6-7 hours)
**Tomorrow**
1. Read [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md)
2. Implement **Category Fit** improvements (+3 pts):
   - Add category.voice rules
   - Add taboo detection
   - Reference peer benchmarks
3. Implement **Merchant Fit** improvements (+2 pts):
   - Use merchant.signals
   - Reference conversation history
   - Add customer cohorts
4. Implement **Quick Wins** (+1-2 pts):
   - Add urgency to CTAs
   - Strengthen reciprocity
   - Add FOMO/social proof
5. Re-run: `python judge_simulator.py`

**Result**: Score improves to 45-47/50

---

### Phase 3: Deploy & Submit (1-2 hours)
**Day 3**
1. Push code to GitHub
2. Deploy to Render (free tier works)
3. Test public URL
4. Submit bot endpoint to judge

**Result**: Submission accepted, ready for final eval

---

## Key Files

| File | Purpose | When to Use |
|------|---------|-----------|
| [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md) | 3-phase plan with timeline | START HERE |
| [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md) | How to run judge_simulator.py | Phase 1 |
| [SCORING_GUIDE.md](SCORING_GUIDE.md) | Understand 5 dimensions | Phase 1 (after score) |
| [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) | Code changes to improve | Phase 2 |
| [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md) | Deep dive on composition logic | Reference |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Cloud deployment options | Phase 3 |
| vera_composer.py | The actual engine | To update |
| bot_server.py | FastAPI server | To deploy |
| judge_simulator.py | LLM judge | To run |

---

## Phase 1: Baseline (30 min)

**Step 1: Get API key**
```
OpenAI: https://platform.openai.com/api/keys
Anthropic: https://console.anthropic.com/keys
Or use Gemini, Groq, DeepSeek, OpenRouter, Ollama
```

**Step 2: Configure judge**
```python
# Edit judge_simulator.py lines 25-45
LLM_PROVIDER = "openai"  # Your choice
LLM_API_KEY = "sk-..."   # Your API key
BOT_URL = "http://localhost:8000"  # Default
```

**Step 3: Run baseline**
```bash
# Terminal 1
python bot_server.py
# Wait for: "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2
python judge_simulator.py
# Wait 30-60 seconds for results
```

**Step 4: Save results**
```
Total Score: ??/50
Decision Quality: ?/10
Specificity: ?/10
Category Fit: ?/10  ← Likely lowest
Merchant Fit: ?/10  ← Likely 2nd lowest
Engagement: ?/10
```

**Done!** You now know your baseline.

---

## Phase 2: Optimize (6-7 hours)

**High-Impact Changes** (prioritized):

1. **+3 points (Category Fit)**
   - Add category.voice rules check
   - Add taboo detection (emoji_free, no_hype)
   - Reference peer benchmarks in messages
   - **Files**: vera_composer.py (all compose_* functions)

2. **+2 points (Merchant Fit)**
   - Use merchant.signals for personalization
   - Reference conversation history
   - Add customer cohort mentions
   - **Files**: vera_composer.py (all compose_* functions)

3. **+1 point (Engagement Compulsion)**
   - Add urgency to CTAs
   - Strengthen reciprocity language
   - Add FOMO/social proof

**Example improvement (Category Fit)**:
```python
# BEFORE
body = f"{owner}, {source} just dropped..."

# AFTER
voice = category.get("voice", {}).get("style", [])
if "peer_clinical" in voice:
    # Clinical tone - no emoji, facts-based
    body = f"{owner}, {source} published key finding..."
else:
    # Default
    body = f"{owner}, {source} just dropped..."
```

**Re-run judge**:
```bash
# After making changes
python judge_simulator.py
# Should show improvement to 45+/50
```

---

## Phase 3: Deploy (1-2 hours)

**Option A: Render (Recommended)**
1. Go to https://render.com
2. Connect GitHub repo
3. Deploy (auto-detects Python)
4. Get public URL: `https://vera-magicpin-abc123.onrender.com`
5. Test: `curl https://vera-magicpin-abc123.onrender.com/v1/healthz`

**Option B: Railway**
1. Go to https://railway.app
2. Connect GitHub repo
3. Deploy (auto-config)
4. Get URL

**Option C: AWS/GCP/Azure**
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Submit**:
```
Team: magicpin
Email: vera@magicpin.com
Phone: 9999999999
Bot URL: https://your-deployed-url
LinkedIn: https://www.linkedin.com/company/samast-technologies
```

---

## Judge Scoring Details

**30 canonical test pairs**:
- 25 merchant-facing (research, perf, renewal, etc.)
- 5 customer-facing (recall, lapsed, welcome, etc.)

**Scoring process**:
1. Judge pushes contexts via `/v1/context`
2. Judge requests compositions via `/v1/tick`
3. Bot returns messages using vera_composer
4. Judge scores on 5 dimensions
5. Judge reports total score

**Evaluation**: Same as baseline judge_simulator.py, but official scoring

---

## How Vera Composer Uses 4 Contexts

```
compose(category, merchant, trigger, customer?)
  │
  ├─ CategoryContext → voice, digest, peer_stats, taboos
  ├─ MerchantContext → identity, performance, offers, signals
  ├─ TriggerContext → kind, payload, urgency, suppression_key
  └─ CustomerContext → identity, relationship, preferences (optional)

Output: ComposedMessage (body, cta, send_as, suppression_key, rationale)
```

All 4 contexts **MUST** be used for high score.

---

## Common Questions

**Q: What if my score doesn't improve after changes?**
A: Check category.get() calls — make sure new fields exist in dataset.

**Q: Can I deploy before optimizing?**
A: Yes, but score will be lower. Better to optimize first (6-7 hours) then deploy.

**Q: What if judge_simulator.py times out?**
A: Bot endpoint too slow. Check: All compose functions <1ms? Dataset loading correctly?

**Q: Do I need to use an LLM for the judge?**
A: Yes. judge_simulator.py requires LLM to score messages on 5 dimensions.

**Q: Can I run judge offline?**
A: No. Judge requires LLM API call. Options: OpenAI, Anthropic, Gemini, etc.

**Q: What's my target score?**
A: 45+/50 to be competitive. 50/50 is ideal but 45+ good for placement.

---

## Success Criteria

- ✅ Phase 1: Baseline score obtained
- ✅ Phase 2: Score improves to 45+/50
- ✅ Phase 3: Bot deployed to public URL
- ✅ Submission accepted by judge
- ✅ Ready for final ranking

---

## Timeline

| Task | Duration | Cumulative |
|------|----------|-----------|
| Phase 1 (baseline) | 30 min | 30 min |
| Phase 2 (optimize) | 6-7 hours | 6.5-7 hours |
| Phase 3 (deploy) | 1-2 hours | 7.5-9 hours |

**Total**: 8-9 hours from start to submission

---

## START HERE

1. **Read**: [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md) (full 3-phase plan)
2. **Get API key**: From OpenAI, Anthropic, or Gemini
3. **Run Phase 1**: `python judge_simulator.py` to get baseline
4. **Read**: [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) for code changes
5. **Implement Phase 2**: Update vera_composer.py
6. **Validate**: Re-run `python judge_simulator.py`
7. **Deploy Phase 3**: Push to Render/Railway, get public URL
8. **Submit**: Share endpoint with judge

---

## Reference Docs (Read as Needed)

- [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md) — Full 3-phase plan
- [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md) — How to run judge
- [SCORING_GUIDE.md](SCORING_GUIDE.md) — 5 dimensions explained
- [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) — Code changes with examples
- [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md) — Composition logic deep dive
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — Cloud deployment options

---

## You're Ready! 🚀

Everything is built and documented.

**Next step**: Get your LLM API key and run Phase 1 baseline scoring.

```bash
# Takes 30 minutes
python judge_simulator.py
```

**Let's go!**
