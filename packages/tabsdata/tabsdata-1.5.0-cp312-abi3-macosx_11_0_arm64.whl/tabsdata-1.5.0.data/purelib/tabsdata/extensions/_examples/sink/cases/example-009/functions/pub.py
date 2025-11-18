#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "root")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_DATABASE = os.getenv("POSTGRES_DATABASE", "example_09")


@td.publisher(
    source=td.PostgresSource(
        uri=f"postgres://{DB_HOST}:{DB_PORT}/{DB_DATABASE}",
        query="select * from persons",
        credentials=td.UserPasswordCredentials(DB_USER, DB_PASSWORD),
    ),
    tables="persons",
)
def pub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons


def test_x():
    import polars as pl

    df = pl.read_database_uri(
        query="select * from persons", uri="oracle://system:oracle@localhost:1521/FREE"
    )
    print(df)
