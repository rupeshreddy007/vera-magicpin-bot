# Vera AI Bot — Submission Checklist

## ✓ Core Files Created

- [x] **bot_server.py** — FastAPI server with 5 required endpoints
- [x] **test_bot.py** — Local test harness
- [x] **quick_test.py** — Quick startup verification
- [x] **requirements.txt** — Python dependencies
- [x] **README.md** — Setup, usage, and submission instructions
- [x] **.env.example** — Environment configuration template
- [x] **Dockerfile** — Container image for deployment
- [x] **docker-compose.yml** — Local development setup
- [x] **dataset/generate_dataset.py** — Dataset generator (provided)
- [x] **expanded/** — Generated dataset (50 merchants, 200 customers, 100 triggers)

## ✓ Endpoints Implemented

- [x] `GET /v1/healthz` — Liveness probe with uptime + context counts
- [x] `GET /v1/metadata` — Bot identity, model, approach, version
- [x] `POST /v1/context` — Store contexts (category/merchant/customer/trigger) with version tracking
- [x] `POST /v1/tick` — Periodic wake-up, compose and return messages
- [x] `POST /v1/reply` — Handle merchant/customer replies

## ✓ 4-Context Framework

- [x] **CategoryContext** — Slow-changing knowledge (voice, offers, digest, trends)
- [x] **MerchantContext** — Business state (perf, offers, signals, history)
- [x] **TriggerContext** — Event that prompts messaging (research, dip, recall, etc.)
- [x] **CustomerContext** — Customer state for customer-facing messages

## ✓ Message Composition

- [x] Uses Claude API for semantic composition
- [x] Extracts and optimizes for 5 evaluation dimensions:
  - Specificity (10) — Numbers, citations, dates
  - Category fit (10) — Tone, vocabulary, taboos
  - Merchant fit (10) — Real data, signals, offers
  - Trigger relevance (10) — Why messaging now
  - Engagement compulsion (10) — Curiosity, reciprocity, CTAs
- [x] Graceful fallbacks if API fails
- [x] Conversation state tracking

## ✓ Testing

- [x] Local test harness (`test_bot.py`) that:
  - Loads expanded dataset
  - Tests all 5 endpoints
  - Validates responses
  - Simulates merchant/customer replies
- [x] Quick startup test (`quick_test.py`)
- [x] Dataset generation verified

## ✓ Deployment Ready

- [x] Docker containerization
- [x] Docker Compose for local development
- [x] Environment variable configuration
- [x] Health check endpoints
- [x] Idempotent context storage
- [x] In-memory state management (suitable for testing)

## Setup Instructions

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Generate dataset (optional, already in repo)
python dataset/generate_dataset.py --seed-dir dataset --out ./expanded

# 4. Start bot server
python bot_server.py

# 5. In another terminal, test
python test_bot.py
```

### Docker Deployment

```bash
# Build image
docker build -t vera-bot .

# Run with API key
docker run -e ANTHROPIC_API_KEY="sk-ant-..." -p 8000:8000 vera-bot

# Or use docker-compose
export ANTHROPIC_API_KEY="sk-ant-..."
docker-compose up
```

### Submit to Judge

1. Ensure bot server is running and publicly accessible
2. Provide base URL: `https://your-domain.com`
3. Judge will verify these are live:
   - `GET https://your-domain.com/v1/healthz` → 200
   - `GET https://your-domain.com/v1/metadata` → 200 + JSON
   - `POST https://your-domain.com/v1/context` → 200 + JSON
   - `POST https://your-domain.com/v1/tick` → 200 + actions array
   - `POST https://your-domain.com/v1/reply` → 200 + action response

## Submission Details

- **Team**: magicpin
- **Contact Email**: vera@magicpin.com
- **Phone**: 9999999999
- **LinkedIn**: https://www.linkedin.com/company/samast-technologies
- **Bot Model**: Claude 3.5 Sonnet
- **Approach**: Single-prompt composer with 4-context dispatch by trigger.kind

## Performance Targets

Based on case studies, target scores:
- **Specificity**: 9-10 (use real numbers, dates, prices)
- **Category fit**: 9-10 (match voice, avoid taboos)
- **Merchant fit**: 9-10 (reference their specific data)
- **Trigger relevance**: 10 (make clear why messaging now)
- **Engagement compulsion**: 8-9 (curiosity + reciprocity + CTAs)

**Target**: 45-49/50 per message

## Key Architecture Decisions

1. **In-memory state** — Fast, suitable for testing. For production, use Redis/DynamoDB.
2. **Claude composition** — Single LLM call per message, structured prompt extraction.
3. **Idempotent context storage** — By `(context_id, version)` tuple, handles out-of-order updates.
4. **Fallback degradation** — If Claude fails, return simple message (graceful).
5. **Stateless design** — Bot can be scaled horizontally with shared state store.

## Next Steps (Post-Submission)

- [ ] Set up database (Redis) for distributed state
- [ ] Add monitoring/logging (CloudWatch, Datadog)
- [ ] Implement conversation persistence
- [ ] A/B test prompt variants
- [ ] Add fine-tuning for category-specific messages
- [ ] Expand to 100+ merchants with real magicpin data
