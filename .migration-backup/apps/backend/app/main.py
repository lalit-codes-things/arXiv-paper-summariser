from __future__ import annotations

import importlib.util

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import router
from app.core.config import settings
from app.core.rate_limit import limiter

app = FastAPI(title=settings.app_name, version="5.0.0")
app.state.limiter = limiter

if importlib.util.find_spec('slowapi') is not None:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.arxivcopilot.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/healthz", tags=["ops"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "version": settings.api_version}


@app.get("/metrics", include_in_schema=False)
def metrics() -> str:
    return "arxiv_copilot_health{service=\"api\"} 1\n"
