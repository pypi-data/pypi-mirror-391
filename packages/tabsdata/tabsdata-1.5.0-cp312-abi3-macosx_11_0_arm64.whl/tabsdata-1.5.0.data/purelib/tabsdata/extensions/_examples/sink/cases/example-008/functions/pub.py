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
DB_DATABASE = os.getenv("MYSQL_DATABASE", "example_08")


@td.publisher(
    source=td.MySQLSource(
        uri=f"mysql://{DB_HOST}:{DB_PORT}/{DB_DATABASE}",
        query="select * from persons",
        credentials=td.UserPasswordCredentials(DB_USER, DB_PASSWORD),
    ),
    tables="persons",
)
def pub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
