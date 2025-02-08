import logging
import redis

from conf.database import client, connect
from redis_lru import RedisLRU
from pymongo import errors

redis_client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(redis_client)

db = client["quotes"]
quote_constructor = {"name": "author", "tag": "tags", "tags": "tags"}
author_constructor = {"person": "name", "description": "description"}


@cache
def find_in_documents(col: str, obj: dict):
    """Searching for data in database documents
    with using regex matching
    and returning string data about quotes or authors"""
    try:
        object_key = list(obj.keys())[0]
        value = obj[object_key]
        key = quote_constructor[object_key] if object_key in quote_constructor \
            else author_constructor[object_key]
        fetched_data = None
        match key:
            case "author" | "tag" | "tags":
                fetched_data = db[col].find(
                    {key: {"$regex": value, "$options": "i"}}
                    if key in ["author", "tag"]
                    else {"$or": [{key: {"$regex": value[0], "$options": "i"}},
                                  {{key: {"$regex": value[1]}, "$options": "i"}}]}
                )
            case "name" | "description":
                fetched_data = db[col].find({key: {"$regex": value, "$options": "i"}})
        result = ""
        for doc in fetched_data:
            keys = doc.keys()
            for key in keys:
                if key in ["_id", "tags"]:
                    continue
                result += f"{key}: {doc.get(key)}\n"
        logging.info("Fetching data successfully") if result \
            else logging.info("Doesn't find any result for this request")
        return result
    except errors.PyMongoError as err:
        logging.error(f"Error while searching for data{err}")


if __name__ == "__main__":
    print(find_in_documents("author", {"person": "stev"}))
