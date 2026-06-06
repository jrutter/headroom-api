# Headroom API

> **Weekly Build #2** — Selected from the Daily AI Builder Digest, 2026-06-06
> Built by Jake Rutter with Claude Code in ~1 hour

A hosted REST API that wraps the open-source [Headroom](https://github.com/chopratejas/headroom) library to compress LLM context by 60–95%. Send your messages, get back compressed tokens, cut your OpenAI/Anthropic API bill immediately.

**Live API:** https://headroom-api.vercel.app
**Docs:** https://headroom-api.vercel.app/docs

---

## The Opportunity

Headroom hit GitHub Trending with 26K+ stars — it compresses LLM context with no accuracy loss. No one has built a hosted, no-code API wrapper for it yet. Every team spending meaningfully on OpenAI/Anthropic has this pain right now, and the ROI calculation sells itself instantly.

**Business model:** Usage-based SaaS ($29–$299/month)
**Target customer:** Solo founders and small teams spending $500–$10,000+/month on LLM API costs
**Realistic MRR at 6 months:** $5,500 (80 customers across tiers)

### Pricing

| Plan    | Price    | Tokens/month | Overage     |
|---------|----------|--------------|-------------|
| Starter | $29/mo   | 10M tokens   | $0.25/M     |
| Builder | $99/mo   | 50M tokens   | $0.20/M     |
| Scale   | $299/mo  | 250M tokens  | $0.15/M     |

**Why this pricing works:** A team spending $1,000/mo on OpenAI with 70% compression saves $700/mo. Paying $99/mo is a 7x ROI.

---

## Quick Start

### 1. Get an API key
```bash
curl -X POST https://headroom-api.vercel.app/v1/keys/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your-email", "name": "production"}'
```

### 2. Compress your messages
```bash
curl -X POST https://headroom-api.vercel.app/v1/compress \
  -H "X-API-Key: hr_your_key" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "..."}]}'
```

### 3. Or use drop-in proxy mode (zero code changes)
```python
import openai

client = openai.OpenAI(
    base_url="https://headroom-api.vercel.app/v1/proxy/openai",
    api_key="hr_your_headroom_key",
    default_headers={"X-OpenAI-Key": "sk-your-openai-key"}
)
# Everything else stays exactly the same
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/compress` | POST | Compress messages array |
| `/v1/proxy/openai/chat/completions` | POST | Drop-in OpenAI proxy |
| `/v1/keys/` | POST | Create API key |
| `/v1/keys/usage` | GET | Get usage stats |
| `/webhooks/stripe` | POST | Stripe subscription events |
| `/docs` | GET | Interactive API docs (Swagger) |
| `/health` | GET | Health check |

### Compression response
```json
{
  "compressed_messages": [...],
  "tokens_in": 1200,
  "tokens_out": 380,
  "tokens_saved": 820,
  "reduction_pct": 68.3,
  "object": "compression"
}
```

---

## Tech Stack

| Layer | Tool | Notes |
|-------|------|-------|
| API | FastAPI (Python) | Headroom is Python-native |
| Compression | Headroom library | 60–95% token reduction |
| Auth | API key via `X-API-Key` header | |
| Database | Supabase (Postgres) | API key storage + usage metering |
| Billing | Stripe Metered Billing | Usage-based pricing |
| Hosting | Railway / Fly.io | Python-friendly deployment |

---

## Project Structure

```
app/
├── main.py                    # FastAPI app + router registration
├── config.py                  # Environment variables
├── compression.py             # Headroom wrapper (mock + real)
├── database.py                # Supabase client (mock + real)
├── middleware/
│   └── auth.py                # API key validation dependency
└── routers/
    ├── compress.py            # POST /v1/compress
    ├── proxy.py               # POST /v1/proxy/openai/...
    ├── keys.py                # POST /v1/keys/, GET /v1/keys/usage
    └── webhooks.py            # POST /webhooks/stripe
```

---

## Running Locally

```bash
git clone https://github.com/jrutter/headroom-api
cd headroom-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

Works fully with mocks — no API keys needed to run locally.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | For production | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | For production | Supabase service role key |
| `STRIPE_SECRET_KEY` | For billing | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | For billing | Stripe webhook signing secret |
| `OPENAI_API_KEY` | For proxy mode | Optional — customers pass their own |

---

## Getting the First 10 Customers

1. Comment on the Headroom GitHub repo — people ask "is there a hosted version?" Answer them
2. Post on IndieHackers: "I built a hosted API for Headroom — free for first 10 beta users"
3. DM people who starred Headroom on GitHub today (2,473 warm leads)
4. Post benchmark results on X/Twitter — tokens in vs. out on real GPT-4 conversations
5. Post in r/LLMDevs and r/MachineLearning with compression benchmarks

---

## Next Steps

- [ ] Install real Headroom library and benchmark compression rates
- [ ] Connect Supabase (replace mock in `app/database.py`)
- [ ] Set up Stripe metered billing products + price IDs
- [ ] Build landing page with live compression demo
- [ ] Add streaming proxy support
- [ ] Add per-customer rate limiting

---

*Part of the [Daily AI Monetization](https://app.notion.com/p/376cecd422ad803ca4a3ec6697dfd2f0) series — one AI product built per week.*
