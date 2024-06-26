import datetime
import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi


def connect_to_db():
    client = MongoClient(
        host="mongodb://db_user:12341234@mongodb:27017/?authSource=test_db",
        server_api=ServerApi("1"),
    )
    return client


def insert_one(db, name: str, message: str):
    date = datetime.datetime.now()
    result_one = db.insert_one(
        {
            "date": date,
            "username": name,
            "message": message,
        }
    )

    print("Inserted item ID:", result_one.inserted_id)
