#
#  Copyright 2025. Tabs Data Inc.
#

import os
import sys

import boto3
from botocore.exceptions import ClientError
from pyiceberg.catalog import load_catalog

EX_S3_ACCESS_KEY = os.getenv("EX_S3_ACCESS_KEY")
EX_S3_SECRET_KEY = os.getenv("EX_S3_SECRET_KEY")
EX_S3_REGION = os.getenv("EX_S3_REGION")
EX_S3_URI = os.getenv("EX_S3_URI")


def read_from_iceberg():
    catalog = load_catalog(
        "default",
        **{
            "type": "glue",
            "client.region": EX_S3_REGION,
            "client.access-key-id": EX_S3_ACCESS_KEY,
            "client.secret-access-key": EX_S3_SECRET_KEY,
        },
    )
    table = catalog.load_table("example-21.persons")
    data = table.scan().to_pandas()
    print(data)


def setup_iceberg():
    bucket = EX_S3_URI.replace("s3://", "").split("/")[0]
    location_uri = f"s3://{bucket}/example-21"

    glue = boto3.client(
        "glue",
        aws_access_key_id=EX_S3_ACCESS_KEY,
        aws_secret_access_key=EX_S3_SECRET_KEY,
        region_name=EX_S3_REGION,
    )

    glue.create_database(
        DatabaseInput={
            "Name": "example-21",
            "LocationUri": location_uri,
            "Description": "Iceberg database for example-21",
        }
    )


def cleanup_iceberg():
    bucket = EX_S3_URI.replace("s3://", "").split("/")[0]
    prefix = "example-21"
    s3 = boto3.client(
        "s3",
        aws_access_key_id=EX_S3_ACCESS_KEY,
        aws_secret_access_key=EX_S3_SECRET_KEY,
        region_name=EX_S3_REGION,
    )
    # Delete all S3 objects under the prefix
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            try:
                s3.delete_object(Bucket=bucket, Key=obj["Key"])
            except ClientError:
                pass

    glue = boto3.client(
        "glue",
        aws_access_key_id=EX_S3_ACCESS_KEY,
        aws_secret_access_key=EX_S3_SECRET_KEY,
        region_name=EX_S3_REGION,
    )
    # Drop the Glue table if it exists
    try:
        glue.delete_table(DatabaseName="example-21", Name="persons")
    except glue.exceptions.EntityNotFoundException:
        pass
    # Drop the Glue database if it exists
    try:
        glue.delete_database(Name="example-21")
    except glue.exceptions.EntityNotFoundException:
        pass


def main():
    if len(sys.argv) == 1:
        print(
            "Missing argument. It must be one of: read-iceberg, setup-iceberg,"
            " cleanup-iceberg"
        )
    elif sys.argv[1] == "setup-iceberg":
        setup_iceberg()
    elif sys.argv[1] == "read-iceberg":
        read_from_iceberg()
    elif sys.argv[1] == "cleanup-iceberg":
        cleanup_iceberg()
    else:
        print(f"Unexpected option {sys.argv[1]}")


if __name__ == "__main__":
    main()
