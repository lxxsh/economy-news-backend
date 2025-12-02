import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, news, saved_news

# 저장 기능 ON/OFF 플래그
# - 기본값: true (네 로컬 개발 환경)
# - 배포 환경에서 FEATURE_SAVE_ENABLED=false 로 설정하면 라이트 버전이 됨
FEATURE_SAVE_ENABLED = (
    os.getenv("FEATURE_SAVE_ENABLED", "true").lower() == "true"
)

app = FastAPI(
    title="경제 뉴스 프로젝트 - A버전",
    description="글로벌 + 한국 경제 뉴스 API (크롤링 + 필터 + (옵션) 저장 기능)",
    version="0.9.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 라우터
app.include_router(health.router)
app.include_router(news.router)

# 저장 기능이 켜져 있을 때만 /saved-news 라우터 등록
if FEATURE_SAVE_ENABLED:
    app.include_router(saved_news.router)
