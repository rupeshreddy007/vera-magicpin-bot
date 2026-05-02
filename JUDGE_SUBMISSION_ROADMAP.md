# Vera Composer — Judge Submission Roadmap

**From this moment to accepted submission in 3 phases**

---

## Your Current State ✅

| Component | Status | Score |
|-----------|--------|-------|
| vera_composer.py | ✅ Complete | — |
| bot_server.py | ✅ Complete | — |
| Dataset | ✅ Complete (50M, 200C, 100T) | — |
| 30 test pairs | ✅ Complete | — |
| Documentation | ✅ Complete (7 docs) | — |
| Docker config | ✅ Complete | — |
| judge_simulator.py | ✅ Available | — |
| **Estimated Judge Score** | — | **38-40/50** |

---

## Phase 1: Baseline Scoring (Today)

**Goal**: Get your official judge score on all 5 dimensions

**Steps**:

1. **Pick an LLM provider** (choose one):
   - OpenAI (GPT-4) — Recommended
   - Anthropic (Claude)
   - Google Gemini
   - Other (Groq, DeepSeek, OpenRouter, Ollama)

2. **Get API key**:
   ```
   OpenAI: https://platform.openai.com/api/keys
   Anthropic: https://console.anthropic.com/keys
   (Save the key somewhere safe)
   ```

3. **Start bot server**:
   ```bash
   # Terminal 1
   python bot_server.py
   # Wait for: "Uvicorn running on http://0.0.0.0:8000"
   ```

4. **Configure judge**:
   ```bash
   # Edit judge_simulator.py lines 25-45:
   LLM_PROVIDER = "openai"  # Your choice
   LLM_API_KEY = "sk-..."   # Your API key
   BOT_URL = "http://localhost:8000"  # Default
   ```

5. **Run judge**:
   ```bash
   # Terminal 2
   python judge_simulator.py
   # Wait 30-60 seconds for results
   ```

6. **Capture output**:
   ```
   Copy the score breakdown and save to baseline_score.txt
   ```

**Expected output**:
```
Total Score: 38-40/50

Decision Quality:      8/10
Specificity:           9/10
Category Fit:          6/10  ← LOWEST
Merchant Fit:          7/10  ← SECOND LOWEST
Engagement Compulsion: 8/10
```

**Deliverable**: `baseline_score.txt` with results

---

## Phase 2: Optimized Scoring (Next 6-7 hours)

**Goal**: Improve score from 38-40 → 45+/50

**Strategy**: Focus on **Category Fit** (+3 points) and **Merchant Fit** (+2 points)

### What to do:

1. **Read the optimization guide**:
   - Open [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md)
   - Review "Phase 1: Category Fit" section
   - Review "Phase 2: Merchant Fit" section

2. **Implement Category Fit improvements** (2-3 hours):
   - Add category.voice rules check
   - Add taboo detection (emoji_free, no_hype)
   - Reference peer benchmarks in messages
   
   **Specific files to update**:
   - vera_composer.py → compose_research_digest()
   - vera_composer.py → compose_performance_dip()
   - vera_composer.py → compose_perf_spike()
   - vera_composer.py → compose_festival_upcoming()

3. **Implement Merchant Fit improvements** (1-2 hours):
   - Use merchant.signals for personalization
   - Reference conversation history
   - Add customer cohort mentions
   
   **Specific files to update**:
   - vera_composer.py → All compose_* functions

4. **Quick wins** (1 hour):
   - Add urgency to CTAs
   - Strengthen reciprocity language
   - Add signal-based routing

5. **Re-run judge**:
   ```bash
   # Terminal 2 (after code changes)
   python judge_simulator.py
   ```

6. **Validate improvement**:
   - Category Fit should jump to 9/10
   - Merchant Fit should jump to 9/10
   - Total should be 45+/50

**Expected results after Phase 2**:
```
Total Score: 45-47/50

Decision Quality:      8/10
Specificity:           9/10
Category Fit:          9/10 ← IMPROVED +3
Merchant Fit:          9/10 ← IMPROVED +2
Engagement Compulsion: 8/10
```

**Deliverable**: Updated `vera_composer.py` + new `optimized_score.txt`

---

## Phase 3: Deployment & Submission (Final 1-2 hours)

**Goal**: Deploy bot to public URL and submit to judge

### Option A: Deploy to Render (Recommended — Free Tier Works)

1. **Push code to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Vera composer - ready for submission"
   git remote add origin https://github.com/YOUR_USERNAME/vera_magicpin.git
   git push -u origin main
   ```

2. **Create Render account**:
   - Go to https://render.com
   - Sign up with GitHub

3. **Deploy**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select repo + branch
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn bot_server:app --host 0.0.0.0 --port $PORT`
   - Click "Deploy"
   - Wait 2-3 minutes for deployment

4. **Get public URL**:
   - Render will show: `https://vera-magicpin-abc123.onrender.com`
   - Test it: `curl https://vera-magicpin-abc123.onrender.com/v1/healthz`

5. **Submit to judge**:
   - Full name: magicpin
   - Email: vera@magicpin.com
   - Phone: 9999999999
   - **Bot URL**: https://vera-magicpin-abc123.onrender.com
   - LinkedIn: https://www.linkedin.com/company/samast-technologies

### Option B: Deploy to Railway

1. Go to https://railway.app
2. Connect GitHub repo
3. Railway auto-detects Python + Dockerfile
4. Get public URL: `https://your-app.railway.app`

### Option C: Deploy to AWS/GCP/Azure

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full instructions

### Step 6: Final Validation

