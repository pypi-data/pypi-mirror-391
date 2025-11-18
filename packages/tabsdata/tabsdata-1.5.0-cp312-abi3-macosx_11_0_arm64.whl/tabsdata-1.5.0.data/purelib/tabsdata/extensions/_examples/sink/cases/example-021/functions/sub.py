#
#  Copyright 2025. Tabs Data Inc.
#

import os

import tabsdata as td

EX_S3_ACCESS_KEY = os.getenv("EX_S3_ACCESS_KEY")
EX_S3_SECRET_KEY = os.getenv("EX_S3_SECRET_KEY")
EX_S3_REGION = os.getenv("EX_S3_REGION")
EX_S3_URI = os.getenv("EX_S3_URI")

s3_credentials = td.S3AccessKeyCredentials(EX_S3_ACCESS_KEY, EX_S3_SECRET_KEY)


#
# Subscriber that loads CSV data from a TabsData table into iceberg.
#
@td.subscriber(
    tables="persons",
    destination=td.S3Destination(
        uri=[f"{EX_S3_URI}/example-21/$DATA_VERSION.parquet"],
        region=f"{EX_S3_REGION}",
        credentials=s3_credentials,
        # Adding file as db for an Iceberg table in AWS Glue catalog
        catalog=td.AWSGlue(
            definition={
                "name": "default",
                "type": "glue",
                "client.region": EX_S3_REGION,
            },
            tables=["example-21.persons"],
            auto_create_at=f"{EX_S3_URI}/example-21",
            if_table_exists="replace",
            credentials=s3_credentials,
        ),
    ),
)
def sub(people: td.TableFrame) -> td.TableFrame:
    return people
