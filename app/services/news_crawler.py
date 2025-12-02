from typing import List, Optional, Tuple, Set
from datetime import datetime, date as date_type

import feedparser

from app.schemas.news import News


# RSS 소스 확장
RSS_SOURCES = {
    "global": {
        "bbc": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "reuters": "https://www.reuters.com/business/?feedType=RSS",
        "cnbc": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    },
    "korea": {
        "hankyung": "https://www.hankyung.com/feed/economy",
        "mk": "https://www.mk.co.kr/rss/30100041/",           # 매일경제 경제
        "yonhap": "https://www.yna.co.kr/economy/all/rss",   # 연합뉴스 경제
    },
}


def _extract_published(entry) -> Tuple[Optional[datetime], Optional[str]]:
    """RSS entry에서 발행일을 파싱해 datetime + 문자열을 반환"""
    dt: Optional[datetime] = None

    if getattr(entry, "published_parsed", None):
        dt = datetime(*entry.published_parsed[:6])
    elif getattr(entry, "updated_parsed", None):
        dt = datetime(*entry.updated_parsed[:6])

    text: Optional[str] = None
    if dt:
        text = dt.isoformat()
    elif getattr(entry, "published", None):
        text = entry.published
    elif getattr(entry, "updated", None):
        text = entry.updated

    return dt, text


def fetch_latest_news(
    category: str = "global",
    keyword: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    sort: str = "desc",
) -> List[News]:
    """
    /news용: 특정 category에서
    키워드/날짜 필터 + 정렬 + 중복 제거 후 전체 리스트 반환
    (페이지네이션은 API 레이어에서 처리)
    """
    if category not in RSS_SOURCES:
        raise ValueError(f"지원하지 않는 category입니다: {category}")

    keyword_lower = keyword.lower() if keyword else None

    # 날짜 범위 파싱
    from_dt = date_type.fromisoformat(from_date) if from_date else None
    to_dt = date_type.fromisoformat(to_date) if to_date else None

    seen_links: Set[str] = set()
    seen_titles: Set[str] = set()

    news_list: List[News] = []
    current_id = 1

    for source_name, rss_url in RSS_SOURCES[category].items():
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            title = entry.title.strip()
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            summary = summary.strip()

            # 날짜 추출
            published_dt, published_text = _extract_published(entry)
            published_date_str = (
                published_dt.date().isoformat() if published_dt else None
            )

            # 날짜 범위 필터
            if (from_dt or to_dt) and published_date_str:
                entry_date = date_type.fromisoformat(published_date_str)

                if from_dt and entry_date < from_dt:
                    continue
                if to_dt and entry_date > to_dt:
                    continue

            # 키워드 필터
            if keyword_lower:
                combined = f"{title} {summary}".lower()
                if keyword_lower not in combined:
                    continue

            # 중복 제거 (link 우선, 없으면 title 기준)
            link = getattr(entry, "link", None)
            if link:
                if link in seen_links:
                    continue
                seen_links.add(link)
            else:
                if title in seen_titles:
                    continue
                seen_titles.add(title)

            news_list.append(
                News(
                    id=current_id,
                    title=title,
                    content=summary,
                    link=link,
                    source=source_name,
                    published=published_text,
                    published_date=published_date_str,
                )
            )
            current_id += 1

    # 정렬
    news_list.sort(
        key=lambda n: (n.published_date or ""),
        reverse=(sort == "desc"),
    )

    return news_list


def fetch_top_headlines(
    limit: int = 10,
    sort: str = "desc",
) -> List[News]:
    """
    /news/top용: 모든 카테고리(global + korea)에서
    최신 헤드라인 TOP N을 가져옴.
    키워드/날짜 입력 없이 자동으로 상위 기사만.
    """
    seen_links: Set[str] = set()
    seen_titles: Set[str] = set()

    news_list: List[News] = []
    current_id = 1

    for category, sources in RSS_SOURCES.items():
        for source_name, rss_url in sources.items():
            feed = feedparser.parse(rss_url)

            for entry in feed.entries:
                title = entry.title.strip()
                summary = getattr(entry, "summary", "") or getattr(
                    entry, "description", ""
                )
                summary = summary.strip()

                # 날짜 추출
                published_dt, published_text = _extract_published(entry)
                published_date_str = (
                    published_dt.date().isoformat() if published_dt else None
                )

                # 중복 제거
                link = getattr(entry, "link", None)
                if link:
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                else:
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)

                news_list.append(
                    News(
                        id=current_id,
                        title=title,
                        content=summary,
                        link=link,
                        source=source_name,
                        published=published_text,
                        published_date=published_date_str,
                    )
                )
                current_id += 1

    # 정렬
    news_list.sort(
        key=lambda n: (n.published_date or ""),
        reverse=(sort == "desc"),
    )

    # TOP N만 잘라서 반환
    return news_list[:limit]
