import os
import sys

import pandas as pd
import sqlalchemy as sql

DB_HOST = os.getenv("ORACLE_HOST", "localhost")
DB_PORT = int(os.getenv("ORACLE_PORT", "1521"))
DB_USER = os.getenv("ORACLE_USER", "system")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD", "oracle")
DB_DATABASE = os.getenv("ORACLE_DATABASE", "FREE")


def _db_connection():
    return sql.create_engine(
        f"oracle+oracledb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )


def setup_database():
    engine = _db_connection()
    conn = engine.connect()

    drop_table = "drop table if exists persons"
    conn.execute(sql.text(drop_table))

    create_table = """
    create table persons (
      seq INT NOT NULL PRIMARY KEY,
      first VARCHAR(255),
      last VARCHAR(255),
      age INT,
      city VARCHAR(255),
      state VARCHAR(255),
      zip INT
    )
    """
    conn.execute(sql.text(create_table))


def load_table():
    df = pd.read_csv("data/persons.csv")
    df.to_sql("persons", con=_db_connection(), if_exists="append", index=False)


def show_table():
    df = pd.read_sql("SELECT * FROM system.persons", con=_db_connection())
    print(df)


def main():
    if len(sys.argv) == 1:
        print(
            "Missing argument. It must be one of: create-database, "
            "load-table, show-table"
        )
    elif sys.argv[1] == "create-database":
        setup_database()
    elif sys.argv[1] == "load-table":
        load_table()
    elif sys.argv[1] == "show-table":
        show_table()
    else:
        print(f"Unexpected option {sys.argv[1]}")


if __name__ == "__main__":
    main()
