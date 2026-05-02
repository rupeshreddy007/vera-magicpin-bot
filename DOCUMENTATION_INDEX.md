# Vera Composer — Complete Documentation Index

**All documents organized by purpose**

---

## 🚀 Start Here

**First time? Read these in order**:

1. [JUDGE_QUICK_START.md](JUDGE_QUICK_START.md) — 1-page overview + 3-phase roadmap (5 min)
2. [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md) — Detailed timeline + steps (10 min)
3. [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md) — How to run judge_simulator.py (5 min)

---

## 📊 Understanding the Judge

**To understand how scoring works**:

- [SCORING_GUIDE.md](SCORING_GUIDE.md) — 5 dimensions + vera_composer scores (15 min)
- [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) — Code changes for each dimension (20 min)

---

## 🛠️ Building & Deployment

**To understand the technical implementation**:

- [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md) — Composition logic deep dive (15 min)
- [VERA_COMPOSER_FINAL.md](VERA_COMPOSER_FINAL.md) — Technical submission overview (10 min)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — Cloud deployment options (10 min)

---

## 📋 Reference Materials

**Complete documentation**:

- [README.md](README.md) — Setup + usage guide
- [FINAL_SUBMISSION.md](FINAL_SUBMISSION.md) — Submission package overview
- [BUILD_SUMMARY.md](BUILD_SUMMARY.md) — Complete build history
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) — Quick command reference
- [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) — Implementation checklist

---

## 📁 File Structure

```
vera_magicpin/
│
├── JUDGE_QUICK_START.md          ← START HERE (1 page)
├── JUDGE_SUBMISSION_ROADMAP.md   ← 3-phase plan
├── JUDGE_SETUP_GUIDE.md          ← Run judge
├── SCORING_GUIDE.md              ← 5 dimensions
├── SCORING_OPTIMIZATION.md       ← Code improvements
│
├── vera_composer.py              ← Core engine (to update)
├── bot_server.py                 ← FastAPI server
├── judge_simulator.py            ← LLM judge (to run)
│
├── test_composer.py              ← Composer tests
├── test_bot.py                   ← Bot tests
├── quick_test.py                 ← Quick startup check
│
├── requirements.txt              ← Python dependencies
├── Dockerfile                    ← Container image
├── docker-compose.yml            ← Local dev setup
├── .env.example                  ← Environment template
│
├── COMPOSER_ENGINE.md            ← Composition logic
├── VERA_COMPOSER_FINAL.md        ← Technical details
├── DEPLOYMENT_GUIDE.md           ← Cloud deployment
│
├── README.md                     ← Setup guide
├── FINAL_SUBMISSION.md           ← Submission overview
├── BUILD_SUMMARY.md              ← Build history
├── QUICK_REFERENCE.md            ← Command reference
├── SUBMISSION_CHECKLIST.md       ← Checklist
│
├── dataset/                      ← Seed templates
│   ├── generate_dataset.py
│   ├── merchants_seed.json
│   ├── customers_seed.json
│   ├── triggers_seed.json
│   └── categories/
│
├── expanded/                     ← Generated dataset
│   ├── merchants/                (50 merchants)
│   ├── customers/                (200 customers)
│   ├── triggers/                 (100 triggers)
│   ├── categories/               (5 categories)
│   └── test_pairs.json           (30 test pairs)
│
└── __pycache__/                  ← Cache
```

---

## 🎯 Quick Navigation

### "I want to..."

**Run the judge and see my score**
→ [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md) → Phase 1 (30 min)

**Improve my score**
→ [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) → Phase 2 (6-7 hours)

**Deploy bot to cloud**
→ [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) → Phase 3 (1-2 hours)

**Understand scoring rubric**
→ [SCORING_GUIDE.md](SCORING_GUIDE.md)

**Understand composition logic**
→ [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md)

**Get a complete overview**
→ [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md)

**Get quick reference**
→ [JUDGE_QUICK_START.md](JUDGE_QUICK_START.md)

---

## 📊 Current Status

### Implementation Status
- ✅ vera_composer.py — Complete (deterministic engine)
- ✅ bot_server.py — Complete (5 endpoints)
- ✅ judge_simulator.py — Available (LLM judge)
- ✅ Dataset — Complete (50M, 200C, 100T, 30 pairs)
- ✅ Docker config — Complete
- ✅ Tests — Complete (test_composer.py, test_bot.py)

### Estimated Judge Score
- **Current**: 38-40/50
- **Target after optimization**: 45+/50
- **All 4 contexts used**: ✅ Yes
- **30 canonical test pairs**: ✅ Ready

---

## ⏱️ Time Estimates

| Phase | Task | Duration | Document |
|-------|------|----------|----------|
| 1 | Baseline scoring | 30 min | JUDGE_SETUP_GUIDE.md |
| 2 | Category Fit improvements | 2-3 hrs | SCORING_OPTIMIZATION.md |
| 2 | Merchant Fit improvements | 1-2 hrs | SCORING_OPTIMIZATION.md |
| 2 | Validation | 30 min | (Re-run judge) |
| 3 | Deployment | 30 min | DEPLOYMENT_GUIDE.md |
| 3 | Final testing | 15 min | (Test endpoints) |
| 3 | Submission | 10 min | (Email judge) |
| **TOTAL** | **All phases** | **~8 hours** | — |

