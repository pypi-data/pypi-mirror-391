#
#  Copyright 2025. Tabs Data Inc.
#

import os
import sys

import pandas as pd
from pymongo import MongoClient

MONGODB_HOST = os.getenv("MONGODB_HOST", "127.0.0.1")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "password")
MONGODB_USER = os.getenv("MONGODB_USER", "admin")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_URI_WITHOUT_CREDENTIALS = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}"
LOCAL_PERSONS_FILE = "data/persons.csv"


def _mongo_client():
    return MongoClient(
        MONGODB_URI_WITHOUT_CREDENTIALS,
        username=MONGODB_USER,
        password=MONGODB_PASSWORD,
    )


def read_from_mongo():
    client = _mongo_client()
    db = client["examples"]
    collection = db["example_16"]
    docs = list(collection.find({}))
    if docs:
        df = pd.DataFrame(docs)
        print(df)
    else:
        print("No documents found in MongoDB collection.")


def load_csv_to_mongo():
    df = pd.read_csv(LOCAL_PERSONS_FILE)
    client = _mongo_client()
    db = client["examples"]
    collection = db["example_16"]
    collection.delete_many({})
    collection.insert_many(df.to_dict(orient="records"))


def cleanup_mongo_collection():
    client = _mongo_client()
    db = client["examples"]
    collection = db["example_16"]
    collection.delete_many({})


def main():
    if len(sys.argv) == 1:
        print(
            "Missing argument. It must be one of: read-mongo, load-mongo, cleanup-mongo"
        )
    elif sys.argv[1] == "read-mongo":
        read_from_mongo()
    elif sys.argv[1] == "load-mongo":
        load_csv_to_mongo()
    elif sys.argv[1] == "cleanup-mongo":
        cleanup_mongo_collection()
    else:
        print(f"Unexpected option {sys.argv[1]}")


if __name__ == "__main__":
    main()
