#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

CONNECTION_PARAMETERS = {
    "account": os.getenv("EX_SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("EX_SNOWFLAKE_USER"),
    "password": os.getenv("EX_SNOWFLAKE_PAT"),
    "role": os.getenv("EX_SNOWFLAKE_ROLE"),
    "database": os.getenv("EX_SNOWFLAKE_DATABASE"),
    "schema": os.getenv("EX_SNOWFLAKE_SCHEMA"),
    "warehouse": os.getenv("EX_SNOWFLAKE_WAREHOUSE"),
}


#
# Subscriber that loads a TabsData table into a Snowflake table.
#
@td.subscriber(
    tables="persons",
    destination=td.SnowflakeDestination(CONNECTION_PARAMETERS, "persons"),
)
def sub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
