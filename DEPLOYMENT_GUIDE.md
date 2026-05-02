# Vera AI Bot — Cloud Deployment Guide

## Option 1: Deploy to Render (Recommended for Quick Setup)

### Prerequisites
- Render account (free tier available)
- GitHub repo with the bot code
- Anthropic API key

### Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Vera AI Bot submission"
git push origin main
```

2. **Create New Web Service on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select branch: `main`

3. **Configure Service**
   - **Name**: `vera-bot`
   - **Root Directory**: `/` (leave empty)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python dataset/generate_dataset.py --seed-dir dataset --out ./expanded`
   - **Start Command**: `python bot_server.py`
   - **Plan**: Free (or Starter for production)

4. **Set Environment Variables**
   - Click "Environment"
   - Add: `ANTHROPIC_API_KEY` = `sk-ant-...`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete
   - Copy public URL (e.g., `https://vera-bot-xxxx.onrender.com`)

6. **Test**
```bash
curl https://vera-bot-xxxx.onrender.com/v1/healthz
```

## Option 2: Deploy to Railway

### Steps

1. **Push to GitHub** (same as Render)

2. **Connect Railway**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Select your repo

3. **Configure**
   - Add `ANTHROPIC_API_KEY` environment variable
   - Railway auto-detects Python

4. **Deploy**
   - Click deploy
   - Get public URL

## Option 3: Deploy to AWS (Lambda + API Gateway)

### Setup (using Serverless Framework)

```bash
# Install serverless
npm install -g serverless

# Create service
serverless create --template aws-python-http-api --path vera-bot

# Configure AWS credentials
serverless config credentials --provider aws --key YOUR_KEY --secret YOUR_SECRET
```

### Edit serverless.yml

```yaml
service: vera-bot

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    ANTHROPIC_API_KEY: ${env:ANTHROPIC_API_KEY}

functions:
  bot:
    handler: bot_server.app
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

### Deploy

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
serverless deploy
```

## Option 4: Deploy to Google Cloud Run

### Steps

```bash
# Create project
gcloud projects create vera-bot

# Set project
gcloud config set project vera-bot

# Create .gcloudignore
cat > .gcloudignore << EOF
.git
.gitignore
__pycache__
*.pyc
.pytest_cache
.DS_Store
EOF

# Deploy
gcloud run deploy vera-bot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-...
```

## Option 5: Deploy to Azure Container Instances

```bash
# Build image
docker build -t vera-bot:latest .

# Push to Azure Container Registry
az acr build --registry myregistry --image vera-bot:latest .

# Deploy
az container create \
  --resource-group mygroup \
  --name vera-bot \
  --image myregistry.azurecr.io/vera-bot:latest \
  --environment-variables ANTHROPIC_API_KEY=sk-ant-... \
  --ports 8000 \
  --ip-address public
```

## Health Check Configuration

Most platforms support health checks. Configure:

- **Endpoint**: `/v1/healthz`
- **Port**: `8000`
- **Interval**: `30s`
- **Timeout**: `10s`
- **Retries**: `3`

## Environment Variables to Set

On your cloud platform, set:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Optional:
```
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

## Monitoring

### Render
- Built-in logs at https://render.com/dashboard
- Email notifications for failures

### Railway
- Logs in Railway dashboard
- Email notifications

### AWS
- CloudWatch logs
- X-Ray for tracing
- SNS for alerts

### Google Cloud Run
- Cloud Logging
- Cloud Monitoring
- Error Reporting

## Cost Estimates

| Provider | Free Tier | Notes |
|----------|-----------|-------|
| **Render** | 500 free hours/month | Good for testing |
| **Railway** | $5 credit/month | Production-ready |
| **AWS** | 1M requests/month | Pay-per-use after free tier |
| **Google Cloud Run** | 2M requests/month | Cheapest at scale |
| **Heroku** | ❌ (Paid only) | $7/month minimum |

## Testing After Deployment

```bash
BOT_URL="https://your-deployment-url"

# Health check
curl $BOT_URL/v1/healthz

# Metadata
curl $BOT_URL/v1/metadata

# Context push
curl -X POST $BOT_URL/v1/context \
  -H "Content-Type: application/json" \
  -d @test_context.json

# Tick
curl -X POST $BOT_URL/v1/tick \
  -H "Content-Type: application/json" \
  -d '{"now":"2026-04-26T10:30:00Z","available_triggers":[]}'
```

## Troubleshooting

### 500 Internal Server Error
- Check logs for Python exceptions
- Verify `ANTHROPIC_API_KEY` is set
- Check Claude API quota

### Timeout (30s)
- Message composition taking too long
- Check Claude API latency
- Reduce max_tokens if needed

### 404 Not Found
- Verify endpoint paths (must be exactly `/v1/XXX`)
- Check request JSON structure

## Auto-deployment from GitHub

Most platforms support auto-deploy on push:

1. Connect GitHub repo
2. Set branch (main)
3. On each push, auto-rebuild and deploy
4. Rollback on build failures

Recommended setup:
```bash
# Branch protection
main branch requires:
  - Tests pass
  - All reviews approved
```

## Final Checklist

- [ ] App deployed and publicly accessible
- [ ] `GET /v1/healthz` returns 200
- [ ] `GET /v1/metadata` returns bot info
- [ ] `ANTHROPIC_API_KEY` environment variable set
- [ ] Health checks pass
- [ ] Public URL working
- [ ] Ready for judge harness
