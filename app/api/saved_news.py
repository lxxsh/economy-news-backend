from fastapi import APIRouter, HTTPException, Query

from app.schemas.saved_news import (
    SavedNewsCreate,
    SavedNews,
    SavedNewsListResponse,
)
from app.services.saved_news import (
    save_news,
    list_saved_news,
    delete_saved_news,
)

router = APIRouter(prefix="/saved-news", tags=["saved-news"])


@router.post("", response_model=SavedNews)
async def save_news_endpoint(payload: SavedNewsCreate):
    """
    사용자가 선택한 기사를 Elasticsearch에 저장.
    """
    return save_news(payload)


@router.get("", response_model=SavedNewsListResponse)
async def list_saved_news_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    """
    저장된 기사 목록 조회 (saved_at 기준 최신순).
    """
    return list_saved_news(page=page, size=size)


@router.delete("/{news_id}")
async def delete_saved_news_endpoint(news_id: str):
    """
    저장된 기사 삭제 (선택 기능).
    """
    ok = delete_saved_news(news_id)
    if not ok:
        raise HTTPException(status_code=404, detail="해당 ID의 문서를 찾을 수 없습니다.")
    return {"status": "ok"}
