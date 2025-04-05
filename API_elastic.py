from fastapi import FastAPI, Query
from elasticsearch import AsyncElasticsearch
from typing import List
import logging

app = FastAPI()
ES_HOST = "http://localhost:9200"
ES_USER = "elastic"
ES_PASSWORD = "123123"

es = AsyncElasticsearch(
    hosts=[ES_HOST],
    basic_auth=(ES_USER, ES_PASSWORD)
)

INDEX_NAME = "openalex_list_works_v0.1"

def build_query(query: str, search_field: List[str], date_field: str, years: List[int], min_score: float, match_type: str) -> dict:
    if match_type == "exact":
        return {
            "min_score": min_score,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                            "title": {
                                "query": query,
                                "operator": "and"
                            }
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                date_field: {
                                    "gte": min(years),
                                    "lte": max(years)
                                }
                            }
                        }
                    ]
                }
            }
        }
    else:
        return {
            "min_score": min_score,
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "fields": search_field,
                                "query": query
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                date_field: {
                                    "gte": min(years),
                                    "lte": max(years)
                                }
                            }
                        }
                    ]
                }
            }
        }


@app.get("/search/")
async def search(
    query: str = Query(..., min_length=1),
    num_articles: int = Query(10, alias="num_articles"),
    min_year: int = Query(2000, alias="min_year"),
    max_year: int = Query(2025, alias="max_year"),
    min_score: float = Query(1.0, alias="min_score"),
    match_type: str = Query("smart", alias="match_type")  # Добавляем параметр match_type
):
    try:
        # Формируем запрос с учетом match_type
        query_body = build_query(
            query=query,
            search_field=["title", "abstract", "keywords"],
            date_field="publication_year",
            years=[min_year, max_year], 
            min_score=min_score,
            match_type=match_type  # Передаем match_type в запрос
        )

        response = await es.search(index=INDEX_NAME, body=query_body, size=num_articles)

        return {"hits": response["hits"]["hits"]}
    
    except Exception as e:
        logging.error(f"Ошибка в /search/: {e}")
        return {"error": str(e)}

@app.get("/article/{article_id}")
async def get_article(article_id: str):
    """Получение информации о статье по ID"""
    try:
        response = await es.get(index=INDEX_NAME, id=article_id)
        return response["_source"]  # Возвращаем содержимое статьи
    except Exception as e:
        logging.error(f"Ошибка при получении статьи {article_id}: {e}")
        return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown():
    await es.close()
