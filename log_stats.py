from pymongo import MongoClient
from config import mongo_config


def _query_to_string(query_type, params):
    if query_type == "keyword":
        mode = "title + description" if params.get("include_description") else "title"
        return f"keyword: {params.get('keyword', '')} ({mode})"

    if query_type == "category_year":
        return (
            f"category: {params.get('category', '')}, "
            f"years: {params.get('min_year', '')}-{params.get('max_year', '')}"
        )

    return str(params) if params else "неизвестный запрос"


def get_top_5_queries():
    """
    Получить 5 популярных запросов по частоте.
    Возвращает список (запрос, частота).
    """
    client = MongoClient(mongo_config)
    try:
        db = client["ich_edit"]
        collection = db["final_project_281125_dam_Kirill_L"]

        pipeline = [
            {
                "$group": {
                    "_id": {"query_type": "$query_type", "params": "$params"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]

        results = []
        for doc in collection.aggregate(pipeline):
            _id = doc.get("_id") or {}
            params = _id.get("params") or {}
            query_type = _id.get("query_type") or "unknown"
            count = doc.get("count", 0)

            results.append((_query_to_string(query_type, params), count))

        return results
    finally:
        client.close()


def get_last_5_queries():
    """
    Получить последние 5 уникальных запросов по времени.
    Уникальность считается по строке, которая показывается пользователю,
    даже если 1 поиск был по названию, а другой - по описанию.
    Возвращает список (запрос, timestamp).
    """
    client = MongoClient(mongo_config)
    try:
        db = client["ich_edit"]
        collection = db["final_project_281125_dam_Kirill_L"]

        cursor = collection.find().sort("timestamp", -1)

        results = []
        seen_queries = set()

        for doc in cursor:
            params = doc.get("params") or {}
            ts = doc.get("timestamp")
            query_type = doc.get("query_type") or "unknown"

            query_str = _query_to_string(query_type, params)

            if query_str in seen_queries:
                continue

            seen_queries.add(query_str)
            results.append((query_str, ts))

            if len(results) == 5:
                break

        return results
    finally:
        client.close()