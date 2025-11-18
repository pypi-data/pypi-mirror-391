#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

EX_DATABRICKS_HOST = os.getenv("EX_DATABRICKS_HOST")
EX_DATABRICKS_TOKEN = os.getenv("EX_DATABRICKS_TOKEN")
EX_DATABRICKS_SCHEMA = os.getenv("EX_DATABRICKS_SCHEMA")
EX_DATABRICKS_CATALOG = os.getenv("EX_DATABRICKS_CATALOG")
EX_DATABRICKS_VOLUME = os.getenv("EX_DATABRICKS_VOLUME")
EX_DATABRICKS_WAREHOUSE_NAME = os.getenv("EX_DATABRICKS_WAREHOUSE_NAME")
EX_DATABRICKS_WAREHOUSE_ID = os.getenv("EX_DATABRICKS_WAREHOUSE_ID")


#
# Subscriber that loads a TabsData table into a Databricks table.
#
@td.subscriber(
    tables="persons",
    destination=td.DatabricksDestination(
        EX_DATABRICKS_HOST,
        EX_DATABRICKS_TOKEN,
        f"{EX_DATABRICKS_CATALOG}.{EX_DATABRICKS_SCHEMA}.persons",
        EX_DATABRICKS_VOLUME,
        warehouse=EX_DATABRICKS_WAREHOUSE_NAME,
    ),
)
def sub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