**Test your deployed URL**:
```bash
# Should all respond with 200 OK
curl https://your-bot-url/v1/healthz
curl https://your-bot-url/v1/metadata
curl -X POST https://your-bot-url/v1/context \
  -H "Content-Type: application/json" \
  -d '{"scope": "merchant", "context_id": "test", "version": 1, "payload": {}}'
```

### Step 7: Submit Endpoint

**Send to challenge judge**:
```
Team: magicpin
Contact: vera@magicpin.com
Phone: 9999999999
Bot Endpoint: https://your-bot-url
LinkedIn: https://www.linkedin.com/company/samast-technologies
```

The judge will:
- Validate all 5 endpoints
- Run 30 canonical test pairs
- Score on 5 dimensions
- Announce results

**Deliverable**: Public bot URL + submission confirmation

---

## Quick Timeline Estimate

| Phase | Task | Duration | When |
|-------|------|----------|------|
| 1 | Baseline scoring | 30 min | Today |
| 1 | Review SCORING_GUIDE.md | 15 min | Today |
| 2 | Implement Category Fit | 2-3 hours | Tomorrow |
| 2 | Implement Merchant Fit | 1-2 hours | Tomorrow |
| 2 | Quick wins | 1 hour | Tomorrow |
| 2 | Validate score | 30 min | Tomorrow |
| 3 | Deploy to cloud | 30 min | Day 3 |
| 3 | Final testing | 15 min | Day 3 |
| 3 | Submit to judge | 10 min | Day 3 |
| **TOTAL** | **All phases** | **~8 hours** | **3 days** |

---

## Checklist

### Phase 1: Baseline (Today)
- [ ] Have LLM API key ready
- [ ] Edit judge_simulator.py configuration
- [ ] Start bot_server.py
- [ ] Run `python judge_simulator.py`
- [ ] Save baseline score
- [ ] Note lowest scoring dimension (likely Category Fit)

### Phase 2: Optimization (Tomorrow)
- [ ] Read SCORING_OPTIMIZATION.md
- [ ] Implement Category Fit improvements
- [ ] Implement Merchant Fit improvements
- [ ] Implement Quick Wins improvements
- [ ] Re-run judge
- [ ] Verify score improved to 45+/50
- [ ] Save optimized score

### Phase 3: Deployment (Day 3)
- [ ] Push code to GitHub (or have it ready)
- [ ] Create Render/Railway account
- [ ] Deploy bot to public URL
- [ ] Test all 5 endpoints on public URL
- [ ] Collect bot URL
- [ ] Submit to challenge judge
- [ ] Save submission confirmation

---

## Critical Path (Minimum Steps)

If you only want to submit without optimizing first:

```bash
# 1. Start bot
python bot_server.py

# 2. Deploy to Render (manual push)
# Connect GitHub → Deploy → Get URL

# 3. Test 5 endpoints on deployed URL
curl https://your-bot-url/v1/healthz

# 4. Submit URL to challenge judge
```

This gets you to submission in ~1 hour, but at current 38-40/50 score.

**Better path**: Do Phase 2 optimizations first (6 hours) to reach 45+/50, THEN deploy. Judges rank by score.

---

## Risk Mitigation

### Risk 1: Deployed bot different from local
**Mitigation**: 
- Same code deploys (just different env)
- Test publicly-deployed bot with judge_simulator before submitting

### Risk 2: LLM judge times out
**Mitigation**:
- Ensure all endpoints respond in <1 second
- Test locally: `python test_bot.py`

### Risk 3: Deployment fails
**Mitigation**:
- Try Render first (easiest)
- Have Railway as backup
- Keep local version as fallback

### Risk 4: Score drops after optimization
**Mitigation**:
- Unlikely (improvements are targeted)
- If it does, revert to previous version
- Keep git history for rollback

---

## Success Criteria

✅ **Phase 1 Success**:
- Judge score obtained
- All 5 dimensions evaluated
- Baseline captured for comparison

✅ **Phase 2 Success**:
- Score improved to 45+/50
- Category Fit at 9/10
- Merchant Fit at 9/10

✅ **Phase 3 Success**:
- Bot deployed to public URL
- All 5 endpoints responding
- Submission confirmed by judge

✅ **Overall Success**:
- Bot accepted into challenge
- Ready for final evaluation
- Potentially top-ranked submission

---

## Next Immediate Actions

### Right Now (Next 30 min):
1. ✅ You've read this roadmap
2. Next: Get LLM API key (OpenAI recommended)
3. Then: Configure judge_simulator.py

### Today (Next 2 hours):
1. Start bot_server.py
2. Run baseline judge score
3. Save results
4. Note the gap (Category Fit -3 pts is the biggest)

### Tomorrow (Next 6 hours):
1. Implement Category Fit improvements
2. Implement Merchant Fit improvements
3. Re-run judge
4. Validate 45+/50 achieved

### Day 3 (Next 1 hour):
1. Deploy to Render/Railway
2. Test public URL
3. Submit to judge

---

## Support Resources

| Question | Resource |
|----------|----------|
| How does scoring work? | [SCORING_GUIDE.md](SCORING_GUIDE.md) |
| How to run judge? | [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md) |
| How to improve score? | [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) |
| What's in vera_composer? | [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md) |
| How to deploy? | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| Full submission overview? | [FINAL_SUBMISSION.md](FINAL_SUBMISSION.md) |

---

## Ready?

**Phase 1 starts now**: Get your baseline judge score in the next 30 minutes.

```bash
# Step 1: Get API key from LLM provider
# Step 2: Update judge_simulator.py
# Step 3: python judge_simulator.py
# Step 4: Save results
```

Let's go! 🚀

---

**Questions? Check the docs or re-read the relevant section above.**

**Good luck! The vera_composer is solid — you've got this.** ✅
