from typing import Optional, List

from pydantic import BaseModel


class News(BaseModel):
    id: int
    title: str
    content: str
    link: Optional[str] = None
    source: Optional[str] = None
    published: Optional[str] = None        # 전체 날짜/시간 문자열
    published_date: Optional[str] = None   # 날짜만 (YYYY-MM-DD)


class NewsListMeta(BaseModel):
    category: str
    keyword: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    sort: str = "desc"

    page: int
    size: int

    total_count: int       # 필터 적용 후 전체 개수
    page_count: int        # 전체 페이지 수
    result_count: int      # 현재 페이지에 실제로 포함된 개수


class NewsListResponse(BaseModel):
    items: List[News]
    meta: NewsListMeta
