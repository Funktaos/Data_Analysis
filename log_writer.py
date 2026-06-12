from pymongo import MongoClient
from config import mongo_config
from datetime import datetime


def save_search(query_type, search_params, results_count):
    """
    Сохранить поисковый запрос в MongoDB.
    query_type: "keyword" или "category_year"
    search_params: dict с параметрами поиска
    results_count: общее количество найденных фильмов
    """
    client = MongoClient(mongo_config)
    try:
        db = client["ich_edit"]
        collection = db["final_project_281125_dam_Kirill_L"]

        record = {
            "query_type": query_type,
            "params": search_params,
            "results_count": results_count,
            "timestamp": datetime.utcnow(),
        }
        collection.insert_one(record)
    finally:
        client.close()