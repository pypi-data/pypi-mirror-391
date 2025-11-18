#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

EX_SALESFORCE_USERNAME = os.getenv("EX_SALESFORCE_USERNAME")
EX_SALESFORCE_PASSWORD = os.getenv("EX_SALESFORCE_PASSWORD")
EX_SALESFORCE_SECURITY_TOKEN = os.getenv("EX_SALESFORCE_SECURITY_TOKEN")
EX_SALESFORCE_INSTANCE_URL = os.getenv("EX_SALESFORCE_INSTANCE_URL")


#
# Publisher that loads Salesforce data from a fixed table into a TabsData table.
#
@td.publisher(
    source=td.SalesforceSource(
        username=EX_SALESFORCE_USERNAME,
        password=EX_SALESFORCE_PASSWORD,
        security_token=EX_SALESFORCE_SECURITY_TOKEN,
        query="SELECT Name FROM Contact",
    ),
    tables="persons",
)
def pub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
