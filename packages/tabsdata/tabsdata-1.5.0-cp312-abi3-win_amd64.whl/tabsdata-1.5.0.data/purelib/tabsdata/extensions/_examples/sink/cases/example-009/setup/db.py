import os
import sys

import pandas as pd
import sqlalchemy as sql

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "root")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_DATABASE = os.getenv("POSTGRES_DATABASE", "example_08")


def _db_connection():
    return sql.create_engine(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )


def setup_database():
    engine = _db_connection()
    conn = engine.connect()

    drop_table = "drop table if exists persons"
    conn.execute(sql.text(drop_table))

    create_table = """
    create table persons (
      id INT NOT NULL PRIMARY KEY,
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
    df.to_sql("persons", con=_db_connection(), if_exists="replace", index=False)


def show_table():
    df = pd.read_sql("SELECT * FROM persons", con=_db_connection())
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
