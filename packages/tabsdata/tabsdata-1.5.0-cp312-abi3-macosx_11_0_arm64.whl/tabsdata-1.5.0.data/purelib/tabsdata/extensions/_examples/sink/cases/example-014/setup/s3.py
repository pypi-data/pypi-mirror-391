#
#  Copyright 2025. Tabs Data Inc.
#

import os
import sys

import boto3
from botocore.exceptions import ClientError

EX_S3_ACCESS_KEY = os.getenv("EX_S3_ACCESS_KEY")
EX_S3_SECRET_KEY = os.getenv("EX_S3_SECRET_KEY")
EX_S3_REGION = os.getenv("EX_S3_REGION")
EX_S3_URI = os.getenv("EX_S3_URI")
LOCAL_PERSONS_FILE = "data/persons.csv"


def _s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=EX_S3_ACCESS_KEY,
        aws_secret_access_key=EX_S3_SECRET_KEY,
        region_name=EX_S3_REGION,
    )


def _bucket_name():
    return EX_S3_URI.replace("s3://", "").split("/")[0]


def setup_s3_bucket():
    s3 = _s3_client()
    bucket = _bucket_name()
    s3.upload_file(LOCAL_PERSONS_FILE, bucket, "persons.csv")


def cleanup_s3_bucket():
    s3 = _s3_client()
    bucket = _bucket_name()
    try:
        s3.delete_object(Bucket=bucket, Key="persons.csv")
    except ClientError:
        pass


def main():
    if len(sys.argv) == 1:
        print("Missing argument. It must be one of: setup-s3, cleanup-s3")
    elif sys.argv[1] == "setup-s3":
        setup_s3_bucket()
    elif sys.argv[1] == "cleanup-s3":
        cleanup_s3_bucket()
    else:
        print(f"Unexpected option {sys.argv[1]}")


if __name__ == "__main__":
    main()
