#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

EX_AZ_ACCOUNT_NAME = os.getenv("EX_AZ_ACCOUNT_NAME")
EX_AZ_ACCOUNT_KEY = os.getenv("EX_AZ_ACCOUNT_KEY")
EX_AZ_URI = os.getenv("EX_AZ_URI")


#
# Publisher that loads CSV data from a Azure into a TabsData table.
#
@td.publisher(
    source=td.AzureSource(
        f"{EX_AZ_URI}/example_17/persons.csv",
        td.AzureAccountKeyCredentials(EX_AZ_ACCOUNT_NAME, EX_AZ_ACCOUNT_KEY),
    ),
    tables="persons",
)
def pub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
