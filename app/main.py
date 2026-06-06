from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import compress, proxy, keys, webhooks

app = FastAPI(
    title="Headroom API",
    description="""
## Hosted Headroom API

Compress your LLM context by **60–95%** before sending to OpenAI or Anthropic.
Cut your API bill dramatically — no infrastructure to manage.

### Quick Start

1. **Get an API key** — `POST /v1/keys/`
2. **Compress your messages** — `POST /v1/compress`
3. **Or use proxy mode** — point your OpenAI client at `/v1/proxy/openai`

### Authentication
All endpoints (except `/v1/keys/` and `/health`) require an `X-API-Key` header.

```
X-API-Key: hr_your_api_key_here
```

### Pricing

| Plan     | Price    | Tokens/month |
|----------|----------|--------------|
| Starter  | $29/mo   | 10M tokens   |
| Builder  | $99/mo   | 50M tokens   |
| Scale    | $299/mo  | 250M tokens  |
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compress.router)
app.include_router(proxy.router)
app.include_router(keys.router)
app.include_router(webhooks.router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "Headroom API",
        "docs": "/docs",
        "version": "0.1.0",
        "endpoints": {
            "compress": "POST /v1/compress",
            "proxy": "POST /v1/proxy/openai/chat/completions",
            "usage": "GET /v1/keys/usage",
            "create_key": "POST /v1/keys/",
        },
    }
