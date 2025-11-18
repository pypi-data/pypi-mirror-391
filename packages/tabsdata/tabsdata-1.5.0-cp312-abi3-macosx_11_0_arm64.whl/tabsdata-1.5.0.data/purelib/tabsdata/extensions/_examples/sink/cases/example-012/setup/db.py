#
#  Copyright 2025. Tabs Data Inc.
#

import os
import re
import sys

import pandas as pd
import sqlalchemy as sql

EX_DATABRICKS_HOST = os.getenv("EX_DATABRICKS_HOST")
EX_DATABRICKS_TOKEN = os.getenv("EX_DATABRICKS_TOKEN")
EX_DATABRICKS_SCHEMA = os.getenv("EX_DATABRICKS_SCHEMA")
EX_DATABRICKS_CATALOG = os.getenv("EX_DATABRICKS_CATALOG")
EX_DATABRICKS_VOLUME = os.getenv("EX_DATABRICKS_VOLUME")
EX_DATABRICKS_WAREHOUSE_NAME = os.getenv("EX_DATABRICKS_WAREHOUSE_NAME")
EX_DATABRICKS_WAREHOUSE_ID = os.getenv("EX_DATABRICKS_WAREHOUSE_ID")


def _db_connection():
    def get_host(h):
        return re.sub(r"^https?://", "", h)

    host = get_host(EX_DATABRICKS_HOST)
    return sql.create_engine(
        f"databricks://token:{EX_DATABRICKS_TOKEN}@{host}"
        f"?schema={EX_DATABRICKS_SCHEMA}&catalog={EX_DATABRICKS_CATALOG}",
        connect_args={"http_path": f"/sql/1.0/warehouses/{EX_DATABRICKS_WAREHOUSE_ID}"},
    )


def cleanup_database():
    engine = _db_connection()
    conn = engine.connect()

    drop_table = "DROP TABLE IF EXISTS persons"
    conn.execute(sql.text(drop_table))


def show_table():
    df = pd.read_sql("SELECT * FROM persons", con=_db_connection())
    print(df)


def main():
    if len(sys.argv) == 1:
        print("Missing argument. It must be one of: cleanup-database, show-table")
    elif sys.argv[1] == "cleanup-database":
        cleanup_database()
    elif sys.argv[1] == "show-table":
        show_table()
    else:
        print(f"Unexpected option {sys.argv[1]}")


if __name__ == "__main__":
    main()
