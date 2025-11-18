#
#  Copyright 2025. Tabs Data Inc.
#

import os
import sys

import pandas as pd
from azure.storage.blob import BlobServiceClient

EX_AZ_ACCOUNT_NAME = os.getenv("EX_AZ_ACCOUNT_NAME")
EX_AZ_ACCOUNT_KEY = os.getenv("EX_AZ_ACCOUNT_KEY")
EX_AZ_URI = os.getenv("EX_AZ_URI")
AZURE_BLOB_PATH = "example_18/persons.csv"
LOCAL_PERSONS_FILE = "data/persons.csv"


def _blob_service():
    return BlobServiceClient(
        f"https://{EX_AZ_ACCOUNT_NAME}.blob.core.windows.net",
        credential=EX_AZ_ACCOUNT_KEY,
    )


def _container_name():
    return EX_AZ_URI.replace("az://", "").split("/")[0]


def upload_csv_to_azure():
    blob_service = _blob_service()
    container_client = blob_service.get_container_client(_container_name())
    blob_client = container_client.get_blob_client(AZURE_BLOB_PATH)
    with open(LOCAL_PERSONS_FILE, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {LOCAL_PERSONS_FILE} to Azure Blob Storage as {AZURE_BLOB_PATH}.")


def read_from_azure():
    blob_service = _blob_service()
    container_client = blob_service.get_container_client(_container_name())
    blob_client = container_client.get_blob_client(AZURE_BLOB_PATH)
    stream = blob_client.download_blob()
    df = pd.read_csv(stream)
    print(df)


def cleanup_azure_blob():
    blob_service = _blob_service()
    container_client = blob_service.get_container_client(_container_name())
    blob_client = container_client.get_blob_client(AZURE_BLOB_PATH)
    try:
        blob_client.delete_blob()
        print(f"Deleted {AZURE_BLOB_PATH} from Azure Blob Storage.")
    except Exception as e:
        print(f"{AZURE_BLOB_PATH} does not exist in Azure Blob Storage: {e}.")


def main():
    if len(sys.argv) == 1:
        print(
            "Missing argument. It must be one of: upload-azure, read-azure,"
            " cleanup-azure"
        )
    elif sys.argv[1] == "upload-azure":
        upload_csv_to_azure()
    elif sys.argv[1] == "read-azure":
        read_from_azure()
    elif sys.argv[1] == "cleanup-azure":
        cleanup_azure_blob()
    else:
        print(f"Unexpected option {sys.argv[1]}")


if __name__ == "__main__":
    main()
