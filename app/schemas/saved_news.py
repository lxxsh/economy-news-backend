from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel


class SavedNewsBase(BaseModel):
    title: str
    content: Optional[str] = None
    link: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None  # korea / global 등
    published: Optional[str] = None
    published_date: Optional[str] = None  # YYYY-MM-DD


class SavedNewsCreate(SavedNewsBase):
    """
    클라이언트(리액트)에서 저장 요청 보낼 때 쓰는 스키마
    """
    pass


class SavedNews(SavedNewsBase):
    """
    ES에 실제 저장된 문서를 API로 돌려줄 때 쓰는 스키마
    """
    id: str
    saved_at: datetime

    class Config:
        orm_mode = True


class SavedNewsListResponse(BaseModel):
    items: List[SavedNews]
    total_count: int
    page: int
    size: int
