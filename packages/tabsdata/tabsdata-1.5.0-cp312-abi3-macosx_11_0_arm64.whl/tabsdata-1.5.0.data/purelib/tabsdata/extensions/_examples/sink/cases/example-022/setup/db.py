#
#  Copyright 2025. Tabs Data Inc.
#

import os
import sys

import pandas as pd
import sqlalchemy as sql

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "mysql")
DB_DATABASE = os.getenv("MYSQL_DATABASE", "example_22")


def create_database():
    engine = sql.create_engine(
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    )
    conn = engine.connect()
    conn.execute(sql.text(f"CREATE DATABASE IF NOT EXISTS {DB_DATABASE}"))
    conn.close()


def _db_connection():
    return sql.create_engine(
        "mysql+mysqlconnector://"
        f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )


def setup_database():
    engine = _db_connection()
    conn = engine.connect()

    drop_table = "drop table if exists persons"
    conn.execute(sql.text(drop_table))


def show_table():
    df = pd.read_sql("SELECT * FROM persons", con=_db_connection())
    print(df)


def main():
    if len(sys.argv) == 1:
        print("Missing argument. It must be one of: create-database, show-table")
    elif sys.argv[1] == "create-database":
        create_database()
        setup_database()
    elif sys.argv[1] == "show-table":
        show_table()
    else:
        print(f"Unexpected option {sys.argv[1]}")


if __name__ == "__main__":
    main()
