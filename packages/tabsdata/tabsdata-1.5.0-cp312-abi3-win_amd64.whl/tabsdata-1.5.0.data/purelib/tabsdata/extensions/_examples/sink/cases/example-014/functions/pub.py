#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td
import tabsdata.tableframe as tdf

EX_S3_ACCESS_KEY = os.getenv("EX_S3_ACCESS_KEY")
EX_S3_SECRET_KEY = os.getenv("EX_S3_SECRET_KEY")
EX_S3_REGION = os.getenv("EX_S3_REGION")
EX_S3_URI = os.getenv("EX_S3_URI")

s3_credentials = td.S3AccessKeyCredentials(EX_S3_ACCESS_KEY, EX_S3_SECRET_KEY)


#
# Publisher that loads CSV data from a fixed S3 file into a TabsData table.
#
@td.publisher(
    source=td.S3Source(
        f"{EX_S3_URI}/persons.csv",
        credentials=s3_credentials,
        region=EX_S3_REGION,
    ),
    tables="persons",
)
def pub(persons: tdf.TableFrame) -> tdf.TableFrame:
    return persons
