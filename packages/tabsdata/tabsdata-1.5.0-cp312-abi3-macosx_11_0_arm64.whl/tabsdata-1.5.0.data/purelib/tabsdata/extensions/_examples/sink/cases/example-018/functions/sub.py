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
# Subscriber that loads CSV data a TabsData table into Azure.
#
@td.subscriber(
    tables="persons",
    destination=td.AzureDestination(
        f"{EX_AZ_URI}/example_18/persons.csv",
        td.AzureAccountKeyCredentials(EX_AZ_ACCOUNT_NAME, EX_AZ_ACCOUNT_KEY),
    ),
)
def sub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
