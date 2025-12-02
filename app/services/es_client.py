import os
from typing import Optional

from elasticsearch import Elasticsearch

# 기본값: 로컬 도커로 띄운 ES
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")

_es_client: Optional[Elasticsearch] = None


def get_es_client() -> Elasticsearch:
    """
    Elasticsearch 클라이언트를 하나만 만들어서 재사용.
    """
    global _es_client
    if _es_client is None:
        _es_client = Elasticsearch(ES_HOST)
    return _es_client
