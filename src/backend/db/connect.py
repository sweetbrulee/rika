import os
import pymongo
from motor import motor_asyncio

cluster_async = motor_asyncio.AsyncIOMotorClient(os.getenv("RIKA_DB_STRING"))
cluster_sync = pymongo.MongoClient(os.getenv("RIKA_DB_STRING"))

if os.getenv("RIKA_MODE") == "prod":
    db_sync = cluster_sync["main"]
    db_async = cluster_async["main"]
elif os.getenv("RIKA_MODE") in ["dev", "stag"]:
    db_sync = cluster_sync["test"]
    db_async = cluster_async["test"]