---

## 🎓 Learning Path

### Beginner (First-time users)
1. Read: [JUDGE_QUICK_START.md](JUDGE_QUICK_START.md)
2. Read: [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md)
3. Do: Phase 1 (baseline scoring)
4. Read: [SCORING_GUIDE.md](SCORING_GUIDE.md)
5. Read: [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md)

### Intermediate (Want to understand composition)
1. Read: [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md)
2. Read: vera_composer.py code
3. Read: [SCORING_GUIDE.md](SCORING_GUIDE.md)
4. Implement: Phase 2 optimizations

### Advanced (Want to customize or deploy)
1. Read: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Read: Dockerfile + docker-compose.yml
3. Read: bot_server.py
4. Deploy: Phase 3 to your platform

---

## 📝 Key Concepts

### 4-Context Framework
**Used by vera_composer to generate messages**:
- CategoryContext — Business type knowledge
- MerchantContext — Specific business state
- TriggerContext — Event prompting message
- CustomerContext — Customer state (optional)

See: [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md)

### 5-Dimension Scoring Rubric
**Used by judge to evaluate messages**:
1. Decision Quality (trigger selection + signal fit)
2. Specificity (real numbers, dates, facts)
3. Category Fit (tone, vocabulary, taboos)
4. Merchant Fit (personalization, signals)
5. Engagement Compulsion (reason to reply + CTA)

See: [SCORING_GUIDE.md](SCORING_GUIDE.md)

### Optimization Strategy
**To improve from 38 → 45+/50**:
1. Add category.voice rules (+3 pts)
2. Use merchant.signals (+2 pts)
3. Improve CTAs & reciprocity (+1-2 pts)
4. Signal-based routing (+1 pt)
5. Template validation (+1 pt)

See: [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md)

---

## 🔍 Debugging

### Problem: Judge times out
**Check**: bot_server.py responding <1 sec?
**Read**: [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md) → Debugging section

### Problem: Score doesn't improve after changes
**Check**: Are new context fields actually in dataset?
**Read**: [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) → Validation script

### Problem: Deployment fails
**Check**: Code pushed to GitHub?
**Read**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) → Option A/B/C

### Problem: Don't know where to start
**Read**: [JUDGE_QUICK_START.md](JUDGE_QUICK_START.md) (1 page) or [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md) (detailed)

---

## 📚 References

### Official Challenge Docs
- challenge-brief.md — Full challenge specification
- challenge-testing-brief.md — Testing contract
- engagement-design.md — Engagement patterns
- engagement-research.md — Research findings

### Code Files
- vera_composer.py — 400+ lines of composition logic
- bot_server.py — FastAPI with 5 endpoints
- judge_simulator.py — LLM-powered judge

### Generated Assets
- expanded/merchants/ — 50 merchant contexts
- expanded/customers/ — 200 customer contexts
- expanded/triggers/ — 100 trigger contexts
- expanded/test_pairs.json — 30 canonical test pairs

---

## ✅ Verification Checklist

**Before submitting to judge**:

- [ ] vera_composer.py is complete
- [ ] All 5 endpoints working (/healthz, /metadata, /context, /tick, /reply)
- [ ] test_composer.py passes all tests
- [ ] test_bot.py validates all endpoints
- [ ] judge_simulator.py score ≥ 45/50
- [ ] Bot deployed to public URL
- [ ] Public URL responds to all 5 endpoints
- [ ] Submission details verified (email, phone, name)

**Submit when all boxes checked!**

---

## 🎯 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Judge Score | 45+/50 | In progress |
| Decision Quality | 9/10 | 8/10 |
| Specificity | 10/10 | 9/10 |
| Category Fit | 9/10 | 6/10 ← Focus here |
| Merchant Fit | 9/10 | 7/10 ← Focus here |
| Engagement Compulsion | 9/10 | 8/10 |
| Bot deployed | Public URL | Phase 3 |
| All endpoints | 5/5 | ✅ 5/5 |
| Test pairs | 30/30 | ✅ 30/30 |

---

## 🚀 Next Steps

1. **Read** [JUDGE_QUICK_START.md](JUDGE_QUICK_START.md) (5 min)
2. **Get** LLM API key (OpenAI recommended)
3. **Run** Phase 1 baseline: `python judge_simulator.py` (30 min)
4. **Read** [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md) (20 min)
5. **Implement** Phase 2 optimizations (6-7 hours)
6. **Deploy** Phase 3 (1-2 hours)
7. **Submit** to judge

**Total time**: 8-9 hours from now to submission

---

## 📞 Support

**Question about...**
- Scoring → [SCORING_GUIDE.md](SCORING_GUIDE.md)
- Optimization → [SCORING_OPTIMIZATION.md](SCORING_OPTIMIZATION.md)
- Judge setup → [JUDGE_SETUP_GUIDE.md](JUDGE_SETUP_GUIDE.md)
- Deployment → [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Composition logic → [COMPOSER_ENGINE.md](COMPOSER_ENGINE.md)
- Overall plan → [JUDGE_SUBMISSION_ROADMAP.md](JUDGE_SUBMISSION_ROADMAP.md)

---

**Everything is ready. Let's get your score!** 🎉

Start with: [JUDGE_QUICK_START.md](JUDGE_QUICK_START.md)
