from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException

from app.schemas.news import News, NewsListResponse, NewsListMeta
from app.services.news_crawler import (
    fetch_latest_news,
    fetch_top_headlines,
    RSS_SOURCES,
)

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=NewsListResponse)
async def get_news_list(
    category: str = Query(
        "korea",
        description="뉴스 카테고리: global 또는 korea",
    ),
    page: int = Query(
        1,
        ge=1,
        description="페이지 번호 (1부터 시작)",
    ),
    size: int = Query(
        10,
        ge=1,
        le=50,
        description="한 페이지당 뉴스 개수 (1~50)",
    ),
    keyword: Optional[str] = Query(
        None,
        description="제목/본문에 포함될 키워드 (옵션)",
    ),
    from_date: Optional[str] = Query(
        None,
        description="시작 날짜 (YYYY-MM-DD, 옵션)",
    ),
    to_date: Optional[str] = Query(
        None,
        description="종료 날짜 (YYYY-MM-DD, 옵션)",
    ),
    sort: str = Query(
        "desc",
        description="정렬 순서 (desc=최신순, asc=오래된순)",
    ),
):
    # category 검증
    if category not in RSS_SOURCES.keys():
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 category입니다: {category}. 사용 가능 값: {list(RSS_SOURCES.keys())}",
        )

    # sort 검증
    if sort not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail="sort 파라미터는 'asc' 또는 'desc'만 가능합니다.",
        )

    # 전체 리스트 크롤링
    try:
        all_items = fetch_latest_news(
            category=category,
            keyword=keyword,
            from_date=from_date,
            to_date=to_date,
            sort=sort,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total_count = len(all_items)

    # 페이지네이션
    start = (page - 1) * size
    end = start + size
    page_items = all_items[start:end]

    page_count = (total_count + size - 1) // size if total_count > 0 else 0

    meta = NewsListMeta(
        category=category,
        keyword=keyword,
        from_date=from_date,
        to_date=to_date,
        sort=sort,
        page=page,
        size=size,
        total_count=total_count,
        page_count=page_count,
        result_count=len(page_items),
    )

    return NewsListResponse(items=page_items, meta=meta)


@router.get("/top", response_model=List[News])
async def get_top_headlines(
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="가져올 TOP 헤드라인 개수 (기본 10)",
    ),
    sort: str = Query(
        "desc",
        description="정렬 순서 (desc=최신순, asc=오래된순)",
    ),
):
    """
    사용자 입력 없이, 전체 카테고리(global + korea)에서
    최신 경제 헤드라인 TOP N을 가져오는 엔드포인트.
    """
    if sort not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail="sort 파라미터는 'asc' 또는 'desc'만 가능합니다.",
        )

    try:
        items = fetch_top_headlines(limit=limit, sort=sort)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return items
