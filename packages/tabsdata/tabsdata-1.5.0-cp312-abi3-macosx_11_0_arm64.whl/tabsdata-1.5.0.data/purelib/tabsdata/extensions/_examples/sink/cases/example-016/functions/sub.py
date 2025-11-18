#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

MONGODB_HOST = os.getenv("MONGODB_HOST", "127.0.0.1")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "password")
MONGODB_USER = os.getenv("MONGODB_USER", "admin")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_URI_WITHOUT_CREDENTIALS = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}"


#
# Subscriber that loads CSV data from a TabsData table into a MongoDB collection.
#
@td.subscriber(
    tables="persons",
    destination=td.MongoDBDestination(
        MONGODB_URI_WITHOUT_CREDENTIALS,
        ("examples.example_16", None),
        credentials=td.UserPasswordCredentials(MONGODB_USER, MONGODB_PASSWORD),
        if_collection_exists="replace",
    ),
)
def sub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
