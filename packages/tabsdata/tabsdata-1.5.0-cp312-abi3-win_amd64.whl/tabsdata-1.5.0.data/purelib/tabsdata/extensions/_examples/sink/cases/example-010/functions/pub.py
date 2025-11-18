#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td

DB_HOST = os.getenv("ORACLE_HOST", "localhost")
DB_PORT = int(os.getenv("ORACLE_PORT", "1521"))
DB_USER = os.getenv("ORACLE_USER", "system")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD", "oracle")
DB_DATABASE = os.getenv("ORACLE_DATABASE", "FREE")


@td.publisher(
    source=td.OracleSource(
        uri=f"oracle://{DB_HOST}:{DB_PORT}/{DB_DATABASE}",
        query="select * from persons",
        credentials=td.UserPasswordCredentials(DB_USER, DB_PASSWORD),
    ),
    tables="persons",
)
def pub(persons: td.TableFrame) -> td.TableFrame:
    return persons


def test_x():
    import polars as pl

    df = pl.read_database_uri(
        query="select * from persons", uri="oracle://system:oracle@localhost:1521/FREE"
    )
    print(df)
