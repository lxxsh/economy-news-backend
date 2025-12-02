from datetime import datetime
from typing import List

from elasticsearch import NotFoundError

from app.schemas.saved_news import (
    SavedNewsCreate,
    SavedNews,
    SavedNewsListResponse,
)
from app.services.es_client import get_es_client

INDEX_NAME = "saved_econ_news"


def ensure_index():
    """
    인덱스가 없으면 간단한 매핑으로 생성.
    개발용이라 매핑은 최소만 잡음.
    """
    es = get_es_client()

    if es.indices.exists(index=INDEX_NAME):
        return

    body = {
        "mappings": {
            "properties": {
                "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "content": {"type": "text"},
                "link": {"type": "keyword"},
                "source": {"type": "keyword"},
                "category": {"type": "keyword"},
                "published": {"type": "text"},
                "published_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd||strict_date_optional_time||epoch_millis",
                },
                "saved_at": {"type": "date"},
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=body)


def save_news(doc: SavedNewsCreate) -> SavedNews:
    """
    기사 1건을 Elasticsearch에 저장.
    """
    ensure_index()
    es = get_es_client()

    body = doc.dict()
    body["saved_at"] = datetime.utcnow()

    resp = es.index(index=INDEX_NAME, document=body)
    es_id = resp["_id"]

    return SavedNews(id=es_id, saved_at=body["saved_at"], **doc.dict())


def list_saved_news(page: int = 1, size: int = 10) -> SavedNewsListResponse:
    """
    저장된 기사 목록 조회 (saved_at 기준 최신순)
    """
    ensure_index()
    es = get_es_client()

    from_ = (page - 1) * size

    resp = es.search(
        index=INDEX_NAME,
        body={
            "query": {"match_all": {}},
            "sort": [{"saved_at": {"order": "desc"}}],
            "from": from_,
            "size": size,
        },
    )

    hits = resp["hits"]["hits"]
    total = resp["hits"]["total"]["value"]

    items: List[SavedNews] = []
    for hit in hits:
        src = hit["_source"]
        saved_at = src.get("saved_at")

        # saved_at이 문자열로 들어올 수도 있어서 처리
        if isinstance(saved_at, str):
            saved_at = datetime.fromisoformat(saved_at.replace("Z", "+00:00"))

        items.append(
            SavedNews(
                id=hit["_id"],
                title=src.get("title"),
                content=src.get("content"),
                link=src.get("link"),
                source=src.get("source"),
                category=src.get("category"),
                published=src.get("published"),
                published_date=src.get("published_date"),
                saved_at=saved_at,
            )
        )

    return SavedNewsListResponse(
        items=items,
        total_count=total,
        page=page,
        size=size,
    )


def delete_saved_news(news_id: str) -> bool:
    """
    (선택) 저장된 기사 삭제용. 지금은 프론트에서 안 써도 됨.
    """
    es = get_es_client()
    try:
        es.delete(index=INDEX_NAME, id=news_id)
        return True
    except NotFoundError:
        return False
