#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "mysql")
DB_DATABASE = os.getenv("MYSQL_DATABASE", "example_22")


@td.subscriber(
    tables="persons",
    destination=td.MySQLDestination(
        uri=f"mysql://{DB_HOST}:{DB_PORT}/{DB_DATABASE}",
        destination_table="persons",
        credentials=td.UserPasswordCredentials(DB_USER, DB_PASSWORD),
    ),
)
def sub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
