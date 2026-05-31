from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="5.0.0")
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
