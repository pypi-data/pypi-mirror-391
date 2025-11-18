#
#  Copyright 2025. Tabs Data Inc.
#

import os
import sys

import pandas as pd
import sqlalchemy as sql

EX_SNOWFLAKE_ACCOUNT = os.getenv("EX_SNOWFLAKE_ACCOUNT")
EX_SNOWFLAKE_USER = os.getenv("EX_SNOWFLAKE_USER")
EX_SNOWFLAKE_PAT = os.getenv("EX_SNOWFLAKE_PAT")
EX_SNOWFLAKE_DATABASE = os.getenv("EX_SNOWFLAKE_DATABASE")
EX_SNOWFLAKE_SCHEMA = os.getenv("EX_SNOWFLAKE_SCHEMA")
EX_SNOWFLAKE_WAREHOUSE = os.getenv("EX_SNOWFLAKE_WAREHOUSE")


def _db_connection():
    return sql.create_engine(
        f"snowflake://{EX_SNOWFLAKE_USER}@{EX_SNOWFLAKE_ACCOUNT}/"
        f"{EX_SNOWFLAKE_DATABASE}/{EX_SNOWFLAKE_SCHEMA}"
        f"?warehouse={EX_SNOWFLAKE_WAREHOUSE}",
        connect_args={"password": EX_SNOWFLAKE_PAT},
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
